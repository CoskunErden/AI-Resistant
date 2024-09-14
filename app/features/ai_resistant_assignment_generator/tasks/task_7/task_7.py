import streamlit as st
from langchain_google_vertexai import VertexAI
from langchain_core.prompts import PromptTemplate
import os
import sys

# Add the syllabus generator path to sys.path
sys.path.append(r"C:\Users\cerde\Desktop\syllabus\kai-ai-backend\app\features\syllabus_generator")

# Import necessary modules from the tasks
from tasks.task_3.task_3 import DocumentProcessor
from tasks.task_4.task_4 import EmbeddingClient
from tasks.task_5.task_5 import ChromaCollectionCreator
from langchain_core.documents import Document

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\cerde\Desktop\syllabus\kai-ai-backend\app\local-auth.json"

class SyllabusGenerator:
    def __init__(self, topic=None, vectorstore=None, grade_level=None, duration=None, learning_objectives=None, 
                 prerequisites=None, format=None, assessment_methods=None, resources=None, teaching_methods=None,
                 special_requirements=None, syllabus_type=None):
        self.topic = topic if topic else "General Topic"
        self.vectorstore = vectorstore
        self.grade_level = grade_level
        self.duration = duration
        self.learning_objectives = learning_objectives
        self.prerequisites = prerequisites
        self.format = format
        self.assessment_methods = assessment_methods
        self.resources = resources
        self.teaching_methods = teaching_methods
        self.special_requirements = special_requirements
        self.syllabus_type = syllabus_type
        self.llm = None
        self.system_template = """
            You are an expert in the topic: {topic}

            Create a detailed syllabus considering the following parameters:

            - Grade Level: {grade_level}
            - Duration: {duration}
            - Learning Objectives: {learning_objectives}
            - Prerequisites: {prerequisites}
            - Format: {format}
            - Assessment Methods: {assessment_methods}
            - Resources: {resources}
            - Teaching Methods: {teaching_methods}
            - Special Requirements: {special_requirements}
            - Syllabus Type: {syllabus_type}

            Structure the syllabus to include key topics and subtopics, descriptions, suggested readings or resources, and any other relevant details.

            Context: {context}
            """
    
    def init_llm(self):
        if self.llm is None:
            self.llm = VertexAI(
                model_name="gemini-pro",
                temperature=0.8,
                max_output_tokens=500
            )
    
    def generate_syllabus_with_vectorstore(self):
        if self.llm is None:
            self.init_llm()

        if self.vectorstore is None:
            raise ValueError("Vectorstore must be initialized for generating the syllabus.")

        from langchain_core.runnables import RunnablePassthrough, RunnableParallel

        retriever = self.vectorstore.db.as_retriever()
        prompt_template = PromptTemplate.from_template(self.system_template)

        setup_and_retrieval = RunnableParallel(
            {"context": retriever, "topic": RunnablePassthrough()}
        )

        # Retrieve the context from the vectorstore
        context_result = setup_and_retrieval.invoke({"topic": self.topic})

        # Debugging: Check what context_result looks like
        print(f"context_result: {context_result}")

        # Convert the context into a string in a safe manner
        if isinstance(context_result, list):
            context = "\n".join([doc.page_content if isinstance(doc, Document) else str(doc) for doc in context_result])
        elif isinstance(context_result, dict):
            context = context_result.get('page_content', str(context_result))
        else:
            context = str(context_result)

        # Now format the prompt using the properly converted context and other details
        prompt = prompt_template.format(
            topic=self.topic,
            grade_level=self.grade_level,
            duration=self.duration,
            learning_objectives=self.learning_objectives,
            prerequisites=self.prerequisites,
            format=self.format,
            assessment_methods=self.assessment_methods,
            resources=self.resources,
            teaching_methods=self.teaching_methods,
            special_requirements=self.special_requirements,
            syllabus_type=self.syllabus_type,
            context=context
        )

        # Use the LLM to generate the syllabus based on the prompt
        response = self.llm.generate(prompt)
        return response


if __name__ == "__main__":
    st.header("Syllabus Generator")

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
        st.subheader("Syllabus Builder")
        st.write("Select the data source for ingestion, enter the syllabus details, and click Generate!")

        # Gather input for the syllabus
        topic_input = st.text_input("Topic for Syllabus", placeholder="Enter the topic for the syllabus")
        grade_level = st.selectbox("Grade Level", ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate"])
        duration = st.text_input("Course Duration", placeholder="e.g., 6 weeks, 1 semester")
        learning_objectives = st.text_area("Learning Objectives", placeholder="List the learning objectives")
        prerequisites = st.text_area("Prerequisites", placeholder="List any prerequisites")
        course_format = st.selectbox("Course Format", ["In-Person", "Online", "Hybrid"])
        assessment_methods = st.text_area("Assessment Methods", placeholder="e.g., Quizzes, Assignments, Exams")
        resources = st.text_area("Suggested Resources", placeholder="e.g., textbooks, articles")
        teaching_methods = st.text_area("Teaching Methods", placeholder="e.g., Lectures, Group Discussions")
        special_requirements = st.text_area("Special Requirements", placeholder="List any special requirements")
        syllabus_type = st.selectbox("Syllabus Type", ["Thematic", "Chronological", "Modular"])

        submitted = st.form_submit_button("Generate Syllabus")
        
        syllabus = None  # Initialize syllabus to None

        if submitted:
            try:
                chroma_creator.create_chroma_collection()
                generator = SyllabusGenerator(
                    topic=topic_input,
                    vectorstore=chroma_creator,
                    grade_level=grade_level,
                    duration=duration,
                    learning_objectives=learning_objectives,
                    prerequisites=prerequisites,
                    format=course_format,
                    assessment_methods=assessment_methods,
                    resources=resources,
                    teaching_methods=teaching_methods,
                    special_requirements=special_requirements,
                    syllabus_type=syllabus_type
                )
                syllabus = generator.generate_syllabus_with_vectorstore()
            except IndexError as e:
                st.error(f"Failed to create Chroma Collection: {e}")
            except Exception as e:
                st.error(f"An error occurred while generating the syllabus: {e}")
    if syllabus:
        st.header("Generated Syllabus:")
        st.json(syllabus)
