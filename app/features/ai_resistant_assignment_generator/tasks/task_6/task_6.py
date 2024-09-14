import sys
import os
import streamlit as st
import chromadb

# Assuming 'syllabus_generator' is in the module path
sys.path.append(r"C:\Users\cerde\Desktop\syllabus\kai-ai-backend\app\features\syllabus_generator")

# Import directly from the task modules
from tasks.task_3.task_3 import DocumentProcessor
from tasks.task_4.task_4 import EmbeddingClient
from tasks.task_5.task_5 import ChromaCollectionCreator

if __name__ == "__main__":
    st.header("Syllabus Generator")

    # Configuration for EmbeddingClient
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "clever-aleph-430315-m7",
        "location": "us-east4"
    }

    # Screen 1: Ingest data from various sources
    screen = st.empty()
    document = None  # Initialize 'document' to None

    with screen.container():
        # 1) Initialize DocumentProcessor to handle different data types
        processor = DocumentProcessor()

        # Offer different options for data input
        st.write("Select the data source for syllabus generation:")

        data_source = st.radio("Choose the data source:",
                               ("Upload PDF", "Enter Text", "YouTube Video Link", "Google Sheets/CSV", "Google Slides/PPT", "Web Pages", "Notes"))

        # Handle the selected data input
        if data_source == "Upload PDF":
            processor.ingest_documents()
        elif data_source == "Enter Text":
            text_data = st.text_area("Enter the text for syllabus generation:")
            if text_data:
                processor.pages.append(text_data)
        elif data_source == "YouTube Video Link":
            video_link = st.text_input("Enter the YouTube video link:")
            if video_link:
                # Assume some function to extract transcript from YouTube
                transcript = get_youtube_transcript(video_link)  # Placeholder function
                processor.pages.append(transcript)
        elif data_source == "Google Sheets/CSV":
            uploaded_file = st.file_uploader("Upload your Google Sheets or CSV file", type=["csv", "xlsx"])
            if uploaded_file:
                # Assume some function to process CSV or Google Sheets
                csv_data = process_csv_or_sheets(uploaded_file)  # Placeholder function
                processor.pages.append(csv_data)
        elif data_source == "Google Slides/PPT":
            uploaded_file = st.file_uploader("Upload your Google Slides or PPT file", type=["pptx"])
            if uploaded_file:
                # Assume some function to process PPT or Google Slides
                ppt_data = process_ppt_or_slides(uploaded_file)  # Placeholder function
                processor.pages.append(ppt_data)
        elif data_source == "Web Pages":
            web_page_link = st.text_input("Enter the web page URL:")
            if web_page_link:
                # Assume some function to scrape web page content
                web_content = scrape_web_page(web_page_link)  # Placeholder function
                processor.pages.append(web_content)
        elif data_source == "Notes":
            notes = st.text_area("Enter your notes (Markdown supported):")
            if notes:
                processor.pages.append(notes)

        # 2) Initialize the EmbeddingClient from Task 4 with embed config
        embed_client = EmbeddingClient(**embed_config)

        # 3) Initialize the ChromaCollectionCreator from Task 5
        chroma_creator = ChromaCollectionCreator(processor, embed_client)

        with st.form("Generate Syllabus"):
            st.subheader("Syllabus Builder")
            st.write("Select the data source, enter the topic, and click Generate!")

            # Capture user inputs for the syllabus topic
            st.write("Topic for Syllabus")
            topic_input = st.text_input(label='Topic for Syllabus', placeholder='Enter the topic of the document', label_visibility='hidden')

            submitted = st.form_submit_button("Generate Syllabus!")
            if submitted:
                # 4) Create the Chroma collection with the ingested data
                chroma_creator.create_chroma_collection()

                # 5) Query the Chroma collection with the user's input topic to generate the syllabus
                document = chroma_creator.query_chroma_collection(topic_input)
                
    # Screen 2: Display the generated syllabus
    if document:
        screen.empty()
        with st.container():
            st.header("Generated Syllabus")
            # If document.page_content is a list of strings, join them into one string with proper formatting
            content = document.page_content
            if isinstance(content, list):
                content = ' '.join(content).replace("', '", "\n").replace("['", "").replace("']", "")
            st.write(content)  # Display the content of the document
