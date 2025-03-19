import sqlite3
import pandas as pd
import chromadb
import uuid
import os


class Portfolio:
    def __init__(self, file_path="resources/my_portfolio.csv"):
        self.file_path = file_path

        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Portfolio CSV not found at {file_path}")

        self.data = pd.read_csv(file_path)
        self.chroma_client = chromadb.PersistentClient("./vectorstore")  # Ensure this is a valid path
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
