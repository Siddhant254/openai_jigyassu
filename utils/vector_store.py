import os
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ✅ FAISS DB path
FAISS_PATH = r"C:\Users\Admin\Desktop\Openai\Jigyassu_Backend\data\vectors\index.faiss"

# ✅ Ensure the directory exists
directory = os.path.dirname(FAISS_PATH)
if not os.path.exists(directory):
    os.makedirs(directory)
    print(f"Directory {directory} created.")

# ✅ OpenAI Embedding model (API key can be stored in an environment variable)
embedding_function = OpenAIEmbeddings(
    openai_api_key="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"  # Replace with your actual key or use environment variable
)

# ✅ Text splitter for long documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,     # Adjust as needed
    chunk_overlap=50    # Overlap for context continuity
)

# ✅ Store function (splits text + appends to FAISS)
def store_in_vector_db(text: str, metadata: dict = None):
    """
    Splits long text into chunks, embeds, and stores in FAISS DB using OpenAI embeddings.
    Appends to existing DB if present.
    """
    # Split into chunks
    chunks = text_splitter.split_text(text)
    documents = [Document(page_content=chunk, metadata=metadata or {}) for chunk in chunks]

    # Check if FAISS index exists
    if os.path.exists(FAISS_PATH):
        try:
            vector_store = FAISS.load_local(
                FAISS_PATH,
                embeddings=embedding_function,
                allow_dangerous_deserialization=True
            )
            vector_store.add_documents(documents)
            print("📦 Added new document chunks to existing FAISS store.")
        except Exception as e:
            print(f"Error loading FAISS index: {e}")
            return
    else:
        # If the index doesn't exist, create a new one
        vector_store = FAISS.from_documents(documents, embedding=embedding_function)
        print("🆕 Created new FAISS vector store.")

    # Save updated store
    vector_store.save_local(FAISS_PATH)
    print(f"FAISS index saved at {FAISS_PATH}")


# ✅ Retrieve function (with optional metadata filtering)
def retrieve_from_vector_db(query: str, subject: str = None, chapter: str = None, k: int = 10) -> str:
    """
    Retrieves top-k relevant documents from FAISS DB, with optional metadata filtering.
    """
    if not os.path.exists(FAISS_PATH):
        raise ValueError("❌ FAISS index not found. Please store data first.")

    try:
        vector_store = FAISS.load_local(
            FAISS_PATH,
            embeddings=embedding_function,
            allow_dangerous_deserialization=True
        )
        print(f"FAISS index loaded from {FAISS_PATH}")
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return "❌ Error loading FAISS index."

    # Step 1: Get top-k similar documents
    all_docs = vector_store.similarity_search(query, k=k)

    # Step 2: Filter based on metadata if provided
    filtered_docs = []
    for doc in all_docs:
        if subject and doc.metadata.get("subject") != subject:
            continue
        if chapter and doc.metadata.get("chapter") != chapter:
            continue
        filtered_docs.append(doc)

    if not filtered_docs:
        return "❗ No matching documents found with the specified filters."

    return "\n".join([doc.page_content for doc in filtered_docs])
