# tests/test_tools.py

import pytest
from syllabus_generator.tools import ingest_documents, setup_embedding_client, create_chroma_collection, generate_syllabus_content, display_syllabus_content

@pytest.fixture
def sample_files():
    # Create or mock sample files needed for testing
    return ["sample1.pdf", "sample2.pdf"]

@pytest.fixture
def embed_config():
    return {
        "model_name": "textembedding-gecko@003",
        "project": "macro-boulevard-426914-e8",
        "location": "us-east4"
    }

def test_ingest_documents(sample_files):
    processor = ingest_documents(sample_files)
    assert processor is not None
    assert hasattr(processor, "pages")

def test_setup_embedding_client(embed_config):
    embed_client = setup_embedding_client(embed_config)
    assert embed_client is not None
    assert hasattr(embed_client, "model")

def test_create_chroma_collection(sample_files, embed_config):
    processor = ingest_documents(sample_files)
    embed_client = setup_embedding_client(embed_config)
    chroma_creator = create_chroma_collection(processor, embed_client)
    assert chroma_creator is not None
    assert hasattr(chroma_creator, "chroma_collection")

def test_generate_syllabus_content(sample_files, embed_config):
    processor = ingest_documents(sample_files)
    embed_client = setup_embedding_client(embed_config)
    chroma_creator = create_chroma_collection(processor, embed_client)
    syllabus = generate_syllabus_content("10", "History", "World War II", chroma_creator)
    assert syllabus is not None
    assert isinstance(syllabus, dict)  # or the expected type

def test_display_syllabus_content(capsys):
    sample_syllabus = {"title": "Sample Syllabus", "content": "This is a sample syllabus content."}
    display_syllabus_content(sample_syllabus)
    captured = capsys.readouterr()
    assert "Sample Syllabus" in captured.out
    assert "This is a sample syllabus content." in captured.out
