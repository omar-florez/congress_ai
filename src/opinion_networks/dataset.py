"""Node that run map-reduce on opinions"""
from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.mapreduce import MapReduceChain
from langchain.prompts import PromptTemplate

from langchain.chains import ReduceDocumentsChain
from langchain.text_splitter import RecursiveCharacterTextSplitter

import os
import pdb
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

import sys
import os
sys.path.append(".")
# from opinion_networks.combine_documents.map_reduce import MapReduceDocumentsChain2
from langchain.chains import MapReduceDocumentsChain
from opinion_networks.prompts import law_prompt
from opinion_networks.opinion import OpinionPair

class Summary:
    def __init__(self, output_folder):
        self.output_folder = output_folder
        """max_tokens: The maximum number of tokens to generate in the completion.
        -1 returns as many tokens as possible given the prompt and
        the models maximal context size."""
        self.llm = OpenAI(temperature=0.0, model_name="text-davinci-003", max_tokens=1000)

    def __call__(self, file_path: str, language: str, overwrite=False) -> OpinionPair:
        file_name = os.path.basename(file_path)
        output_file = os.path.join(self.output_folder, file_name)
        if os.path.exists(output_file) and not overwrite:
            with open(output_file, 'r') as f:
                summary = f.read()
            return summary

        with open(file_path, 'r') as f:
            raw_text = f.read()           
        # LLM to use in map and reduce stages 
        
        map_llm_chain = LLMChain(llm=self.llm, prompt=law_prompt.MAP_PROMPT)
        reduce_llm_chain = LLMChain(llm=self.llm, prompt=law_prompt.REDUCE_PROMPT)

        # Takes a list of documents and combines them into a single string
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_llm_chain,
            document_variable_name="text",
        )

        # Combines and iteravely reduces the mapped documents 
        reduce_documents_chain = ReduceDocumentsChain(
                # This is final chain that is called.
                combine_documents_chain=combine_documents_chain,
                # If documents exceed context for `combine_documents_chain`
                collapse_documents_chain=combine_documents_chain,
                # The maximum number of tokens to group documents into
                token_max=3000)

        # Combining documents by mapping a chain over them, then combining results with reduce chain
        combine_documents = MapReduceDocumentsChain(
            # Map chain
            llm_chain=map_llm_chain,
            # Reduce chain
            reduce_documents_chain=reduce_documents_chain,
            # The variable name in the llm_chain to put the documents in
            document_variable_name="text",
            #return_intermediate_steps=True
        )

        map_reduce = MapReduceChain(
            combine_documents_chain=combine_documents,
            text_splitter=RecursiveCharacterTextSplitter(    
                separators=["\n\n", "\n"], 
                chunk_size=5000, 
                chunk_overlap=350
            )
        )
        summary = map_reduce.run(input_text=raw_text, language=language)
        
        output_path = os.path.join(self.output_folder, file_name)
        with open(output_path, 'w') as f:
            f.write(summary)
        return summary

if __name__ == "__main__":
    import os
    os.environ["SERPAPI_API_KEY"] = ""
    os.environ["OPENAI_API_KEY"] = ""
    openai_api_key = ""

    raw_text = open('./data/peru/laws/pdfs/00336.txt').read()
    language = "Spanish"
    summary = Summary()
    output = summary(raw_text, language)
    print(output)
    