import sys
import os
import streamlit as st
import chromadb

# Update sys.path to include the directory for the AI-Resistant Assignment Generator
sys.path.append(r"C:\Users\cerde\Desktop\RadicalAI\AI-Resistant\app\features\ai_resistant_assignment_generator")

# Import directly from the task modules
from langchain_core.documents import Document
from tasks.task_3.task_3 import DocumentProcessor
from tasks.task_4.task_4 import EmbeddingClient
from tasks.task_5.task_5 import ChromaCollectionCreator

if __name__ == "__main__":
    st.header("AI-Resistant Assignment Generator")

    # Configuration for EmbeddingClient
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "ai-resistant",
        "location": "us-east4"
    }

    # Screen 1: Ingest data from various sources
    screen = st.empty()
    document = None  # Initialize 'document' to None

    with screen.container():
        # 1) Initialize DocumentProcessor to handle different data types
        processor = DocumentProcessor()

        # Offer different options for data input
        st.write("Select the data source for assignment generation:")

        data_source = st.radio("Choose the data source:",
                               ("Upload PDF", "Upload DOCX", "Upload PPT", "Enter Plain Text"))

        # Handle the selected data input
        if data_source == "Upload PDF":
            processor.ingest_documents()  # Assuming this handles PDF processing
        elif data_source == "Upload DOCX":
            uploaded_file = st.file_uploader("Upload your DOCX file", type=["docx"])
            if uploaded_file:
                # Process DOCX files
                docx_data = processor.handle_docx_upload(uploaded_file)
                processor.pages.append(docx_data)
        elif data_source == "Upload PPT":
            uploaded_file = st.file_uploader("Upload your PPT file", type=["pptx"])
            if uploaded_file:
                # Process PPT files
                ppt_data = processor.handle_google_slides_ppt_upload(uploaded_file)
                processor.pages.append(ppt_data)
        elif data_source == "Enter Plain Text":
            text_data = st.text_area("Enter the plain text for assignment generation:")
            if text_data:
                processor.pages.append(text_data)

        # 2) Initialize the EmbeddingClient from Task 4 with embed config
        embed_client = EmbeddingClient(**embed_config)

        # 3) Initialize the ChromaCollectionCreator from Task 5
        chroma_creator = ChromaCollectionCreator(processor, embed_client)

        with st.form("Generate Assignment"):
            st.subheader("Assignment Builder")
            st.write("Select the data source, enter the topic, and click Generate!")

            # Capture user inputs for the assignment topic
            st.write("Topic for Assignment")
            topic_input = st.text_input(label='Topic for Assignment', placeholder='Enter the topic of the document', label_visibility='hidden')

            submitted = st.form_submit_button("Generate Assignment!")
            if submitted:
                # 4) Create the Chroma collection with the ingested data
                chroma_creator.create_chroma_collection()

                # 5) Query the Chroma collection with the user's input topic to generate the assignment
                document = chroma_creator.query_chroma_collection(topic_input)
                
    # Screen 2: Display the generated assignment
    if document:
        screen.empty()
        with st.container():
            st.header("Generated Assignment")
            # If document.page_content is a list of strings, join them into one string with proper formatting
            content = document.page_content
            if isinstance(content, list):
                content = ' '.join(content).replace("', '", "\n").replace("['", "").replace("']", "")
            st.write(content)  # Display the content of the document
