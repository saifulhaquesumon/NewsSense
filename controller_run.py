import asyncio
from dataclasses import dataclass
from datetime import datetime
import os
import json
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel, Field
import logfire

from trending_news_web import trending_news_agent
from rag_fact_check import fact_check_agent
from summarizer_agent import article_summarizer_agent


# --- Configuration ---

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("BASE_URL") 
API_KEY = os.getenv("API_KEY") 
MODEL_NAME = os.getenv("MODEL_NAME") 
LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN") 



# Set up Logfire for observability
# You can get a free Logfire account to view detailed logs.
# For this example, we'll log to the console.
logfire.configure(
    send_to_logfire=False, # Set to True to send to the Logfire service
    token=LOGFIRE_TOKEN,  # Your Logfire token    
)

logfire.instrument_openai_agents()

# Initialize the OpenAI client
if not BASE_URL or not API_KEY or not MODEL_NAME:
    raise ValueError(
        "Please set BASE_URL, API_KEY, and MODEL_NAME."
    )
    

client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=False)




conversation_agent = Agent(
    name="News Sense Agent",
    handoff_description="Conversational agent. Provides news sense and connects to appropriate agent.",
    instructions="""
    You are a news sense assistant. Your role is to identify the right specialist agent to hand off to.
    You can hand off to specialist agents for specific tasks like Fact Checker, News Summarizer or Trending News Specialist.

    Don't try to answer the user's question directly. Instead, analyze the query and determine which specialist agent is best suited to handle it.
    """,
    model=OpenAIChatCompletionsModel(
        openai_client=client,
        model=MODEL_NAME
    ),

    handoffs=[trending_news_agent, fact_check_agent, article_summarizer_agent],
)



async def main():

    input_text = "I want to become a Data Scientist. What skills do I need?"
    print("\n" + "="*50)
    print(f"QUERY: {input_text}")
    result = await Runner.run(conversation_agent, input_text)
    #print(f"RESULT: {result}")

    if hasattr(result.final_output, "headlines"):  
        #print("********Trending News************")
        for item in result.final_output.headlines:
            print(f"  Rank #{item.rank}: {item.headline}")
            print(f"  Source: {item.source}\n")
    elif hasattr(result.final_output, "result"): 
        #print("*******Fact check*********")                
        print(f"{result.final_output.result}")
    elif hasattr(result.final_output, "summary_text"):  
        #print("**********Summarize Article***********")
        print(f"Summary: {result.final_output.summary_text}")        
    else:
        print("Sorry, I can't assist with that.")




# async def ask_agent(input_text: str):    
#     print("\n" + "="*50)
#     print(f"QUERY: {input_text}")
#     result = await Runner.run(conversation_agent, input_text)
#     #print(f"RESULT: {result}")

#     if hasattr(result.final_output, "headlines"):  
#         #print("********Trending News************")
#         output = ""
#         for item in result.final_output.headlines:
#             output += f"  Rank #{item.rank}: {item.headline}\n"
#             output += f"  Source: {item.source}\n"
#         return output
#     elif hasattr(result.final_output, "result"): 
#         #print("*******Fact check*********")                
#         return result.final_output.result.summary
#     elif hasattr(result.final_output, "summary_text"):  
#         #print("**********Summarize Article***********")
#         return result.final_output.summary_text
#     else:
#         return "Sorry, I can't assist with that."


@dataclass
class UserContext:  
    user_id: str
    session_start: datetime = None

if __name__ == "__main__":
    #print(get_jobs(user_skills=["Python", "SQL"]))
    asyncio.run(main())