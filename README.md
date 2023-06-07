# Personal Research Assistant
This is a GPT-based personal research assistant, it helps query your obsidian database (by performing semantic search with OpenAI's API) and Automatically summarize PDFs for skimming.

# Setup
Please use `python3` and install the dependencies:
```bash
pip install -r requirements.txt
```
Create a `settings.py` file in the root folder with the following content:

```python
OPENAI_API_KEY= "<YOUR-OPENAI-API-KEY>"
OBSIDIAN_PATH = "<ResearchFolder>"
PDF_DICT_PATH = "pdf_dict.json"
PDF_RESULT_PATH = "pdf_result.json"
PDF_RESULT_PATH_LIGHT = "pdf_result_light.json"
PDF_DB_DIR = "pdf_db"
PDF_RESULT_DIR = "pdf_result"
PDF_RESULT_DIR_LIGHT = "pdf_result_light"
```

Where `<ResearchFolder` is an obsidian vault:
```shell
OBSIDIAN_PATH = "/Users/thanhdatn/ResearchVault/Research/"
```

# Usage
## Querying obsidian
To start querying the vault, call: 
```shell
python obsidian_interface.py
```
This will give you an interface where each time you enter, it queries the obsidian database and return an answer. For example
```shell
query: [CRITICAL] Summarize the direction in neural network repair

Answer: The direction in neural network repair involves various approaches such as verification-based adjustments to output layer weights, inductive synthesis, constraint-based repair, and causal-based testing and repair using structural causal models. 
Some challenges include scalability issues and limited effectiveness in repairing neural networks. Recent developments focus on causality-aware coverage criteria and model-centric fault localization to improve repair performance.

The sources are from the following files:  Causality-Based Neural Network Repair (CARE).md, Neural Network Repair.md
```
The tag `[CRITICAL]` as above is put in case you want more precise and comprehensive answer from `gpt-4` (The price will be more expensive also, so please set your limit on OpenAI usage page before using), or you can just put a query without any tag to query `gpt-3.5-turbo`.

## Summarize PDFs
If you want to summarize pdfs in your obsidian vaults, please make sure that the pdf is in the root folder of the vault (e.g., `<OBSIDIAN_PATH>/your_pdf.pdf`) and run the following script:
```shell
python pdf_utils.py --light --pdf_files <file_1.pdf> <file_2.pdf> ...
```
It will returns the following answer, which is cached for the next calls
