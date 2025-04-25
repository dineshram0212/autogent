# Retrieval‐Augmented Generation (RAG) Module

This folder implements a **fully‐pluggable RAG pipeline** for your `agentlib` framework. It provides:

1. **Data Connectors** — load raw text from any source  
2. **Chunker** — split large documents into retrievable passages  
3. **Embedders** — convert text to vectors (OpenAI or HuggingFace)  
4. **Vector Stores** — FAISS or Chroma backends  
5. **Retrievers** — Standard, Hybrid, HyDE, Speculative, Query‐Based, Contextual, Long‐Form  
6. **Reranker** — optional LLM‐driven rescoring  

---

## 📦 Installation

```bash
pip install agentlib[rag]    # assumes you bundle rag deps in extras
# or manually:
pip install openai faiss-cpu chromadb sentence-transformers boto3 pdfplumber python-docx pandas beautifulsoup4 pytesseract sqlalchemy
```

---

## ⚙️ Components

### 1. Data Connectors

- `SQLConnector` – any SQL table via SQLAlchemy  
- `S3Connector` – load text files from S3  
- `VectorDBConnector` – wrap a vector‐db collection  

```python
from agentlib.rag.connectors.sql_connector import SQLConnector

sql = SQLConnector("postgresql://...", table="articles")
ids = sql.list_sources()
text = sql.load(ids[0])
```

### 2. Chunker

```python
from agentlib.rag.chunker import Chunker

chunker = Chunker(chunk_size=1000, overlap=200)
chunks = chunker.chunk(text, mode="sliding_window")
```

### 3. Embedders

```python
from agentlib.rag.embedder import OpenAIEmbedder, HFEmbedder

# OpenAI
emb = OpenAIEmbedder(api_key="sk-…")
vectors = emb.embed(chunks)

# HF
hf = HFEmbedder("all-MiniLM-L6-v2")
vectors = hf.embed(chunks)
```

### 4. Vector Stores

```python
from agentlib.rag.vector_store import FAISSStore, ChromaStore

# FAISS
faiss_store = FAISSStore()
faiss_store.add(vectors, metadatas)

# Chroma
chroma_store = ChromaStore(collection_name="docs")
chroma_store.add(vectors, metadatas)
```

### 5. Retrievers

```python
from agentlib.rag.retrievers.standard_rag import StandardRAG
from agentlib.rag.retrievers.hybrid_rag import HybridRAG
from agentlib.rag.reranker import Reranker

# Standard
std = StandardRAG(api_key="sk-…", store=faiss_store)
docs = std.retrieve("latest sales numbers")

# Hybrid (requires a text_store with .keyword_search)
hyb = HybridRAG(text_store, std, reranker=None)
docs = hyb.retrieve("menu allergens", top_k=10)

# HyDE
from agentlib.rag.retrievers.hyde_rag import HyDERAG
hyde = HyDERAG(api_key="sk-…", llm_model="gpt-4", embed_model="text-embedding-ada-002", store=faiss_store)
docs = hyde.retrieve("What is the side effect of Drug X?")

# Speculative
from agentlib.rag.retrievers.speculative_rag import SpeculativeRAG
spec = SpeculativeRAG(api_key="sk-…", llm_model="gpt-4", embedder=emb, store=faiss_store, reranker=Reranker(LLMClient(...)))
docs = spec.retrieve("Recommend top 3 hotels in Paris", top_k=5)
```

### 6. Contextual & Long-Form

```python
from agentlib.rag.retrievers.contextual_rag import ContextualRAG
from agentlib.rag.retrievers.long_rag import LongRAG

# Contextual: pass prior chat turns
ctx = ContextualRAG(std, context_window=4)
docs = ctx.retrieve("Check appointment available", context=chat_history)

# Long-Form: index then retrieve
long = LongRAG(api_key="sk-…", store=faiss_store, chunk_size=800, overlap=200)
long.index_document("big_manual", raw_text)
docs = long.retrieve("How to calibrate machine?")
```

### 7. Reranking

```python
from agentlib.rag.reranker import Reranker
from agentlib.llm.client import LLMClient

llm = LLMClient(api_key="sk-…", model="gpt-4")
reranker = Reranker(llm)
ranked = reranker.rerank("urgent compliance update", docs)
```

---

## 🔄 End-to-End Example

```python
from agentlib.rag.connectors.pdf_loader import PDFLoader
from agentlib.rag.chunker import Chunker
from agentlib.rag.embedder import OpenAIEmbedder
from agentlib.rag.vector_store import FAISSStore
from agentlib.rag.retrievers.standard_rag import StandardRAG

# 1) Load
loader = PDFLoader("guide.pdf")
pages = loader.load()  # list of {source, text}

# 2) Chunk & Embed & Index
chunker = Chunker(1000, 200)
store   = FAISSStore()
emb     = OpenAIEmbedder(api_key="sk-…")

for doc in pages:
    chunks = chunker.chunk(doc["text"], mode="sentence")
    vectors = emb.embed(chunks)
    metas   = [{"source": doc["source"], "chunk": i, "text": c} for i,c in enumerate(chunks)]
    store.add(vectors, metas)

# 3) Retrieve
rag = StandardRAG(api_key="sk-…", store=store)
results = rag.retrieve("Installation steps for module X", top_k=3)
for r in results:
    print(r["metadata"]["text"], "(score:", r["score"], ")")
```

---

## 🔧 Customization & Extensions

- **Add new connectors** under `rag/connectors/` by subclassing `BaseConnector`.  
- **Add new retrievers** under `rag/retrievers/` by subclassing `BaseRetriever`.  
- Tweak **chunk_size**, **overlap**, **top_k**, **reranking** strategy via config.  
- Combine **multiple retrievers** in a custom pipeline for domain‐specific performance.
