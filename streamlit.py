import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Import your existing LangGraph agent
# Make sure this matches your file name
from langgraph_agent import agent  

st.set_page_config(page_title="🛍️ AI Shopping Agent", layout="centered")

st.title("🛍️ AI Shopping Assistant")
st.caption("Chat with a LangGraph-powered shopping agent")

# -------------------------------
# Initialize Session State
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "llm_calls" not in st.session_state:
    st.session_state.llm_calls = 0

# -------------------------------
# Display Chat History
# -------------------------------
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)

    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

            # Show tool calls (if any)
            if msg.tool_calls:
                with st.expander("🔧 Tool Calls"):
                    for tc in msg.tool_calls:
                        st.json(tc)

    elif isinstance(msg, ToolMessage):
        with st.chat_message("assistant"):
            st.markdown("**🛠 Tool Result:**")
            st.write(msg.content)

# -------------------------------
# User Input
# -------------------------------
user_input = st.chat_input("Ask me to find products, filter by price, color, or type...")

if user_input:
    # Add user message
    human_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(human_msg)

    with st.chat_message("user"):
        st.write(user_input)

    # -------------------------------
    # Invoke LangGraph Agent
    # -------------------------------
    with st.spinner("🤖 Thinking..."):
        result = agent.invoke(
            {
                "messages": st.session_state.messages,
                "llm_calls": st.session_state.llm_calls,
            }
        )

    # Update session state
    st.session_state.messages = result["messages"]
    st.session_state.llm_calls = result.get("llm_calls", st.session_state.llm_calls)

    # Display new messages
    for msg in result["messages"][-3:]:  # show only latest cycle
        if isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.write(msg.content)

                if msg.tool_calls:
                    with st.expander("🔧 Tool Calls"):
                        for tc in msg.tool_calls:
                            st.json(tc)

        elif isinstance(msg, ToolMessage):
            with st.chat_message("assistant"):
                st.markdown("**🛠 Tool Result:**")
                st.write(msg.content)

# -------------------------------
# Sidebar Debug Panel
# -------------------------------
with st.sidebar:
    st.header("🧠 Agent Debug Info")
    st.write(f"LLM Calls: {st.session_state.llm_calls}")
    st.write(f"Messages in State: {len(st.session_state.messages)}")

    if st.button("🧹 Clear Conversation"):
        st.session_state.messages = []
        st.session_state.llm_calls = 0
        st.experimental_rerun()
