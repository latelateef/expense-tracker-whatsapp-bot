from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain import hub
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
import os


# Function to retrieve the user's expenses
def retrieve_expense(user_phone, user_query):
    agent_executor = create_agent() # Create the agent
    # Load the agent prompt
    prompt_path = os.path.join(os.path.dirname(__file__), "agent_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()

    prompt_template = prompt_template.format(user_phone=user_phone, user_query=user_query)

    # Stream the agent's response
    events = agent_executor.stream(
        {"messages": [("user", prompt_template)]}, stream_mode="values"
    )

    # Get the last response
    last_response = """"""
    for event in events:
        last_response = event["messages"][-1].content
        event["messages"][-1].pretty_print()

    return last_response


# Function to create the agent
def create_agent():
    llm = init_chat_model("gemini-1.5-flash", model_provider="google_genai") # Load the language model
    agent_db = SQLDatabase.from_uri("sqlite:///instance/expenses.db") # Load the database
    toolkit = SQLDatabaseToolkit(db=agent_db, llm=llm) # Load the toolkit
    tools = toolkit.get_tools() # Get the tools

    prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt") # Load the pre-built system prompt
    system_message = prompt_template.format(dialect="SQLite", top_k=5) # Format the system message
    # Create the agent executor
    agent_executor = create_react_agent(
        llm, tools, state_modifier=system_message
    )
    return agent_executor