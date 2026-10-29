import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# s.sesssion_state -> dict -> stores data, without resetting it

CONFIG = {"configurable" : {"thread_id": "thread-1"}}

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []
    



# we r loading the conversation history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])


  

user_input = st.chat_input("Type here")

if user_input:
    
    # first add the message of user to message history
    st.session_state["message_history"].append({"role":"user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)
      
   
    
    
    # first add the message of assistant to message history
    # st.session_state["message_history"].append({"role": "assistant", "content": ai_message})
    with st.chat_message("assistant"):
        
        # streaming
        ai_message = st.write_stream(
            message_chunk.content for message_chunk , metadeta in chatbot.stream(
                {"messages" : [HumanMessage(content = user_input)]},
                config = {"configurable" : {"thread_id": "thread-1"}},
                stream_mode = "messages"
            )
        )
        
        st.session_state["message_history"].append({"role": "assistant", "content": ai_message})

    