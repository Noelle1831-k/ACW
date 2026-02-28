from __future__ import annotations

import argparse
import enum
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import jsonlines
from openai import OpenAI, APIError, RateLimitError
from tqdm import tqdm


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("llm_codegen")


SYSTEM_PROMPT = (
    "You are a professional Python programmer. "
    "Complete the given problem with valid, compilable Python code."
)
class TaskType(enum.Enum):
    RENAME  = "rename"
    REWRITE = "rewrite"


TASK_PROMPTS: dict[TaskType, str] = {
    TaskType.RENAME: (
        "\n\nRename the local variable and function names "
        "in the following Python code. You must strictly preserve the "
        "input argument names and return values, and do not alter the "
        "logic, structure, or implementation details of the code."
    ),
    TaskType.REWRITE: (
        "\n\nRewrite the internal logic of the following Python code completely, "
        "including changes to the algorithms, control structures, and variable names. "
        "You must strictly preserve the function signature, including the function name, "
        "input arguments, and return types, and ensure that the functionality remains "
        "exactly the same."
    ),
}


def build_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")

    if not api_key:
        raise EnvironmentError("Environment variable OPENAI_API_KEY is not set.")
    if not base_url:
        raise EnvironmentError("Environment variable OPENAI_BASE_URL is not set.")

    return OpenAI(api_key=api_key, base_url=base_url)

def generate_code(
    client: OpenAI,
    model: str,
    idx: int,
    data: dict,
    task_type: TaskType = TaskType.RENAME,
    max_retries: int = 3,
) -> dict:
    prompt = data["completion"]
    task_id = data["task_id"]

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt + TASK_PROMPTS[task_type]},
                ],
                temperature=0.7,
            )
            generated = response.choices[0].message.content
            logger.debug("idx=%d task_id=%s generated %d chars", idx, task_id, len(generated))
            return {"task_id": task_id, "completion": generated, "language": "python", "task_type": task_type.value}

        except RateLimitError as exc:
            wait = 2 ** attempt
            logger.warning("Rate-limited on idx=%d (attempt %d/%d). Retrying in %ds. %s",
                           idx, attempt, max_retries, wait, exc)
            time.sleep(wait)
        except APIError as exc:
            logger.error("API error on idx=%d (attempt %d/%d): %s", idx, attempt, max_retries, exc)
            if attempt == max_retries:
                raise

    raise RuntimeError(f"All {max_retries} attempts failed for idx={idx}")



def run_pipeline(
    input_file: Path,
    start_idx: int,
    end_idx: int,
    model: str,
    task_type: TaskType,
    max_workers: int,
    max_retries: int,
) -> None:
    logger.info("Loading prompts from %s", input_file)
    with jsonlines.open(input_file) as reader:
        prompts = list(reader)
    logger.info("Loaded %d prompts. Processing indices [%d, %d].", len(prompts), start_idx, end_idx)

    client = build_client()
    output_file = input_file.parent / f"generated_{start_idx}-{end_idx}_{model}_{task_type.value}.jsonl"

    indices = range(start_idx, min(end_idx + 1, len(prompts)))
    with jsonlines.open(output_file, mode="w") as writer:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(generate_code, client, model, i, prompts[i], task_type, max_retries): i
                for i in indices
            }
            for future in tqdm(as_completed(futures), total=len(futures), desc="Generating"):
                i = futures[future]
                try:
                    writer.write(future.result())
                except Exception as exc:
                    logger.error("Failed for idx=%d: %s", i, exc)

    logger.info("Results saved to %s", output_file)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LLM batch code generation pipeline.")
    parser.add_argument("--input",       type=Path,  default=Path("CodeNet.jsonl"), help="Input JSONL file")
    parser.add_argument("--start",       type=int,   default=0,                    help="Start index (inclusive)")
    parser.add_argument("--end",         type=int,   default=999,                  help="End index (inclusive)")
    parser.add_argument("--model",       type=str,   default=os.getenv("MODEL_NAME", "gpt-4o"), help="Model name")
    parser.add_argument("--task-type",   type=TaskType, default=TaskType.RENAME,
                        choices=list(TaskType),
                        help="Transformation type: 'rename' (variable/function renaming) or 'rewrite' (logic rewrite)")
    parser.add_argument("--workers",     type=int,   default=int(os.getenv("MAX_WORKERS", "20")), help="Thread workers")
    parser.add_argument("--max-retries", type=int,   default=int(os.getenv("MAX_RETRIES", "3")),  help="Retry limit")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(
        input_file=args.input,
        start_idx=args.start,
        end_idx=args.end,
        model=args.model,
        task_type=args.task_type,
        max_workers=args.workers,
        max_retries=args.max_retries,
    )
