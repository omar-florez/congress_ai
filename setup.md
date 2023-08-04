## Virtual environment
* python -m venv .venv
* source .venv/bin/activate
* pip freeze > requirements.txt

## Install dependencies
* requirements.txt
* pip install streamlit-d3graph
* pip install langchain
* pip install openai

--------
## OCR
* pip install pdf2image
* pip install langchain
* pip install pypdf
* pip install pytesseract
* pip3 install opencv-python

## Linux:
* sudo apt-get install poppler-utils
* sudo apt-get install libleptonica-dev tesseract-ocr libtesseract-dev python3-pil tesseract-ocr-eng tesseract-ocr-script-latn
## Mac:
* brew install tesseract

--------
* pip install google-api-python-client
* pip install wikipedia

--------
## Run 

### Virtual environment:
source .venv/bin/activate

#### Run crawler (get metadata in JSONL format from html files):
* python data/peru/run_crawler.py

#### Run congress agent:
* python opinion_networks/run.py

pip3 install graphviz
brew install graphviz