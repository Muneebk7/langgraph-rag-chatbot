
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI 
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver


load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]   
    
def chat_mode(state: ChatState):
       
    messages = state["messages"]
    response = llm.invoke(messages)
    
    return {"messages":[response]}

#checkpointer
checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_mode", chat_mode)

graph.add_edge(START, "chat_mode")
graph.add_edge("chat_mode", END)


chatbot = graph.compile(checkpointer=checkpointer)





