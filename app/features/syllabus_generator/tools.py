# tools.py

import os
import sys
sys.path.append(os.path.abspath('../../'))  # Update the path as needed
from tasks.task_3.task_3 import DocumentProcessor
from tasks.task_4.task_4 import EmbeddingClient
from tasks.task_5.task_5 import ChromaCollectionCreator
from tasks.task_6.task_6 import generate_syllabus
from tasks.task_7.task_7 import display_syllabus

def ingest_documents(files):
    processor = DocumentProcessor()
    processor.ingest_documents(files)
    return processor

def setup_embedding_client(config):
    return EmbeddingClient(**config)

def create_chroma_collection(processor, embed_client):
    chroma_creator = ChromaCollectionCreator(processor, embed_client)
    chroma_creator.create_chroma_collection()
    return chroma_creator

def generate_syllabus_content(grade_level, topic, context, chroma_creator):
    return generate_syllabus(grade_level=grade_level, topic=topic, context=context, chroma_creator=chroma_creator)

def display_syllabus_content(syllabus):
    display_syllabus(syllabus)
