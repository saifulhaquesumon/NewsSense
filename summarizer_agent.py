import asyncio
import os
import json
from typing import List
from dotenv import load_dotenv
import logfire
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool, set_tracing_disabled,Runner
from pydantic import BaseModel, Field

# --- 1. Load Environment Variables ---
# Load keys from the .env file
load_dotenv()

BASE_URL = os.getenv("BASE_URL") 
API_KEY = os.getenv("API_KEY") 
MODEL_NAME = os.getenv("MODEL_NAME") 
LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN") 


# Check if keys are available
if not os.getenv("API_KEY") or not os.getenv("TAVILY_API_KEY"):
    raise ValueError("OpenAI and Tavily API keys must be set in the .env file.")

client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)

class SummarizeInput(BaseModel):
    """Input schema for the News Summarizer Agent."""
    article_text: str = Field(..., description="The full text of the news article to be summarized.")

class SummarizeOutput(BaseModel):
    """Output schema for the News Summarizer Agent."""
    summary_text: str = Field(..., description="Summarized text from a given article.")

@function_tool
@logfire.instrument("summarize_news tool called")
def summarize_news(article_text: str) -> dict:
    """
    Take the user article and validate it. Later this will be replaced with a tool to read article from db or webpage.
    """
    #article_text = params.article_text
    print(f"⚙️ Tool: Summarizing article...")
    # A simple extractive summarization simulation
    # summary_points = [
    #     "The article discusses the rapid advancements in Large Language Models (LLMs).",
    #     "It highlights the competitive landscape between major tech companies.",
    #     "Key challenges include managing computational costs and addressing ethical concerns.",
    #     "The future outlook points towards more personalized and multi-modal AI assistants."
    # ]
    return article_text 


article_summarizer_agent = Agent(
    name="Article Summarizer",
    handoff_description="Summarizes articles into concise overviews.",
    instructions="""
    This agent helps users summarize articles into concise overviews.

    Make bullet points of the key information in the article.
    Focus on the most important details and insights.
    Avoid unnecessary details or filler content.
    Use clear, concise language.

    """,
    model=OpenAIChatCompletionsModel(
        openai_client=client,
        model=MODEL_NAME
    ),
    tools=[summarize_news],
    output_type=SummarizeOutput
)


if __name__ == "__main__":
    # Run the agent in a simple test loop
    async def main():
        long_article = """
        In a landmark development for the artificial intelligence industry, leading tech giants are now locked in a fierce competition
        to produce the most powerful and efficient Large Language Models (LLMs). This technological race is not just about bragging rights;
        it's about capturing a market expected to be worth trillions. The core of the battle lies in balancing immense computational power,
        which is costly and energy-intensive, with the growing demand for accessible and ethically-sound AI tools. Experts point out that
        while model performance is skyrocketing, significant hurdles remain in areas like bias mitigation, factual accuracy, and the high
        financial barrier to entry for smaller players. The industry's trajectory suggests a future dominated by a few key platforms,
        leading to a new era of personalized, multi-modal AI assistants that could redefine human-computer interaction.
        """
        input_data = SummarizeInput(article_text="This is a sample article text that needs to be summarized.")
        #output = await article_summarizer_agent.run(input_data)
        result = await Runner.run(article_summarizer_agent, long_article)
        print(f"Summary Output: {result.final_output.summary_text}")

    asyncio.run(main())