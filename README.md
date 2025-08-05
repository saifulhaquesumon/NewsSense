🧠 AI News Intelligence Agent – “NewsSense”
NewsSense is a multi-agent system designed to help users track, verify, and summarize breaking news from across the web. It uses a controller agent to understand user intent and route tasks to specialized agents for efficient handling.

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

When you run the code above (after adding your API key), you will see output similar to this. The logfire console output will be interleaved with the print statements.

--- Running Flow 1: Trending News ---
👤 User Query: 'What's trending in AI today?'
logfire: Instrument "Conversation Agent Running"
logfire: Received user query: What's trending in AI today?
logfire: Model decided to call a tool: get_trending_news
⚙️ Tool: Fetching trending news for topic: ai
logfire: Instrument "get_trending_news tool called"
✅ Agent Response:
{
  "status": "success",
  "headlines": [
    "Meta releases Llama 3, claiming state-of-the-art performance.",
    "Apple is in talks to integrate Google's Gemini into the iPhone.",
    "Elon Musk's xAI announces major updates for its Grok chatbot.",
    "Venture capital funding for AI startups reaches a new peak in Q1 2025."
  ]
}
logfire: Tool get_trending_news executed successfully.

--- Running Flow 2: Fact Checker ---
👤 User Query: 'Is it true that OpenAI is partnering with Apple?'
logfire: Instrument "Conversation Agent Running"
logfire: Received user query: Is it true that OpenAI is partnering with Apple?
logfire: Model decided to call a tool: fact_check_claim
⚙️ Tool: Fact-checking claim: 'is openai partnering with apple?'
logfire: Instrument "fact_check_claim tool called"
✅ Agent Response:
{
  "status": "success",
  "result": {
    "verdict": "Unconfirmed, but widely rumored.",
    "summary": "Multiple tech news outlets have reported on ongoing discussions between Apple and OpenAI to integrate generative AI features into iOS. However, neither company has issued an official confirmation. Sources suggest a deal is plausible but not finalized.",
    "sources": [
      "TechCrunch Report, Bloomberg News"
    ]
  }
}
logfire: Tool fact_check_claim executed successfully.

--- Running Flow 3: News Summarizer ---
👤 User Query: 'Can you please summarize this for me: ...'
logfire: Instrument "Conversation Agent Running"
logfire: Received user query: Can you please summarize this for me: ...
logfire: Model decided to call a tool: summarize_news
⚙️ Tool: Summarizing article...
logfire: Instrument "summarize_news tool called"
✅ Agent Response:
{
  "status": "success",
  "summary": [
    "The article discusses the rapid advancements in Large Language Models (LLMs).",
    "It highlights the competitive landscape between major tech companies.",
    "Key challenges include managing computational costs and addressing ethical concerns.",
    "The future outlook points towards more personalized and multi-modal AI assistants."
  ]
}
logfire: Tool summarize_news executed successfully.