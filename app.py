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
from helpers import *
from qa_system import *
os.environ["OPENAI_API_KEY"] = st.secrets["openai_api_key"]

import base64
#############
## Page Set up
#############
st.set_page_config(page_title="PIDQA")
st.title("P&ID QA System")


def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.
 
    Returns
    -------
    The background.
    '''
    # set bg name
    main_bg_ext = "png"
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
    
set_bg_hack("media/KG_neo4j.png")



#############
## Load data
#############
# Image
image_path = Path('data/0.jpg')
original_image = cv2.imread(str(image_path))
image = crop_image(original_image, 400, 5500, 400, 4200)
image = (image > 200).astype(np.uint8)*255

# Edges data
edges_dict = load_pickle(Path('data/0_refined_edges_dict.pkl'))

# Nodes data
nodes_dict = load_pickle(Path('data/0_refined_nodes_dict.pkl'))


######################
## Overlay Graph
######################
graph_as_image = original_image.copy()
graph_as_image = overlay_graph(graph_as_image, edges_dict, nodes_dict)
graph_as_image = crop_image(graph_as_image, 400, 5500, 400, 4200)
graph_as_image = (graph_as_image > 200).astype(np.uint8)*255

#####################
## Display Images
#####################
st.write("Use the slider to compare the original P&ID with the graph overlay.")
image_comparison(
    img1=image,
    img2=graph_as_image,
    label1="Original P&ID",
    label2="Graph Overlay",
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
             "Count the number of 10 symbols that are directly connected to 18 symbols",
             "Are class 11 and class 28 symbols connected to one another?.", 
             "What are the tags of class 12 symbols?",
             "Can you determine if symbols of class 10 are situated between those of class 4 and class 12?",
             ]

# Let the user select or enter a custom question
user_question = st.selectbox("See example questions or enter your own:", ["Enter a new question..."] + sample_questions)

# If the user selects "Enter a new question...", show a text input field
if user_question == "Enter a new question...":
    user_question = st.text_input("Enter your question:")

if user_question:
    # select few-shot examples dynamically
    selected_fewshot_examples = example_selector.select_examples({"question": user_question})
    # pass the user question and few-shot examples to the model
    messages = [SystemMessage(f"{system_prompt_for_generating_cypher}"),
                SystemMessage(f"Here is few examples of questions and their corresponding Cypher queries: {selected_fewshot_examples}."),
                HumanMessage(f"{user_question}")]
    # generate cypher query
    cypher_generated = cypher_generating_model(messages).content
    st.write(f"User query converted to: {cypher_generated}")
    # run the generated cypher query on the graph
    result = run_query(cypher_generated, pidKG)
    output_text = "\n".join(str(record) for record in result)
    st.text_area("Query Results", output_text, height=100)



    