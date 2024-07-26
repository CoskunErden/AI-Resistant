import os
import sys

# Add the path to the project root or relevant directories
sys.path.append(os.path.abspath('../../'))  # needs to be updated

# Import the necessary classes from your task files
from tasks.task_3.task_3 import DocumentProcessor     # needs to be updated
from tasks.task_4.task_4 import EmbeddingClient       # needs to be updated 
from tasks.task_5.task_5 import ChromaCollectionCreator # needs to be updated
from tasks.task_8.task_8 import SyllabusGenerator  #not ready yet!

# Setup logger
from services.logger import setup_logger
logger = setup_logger()

def executor(grade_level: str, topic: str, context: str, files: list[ToolFile], verbose: bool = False) -> dict:
    """
    Generate a syllabus based on input parameters.

    Parameters:
    - grade_level (str): Educational grade level for the syllabus.
    - topic (str): Subject or topic for the syllabus.
    - context (str): Additional context or instructions for syllabus generation.
    - files (list[ToolFile]): List of files to process.
    - verbose (bool): Flag to output detailed logs for debugging.

    Returns:
    - dict: A dictionary containing the generated syllabus, including sections such as introduction, course outline, learning outcomes, assessment methods, and additional resources.
    """
    
    try:
        if verbose:
            logger.debug(f"Grade Level: {grade_level}, Topic: {topic}, Context: {context}")
            logger.debug(f"Files: {files}")

        # Step 1: Process the uploaded files
        document_processor = DocumentProcessor()
        processed_documents = []
        for file in files:
            processed_document = document_processor.process(file)
            processed_documents.append(processed_document)
        
        if verbose:
            logger.debug(f"Processed Documents: {processed_documents}")

        # Step 2: Generate text chunks from documents
        text_chunks = []
        for doc in processed_documents:
            chunks = document_processor.get_chunks(doc)
            text_chunks.extend(chunks)
        
        if verbose:
            logger.debug(f"Text Chunks: {text_chunks}")

        # Step 3: Create embeddings for text chunks
        embedding_client = EmbeddingClient()
        embeddings = embedding_client.embed(text_chunks)
        
        if verbose:
            logger.debug(f"Embeddings: {embeddings}")

        # Step 4: Create Chroma collection
        chroma_creator = ChromaCollectionCreator()
        chroma_collection = chroma_creator.create_collection(embeddings)
        
        if verbose:
            logger.debug(f"Chroma Collection: {chroma_collection}")

        # Step 5: Generate syllabus using the processed data
        quiz_generator = QuizGenerator(grade_level, topic, context, chroma_collection, verbose=verbose)
        syllabus = quiz_generator.create_syllabus()
        
        if verbose:
            logger.debug(f"Generated Syllabus: {syllabus}")
        
    except LoaderError as e:
        error_message = f"Error in processing files: {e}"
        logger.error(error_message)
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return syllabus

