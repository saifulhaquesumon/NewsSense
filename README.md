🧠 AI News Intelligence Agent – “NewsSense”
NewsSense is a multi-agent system designed to help users track, verify, and summarize breaking news from across the web. It uses a controller agent to understand user intent and route tasks to specialized agents for efficient handling.



project structure
- streamlit_run.py --Run this file, 

This program written in  VSCode.
## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your OpenAI API key:


API_KEY= "your open ai key" 
BASE_URL= "https://models.github.ai/inference"
MODEL_NAME= "openai/gpt-4.1-nano"
LOGFIRE_TOKEN="your token here"
TAVILY_API_KEY="your key here" #https://app.tavily.com/home
EMBEDDING_MODEL="all-MiniLM-L6-v2"

run the streamlit_ui.py file


if you don't want to send to logfire

logfire.configure(
    send_to_logfire=False, # Set to True to send to the Logfire service
    token=LOGFIRE_TOKEN,  # Your Logfire token    
)


🗺️ System Diagram & Flow
The user interacts with the Conversation Agent, which acts as a controller. Based on the user's query, it decides which specialist agent to invoke.

User
 |
 ↓
🧠 Conversation Agent (Controller)
 ├──> 📈 Trending News Agent ──> get_trending_news() [Simulates Web Search]
 ├──> ✅ Fact Checker Agent   ───> fact_check_claim()  [Simulates RAG]
 └──> ✍️ News Summarizer Agent ─> summarize_news()    [Simulates Summarization]

 All agent actions and decisions are logged via Logfire.
 All tool inputs are validated using Pydantic schemas.
🤖 Agent Roles
Conversation Agent (Controller)

Purpose: Acts as the primary user interface and router.

Logic: Uses the OpenAI gpt-4o model with a tool_choice parameter to analyze the user's query and select the most appropriate tool (get_trending_news, fact_check_claim, or summarize_news).

Entry Point: The run_news_sense(user_query) function.

Trending News Agent

Purpose: To find and report on trending news topics.

Tool: get_trending_news(topic: str)

Implementation: Simulates fetching headlines from a dummy database for categories like 'AI', 'tech', etc.

Fact Checker Agent

Purpose: To verify specific factual claims.

Tool: fact_check_claim(claim: str)

Implementation: Simulates a Retrieval-Augmented Generation (RAG) system by checking the user's claim against a predefined knowledge base.

News Summarizer Agent

Purpose: To condense long articles into concise summaries.

Tool: summarize_news(article_text: str)

Implementation: Simulates an extractive summarization model by providing a pre-written, bullet-point summary.

✅ Key Features Implemented
Multi-Agent Routing: The Conversation Agent intelligently routes tasks to specialist agents using OpenAI's function calling feature.

Logfire Integration: All major operations, from receiving a query to executing a tool, are logged using logfire.instrument and logfire.info for observability.

Pydantic Validation: Agent tool inputs are defined with Pydantic models (TrendingNewsInput, FactCheckInput, SummarizeInput) to ensure type safety and data integrity before execution.

Simulated Tools: The project uses dummy functions to simulate complex backend operations like web search, RAG, and summarization, allowing for a focus on the agentic architecture.

Modular Code: The code is organized into logical blocks for configuration, schema definitions, tool implementations, and the main controller, making it easy to understand and extend.



Expected Output and Logfire Logs
===================================================================

User Question: Is open AI partnering with Apple?
Output : Multiple tech news outlets have reported on ongoing discussions between Apple and OpenAI to integrate generative AI features into iOS. However, neither company has issued an official confirmation. Sources suggest a deal is plausible but not finalized.

Logfire Log: 
https://logfire-us.pydantic.dev/shared-trace/211f7868-d46e-4bce-b926-5bf06de7c53c


Question: What’s trending in AI today?
Output: 
1: Advancements in Artificial Intelligence and Machine Learning

Source: https://online-engineering.case.edu/blog/advancements-in-artificial-intelligence-and-machine-learning


2: AI News & Articles - Artificial Intelligence Updates - IEEE Spectrum

Source: https://spectrum.ieee.org/topic/artificial-intelligence/


3: Latest Development of Artificial Intelligence | InData Labs

Source: https://indatalabs.com/blog/ai-latest-developments


4: Top AI Trends 2025: Key Developments to Watch - Appinventiv

Source: https://appinventiv.com/blog/ai-trends/


5: Top 24 Artificial Intelligence Applications and Uses - Simplilearn.com
Source: https://www.simplilearn.com/tutorials/artificial-intelligence-tutorial/artificial-intelligence-applications

Logfire log :
https://logfire-us.pydantic.dev/shared-trace/afbd4ee5-245e-44c8-a781-ba02b6868333




Question: Can you please summarize this for me: In a landmark development for the artificial intelligence industry, leading tech giants are now locked in a fierce competition to produce the most powerful and efficient Large Language Models (LLMs). This technological race is not just about bragging rights; it's about capturing a market expected to be worth trillions. The core of the battle lies in balancing immense computational power, which is costly and energy-intensive, with the growing demand for accessible and ethically-sound AI tools. Experts point out that while model performance is skyrocketing, significant hurdles remain in areas like bias mitigation, factual accuracy, and the high financial barrier to entry for smaller players. The industry's trajectory suggests a future dominated by a few key platforms, leading to a new era of personalized, multi-modal AI assistants that could redefine human-computer interaction.

Output: 
Major tech companies are competing to develop the most powerful and efficient Large Language Models (LLMs), aiming to dominate a market worth trillions. The challenge involves balancing high computational costs and energy use with the need for accessible, ethical AI. Despite rapid improvements, issues like bias, factual accuracy, and high costs limit smaller players. The industry is heading toward a landscape dominated by a few platforms, ushering in advanced, personalized AI assistants that could transform human-computer interactions.


Logfire Log: https://logfire-us.pydantic.dev/shared-trace/395ba92f-ef3e-45e3-9659-9ee580b4a168