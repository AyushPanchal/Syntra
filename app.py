import uvicorn
from fastapi import FastAPI, Request
from src.graphs.graph_builder import GraphBuilder
from src.llms.groq_llm import GroqLLM
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


# APIs

@app.post("/message")
async def query(request: Request):

    data = await request.json()
    user_message = data.get("user_message", "")

    # Get the llm
    groq_llm = GroqLLM()
    llm = groq_llm.get_llm()

    # Graph Builder
    graph_builder = GraphBuilder(llm)
    if user_message:
        graph = graph_builder.setup_graph(usecase="language")
        state = graph.invoke({"messages": HumanMessage(content=user_message)})

    return {"data": state}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", reload=True, port=8000)
