import os, sys
sys.path.append(".")
from tqdm import tqdm
import pdb

from opinion_networks.dataset import Summary
from opinion_networks.nn import MLP
from opinion_networks import trace_graph

if __name__ == '__main__':
    os.environ["SERPAPI_API_KEY"] = "a3e7d04fddfaad4939476007b2713e4ca614354fa7d0221024827e716a9c4c74"
    os.environ["OPENAI_API_KEY"] = "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"
    
    xs = [
        [1.0],
        [1.0],
        [1.0],
        [1.0]
    ]
    
    output_folder = './data/peru/laws/summaries'
    summary = Summary(output_folder)
    files = [
        './data/peru/laws/pdfs/00336.txt',
        './data/peru/laws/pdfs/00350.txt',
        './data/peru/laws/pdfs/00349.txt',
        './data/peru/laws/pdfs/00180.txt',
    ]
    docs = [summary(file_path, language='Spanish', overwrite=False) for file_path in files]

    ys = [
        [0.0, 1.0], # published
        [0.0, 1.0], # published
        [1.0, 0.0], # archived
        [1.0, 0.0]  # archived
    ]

    ys = [[0.0, 1.0], [0.0, 1.0], [1.0, 0.0], [1.0, 0.0]]

    # TODO: test model = MLP(1, [1, 1]), model = MLP(1, [1])
    #model = MLP(1, [3, 1])
    model = MLP(1, [1, 1])
    epochs = 10
    lr = 1e-4
    for epoch in range(epochs):
        # forward
        loss = 0
        for i in tqdm(range(len(docs))):
            opinions = model(docs[i])
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