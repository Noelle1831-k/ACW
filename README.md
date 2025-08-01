<p align="center">
     <a href="https://arxiv.org/abs/2402.07518">
<img width="765" alt="image" src="assets/title.png">
     </a>
   <p align="center">
    <a><strong>Boquan Li<sup>1,2</sup></strong></a>
    .
    <a><strong>Zirui Fu<sup>1</sup></strong></a>
    .
    <a><strong>Mengdi Zhang<sup>2</sup></strong></a>
    .
    <a><strong>Peixin Zhang<sup>2</sup></strong></a>
    .
    <a><strong>Jun Sun<sup>2</sup></strong></a>
    .
    <a><strong>Xingmei Wang<sup>1</sup></strong></a>
   
    
<p align="center">
    <strong><sup>1</sup>Harbin Engineering University</strong> &nbsp;
    <strong><sup>2</sup>Singapore Management University</strong> &nbsp;
<p align="center">
    <a href='https://arxiv.org/abs/2402.07518'>
      <img src='https://img.shields.io/badge/arXiv-PDF-green?style=flat&logo=arXiv&logoColor=green' alt='arXiv PDF'>
         </a>
  

# ACW : AI-Generated Code Watermarking  <a id="acw"></a>


Large language models (LLMs) have significantly enhanced the usability of AI-generated code, providing effective assistance to programmers. 
This advancement also raises ethical and legal concerns, such as academic dishonesty or the generation of malicious code.
For accountability, it is imperative to detect whether a piece of code is AI-generated.
Watermarking is broadly considered a promising solution and has been successfully applied to identify LLM-generated text. 
However, existing efforts on code are far from ideal, suffering from limited universality and excessive time and memory consumption.
In this work, we propose a plug-and-play watermarking approach for AI-generated code detection, named **ACW** (**A**I **C**ode **W**atermarking).
**ACW** is training-free and works by selectively applying a set of carefully-designed, semantic-preserving and idempotent code transformations to LLM code outputs.
The presence or absence of the transformations serves as implicit watermarks, enabling the detection of AI-generated code.
Our experimental results show that ACW effectively detects AI-generated code, preserves code utility, and is resilient against code optimizations.
Especially, **ACW** is efficient and is universal across different LLMs, addressing the limitations of existing approaches.
<img src="assets/Overview.png">

</p>

## Quick Start

### Step 1: Install Dependencies

Install the required Python libraries by running:

```bash
pip install -r requirements.txt
```

Login Sourcery API by running (please apply for a token on the [official Sourcery website](https://docs.sourcery.ai/Coding-Assistant/Guides/Getting-Started/CI/) if necessary):

```bash
sourcery login --token $SOURCERY_TOKEN
```

### Step 2: Prepare the Dataset

We have provided our complete experimental data containing AI-generated and human-written code.
If additional data is necessary, please add its relative path of the dataset to the  **folder_list.py** file, like this:

```python
folder_paths = ["G/Data"]
```

### Step 3: Get the Results

#### Evaluation results on discriminability

```bash
python RQ1-get-results.py
```

The results will be saved as _output.json_, containing the number of positive and negative examples for computation.

#### Evaluation results on utility

##### Pass Rate on APPS

After setting up and downloading the APPS dataset as instructed on the [APPS project page](https://github.com/hendrycks/apps), 
use the following command to perform a pass rate test on the APPS code data:

```bash
python test_one_solution.py -r <code_dir> -t <test_dir> --save /path/to/save_dir --print_results
```

##### Pass Rate based on MBPP and HumanEval:

First, please consolidate the code data into a JSONL file:

```bash
python folder_to_jsonl.py convert_py_folder_to_jsonl --input_folder=<code_dir>
```

After setting up as instructed on the [mxeval project page](https://github.com/amazon-science/mxeval), 
testing the pass rate using the command::

```bash
evaluate_functional_correctness <mbpp_data>.jsonl --problem_file data/mbxp/mbpp_release_v1.jsonl
evaluate_functional_correctness <humaneval_data>.jsonl --problem_file data/multilingual_humaneval/HumanEval.jsonl
```

#### Evaluation results on resilience

Running the following command for testing:
```bash
python one-click-get-results_ruff_attack.py folder_process --strength= <1 or 2>
```
Strength 1 and 2 correspond to the Default-level and Maximum-level modifications.

## Overview of this repository

- [Quick Start](#quick-start)
- [Appendix](#appendix)
    - [Transformation Rules](#transformation-rules-of-acw)
    - [Evaluation of Multi-bit Watermarking](#evaluation-results-of-multi-bit-watermarking)
- [Contact](#contact)

## Appendix

### Transformation Rules

Transformation Rules.
<img src="assets/rules.png">

### Evaluation of Multi-bit Watermarking

| Dataset | BitACC (%)-0000 |                | BitACC (%)-0101 |                | BitACC (%)-1010 |                | BitACC (%)-1111 |                |
|---------|-----------------|----------------|-----------------|----------------|-----------------|----------------|-----------------|----------------|
|         | Uncorrected     | Corrected      | Uncorrected     | Corrected      | Uncorrected     | Corrected      | Uncorrected     | Corrected      |
| MBPP-GPT-4 | 78.14          | **100**        | 92.69           | **99.48**      | 86.89           | **100**        | 98.91           | **98.91**      |
| APPS-GPT-4 | 85.98          | **99.63**      | 93.03           | **99.35**      | 81.92           | **99.63**      | 100             | **100**        |



The above table presents our results.
Following our error-correction strategies, in this experiment, we collect the watermarked codes with four applicable transformations in MBPP-GPT-4 and APPS-GPT-4 datasets, i.e., each code snippet is embedded with 4-bit watermarks, where the first two bits are original watermarks and the next two bits are generated based on BCH.
We present the BitACC results before and after error corrections, where the former uncorrected ones are intermediate results for comparisons.
As shown by the result, **ACW** achieves promising performance on watermark extraction, and the results are significantly increased based on error correction.
Especially, as the bold values in the table, all the BitACC results are over 98\% after correction, indicating that **ACW** has the ability to embed and extract multi-bit watermarks, and has the potential to be applied to more tasks beyond AI-generated code detection. 

## Contact
We are looking forward to any valuable questions or suggestions, please feel free to contact us at ```noelle@hrbeu.edu.cn```