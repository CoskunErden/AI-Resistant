import streamlit as st
from langchain_google_vertexai import VertexAI
from langchain_core.prompts import PromptTemplate
import os
import sys

# Update sys.path to include the directory for the AI-Resistant Assignment Generator
sys.path.append(r"C:\Users\cerde\Desktop\RadicalAI\AI-Resistant\app\features\ai_resistant_assignment_generator")

# Import necessary modules from the tasks
from tasks.task_3.task_3 import DocumentProcessor
from tasks.task_4.task_4 import EmbeddingClient
from tasks.task_5.task_5 import ChromaCollectionCreator
from langchain_core.documents import Document

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\cerde\Desktop\RadicalAI\AI-Resistant\app\features\ai_resistant_assignment_generator\local-auth\local-auth.json"

class AIResistantAssignmentGenerator:
    def __init__(self, assignment_topic=None, vectorstore=None, grade_level=None, core_objectives=None, 
                 modifications=None, assignment_format=None, resources=None, assessment_methods=None):
        self.assignment_topic = assignment_topic if assignment_topic else "General Assignment Topic"
        self.vectorstore = vectorstore
        self.grade_level = grade_level
        self.core_objectives = core_objectives
        self.modifications = modifications
        self.assignment_format = assignment_format
        self.resources = resources
        self.assessment_methods = assessment_methods
        self.llm = None
        self.system_template = """
            You are an expert in designing educational assignments resistant to AI tools like ChatGPT or Gemini.

            Create an AI-resistant version of the assignment based on the following parameters:

            - Grade Level: {grade_level}
            - Core Objectives: {core_objectives}
            - Modifications: {modifications}
            - Format: {assignment_format}
            - Assessment Methods: {assessment_methods}
            - Resources: {resources}

            Context: {context}

            Provide three distinct versions of the assignment, with explanations on how each is designed to be resistant to AI tools.
            """
    
    def init_llm(self):
        if self.llm is None:
            self.llm = VertexAI(
                model_name="gemini-pro",
                temperature=0.8,
                max_output_tokens=500
            )
    
    def generate_ai_resistant_assignments(self):
        if self.llm is None:
            self.init_llm()

        if self.vectorstore is None:
            raise ValueError("Vectorstore must be initialized for generating the assignment.")

        from langchain_core.runnables import RunnablePassthrough, RunnableParallel

        retriever = self.vectorstore.db.as_retriever()
        prompt_template = PromptTemplate.from_template(self.system_template)

        setup_and_retrieval = RunnableParallel(
            {"context": retriever, "assignment_topic": RunnablePassthrough()}
        )

        # Retrieve the context from the vectorstore
        context_result = setup_and_retrieval.invoke({"assignment_topic": self.assignment_topic})

        # Debugging: Check what context_result looks like
        print(f"context_result: {context_result}")

        # Convert the context into a string in a safe manner
        if isinstance(context_result, list):
            context = "\n".join([doc.page_content if isinstance(doc, Document) else str(doc) for doc in context_result])
        elif isinstance(context_result, dict):
            context = context_result.get('page_content', str(context_result))
        else:
            context = str(context_result)

        # Format the prompt with assignment-related details and context
        prompt = prompt_template.format(
            assignment_topic=self.assignment_topic,
            grade_level=self.grade_level,
            core_objectives=self.core_objectives,
            modifications=self.modifications,
            assignment_format=self.assignment_format,
            assessment_methods=self.assessment_methods,
            resources=self.resources,
            context=context
        )

        # Use the LLM to generate AI-resistant assignments based on the prompt
        response = self.llm.generate(prompt)
        return response


if __name__ == "__main__":
    st.header("AI-Resistant Assignment Generator")

    # Configuration for EmbeddingClient
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "clever-aleph-430315-m7",
        "location": "us-east4"
    }

    # Initialize DocumentProcessor
    processor = DocumentProcessor()
    processor.ingest_documents()

    # Initialize EmbeddingClient
    embed_client = EmbeddingClient(**embed_config)

    # Initialize ChromaCollectionCreator
    chroma_creator = ChromaCollectionCreator(processor, embed_client)

    with st.form("Load Data to Chroma"):
        st.subheader("AI-Resistant Assignment Builder")
        st.write("Select the data source for ingestion, enter assignment details, and click Generate!")

        # Gather input for the assignment
        assignment_topic = st.text_input("Assignment Topic", placeholder="Enter the topic for the assignment")
        grade_level = st.selectbox("Grade Level", ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate"])
        core_objectives = st.text_area("Core Objectives", placeholder="List the core objectives for the assignment")
        modifications = st.text_area("AI-Resistance Modifications", placeholder="Describe how the assignment should be modified to resist AI tools")
        assignment_format = st.selectbox("Assignment Format", ["Essay", "Project", "Presentation", "Quiz", "Other"])
        assessment_methods = st.text_area("Assessment Methods", placeholder="e.g., Quizzes, Assignments, Peer Review")
        resources = st.text_area("Suggested Resources", placeholder="e.g., textbooks, articles")

        submitted = st.form_submit_button("Generate Assignment")
        
        assignment = None  # Initialize assignment to None

        if submitted:
            try:
                chroma_creator.create_chroma_collection()
                generator = AIResistantAssignmentGenerator(
                    assignment_topic=assignment_topic,
                    vectorstore=chroma_creator,
                    grade_level=grade_level,
                    core_objectives=core_objectives,
                    modifications=modifications,
                    assignment_format=assignment_format,
                    assessment_methods=assessment_methods,
                    resources=resources
                )
                assignment = generator.generate_ai_resistant_assignments()
            except IndexError as e:
                st.error(f"Failed to create Chroma Collection: {e}")
            except Exception as e:
                st.error(f"An error occurred while generating the assignment: {e}")
    if assignment:
        st.header("Generated AI-Resistant Assignments:")
        st.json(assignment)
