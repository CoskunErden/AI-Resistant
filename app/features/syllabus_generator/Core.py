import streamlit as st
import os
import sys
import json

sys.path.append(os.path.abspath('../../'))  # to be updated
from tasks.task_3.task_3 import DocumentProcessor  # to be updated
from tasks.task_4.task_4 import EmbeddingClient # to be updated
from tasks.task_5.task_5 import ChromaCollectionCreator # to be updated
from tasks.task_6.task_6 import generate_syllabus # to be updated
from tasks.task_7.task_7 import display_syllabus # to be updated
persist_directory = r"C:\Users\cerde\Desktop\RadicalAI\mission-quizify\chroma_db"

embed_config = {
    "model_name": "textembedding-gecko@003",
    "project": "macro-boulevard-426914-e8",
    "location": "us-east4"
}

def main():
    # Add Session State
    if 'syllabus' not in st.session_state or len(st.session_state['syllabus']) == 0:
        st.session_state['syllabus'] = {}
    
        screen = st.empty()
        with screen.container():
            st.header("Syllabus Generator")
            
            # Create a new st.form flow control for Data Ingestion
            with st.form("Load Data to Chroma"):
                st.write("Select PDFs for Ingestion, provide the topic and context for the syllabus, and click Generate!")
                
                processor = DocumentProcessor()
                files = st.file_uploader("Upload your documents", type=['pdf'], accept_multiple_files=True)
                if files:
                    processor.ingest_documents()

                embed_client = EmbeddingClient(**embed_config) 
            
                chroma_creator = ChromaCollectionCreator(processor, embed_client)
                
                # Step 2: Set topic input and context using Streamlit's widgets for input
                topic_input = st.text_input("Topic for Syllabus", placeholder="Enter the topic of the document")
                context_input = st.text_area("Context for Syllabus", placeholder="Enter the context or instructions for the syllabus")
                    
                submitted = st.form_submit_button("Submit")
                
                if submitted:
                    chroma_creator.create_chroma_collection()
                        
                    if len(processor.pages) > 0:
                        st.write(f"Generating syllabus for topic: {topic_input}")
                    
                    # Generate syllabus
                    syllabus = generate_syllabus(grade_level="N/A", topic=topic_input, context=context_input, chroma_creator=chroma_creator)
                    st.session_state["syllabus"] = syllabus
                    st.session_state["display_syllabus"] = True

    if st.session_state.get("display_syllabus", False):
        display_syllabus(st.session_state["syllabus"])


