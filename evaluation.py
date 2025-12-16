from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

class EvalScore(BaseModel):
    quality_score: int = Field(description="Quality score between 1 and 10")
    feedback: str = Field(description="Feedback on why the score was given")

llm = ChatOpenAI(model="gpt-4o", temperature=0)

eval_prompt = PromptTemplate(
    template="""You are a Quality Assurance AI.
    Evaluate the quality of the following analysis.
    
    Original News:
    {original_text}
    
    Generated Analysis (Summary & Score):
    Summary: {summary}
    Score: {score}
    Reasoning: {reasoning}
    
    Check for:
    1. Accuracy: Does the summary reflect the original text?
    2. Consistency: Does the score and reasoning make sense for the content?
    
    Rate the quality on a scale of 1-10. Returns valid JSON.
    {{
        "quality_score": 8,
        "feedback": "Summary is accurate but score seems too high for this minor event."
    }}
    """,
    input_variables=["original_text", "summary", "score", "reasoning"],
)

eval_chain = eval_prompt | llm | JsonOutputParser(pydantic_object=EvalScore)

def evaluate_analysis(original_text, analysis):
    res = eval_chain.invoke({
        "original_text": original_text,
        "summary": analysis['summary'],
        "score": analysis['score'],
        "reasoning": analysis['reasoning']
    })
    return res
