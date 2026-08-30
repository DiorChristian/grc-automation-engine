import os
import chromadb
from chromadb.utils import embedding_functions

class ComplianceRAGEngine:
    def __init__(self, db_path="./chroma_compliance_db"):
        # Initialize local persistent Chroma client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Use default lightweight local embedding function
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create collection for NIST / HIPAA controls
        self.collection = self.client.get_or_create_collection(
            name="enterprise_compliance_controls",
            embedding_function=self.embedding_function
        )

    def ingest_controls(self, documents: list, metadatas: list, ids: list):
        """
        Ingests compliance framework text chunks (e.g., NIST SP 800-53) 
        into the local vector database.
        """
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"[+] Successfully embedded and stored {len(ids)} compliance controls locally.")

    def query_control(self, drift_description: str, n_results: int = 2) -> str:
        """
        Queries ChromaDB semantically using the live AWS drift event description
        to pull the exact statutory compliance requirements.
        """
        results = self.collection.query(
            query_texts=[drift_description],
            n_results=n_results
        )
        
        retrieved_texts = results.get("documents", [[]])[0]
        retrieved_metas = results.get("metadatas", [[]])[0]
        
        context_block = ""
        for text, meta in zip(retrieved_texts, retrieved_metas):
            control_id = meta.get("control_id", "N/A")
            framework = meta.get("framework", "NIST/HIPAA")
            context_block += f"\n--- [{framework} Control: {control_id}] ---\n{text}\n"
            
        return context_block