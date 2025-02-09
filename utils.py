from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain import hub
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from gemini import classify_message
from models import db, User, Expense
import json
from datetime import datetime
from sqlalchemy import func

def create_agent():
    llm = init_chat_model("gemini-1.5-flash", model_provider="google_genai")
    db = SQLDatabase.from_uri("sqlite:///instance/expenses.db")
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    toolkit.get_tools()

    prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
    system_message = prompt_template.format(dialect="SQLite", top_k=5)

    agent_executor = create_react_agent(
        llm, toolkit.get_tools(), state_modifier=system_message
    )
    return agent_executor


def process_user_query(user_phone, user_query):
    agent_executor = create_agent()
    example_query = f"""
    You are a expense tracker and manager bot which help users to track there expenses and manage it and provide a detailed breakdown of the total expenses incurred by the user.
    Can you provide a resolution to the following query for user with user_phone {user_phone}?
    The user phone is in structure *whatsapp:+91XXXXXXXXXX*
    <User Query>:
    {user_query}
    </User Query>
    If the user asks for the expenses then provide the expenses in each category with decription and date of spend and total expenses.
    Also if the user has exceeded the budget then provide a warning message.
    Present the response in a visually appealing manner with all descriptions using emojis and a light joke for user for his day.
    """
    events = agent_executor.stream(
        {"messages": [("user", example_query)]}, stream_mode="values"
    )
    last_response = ""
    for event in events:
        last_response = event["messages"][-1].content
        event["messages"][-1].pretty_print()

    return last_response


def analyze_sentiment(message, phone):
    res = classify_message(message)
    res = json.loads(res)
    print(res)
    user = db.session.query(User).filter_by(user_phone=phone).first()

    if res.get("retrieve_expense"):
        return process_user_query(user_phone=phone, user_query=message)
    elif res.get("add_expense"):
        expense = Expense(
            user_id=user.id,
            category=res["add_expense"]["category"],
            amount=res["add_expense"]["amount"],
            description=res["add_expense"]["description"],
        )

        db.session.add(expense)
        db.session.commit()
        message = f"""
        ✅ Expense added successfully!
        🗓 Date: {expense.date.strftime("%d-%m-%Y")}
        💰 Amount: ₹ {expense.amount}
        📝 Category: {expense.category}
        📄 Description: {expense.description}
        """
        bugdet = user.limit_amount
        current_month = datetime.now().month
        current_year = datetime.now().year
        total_expenses = db.session.query(func.sum(Expense.amount)).filter(
            func.extract('month', Expense.date) == current_month,
            func.extract('year', Expense.date) == current_year
        ).scalar()
        if total_expenses > bugdet:
            message += f"""\n🚨 You have exceeded your budget of *₹ {bugdet}* for this month. 💸 The total expenses for the current month is *₹ {total_expenses}*."""
        else:
            message += f"""\n💸 The total expenses for the current month is *₹ {total_expenses}*. You have *₹ {bugdet - total_expenses}* left in your budget for this month."""
        return message
    elif res.get("update_limit"):
        user.limit_amount = res["update_limit"]["limit_amount"]  # Update the limit
        db.session.commit()

        current_month = datetime.now().month
        current_year = datetime.now().year
        total_expenses = db.session.query(func.sum(Expense.amount)).filter(
            func.extract('month', Expense.date) == current_month,
            func.extract('year', Expense.date) == current_year
        ).scalar()
        msg = f"""
        ✅ The limit amount has been updated.\n 💵 You have currently set a limit of *₹ {res["update_limit"]["limit_amount"]}*.\n 💸 The total expenses for the current month is *₹ {total_expenses}*.
        """
        return msg
    else:
        return "Some error occurred . Please try after sometime"  # Default case if no matching category
