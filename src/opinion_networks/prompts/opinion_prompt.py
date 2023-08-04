from langchain.prompts import PromptTemplate

def get_background(background):
    if background is None:
        return "\n"
    prompt = """\nAlign this opinion with the values, experiences, and goals of someone that has the following background: {background} \n"""
    return prompt.format(background=background).strip()

#------------------------------------------------------------------------------------------------------------------------
read_template = """Considering the following law:
{law}
{background}
Return two opinions, one in favor and another against that law, in the following JSON format:

[
{{
"Opinion": "+",
"Reasoning": "Reasons why you would vote in favor of that law.",
"Score": "A numeric value between 0.0 and 1.0 indicating how much you are support your opinion."
}},
{{
"Opinion": "-",
"Reasoning": "Reasons why you would vote against that law.",
"Score": "A numeric value between 0.0 and 1.0 indicating how much you are support your opinion."
}}
]

The output should be in {language}. 


OUTPUT:
"""

#------------------------------------------------------------------------------------------------------------------------
reduce_template = """Given this law:
{law}

and this list of opinions:
{opinions}

Your task is to use your critical thinking to generate a two well-thought and diverse opinions, one in favor and another against that law, combining opinions that are similar, and creating new ones by weighing the evidence presented and associating ideas in such a way as to enhance the original opinions. 
{background}

Return the two opinions in the following JSON format:

[
{{
"Opinion": "+",
"Reasoning": "Reasons why you would vote in favor of that law.",
"Score": "A numeric value between 0.0 and 1.0 indicating how much you are support your opinion."
}},
{{
"Opinion": "-",
"Reasoning": "Reasons why you would vote against that law.",
"Score": "A numeric value between 0.0 and 1.0 indicating how much you are support your opinion."
}}
]

The output should be in {language}. 


OUTPUT:
"""

#------------------------------------------------------------------------------------------------------------------------
collapse_template = """Given this law:
{law}

and this list of opinions:
{opinions}

Your task is to use your critical thinking to generate a bulleted list of diverse opinions, combining opinions that are similar, and creating new ones by weighing the evidence presented and associating ideas in such a way as to enhance the original opinions. 


OUTPUT:
"""

READ_PROMPT = PromptTemplate(input_variables=["law", "background", "language"], template=read_template)
COLLAPSE_PROMPT = PromptTemplate(input_variables=["law", "opinions"], template=collapse_template)
REDUCE_PROMPT = PromptTemplate(input_variables=["law", "opinions", "background", "language"], template=reduce_template)
DECIDE_PROMPT = PromptTemplate(input_variables=["law", "opinions", "background", "language"], template=reduce_template)