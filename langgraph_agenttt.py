# UPDATED IMPORTS: using langchain_core for messages and tools
from langchain_core.tools import tool
from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage, HumanMessage
from typing_extensions import TypedDict, Annotated
import operator
import os
from dotenv import load_dotenv
from typing import Literal
from langgraph.graph import StateGraph, START, END

# We use the specific OpenAI class for better stability, 
# or you can ensure 'langchain' is installed to use init_chat_model
from langchain_openai import ChatOpenAI

load_dotenv()

# Initialize the model directly using ChatOpenAI
# This avoids the 'init_chat_model' dependency issues if the main langchain package is missing
model = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

# ----------------- Define Tools -----------------

@tool
def recommend_products(user_query: str, limit: int = 5) -> list:
    """Recommends products based on user query.

    Args:
        user_query: The user's search query.
        limit: Number of products to return (default 5).
    """
    print(f"--- Tool Triggered: Recommend Products for '{user_query}' ---")
    return [f"Product {i+1} ({user_query})" for i in range(limit)]

@tool
def filter_by_price(products: list, min_price: float, max_price: float) -> list:
    """Filter products by price range.

    Args:
        products: List of products.
        min_price: Minimum price.
        max_price: Maximum price.
    """
    print(f"--- Tool Triggered: Filter Price {min_price}-{max_price} ---")
    return [p for p in products if "Product 1" in p or "Product 2" in p]

@tool
def filter_by_color(products: list, color: str) -> list:
    """Filter products by color.

    Args:
        products: List of products.
        color: Desired color.
    """
    print(f"--- Tool Triggered: Filter Color {color} ---")
    return [p for p in products if "Red" in color or "red" in color]

@tool
def filter_by_type(products: list, product_type: str) -> list:
    """Filter products by type.

    Args:
        products: List of products.
        product_type: Desired product type.
    """
    print(f"--- Tool Triggered: Filter Type {product_type} ---")
    return [p for p in products]

# Bind tools to the model
tools = [recommend_products, filter_by_price, filter_by_color, filter_by_type]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)

# ----------------- Define State -----------------

class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add] 
    llm_calls: int

# ----------------- Nodes -----------------

def llm_call(state: MessagesState):
    """LLM decides whether to call a tool or not"""
    
    sys_msg = SystemMessage(
        content="You are a helpful shopping assistant. Use the provided tools to search for products, filter them by price, color, or type, and recommend them to the user."
    )
    
    # We invoke the model with the system message + conversation history
    response = model_with_tools.invoke([sys_msg] + state["messages"])

    return {
        "messages": [response],
        "llm_calls": state.get('llm_calls', 0) + 1
    }

def tool_node(state: MessagesState):
    """Performs the tool call"""
    result = []
    last_message = state["messages"][-1]
    
    for tool_call in last_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        # Execute tool
        observation = tool.invoke(tool_call["args"])
        # Create ToolMessage
        result.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
        
    return {"messages": result}

def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tool_node"
    return END

# ----------------- Build Graph -----------------

agent_builder = StateGraph(MessagesState)

agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")

agent = agent_builder.compile()

# ----------------- Execution -----------------

if __name__ == "__main__":
    # Display Graph (Only works in Jupyter/IPython)
    try:
        from IPython.display import Image, display
        display(Image(agent.get_graph(xray=True).draw_mermaid_png()))
    except Exception:
        pass 

    # Run the Agent
    user_input = "Can you find me some red shoes?"
    print(f"User: {user_input}\n")

    messages = [HumanMessage(content=user_input)]
    result = agent.invoke({"messages": messages})

    print("\n--- Final Conversation History ---")
    for m in result["messages"]:
        m.pretty_print()