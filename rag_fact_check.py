import asyncio
import os
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool, set_tracing_disabled
import chromadb
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
import logfire


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

client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
#set_tracing_disabled(disabled=True)


# Define the input model for type hinting and validation
class FactCheckInput(BaseModel):
    claim: str

class VerificationResult(BaseModel):
    verdict: str
    summary: str
    sources: list[str] = []  # List of source URLs or names

class FactCheckOutput(BaseModel):
    status: str
    result: VerificationResult




@function_tool
@logfire.instrument("fact_check_claim tool called")
def fact_check_claim(params: FactCheckInput) -> dict:
    """
    Verifies a claim against a knowledge base stored in a local ChromaDB
    instance using vector search.
    """
    claim = params.claim
    print(f"⚙️ Tool: Fact-checking claim with ChromaDB: '{claim}'")

    # 1. Initialize ChromaDB client and embedding function
    # Using a persistent client to store data on disk
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Use the "all-MiniLM-L6-v2" model for embeddings
    from chromadb.utils import embedding_functions
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # 2. Get or create the collection
    collection = client.get_or_create_collection(
        name="knowledge_base",
        embedding_function=sentence_transformer_ef,
        metadata={"hnsw:space": "cosine"} # Use cosine similarity
    )

    # 3. Populate the knowledge base (only if it's empty)
    if collection.count() == 0:
        print("📚 Populating ChromaDB with knowledge base data for the first time...")
        knowledge_base_data = {
            "is openai partnering with apple?": {
                "verdict": "Unconfirmed, but widely rumored.",
                "summary": "Multiple tech news outlets have reported on ongoing discussions between Apple and OpenAI to integrate generative AI features into iOS. However, neither company has issued an official confirmation. Sources suggest a deal is plausible but not finalized.",
                "sources": ["TechCrunch Report", "Bloomberg News"]
            },
            "did apple acquire openai?": {
                "verdict": "False.",
                "summary": "There is no credible evidence or official announcement that Apple has acquired OpenAI. This is a false claim.",
                "sources": ["Internal Knowledge Base"]
            }
        }
        
        documents = []
        metadatas = []
        ids = []
        
        for i, (question, data) in enumerate(knowledge_base_data.items()):
            documents.append(question)
            # Metadata values must be strings, ints, floats, or bools.
            # We serialize the list of sources into a JSON string.
            metadatas.append({
                "verdict": data["verdict"],
                "summary": data["summary"],
                "sources": json.dumps(data["sources"]) # Serialize list to JSON string
            })
            ids.append(f"id_{i+1}")

        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("✅ Knowledge base populated successfully.")

    # 4. Perform vector search (query)
    # Find the single most similar document to the claim.
    results = collection.query(
        query_texts=[claim],
        n_results=1
    )

    # 5. Process and return the result
    # Check if any results were found and if the distance is below a threshold
    # For cosine similarity, distance = 1 - similarity. A smaller distance is better.
    # We set a threshold of 0.6 to avoid returning irrelevant results.
    if results['ids'][0] and results['distances'][0][0] < 0.6:
        retrieved_metadata = results['metadatas'][0][0]
        
        # De-serialize the sources string back into a list
        retrieved_metadata["sources"] = json.loads(retrieved_metadata["sources"])
        
        return {"status": "success", "result": retrieved_metadata}
    else:
        return {
            "status": "info",
            "result": {
                "verdict": "Not found",
                "summary": "Could not verify this claim with available data."
            }
        }




fact_check_agent = Agent(
    name="Fact Check Agent",
    handoff_description="Fact-checks claims and provides evidence-based responses.",
    instructions="""
    This agent will check the validity of claims made in news articles.

    You will use a local knowledge base stored in ChromaDB to verify claims.
    A tools given to you. If the claim is found, return the verdict, summary, and sources.

    If the claim is not found, return a message indicating that the claim could not be verified.
    """,
    model=OpenAIChatCompletionsModel(
        openai_client=client,
        model=MODEL_NAME
    ),
    tools=[fact_check_claim],
    output_type=FactCheckOutput
)

# --- Example Usage ---
if __name__ == "__main__":

    async def main():
        print("--- Running Fact-Check Examples ---")

        # # Example 1: A claim that closely matches a document
        # claim1 = FactCheckInput(claim="What is the status of the Apple and OpenAI partnership?")
        # result1 = fact_check_claim(claim1)

        # print("\n--- Result for Claim 1 ---")
        # print(json.dumps(result1, indent=2))

        # # Example 2: A claim that is a direct false statement
        # claim2 = FactCheckInput(claim="I heard Apple bought OpenAI, is that true?")
        # result2 = fact_check_claim(claim2)
        # print("\n--- Result for Claim 2 ---")
        # print(json.dumps(result2, indent=2))
    
        # # Example 3: A claim not in the knowledge base
        # claim3 = FactCheckInput(claim="Is Google launching a new smartphone?")
        # result3 = fact_check_claim(claim3)
        # print("\n--- Result for Claim 3 ---")
        # print(json.dumps(result3, indent=2))

        claim = "Is Google launching a new smartphone?"
        result = await Runner.run(fact_check_agent, claim)
        print(f" Output: {result.final_output}")

    asyncio.run(main())