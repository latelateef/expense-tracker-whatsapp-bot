from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain import hub
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model

def create_agent():
    llm = init_chat_model("gemini-1.5-flash", model_provider="google_genai")
    agent_db = SQLDatabase.from_uri("sqlite:///instance/expenses.db")
    toolkit = SQLDatabaseToolkit(db=agent_db, llm=llm)
    tools = toolkit.get_tools()

    prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
    system_message = prompt_template.format(dialect="SQLite", top_k=5)
    print(prompt_template)
    print(system_message)
    agent_executor = create_react_agent(
        llm, tools, state_modifier=system_message
    )
    return agent_executor


def retrieve_expense(user_phone, user_query):
    agent_executor = create_agent()
    prompt_template = """
    You are an expense tracking assistant that helps users manage and analyze their spending.
    - The user has the phone number: {user_phone}
    - They asked: "{user_query}"

    Your task:
    1. Retrieve their expenses categorized by type (e.g., food, travel, bills).
    2. Provide the **description and date** for each expense.
    3. Show the **total expense amount**.
    4. If the budget is exceeded, **warn the user**.
    5. Format the response attractively using **emojis and humor**.

    Ensure the response is **clear, engaging, and informative**.
    """
    formatted_prompt = prompt_template.format(user_phone=user_phone, user_query=user_query)

    events = agent_executor.stream(
        {"messages": [("user", formatted_prompt)]}, stream_mode="values"
    )
    last_response = ""
    for event in events:
        last_response = event["messages"][-1].content
        print(last_response)
        event["messages"][-1].pretty_print()

    return last_response
