# LangGraph RAG Chatbot

A multi-threaded chatbot built with **LangGraph**, **LangChain** and **Streamlit**. You can upload a PDF to any conversation and ask questions about it (RAG), and the same assistant can search the web, check stock prices and do arithmetic using tools. Conversations are saved to SQLite, so past chats can be reopened.

I built this step by step while learning LangGraph from the [CampusX](https://www.youtube.com/@campusx-official) course, starting from a plain chatbot and adding one feature at a time. Every stage is kept in [`evolution/`](evolution/), and the story is below.

## Features

- Chat with an LLM (`gpt-4o-mini`) with token-by-token streaming
- Upload a PDF per conversation and ask questions about it
- Tool use: web search (DuckDuckGo), live stock price (Alpha Vantage), calculator
- Multiple conversations with a sidebar to switch between them
- Chat history saved in SQLite through LangGraph's checkpointer
- Live status in the UI while a tool is running

## How it works

```
User message
     |
     v
 chat_node  (LLM, with tools bound)
     |
     +-- needs a tool? --> tools node --> back to chat_node
     |
     +-- otherwise ------> answer streamed to the UI
```

**RAG pipeline** (`ingest_pdf` in `RAG_chatbot_backend.py`). RAG (Retrieval-Augmented Generation) was introduced in [Lewis et al., 2020](https://arxiv.org/abs/2005.11401), where a language model is given relevant passages retrieved from external documents instead of relying only on what it memorized:

1. The uploaded PDF is loaded with `PyPDFLoader`
2. It is split into chunks of 1000 characters with 200 overlap (`RecursiveCharacterTextSplitter`)
3. Chunks are embedded with OpenAI `text-embedding-3-small` and stored in a FAISS index
4. Each chat thread gets its own retriever (top 4 chunks by similarity)
5. The model decides when to call `rag_tool`, so questions that are not about the document do not trigger retrieval

## Project structure

```
RAG_chatbot_backend.py      LangGraph graph, tools, PDF ingestion, SQLite checkpointer
streamlit_RAG_frontend.py   Streamlit UI (chat, PDF upload, thread sidebar)
evolution/                  Earlier versions that led to this one
requirements.txt
.env.example
```

## Getting started

```bash
git clone https://github.com/Muneebk7/langgraph-rag-chatbot.git
cd langgraph-rag-chatbot
pip install -r requirements.txt
cp .env.example .env      # then add your own keys
streamlit run streamlit_RAG_frontend.py
```

You need an OpenAI API key. The Alpha Vantage key is only needed for the stock price tool, and LangSmith keys are optional.

## Development journey

I did not start with RAG. Each step below added one idea, and the files for each step are in [`evolution/`](evolution/).

| Step | What I added | Files |
|---|---|---|
| 1. Basic chatbot | A single-node LangGraph graph with an in-memory checkpointer, and a simple Streamlit chat page | `langgraph_backend.py`, `streamlit_frontend.py` |
| 2. Streaming | Responses stream token by token with `chatbot.stream` and `st.write_stream` | `streamlit_frontend_streaming.py` |
| 3. Multiple threads | A thread ID per conversation, a New Chat button and a sidebar to switch chats | `streamlit_frontend_threading.py` |
| 4. Persistence | Swapped the in-memory checkpointer for SQLite so conversations survive restarts, and added a helper to list saved threads | `langgraph_backend_database.py` |
| 5. Tools | Calculator and stock price tools, with the graph looping between the LLM and a `ToolNode` | `langgraph_tool_backend.py`, `streamlit_frontend_database.py` |
| 6. Side experiments | Tool calling in a standalone script, an async version, and a start on MCP tools | `chatbot.py`, `chatbot_async.py`, `chatbot_mcp.py` |
| 7. RAG | PDF upload, FAISS retrieval per thread, web search, a thread-aware system prompt and a tool status indicator in the UI | `RAG_chatbot_backend.py`, `streamlit_RAG_frontend.py` |

Things I learned along the way:

- LangGraph state is a message list with a reducer (`add_messages`), and a checkpointer plus `thread_id` is what gives each chat its memory
- A conditional edge from the LLM node to a tool node and back is the basic agent loop
- Giving the model a retrieval *tool* instead of always retrieving keeps normal chat and tool calls working in the same conversation
- The tool needs the `thread_id` to find the right PDF, so the system prompt passes it to the model on every turn

## Known limitations

- Chat history is saved in SQLite, but the FAISS indexes live in memory. After a restart you can reopen old chats, but you need to upload the PDF again to ask about it.
- Past chats are listed by thread ID rather than a readable title.
- `evolution/chatbot_mcp.py` is an unfinished experiment and will not run as it is.
- This is a learning project, so there are no tests yet.

## Tech stack

Python, LangGraph, LangChain, OpenAI API, FAISS, SQLite, Streamlit

## References

- Lewis, P., Perez, E., Piktus, A., et al. (2020). [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401). NeurIPS 2020.

## Acknowledgements

Big thanks to [CampusX](https://www.youtube.com/@campusx-official) on YouTube. I learned LangGraph from their teaching, and this project grew out of following along and then extending it with my own changes.

## Ideas for next steps

- Persist the vector store so documents survive restarts
- Support multiple PDFs per chat and show source pages in answers
- Name conversations automatically
- Finish the MCP tools experiment
