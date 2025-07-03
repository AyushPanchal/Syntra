from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.document_loaders.document_loader import DocumentLoader
from src.helper import save_urls_to_text_file
from src.retrievers.vectore_store import FaissIndex

# ---- CONFIGURATION ----
parent_url = "https://www.svnit.ac.in/web/department/computer/"  # Replace it with your actual parent URL
dir_name = "SVNIT"

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

print("++++ Embedding Successful ++++")
