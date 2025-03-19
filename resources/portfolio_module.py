import os
os.environ["PYTHONUTF8"] = "1"  # Ensures UTF-8 compatibility
os.environ["LD_LIBRARY_PATH"] = "/usr/local/lib"  # Helps with SQLite compatibility
import pandas as pd
import chromadb
import uuid

# Force Python to use `pysqlite3` instead of built-in `sqlite3`
import pysqlite3
import sys
sys.modules["sqlite3"] = pysqlite3  # Override sqlite3 module

class Portfolio:
    def __init__(self, file_path=None):
        if file_path is None:
            file_path = os.path.join(os.getcwd(), "resources", "my_portfolio.csv")

        self.file_path = file_path

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Portfolio CSV not found at {file_path}")

        self.data = pd.read_csv(file_path)
        self.chroma_client = chromadb.PersistentClient("./vectorstore")
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        if not self.collection.count():
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=row["Techstack"],
                    metadatas={"links": row["Links"]},
                    ids=[str(uuid.uuid4())]
                )

    def query_links(self, skills):
        result = self.collection.query(query_texts=skills, n_results=2)
        return result.get("metadatas", []) if result else []
