import os
import argparse
from pathlib import Path
import jsonlines
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer
)
from peft import get_peft_model, LoraConfig, TaskType, PeftModel

def prepare_dataset(data_path: str | Path, tokenizer: AutoTokenizer, max_source_length: int = 512, max_target_length: int = 512):
    dataset = load_dataset("json", data_files=str(data_path), split="train")

    def preprocess_function(examples):
        inputs = examples["transformed"]
        targets = examples["original"]
        
        model_inputs = tokenizer(inputs, max_length=max_source_length, padding="max_length", truncation=True)
        
        labels = tokenizer(text_target=targets, max_length=max_target_length, padding="max_length", truncation=True)
        model_inputs["labels"] = labels["input_ids"]
        
        return model_inputs

    tokenized_dataset = dataset.map(preprocess_function, batched=True, remove_columns=dataset.column_names)
    return tokenized_dataset


def run_inference(
    model_dir: str | Path,
    base_model: str,
    source_codes: list[str],
    max_new_tokens: int = 512,
    num_beams: int = 4,
) -> list[str]:
    """Load the saved LoRA adapter and run code transformation inference."""
    model_dir = Path(model_dir)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"\n[Inference] Loading tokenizer and adapter from {model_dir}")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    base = AutoModelForSeq2SeqLM.from_pretrained(base_model)
    model = PeftModel.from_pretrained(base, model_dir)
    model.eval().to(device)

    results: list[str] = []
    for i, code in enumerate(source_codes, 1):
        inputs = tokenizer(
            code,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True,
        ).to(device)

        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                num_beams=num_beams,
                early_stopping=True,
            )
        transformed = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        print(f"\n[Inference {i}/{len(source_codes)}]")
        print("── Input  ──\n", code)
        print("── Output ──\n", transformed)
        results.append(transformed)

    return results


def main():
    parser = argparse.ArgumentParser(description="Fine-tune CodeT5p with LoRA.")
    parser.add_argument("--model-name", default="Salesforce/codet5p-770m-py", help="Base model name or path")
    parser.add_argument("--train-data", required=True, help="Path to the training JSONL file")
    parser.add_argument("--val-data", help="Path to the validation JSONL file (Optional)")
    parser.add_argument("--output-dir", default="./codet5p-lora-output", help="Output directory for model and checkpoints")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=8, help="Training batch size")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--lora-r", type=int, default=8, help="LoRA rank (r)")
    parser.add_argument("--lora-alpha", type=int, default=32, help="LoRA alpha variable")
    parser.add_argument("--lora-dropout", type=float, default=0.05, help="LoRA dropout rate")
    # Inference
    parser.add_argument("--infer-input", type=str, default=None,
                        help="Source code string to transform after training")
    parser.add_argument("--infer-file",  type=str, default=None,
                        help="JSONL file for batch inference after training (reads 'transformed' field)")
    parser.add_argument("--num-beams",       type=int, default=4,   help="Beam search width for inference")
    parser.add_argument("--max-new-tokens",  type=int, default=512, help="Max tokens to generate per sample")

    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    print(f"Loading tokenizer and model: {args.model_name}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name)

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=["q", "v"],
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type=TaskType.SEQ_2_SEQ_LM
    )

    print("Configuring PEFT LoRA model...")
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    model.to(device)

    print("Preparing datasets...")
    train_dataset = prepare_dataset(args.train_data, tokenizer)
    eval_dataset = prepare_dataset(args.val_data, tokenizer) if args.val_data and os.path.exists(args.val_data) else None

    data_collator = DataCollatorForSeq2Seq(
        tokenizer,
        model=model,
        label_pad_token_id=tokenizer.pad_token_id,
        pad_to_multiple_of=8
    )

    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        eval_strategy="epoch" if eval_dataset else "no",
        save_strategy="epoch",
        learning_rate=args.lr,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        weight_decay=0.01,
        save_total_limit=3,
        num_train_epochs=args.epochs,
        predict_with_generate=True,
        fp16=torch.cuda.is_available(),
        logging_steps=10,
        report_to="none"
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )

    print("Starting training...")
    trainer.train()

    print(f"Saving final adapter weights to {args.output_dir}")
    trainer.model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print("Fine-tuning complete!")

    # ── Post-training inference (optional) ────────────────────────────────
    sources: list[str] = []
    if args.infer_input:
        sources.append(args.infer_input)
    if args.infer_file and os.path.exists(args.infer_file):
        with jsonlines.open(args.infer_file) as reader:
            sources.extend(obj["transformed"] for obj in reader)

    if sources:
        run_inference(
            model_dir=args.output_dir,
            base_model=args.model_name,
            source_codes=sources,
            max_new_tokens=args.max_new_tokens,
            num_beams=args.num_beams,
        )


if __name__ == "__main__":
    main()
