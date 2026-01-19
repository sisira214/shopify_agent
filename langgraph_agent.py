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

from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from openai import OpenAI

from langchain_community.vectorstores import Qdrant

import os
from dotenv import load_dotenv

load_dotenv()  # <-- MUST be before OpenAI initialization


qdrant = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
COLLECTION_NAME = "shopify_products"
'''
qdrant = Qdrant.from_existing_collection(
    client=qdrant,
    collection_name=COLLECTION_NAME,
    embedding=embeddings
)
'''
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

COLLECTION_NAME = "shopify_products"
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")



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
def search_products_qdrant(
    query: str,
    limit: int = 5
) -> list:
    """
    Perform a semantic product search using Qdrant via query_points.

    Args:
        query: Natural language search query describing the desired product.
        limit: Maximum number of products to return.

    Returns:
        A list of product dictionaries containing:
        - product_id
        - title
        - price
        - vendor
        - tags
        - description
        - url (Shopify product link)
    """
    
    print(f"--- Tool: Qdrant Search | Query='{query}' ---")

    # 1. Embed query
    embedding = openai_client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    ).data[0].embedding

    # 2. Correct Qdrant call
    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        limit=limit
    )

    # 4. Extract matches for the first query vector
    matches = results.points

    
    # 4. Format response
    products = []
    for r in matches:
        point_id = r.id
        score = r.score
        payload = r.payload or {}
        products.append({
            "product_id": point_id,
            "title": payload.get("title"),
            "price": payload.get("price"),
            "vendor": payload.get("vendor"),
            "tags": payload.get("tags"),
            "description": payload.get("description"),
            "url": f"https://{SHOPIFY_STORE_URL}/products/{payload.get('handle')}"
        })

    return products
 


@tool
def filter_products(
        products: list,
        min_price: float | None = None,
        max_price: float | None = None,
        color: str | None = None
    ) -> list:
        """
        Filter a list of products based on price range and color.

        Use this tool after retrieving products to narrow down the results
        according to user preferences such as budget or color.

        Args:
            products: List of product dictionaries to filter.
            min_price: Minimum acceptable product price.
            max_price: Maximum acceptable product price.
            color: Desired color to filter by (matched against product tags).

        Returns:
            A filtered list of product dictionaries that satisfy the criteria.
        """


        print("--- Tool: Filter Products ---")

        filtered = []

        for p in products:
            price = float(p["price"])

            if min_price is not None and price < min_price:
                continue
            if max_price is not None and price > max_price:
                continue
            if color and color.lower() not in (p.get("tags") or "").lower():
                continue

            filtered.append(p)

        return filtered


@tool
def filter_by_color(products: list, color: str) -> list:
    """
    Filter products by a specific color.

    Use this tool when the user explicitly requests products of a certain
    color and the product list has already been retrieved.

    Args:
        products: List of product dictionaries.
        color: Desired color (e.g., red, blue, black).

    Returns:
        A list of products that match the requested color.
    """

    print(f"--- Tool Triggered: Filter Color {color} ---")
    return [p for p in products if "Red" in color or "red" in color]

@tool
def filter_by_type(products: list, product_type: str) -> list:
    """
    Filter products by product type or category.

    Use this tool when the user specifies a particular type of product,
    such as shoes, smartphones, jackets, or accessories.

    Args:
        products: List of product dictionaries.
        product_type: Desired product category or type.

    Returns:
        A list of products that match the requested product type.
    """

    print(f"--- Tool Triggered: Filter Type {product_type} ---")
    return [p for p in products]

@tool
def get_product_details(product_id: int) -> dict:
    """
    Retrieve detailed information for a specific product.

    Use this tool when the user asks for more details about a specific
    product, such as its description, price, vendor, or features.

    Args:
        product_id: Unique identifier of the product in Qdrant.

    Returns:
        A dictionary containing detailed product information including:
        - title
        - description
        - price
        - vendor
        - tags
        - url (Shopify product link)
    """


    print(f"--- Tool: Get Product Details (Qdrant) | {product_id} ---")

    points = qdrant.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[product_id],
        with_payload=True
    )

    if not points:
        return {"error": "Product not found"}

    payload = points[0].payload

    return {
        "title": payload.get("title"),
        "description": payload.get("description"),
        "price": payload.get("price"),
        "vendor": payload.get("vendor"),
        "tags": payload.get("tags"),
        "url": f"https://{SHOPIFY_STORE_URL}/products/{payload.get('handle')}"
    }


@tool
def compare_products(product_ids: list[int]) -> dict:
    """
    Compare multiple products side-by-side.

    Use this tool when the user asks to compare two or more products based
    on features, price, or other attributes.

    Args:
        product_ids: List of product IDs to compare.

    Returns:
        A dictionary containing a comparison of the selected products.
    """


    print(f"--- Tool: Compare Products | {product_ids} ---")

    products = []
    for pid in product_ids:
        products.append(get_product_details(pid))

    return {"comparison": products}


@tool
def add_to_cart(product_id: int, quantity: int = 1) -> dict:
    """
    Add a product to the shopping cart.

    Use this tool when the user explicitly requests to add a product
    to their cart.

    Args:
        product_id: Unique identifier of the product.
        quantity: Number of units to add to the cart.

    Returns:
        A confirmation dictionary indicating the product was added.
    """

    return {"status": "added", "product_id": product_id, "quantity": quantity}

@tool
def view_cart() -> dict:
    """
    View the current contents of the shopping cart.

    Use this tool when the user asks to see what items are currently
    in their cart.

    Returns:
        A dictionary representing the current cart contents.
    """

    return {"items": "cart_items_placeholder"}

@tool
def checkout_cart() -> dict:
    """
    Initiate the checkout process for the current cart.

    Use this tool when the user asks to proceed to checkout or complete
    their purchase.

    Returns:
        A dictionary containing the checkout URL.
    """

    return {
        "checkout_url": f"https://{SHOPIFY_STORE_URL}/checkout"
    }




# Bind tools to the model
tools = [
    search_products_qdrant,
    filter_products,
    get_product_details,
    compare_products,
    add_to_cart,
    view_cart,
    checkout_cart
]

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