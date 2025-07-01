import os
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_core.documents import Document

load_dotenv()


class FaissIndex:
    def __init__(self, persist_path: str = "../../faiss_index", model="text-embedding-3-large"):
        self.persist_path = persist_path
        self.embedding = OpenAIEmbeddings(model=model)

        if os.path.exists(persist_path):
            self.store = FAISS.load_local(persist_path, self.embedding, allow_dangerous_deserialization=True)
        else:
            self.store = None

    def create_store(self, docs: list[str], metadatas: list[dict] = None):
        """
        Creates a new FAISS store with documents and optional metadata.
        """
        metadatas = metadatas or [{} for _ in docs]
        langchain_docs = [
            Document(page_content=doc, metadata=meta)
            for doc, meta in zip(docs, metadatas)
        ]
        self.store = FAISS.from_documents(langchain_docs, self.embedding)
        self.store.save_local(self.persist_path)

    def add_documents(self, docs: list[str], metadatas: list[dict] = None):
        """
        Adds new documents to the existing FAISS index.
        """
        if not self.store:
            self.create_store(docs, metadatas)
        else:
            metadatas = metadatas or [{} for _ in docs]
            new_docs = [Document(page_content=doc, metadata=meta) for doc, meta in zip(docs, metadatas)]
            self.store.add_documents(new_docs)
            self.store.save_local(self.persist_path)

    def query(self, query: str, k: int = 5) -> list[dict]:
        """
        Returns top k most similar documents.
        """
        if not self.store:
            raise ValueError("Vector store is empty.")
        docs = self.store.similarity_search(query, k=k)
        return [{"document": doc.page_content, "metadata": doc.metadata} for doc in docs]


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    vs = FaissIndex()

    docs = [
        "OpenAI is advancing general AI capabilities.",
        "FAISS is a fast similarity search library by Facebook.",
        "LangChain helps build applications with LLMs using tools and memory."
    ]
    metas = [{"source": "openai"}, {"source": "faiss"}, {"source": "langchain"}]

    vs.add_documents(docs, metas)

    results = vs.query("What is FAISS?")
    for res in results:
        print(res)
