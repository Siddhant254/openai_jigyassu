import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings

# Get absolute path to the .env file in the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dotenv_path = os.path.join(project_root, ".env")

load_dotenv(dotenv_path)
print("FAISS_DIR:", os.getenv("FAISS_DIR"))
print("UPLOAD_DIR:", os.getenv("UPLOAD_DIR"))

# ✅ Environment config
openai_api_key = os.getenv("OPENAI_API_KEY")

# ✅ Embeddings
embedding_function = OpenAIEmbeddings(openai_api_key=openai_api_key)

# ✅ Text Splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=20
)

# ✅ FAISS config
FAISS_DIR = os.getenv("FAISS_DIR")
FAISS_PATH = os.path.join(FAISS_DIR, "index.faiss")

# Ensure directory exists
os.makedirs(FAISS_DIR, exist_ok=True)

# ✅ FAISS index (in-memory global variable)
faiss_index = None

def init_faiss():
    """
    Initializes the FAISS index. Loads it from disk if it exists.
    """
    global faiss_index
    if faiss_index is not None:
        print("FAISS index already loaded.")
        return

    if os.path.exists(os.path.join(FAISS_PATH)):
        try:
            faiss_index = FAISS.load_local(
                FAISS_DIR,
                embeddings=embedding_function,
                allow_dangerous_deserialization=True
            )
            print(f"✅ FAISS index loaded from {FAISS_PATH}")
        except Exception as e:
            print(f"❌ Error loading FAISS index: {e}")
            faiss_index = None
    else:
        print("⚠️ No existing FAISS index found. A new one will be created on first store.")


def store_in_vector_db(text: str, metadata: dict = None):
    """
    Stores text into FAISS vector DB after chunking and embedding.
    Creates new index if one doesn't exist.
    """
    global faiss_index
    metadata= metadata or {}

    # Split and prepare documents
    chunks = text_splitter.split_text(text)
    documents = [Document(page_content=chunk, metadata=metadata) for chunk in chunks]

    # Load or create index
    if faiss_index is None:
        print("Initializing FAISS...")
        init_faiss()

    if faiss_index is None:
        print("⚙️ Creating new FAISS index...")
        faiss_index = FAISS.from_documents(documents, embedding_function)
        faiss_index.save_local(FAISS_DIR)
        print(f"✅ New FAISS index created and saved at {FAISS_PATH}")
    else:
        faiss_index.add_documents(documents)
        faiss_index.save_local(FAISS_DIR)
        print("📦 Added documents and saved updated FAISS index.")


def retrieve_from_vector_db(
    query: str = None,
    subject: str = None,
    chapter: str = None,
    material_id: str = None,
    k: int = 50
) -> str:
    """
    Retrieves relevant documents from FAISS DB.
    - If `material_id` is provided, fetch docs with matching metadata.
    - If `query` is provided (e.g., natural language), perform similarity search.
    """
    if faiss_index is None:
        raise ValueError("❌ FAISS index is not initialized. Please call init_faiss first.")

    # 🔍 Case 1: Use material_id metadata filtering (used in coding module)
    if material_id:
        all_docs = faiss_index.docstore._dict.values()
        filtered_docs = []

        for doc in all_docs:
            if material_id and doc.metadata.get("material_id") != material_id:
                continue
            if subject and doc.metadata.get("subject") != subject:
                continue
            if chapter and doc.metadata.get("chapter") != chapter:
                continue
            filtered_docs.append(doc)

        if not filtered_docs:
            return "❗ No matching documents found with the specified metadata."

        return "\n".join(doc.page_content for doc in filtered_docs)

    # 🧠 Case 2: Use semantic similarity search (used in assessment module)
    elif query:
        results = faiss_index.similarity_search(query, k=k)
        if not results:
            return "❗ No relevant documents found for the query."
        return "\n".join(doc.page_content for doc in results)

    return "❗ You must provide either a query or a material_id."
