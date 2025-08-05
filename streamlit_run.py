from agents import Runner, set_tracing_disabled
from dotenv import load_dotenv
import logfire
import streamlit as st
import asyncio
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any
import os
from controller_run import conversation_agent, UserContext

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("BASE_URL") 
API_KEY = os.getenv("API_KEY") 
MODEL_NAME = os.getenv("MODEL_NAME") 
LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN") 

logfire.configure(
    send_to_logfire=True, # Set to True to send to the Logfire service
    token=LOGFIRE_TOKEN,  # Your Logfire token
)

logfire.instrument_openai_agents()
set_tracing_disabled(disabled=False)

# Page configuration
st.set_page_config(
    page_title="News Sense Agent",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📰 News Sense Agent")
st.caption("Ask me about the latest news, trends, and insights!")

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e6f7ff;
        border-left: 5px solid #2196F3;
    }
    .chat-message.assistant {
        background-color: #f0f0f0;
        border-left: 5px solid #4CAF50;
    }
    .chat-message .content {
        display: flex;
        margin-top: 0.5rem;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .message {
        flex: 1;
        color: #000000;
    }
    .timestamp {
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "user_context" not in st.session_state:
    st.session_state.user_context = UserContext(
        user_id=str(uuid.uuid4())
    )

# Display chat messages
for message in st.session_state.chat_history:
    with st.container():
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="content">
                    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed={st.session_state.user_context.user_id}" class="avatar" />
                    <div class="message">
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant">
                <div class="content">
                    <img src="https://api.dicebear.com/7.x/bottts/svg?seed=travel-agent" class="avatar" />
                    <div class="message">
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def format_agent_response(output):
    """Format the agent's response for display"""
    if isinstance(output, str):
        return output
    elif hasattr(output, "headlines"):  # For TrendingNews
        response = ""
        i=0
        for item in output.headlines:
            i += 1
            response += f"<p><b>{i}:</b> {item.headline}</p>"
            response += f"<p><i>Source:</i> <a href='{item.source}' target='_blank'>{item.source}</a></p><br>"
        return response
    elif hasattr(output, "result"):  # For fact check
        return output.result.summary
    elif hasattr(output, "summary_text"):  # For article summary
        return output.summary_text
    return "Sorry, I can't assist with that."

async def process_message(user_input: str):
    """Process user input with the agent"""
    try:
        # Run the agent with the input
        result = await Runner.run(
            conversation_agent, 
            user_input, 
            context=st.session_state.user_context
        )
        
        # Format the response
        return format_agent_response(result.final_output)
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# User input
user_input = st.chat_input("Ask me anything about news...")
if user_input:
    # Add user message to chat history immediately
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })
    
    # Display a temporary "Thinking..." message
    with st.spinner("Thinking..."):
        # Process the message asynchronously
        response_content = asyncio.run(process_message(user_input))
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().strftime("%I:%M %p")
        })
    
    # Force a rerun to display the new messages
    st.rerun()

# Footer
st.divider()
st.caption("Powered by OpenAI Agents SDK | Built with Streamlit")