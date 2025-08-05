import asyncio
import os
import json
from typing import List
from dotenv import load_dotenv
import logfire
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool, set_tracing_disabled,Runner
from pydantic import BaseModel, Field
#from langchain_community.tools.tavily_search import TavilySearchResults
from tavily import TavilyClient


# --- 1. Load Environment Variables ---
# Load keys from the .env file
load_dotenv()

BASE_URL = os.getenv("BASE_URL") 
API_KEY = os.getenv("API_KEY") 
MODEL_NAME = os.getenv("MODEL_NAME") 
LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN") 
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Check if keys are available
if not os.getenv("API_KEY") or not os.getenv("TAVILY_API_KEY"):
    raise ValueError("OpenAI and Tavily API keys must be set in the .env file.")


# --- 2. Define Pydantic Output Schema ---
# This defines the structure of the final output.

class NewsHeadline(BaseModel):
    """A single, ranked news headline with its source."""
    rank: int = Field(description="The rank of the headline based on its trend frequency (1 is the most trending).")
    headline: str = Field(description="The concise news headline.")
    source: str = Field(description="The source URL for the news article.")
    
class TrendingNews(BaseModel):
    """A collection of trending news headlines for a specific topic."""
    topic: str = Field(description="The central topic these headlines relate to.")
    headlines: List[NewsHeadline] = Field(description="A list of ranked, trending headlines about the topic.")

# --- 3. Set Up Tools and LLM ---

# # Initialize the free web search tool. We ask for more results to get a better sample.
# search_tool = TavilySearchResults(max_results=20)

# # Helper function to format search results into a readable string for the LLM
# def format_search_results(results: List[dict]) -> str:
#     """Converts the list of search result dicts into a single string."""
#     return "\n\n".join(
#         f"Source URL: {res['url']}\nHeadline: {res['title']}\nSnippet: {res['content']}"
#         for res in results
#     )


# To install: pip install tavily-python
@function_tool
@logfire.instrument("search_tavily tool called")
def search_tavily(query: str) -> List[dict]:
    """Search Tavily for the given query and return results."""
    client = TavilyClient(TAVILY_API_KEY)
    response = client.search(query=query, max_results=20)
    
    # Extract relevant fields from the response
    results = [
        {
            "rank": item["score"],
            "source": item["url"],
            "headline": item["title"]
        }
        for item in response["results"]
    ]
    
    return results

# client = TavilyClient(TAVILY_API_KEY)
# response = client.search(
#     query="What are the most promising applications of AI in healthcare?",
#     max_results=20
# )
# print(response)


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)

trending_news_agent = Agent(
    name="Trending News Agent",
    handoff_description="Finds trending news articles based on user-defined topics.",
    instructions="""
    This agent helps users find trending news articles on any topic.

    Use the following guidelines:
    1. Identify the most frequently mentioned stories
    2. Rank them by importance and recency
    3. Include only verified sources
    4. Provide concise headlines with direct links
    
    Example output format:
    {
        "topic": "Politics in Bangladesh",
        "headlines": [
            {
                "rank": 1,
                "headline": "Election results announced",
                "source": "https://example.com/news/123"
            }
        ]
    }
    """,
    model=OpenAIChatCompletionsModel(
        openai_client=client,
        model=MODEL_NAME
    ),
    tools=[search_tavily],
    output_type=TrendingNews
)

if __name__ == "__main__":
    # Example usage
    topic = "Trending news on politics in bangladesh"
    print(f"🔍 Searching for: {topic}")

    async def main():
        # Run the agent to get trending news
        #response = asyncio.run(trending_news_agent.run(topic))
        response = await Runner.run(trending_news_agent, topic)
        
        print(f"📰 Trending News Response: {response.final_output}")

        for item in response.final_output.headlines:
            print(f"  Rank #{item.rank}: {item.headline}")
            print(f"  Source: {item.source}\n")
        # Print the structured output
        #print(f"📰 Trending News Response: {response.json(indent=2)}")
        
        # # Log the response
        # with open("trending_news_output.json", "w") as f:
        #     json.dump(response.dict(), f, indent=2)

    asyncio.run(main())