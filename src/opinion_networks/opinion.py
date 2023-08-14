from pydantic import BaseModel
from opinion_networks.engine import Value
import json
import pdb

class Opinion:
    def __init__(self, opinion_type: str, reasoning: str, score: Value):
        self.opinion_type: str = opinion_type
        self.reasoning: str = reasoning
        self.score: Value = score

    def __repr__(self):
        dic = {
            'opinion_type': self.opinion_type,
            'reasoning': self.reasoning,
            'score': self.score
        }
        print_text = "\n".join(f"\t'{k}':\n\t{v}" for k, v in dic.items())
        print_text = '{\n' + print_text + '\n}\n'
        return print_text

class OpinionPair:
    def __init__(self, opinions_json: str, law_str: str):
        self.law: str = law_str
        try:
            opinions = self.from_json(opinions_json)
        except:
            pdb.set_trace()
        self.pos_opinion: Opinion = opinions[0]
        self.neg_opinion: Opinion = opinions[1]

    def from_json(self, opinions_json):
        opinions_list = json.loads(opinions_json)
        pos_opinion = Opinion(
            opinion_type=opinions_list[0]['Opinion'].strip(), 
            reasoning=opinions_list[0]['Reasoning'].strip(), 
            score=Value(float(opinions_list[0]['Score']), _op='Positive opinion')
        ) 
        neg_opinion = Opinion(
            opinion_type=opinions_list[1]['Opinion'].strip(), 
            reasoning=opinions_list[1]['Reasoning'].strip(), 
            score=Value(float(opinions_list[1]['Score']), _op='Negative opinion')
        )
        return (pos_opinion, neg_opinion) 

    def get_pos_neg_opinions(self):
        return (self.pos_opinion, self.neg_opinion)

    def __repr__(self):
        return f"""\nOpinionPair:\nPositive opinion:{self.pos_opinion}\nNegativeOpinion{self.neg_opinion}\n"""

        
