import os
import re
import uuid
import urllib.parse
import requests

from tqdm import tqdm
from bs4 import BeautifulSoup
from typing import List, Tuple

from langchain_community.document_loaders import (
    RecursiveUrlLoader,
    WebBaseLoader,
    UnstructuredPDFLoader,
)

from src.helper import save_urls_to_text_file
from src.retrievers.vectore_store import FaissIndex


class DocumentLoader:
    def __init__(self, parent_url: str, vector_store: FaissIndex):
        self.parent_url = parent_url
        self.vector_store = vector_store
        self.pdf_dir = "downloaded_pdfs"
        os.makedirs(self.pdf_dir, exist_ok=True)

    @staticmethod
    def _extract_text_bs4(html: str) -> str:
        """Clean HTML to plain text using BeautifulSoup."""
        soup = BeautifulSoup(html, "lxml")
        return re.sub(r"\n\n+", "\n\n", soup.text).strip()

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        return bool(url and url.startswith("http"))

    def _classify_url(self, url: str) -> Tuple[bool, str]:
        """Classify if a URL is PDF or HTML."""
        try:
            encoded_url = urllib.parse.quote(url, safe=':/')
            response = requests.head(encoded_url, allow_redirects=True, timeout=5)
            if response.status_code != 200:
                return False, ""

            content_type = response.headers.get("Content-Type", "").lower()
            if "application/pdf" in content_type or encoded_url.lower().endswith(".pdf"):
                return True, "pdf"
            elif "text/html" in content_type:
                return True, "html"
        except requests.RequestException:
            pass
        return False, ""

    def get_child_urls(self, max_depth: int = 1000) -> Tuple[List[str], List[str]]:
        """Recursively crawls URLs and classifies into PDF or HTML."""
        html_urls, pdf_urls = [], []
        try:
            loader = RecursiveUrlLoader(
                url=self.parent_url,
                max_depth=max_depth,
                extractor=self._extract_text_bs4,
                continue_on_failure=True,
                check_response_status=True,
                autoset_encoding=True
            )
            for doc in tqdm(loader.lazy_load(), desc="🔍 Crawling URLs"):
                url = doc.metadata.get('source', '').strip()
                if not self._is_valid_url(url):
                    continue

                is_valid, url_type = self._classify_url(url)
                if is_valid:
                    if url_type == "pdf":
                        print(f"[PDF]  {url}")
                        pdf_urls.append(url)
                    elif url_type == "html":
                        print(f"[HTML] {url}")
                        html_urls.append(url)

        except Exception as e:
            print(f"❌ Unexpected error while loading URLs: {e}")

        return html_urls, pdf_urls

    def _load_html_documents(self, urls: List[str], text_splitter) -> List:
        docs = []
        for url in urls:
            try:
                loader = WebBaseLoader(url)
                html_docs = loader.load()
                split_docs = text_splitter.split_documents(html_docs)
                docs.extend(split_docs)
                print(f"✅ Added HTML: {url}")
            except Exception as e:
                print(f"❌ Failed HTML: {url} - {e}")
        return docs

    def _download_pdf(self, url: str) -> str:
        filename = f"{uuid.uuid4().hex}.pdf"
        path = os.path.join(self.pdf_dir, filename)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)
        return path

    def _load_pdf_documents(self, urls: List[str], text_splitter) -> List:
        docs = []
        for url in urls:
            try:
                pdf_path = self._download_pdf(url)
                loader = UnstructuredPDFLoader(pdf_path, mode="elements", strategy="hi_res")
                pdf_docs = loader.load()
                split_docs = text_splitter.split_documents(pdf_docs)
                docs.extend(split_docs)
                print(f"✅ Added PDF: {url}")
            except Exception as e:
                print(f"❌ Failed PDF: {url} - {e}")
        return docs

    def split_and_embed_urls_documents(self, html_url_txt: str, pdf_url_txt: str, text_splitter):
        """Load, split, and embed all documents into the FAISS store."""
        all_docs = []

        # ---- Load HTML ----
        with open(html_url_txt, "r") as f:
            html_urls = [line.strip() for line in f if line.strip()]
        all_docs.extend(self._load_html_documents(html_urls, text_splitter))

        # ---- Load PDFs ----
        with open(pdf_url_txt, "r") as f:
            pdf_urls = [line.strip() for line in f if line.strip()]
        all_docs.extend(self._load_pdf_documents(pdf_urls, text_splitter))

        # ---- Build FAISS Index ----
        if all_docs:
            self.vector_store.create_store(all_docs)
            print("📦 FAISS vector DB stored with embeddings.")
        else:
            print("⚠️ No documents were added to FAISS.")


if __name__ == "__main__":
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    # ---- CONFIGURATION ----
    parent_url = "https://www.svnit.ac.in/web/department/computer/"  # Replace it with your actual parent URL
    dir_name = "data"

    # ---- INIT VECTOR STORE & LOADER ----
    vector_store = FaissIndex()
    loader = DocumentLoader(parent_url, vector_store)

    # ---- FETCH CHILD URLs ----
    html_urls, pdf_urls = loader.get_child_urls()

    # ---- SAVE TO FILES ----
    html_url_file, pdf_url_file = save_urls_to_text_file(html_urls, pdf_urls, directory_name=dir_name)

    # ---- INIT TEXT SPLITTER ----
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", "!", "?", " "],
        length_function=len,
    )

    # ---- LOAD, SPLIT, AND EMBED ----
    loader.split_and_embed_urls_documents(
        html_url_txt=html_url_file,
        pdf_url_txt=pdf_url_file,
        text_splitter=text_splitter
    )
