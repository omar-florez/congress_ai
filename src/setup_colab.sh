git clone https://github.com/omar-florez/congress_ai.git
pip install -qU transformers accelerate einops langchain xformers bitsandbytes
pip install -r congress_ai/requirements.txt
pip install openai

#cd congress_ai/src/
#python opinion_networks/run_llama.py
#git add .; git commit -a --amend; git push orign main