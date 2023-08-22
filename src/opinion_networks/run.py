import os, sys
sys.path.append(".")
from tqdm import tqdm
import pdb

from opinion_networks.dataset import Summary
from opinion_networks.dataset import LawDataset 
from opinion_networks.nn import MLP
from opinion_networks import trace_graph

import torch
from torch import cuda, bfloat16
from langchain.llms import HuggingFacePipeline
import random
from typing import List, Optional, Any, Dict

import json
from collections import Counter

def background_fn():
    cities = [
        "Lima in Peru",
        "Arequipa in Peru",
        "Cusco in Peru",
        "Trujillo in Peru",
        "Chiclayo in Peru",
        "Puno in Peru",
        "Iquitos in Peru",
        "Cajamarca in Peru",
        "Tacna in Peru",
        "Huancayo in Peru",
        "Piura in Peru",
        "Ayacucho in Peru",
        "Chimbote in Peru",
        "Huaraz in Peru",
        "Tumbes in Peru",
        "Puerto Maldonado in Peru"
    ]

    political_stand = [
        "liberal",
        "conservative"
    ]

    role = [
        "student",
        "worker",
        "lawyer",
        "teacher",
        "driver",
        "journalist",
        "unemployed",
        "sindicalist",
        "engineer"
    ]

    background = f"A person from {random.choice(cities)}, {random.choice(political_stand)}, and whose role is: {random.choice(role)}."
    return background



def run(model_id, openai_auth):
    os.environ["OPENAI_API_KEY"] = openai_auth
    
    raw_text_root = "data/peru/laws/texts"
    crawled_files_root = 'data/peru/laws/crawled/'
    summaries_root = 'data/peru/laws/summaries'
    dataset = LawDataset(raw_text_root, crawled_files_root, summaries_root)
    x, y = dataset.load()
    
    # TODO: test model = MLP(1, [1, 1]), model = MLP(1, [1])
    #model = MLP(1, [3, 1])
    model = MLP(1, [2, 1], background_fn=background_fn)
    epochs = 10
    lr = 1e-4
    for epoch in range(epochs):
        # forward
        loss = 0
        for i in tqdm(range(len(x))):
            opinions = model(x[i])
            ypred = [opinion.score for opinion_pair in opinions for opinion in opinion_pair.get_pos_neg_opinions()]
            loss += sum([(y- yp)**2 for y, yp in zip(ys[i], ypred)])
        
        # backward
        model.zero_grad()            
        loss.backward()
        
        # update params
        for p in model.parameters():
            p.data += -lr*p.grad
        print(f'epoch {epoch},  iteration: {i}, loss: {loss}')
        pdb.set_trace()
        trace_graph.draw_dot(loss, format='png', output_filepath=f'./data/peru/laws/summaries/epoch_{epoch}')


import argparse
import os
os.environ['LANGCHAIN_WANDB_TRACING'] = "true"
os.environ['WANDB_PROJECT'] = "langchain-tracking"
from llama_index import set_global_handler
set_global_handler("wandb", run_args={"project": "llamaindex"})

if __name__ == '__main__':
    #model_id = 'meta-llama/Llama-2-70b-chat-hf'
    #model_id = "meta-llama/Llama-2-7b-hf"
    model_id = "meta-llama/Llama-2-7b-chat-hf"
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--openai_auth", help="Open AI Key")
    args = parser.parse_args()
    run(model_id, args.openai_auth)
