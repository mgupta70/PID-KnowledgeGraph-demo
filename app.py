import os
import cv2
import numpy as np
from pathlib import Path
from neo4j import GraphDatabase
import streamlit as st
from langchain_community.graphs import Neo4jGraph 
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import OpenAIEmbeddings
from streamlit_image_comparison import image_comparison
from annotated_text import annotated_text
from helpers import *
from qa_system import *
os.environ["OPENAI_API_KEY"] = st.secrets["openai_api_key"]

import base64
#############
## Page Set up
#############
st.set_page_config(page_title="PIDQA", page_icon=":bulb:")
st.title("P&ID QA System")
# set_bg_hack("media/KG_neo4j_h.png")
#############
## Load data
#############
# Image
image_path = Path('data/0.png')
original_image = cv2.imread(str(image_path))
image = crop_image(original_image, 350, 3250, 800, 3200)
image = (image > 200).astype(np.uint8)*255


######################
## Overlay Graph
######################
graph_as_image_path = Path('data/0_graph.png')
graph_as_image = cv2.imread(str(graph_as_image_path))
graph_as_image = cv2.cvtColor(graph_as_image, cv2.COLOR_BGR2RGB)
graph_as_image = crop_image(graph_as_image, 250, 3250, 800, 3200)
graph_as_image = (graph_as_image > 200).astype(np.uint8)*255

#####################
## Display Images
#####################
annotated_text("Use the ", ("slider", ""), " to compare the original P&ID with the graph overlay.")
image_comparison(
    img1=image,
    img2=graph_as_image,
    label1="Original P&ID",
    label2="P&ID + Graph Overlay",
)

######################
## Create Neo4j graph
######################
# Make connection to database using database credentials
uri = st.secrets["neo4j_uri"]
user = st.secrets["neo4j_user"]
password = st.secrets["neo4j_password"]
data_base_connection = GraphDatabase.driver(uri = uri, auth = (user, password)) 
pidKG = data_base_connection.session() 
pidKG_schema = st.secrets["pidKG_schema"]
examples = st.secrets["examples"]

######################
## Develop QA system
######################
cypher_generating_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0) # temp = 0 -> most-deterministic 
system_prompt_for_generating_cypher = f'''You are a Neo4j expert. Given an input question, create a syntactically correct Cypher query to run. 
Here is the schema information for the underlying graph database: {pidKG_schema}.
Don't add any preambles, just return the correct cypher query with no further commentary.
Output the final Cypher query only.'''

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples, # examples to select from
    OpenAIEmbeddings(), # embedding class to produce embeddings to measure semantic similarity.
    FAISS, # Chroma (old): VectorStore class that is used to store the embeddings
    k=3, # number of examples to produce.
)

##########################
# get question from user
##########################
st.write("This is a Question Answering System for P&ID (Piping and Instrumentation Diagram) graphs.")
st.write("The P&ID linked above contains 32 symbols, each labeled numerically from 1 to 32.")
with st.expander("For more info on symbols representation - Click here"):
    st.image('media/one_shot_symbols.png')
    
st.write("Try asking questions related to counting or connections between symbols. While asking question ensure that you use the class number of the symbols as their names.")
sample_questions = ["What is total number of class 10 symbols?", 
             "Count the number of class 10 symbols that are directly connected to class 18 symbols",
             "Are class 11 and class 28 symbols connected to one another?", 
             "What are the tags of class 12 symbols?",
             "Can you determine if symbols of class 10 are situated between those of class 4 and class 12?",
             ]

# Let the user select or enter a custom question
user_question = st.selectbox("See example questions or enter your own:", ["I want to add a question"] + sample_questions)

# If the user wants to enter a question, show a text input field
if user_question == "I want to add a question":
    col1, col2 = st.columns([1, 6])
    with col2:
        annotated_text(("Enter your question:", "", "#fea"))
        user_question = st.text_input("")

if user_question:
    # guardrail
    message_g = [SystemMessage("Check if the Question asked by user talks about symbols or classes of symbols. Questions can be about number of symbols, types of symbols, connections between symbols - all related to piping and instrumentation diagrams. Output 1 if the question is about symbols else output 0. Don't add any preambles, just return the 0 or 1 with no further commentary."),
                 HumanMessage(f"{user_question}")]
    response_g = cypher_generating_model(message_g).content
    
    if response_g in  ["0", 0]:
        st.write("The question asked is not related to the Piping and Instrumentation knowledge graph.")
    else:
        st.write("Generating response...")

        # select few-shot examples dynamically
        selected_fewshot_examples = example_selector.select_examples({"question": user_question})
        # pass the user question and few-shot examples to the model
        messages = [SystemMessage(f"{system_prompt_for_generating_cypher}"),
                    SystemMessage(f"Here is few examples of questions and their corresponding Cypher queries: {selected_fewshot_examples}."),
                    HumanMessage(f"{user_question}")]
        # generate cypher query
        cypher_generated = cypher_generating_model(messages).content
        
        ##############################################
        # Run the generated cypher query on the graph
        ##############################################
        try:
            result = run_query(cypher_generated, pidKG)
            output_text = "\n".join(str(record) for record in result)
            qa_messages = [HumanMessage(f"Question is {user_question} and the answer by running cypher query is {result}: Generate a human readable answer for the question.")]
            response = cypher_generating_model(qa_messages).content # llm is same as cypher_generating_model
            if output_text is not None:
                st.text_area("Query Results", response, height=100)
            else:
                output_text = "Unable to get the results! Maybe the question is not right or is out-of-scope.If you think the question is valid, please try rephrasing it."
                st.text_area("Query Results", output_text, height=100)
        except Exception as e:
            output_text = "Unable to get the results! Maybe the question is not right or is out-of-scope.If you think the question is valid, please try rephrasing it."
            st.text_area("Query Results", output_text, height=100)
        

# Footer
st.markdown(
    '''
    :email:: Drop an email at mgupta70@asu.edu with your feedback or suggestion for more useful features related to P&ID processing ([Mohit Gupta](https://mgupta70.github.io), Ph.D., Arizona State University)
    '''
)

st.markdown("""
    <div style="
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        text-align: center;
        padding: 10px;
        box-shadow: 0px -2px 5px rgba(0,0,0,0.1);
    ">
        Enjoyed this demo on P&IDs? Drop a ⭐ on my GitHub and I will make more! on <a href="https://github.com/mgupta70/PID-KnowledgeGraph-demo" target="_blank">GitHub</a>
    </div>
    """,
    unsafe_allow_html=True)
