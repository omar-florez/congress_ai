git clone https://github.com/omar-florez/congress_ai.git
pip install -qU transformers accelerate einops langchain xformers bitsandbytes
pip install -r congress_ai/requirements.txt
pip install openai

#cd congress_ai/src/
#python opinion_networks/run_llama.py -k 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 -h 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
#git add .; git commit -m "Changes on opinion networks"; git push origin main