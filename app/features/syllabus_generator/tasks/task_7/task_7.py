import streamlit as st
from langchain_google_vertexai import VertexAI
from langchain_core.prompts import PromptTemplate
import os
import sys

# Add the syllabus generator path to sys.path
sys.path.append(r"C:\Users\cerde\Desktop\syllabus\kai-ai-backend\app\features\syllabus_generator")

# Import necessary modules from previous tasks
from tasks.task_3.task_3 import DocumentProcessor
from tasks.task_4.task_4 import EmbeddingClient
from tasks.task_5.task_5 import ChromaCollectionCreator

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\cerde\Desktop\syllabus\kai-ai-backend\app\local-auth.json"

class SyllabusGenerator:
    def __init__(self, topic=None, vectorstore=None, grade_level=None, duration=None, learning_objectives=None, 
                 prerequisites=None, format=None, assessment_methods=None, resources=None, teaching_methods=None,
                 special_requirements=None, syllabus_type=None):
        """
        Initializes the SyllabusGenerator with various parameters to create a detailed and tailored syllabus.

        :param topic: The required topic of the syllabus.
        :param vectorstore: An optional vectorstore instance (e.g., ChromaDB) for querying information related to the syllabus topic.
        :param grade_level: The educational level for which the syllabus is being created (e.g., "Undergraduate").
        :param duration: The duration of the course or syllabus (e.g., "6 weeks").
        :param learning_objectives: A list of specific learning objectives or outcomes.
        :param prerequisites: A list of prerequisites or prior knowledge required.
        :param format: The format of the course (e.g., "online").
        :param assessment_methods: A list of assessment methods (e.g., "quizzes").
        :param resources: A list of suggested readings or resources.
        :param teaching_methods: A list of teaching methods or instructional strategies.
        :param special_requirements: Any special requirements or accommodations needed.
        :param syllabus_type: The type of syllabus (e.g., "thematic").
        """
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
        """
        Initialize the Large Language Model (LLM) for syllabus generation.
        """
        self.llm = VertexAI(
            model_name="gemini-pro",
            temperature=0.8,
            max_output_tokens=500
        )
    
    def generate_syllabus_with_vectorstore(self):
        """
        Generate a syllabus using the topic and additional parameters provided, along with context from the vectorstore.
        """
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

        chain = setup_and_retrieval | prompt_template | self.llm
        response = chain.invoke({
            "topic": self.topic,
            "grade_level": self.grade_level,
            "duration": self.duration,
            "learning_objectives": self.learning_objectives,
            "prerequisites": self.prerequisites,
            "format": self.format,
            "assessment_methods": self.assessment_methods,
            "resources": self.resources,
            "teaching_methods": self.teaching_methods,
            "special_requirements": self.special_requirements,
            "syllabus_type": self.syllabus_type
        })
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
        if submitted:
            try:
                chroma_creator.create_chroma_collection()
                st.success("Chroma Collection created successfully!")
            except Exception as e:
                st.error(f"An error occurred while creating Chroma Collection: {e}")

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

    if syllabus:
        st.header("Generated Syllabus:")
        st.json(syllabus)
