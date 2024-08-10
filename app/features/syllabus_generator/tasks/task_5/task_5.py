import sys
import os
import streamlit as st

# Absolute paths to task directories
persist_directory = r"C:\Users\cerde\Desktop\syllabus\kai-ai-backend\app\features\syllabus_generator\chroma_db"

# Adding task directories to sys.path
sys.path.append(os.path.abspath('../../'))
# Import Task 3 and Task 4 modules
from tasks.task_3.task_3 import DocumentProcessor
from tasks.task_4.task_4 import EmbeddingClient

# Import other required libraries
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma

# Set the path to service account key file
credentials_path = r"C:\Users\cerde\Desktop\syllabus\kai-ai-backend\app\local-auth.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path


class ChromaCollectionCreator:
    def __init__(self, processor, embed_model):
        """
        Initializes the ChromaCollectionCreator with a DocumentProcessor instance and embeddings configuration.
        :param processor: An instance of DocumentProcessor that has processed documents.
        :param embeddings_config: An embedding client for embedding documents.
        """
        self.processor = processor  # This will hold the DocumentProcessor from Task 3
        self.embed_model = embed_model  # This will hold the EmbeddingClient from Task 4
        self.db = None  # This will hold the Chroma collection
        # Ensure the persist directory exists
        if not os.path.exists(persist_directory):
            os.makedirs(persist_directory)

    def create_chroma_collection(self):
        """
        Task: Create a Chroma collection from the documents processed by the DocumentProcessor instance.

        Steps:
        1. Check if any documents have been processed by the DocumentProcessor instance. If not, display an error message using streamlit's error widget.

        2. Split the processed documents into text chunks suitable for embedding and indexing. Use the CharacterTextSplitter from Langchain to achieve this. You'll need to define a separator, chunk size, and chunk overlap.
        3. Create a Chroma collection in memory with the text chunks obtained from step 2 and the embeddings model initialized in the class. Use the Chroma.from_documents method for this purpose.
        """
        
        # Step 1: Check for processed documents
        if len(self.processor.pages) == 0:
            st.error("No documents found!", icon="🚨")
            return
        # Convert each page to a Document object
        documents = [Document(page_content=str(page)) for page in self.processor.pages]

        # Step 2: Split documents into text chunks
        text_splitter = CharacterTextSplitter(
            separator='\n',  # Define a suitable separator
            chunk_size=1000,  # Define the chunk size
            chunk_overlap=200,  # Define the chunk overlap
            length_function=len
        )
        texts = text_splitter.split_documents(documents)
        if texts:
            st.success(f"Successfully split pages into {len(texts)} documents!", icon="✅")
        else:
            st.error("Failed to split documents into chunks!", icon="🚨")
            return

        # Step 3: Create the Chroma Collection
        try:
            self.db = Chroma.from_documents(
                documents=texts,
                embedding=self.embed_model,
                persist_directory=persist_directory
            )
            st.success(f"Successfully created Chroma Collection!", icon="✅")
        except Exception as e:
            st.error(f"Failed to create Chroma Collection: {str(e)}", icon="🚨")

    def as_retriever(self):
        if self.db:
            return self.db.as_retriever()  # Assuming this is the correct method
        else:
            raise ValueError("Chroma collection is not initialized.")

    def query_chroma_collection(self, query) -> Document:
        """
        Queries the created Chroma collection for documents similar to the query.
        :param query: The query string to search for in the Chroma collection.

        Returns the first matching document from the collection with similarity score.
        """
        if self.db:
            retriever = self.as_retriever()
            docs = retriever.get_relevant_documents(query)
            if docs:
                return docs[0]
            else:
                st.error("No matching documents found!", icon="🚨")
        else:
            st.error("Chroma Collection has not been created!", icon="🚨")

if __name__ == "__main__":
    processor = DocumentProcessor()  # Initialize from Task 3

    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "clever-aleph-430315-m7",
        "location": "us-east4"
    }

    embed_client = EmbeddingClient(**embed_config)  # Initialize from Task 4

    chroma_creator = ChromaCollectionCreator(processor, embed_client)

    with st.form("Load Data to Chroma"):
        st.write("Select PDFs for Ingestion, then click Submit")

        # Ingest documents from PDF uploader
        processor.ingest_documents()

        submitted = st.form_submit_button("Submit")
        if submitted:
            chroma_creator.create_chroma_collection()
