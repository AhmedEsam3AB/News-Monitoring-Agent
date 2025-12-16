import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Define Pydantic models for structured output
class NewsSummary(BaseModel):
    summary: str = Field(description="Concise bullet point summary")
    entities: list[str] = Field(description="List of key entities mentioned")
    category: str = Field(description="Category of the news (e.g., Markets, Tech, Politics, Earnings)")

class NewsScore(BaseModel):
    score: int = Field(description="Importance score between 0 and 100")
    reasoning: str = Field(description="Reasoning for the score, focusing on market impact and urgency")
    why_it_matters: str = Field(description="Explanation of why this news matters")

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Summary Chain
summary_prompt = PromptTemplate(
    template="""You are a financial news analyst.
    Analyze the following news item:
    Title: {title}
    Summary: {content}

    Provide a concise summary in bullet points, identify key entities, and categorize the news.
    Output valid JSON matching the following structure:
    {{
        "summary": "- Key point 1\\n- Key point 2",
        "entities": ["entity1", "entity2"],
        "category": "CategoryName"
    }}
    """,
    input_variables=["title", "content"],
)
summary_chain = summary_prompt | llm | JsonOutputParser(pydantic_object=NewsSummary)

# Scoring Chain
score_prompt = PromptTemplate(
    template="""You are a senior market analyst.
    Evaluate the importance of the following news item on a scale of 0-100.
    Focus on market impact, urgency, and relevance to global finance.
    0 = Noise/Irrelevant
    100 = Critical/Market Moving

    Title: {title}
    Summary: {content}

    Provide the score, a brief reasoning, and an explanation of why it matters.
    Output valid JSON matching the following structure:
    {{
        "score": 85,
        "reasoning": "This event directly affects interest rates...",
        "why_it_matters": "Investors should watch..."
    }}
    """,
    input_variables=["title", "content"],
)
score_chain = score_prompt | llm | JsonOutputParser(pydantic_object=NewsScore)

def analyze_news(title: str, content: str):
    """
    Runs both summary and scoring chains.
    """
    # Run in parallel or sequence. Sequence is easier to debug for now.
    summary_res = summary_chain.invoke({"title": title, "content": content})
    score_res = score_chain.invoke({"title": title, "content": content})
    
    return {
        "summary": summary_res["summary"],
        "entities": summary_res["entities"],
        "category": summary_res["category"],
        "score": score_res["score"],
        "reasoning": score_res["reasoning"],
        "why_it_matters": score_res["why_it_matters"]
    }
