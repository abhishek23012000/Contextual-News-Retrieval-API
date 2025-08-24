
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .models import LLMQueryAnalysis

load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1
)

def get_query_analyzer_chain():
    """
    Creates a Langchain chain to analyze a user's query and return a structured
    JSON object based on the LLMQueryAnalysis model.
    """
    parser = JsonOutputParser(pydantic_object=LLMQueryAnalysis)

    template = """
    You are an expert system that analyzes a user's news query. Your goal is to
    understand their intent and extract key information.

    Analyze the user's query and respond ONLY with a valid JSON object that
    conforms to the following format. Do not add any explanatory text before or after the JSON.

    {format_instructions}

    Rules for determining the intent:
    - 'nearby': If the query contains words like 'near', 'around', 'close to', or a specific location.
    - 'source': If a specific news publication is named (e.g., 'Reuters', 'New York Times').
    - 'category': If a general news topic is mentioned (e.g., 'Technology', 'Sports').
    - 'score': If the user asks for 'top', 'most relevant', or 'important' news.
    - 'search': Use this as the default or if specific keywords are the main focus.

    User Query:
    "{query}"
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # The chain combines the prompt, the LLM, and the parser
    return prompt | llm | parser

def get_summarizer_chain():
    """
    Creates a simple Langchain chain to generate a one-sentence summary for an article.
    """
    template = """
    Provide a concise, one-sentence summary of the following news article.

    Title: "{title}"
    Description: "{description}"

    One-sentence summary:
    """
    prompt = PromptTemplate.from_template(template)


    return prompt | llm

query_analyzer_chain = get_query_analyzer_chain()
summarizer_chain = get_summarizer_chain()