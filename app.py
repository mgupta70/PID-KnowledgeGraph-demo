import os
import cv2
import numpy as np
from pathlib import Path
from neo4j import GraphDatabase
from helpers import *
from few_shot import examples
import streamlit as st
from langchain_community.graphs import Neo4jGraph 
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import OpenAIEmbeddings
from streamlit_image_comparison import image_comparison
os.environ["OPENAI_API_KEY"] = st.secrets["openai_api_key"]

#############
## Load data
#############
# 1. Load image
image_path = Path('data/0.jpg')
original_image = cv2.imread(str(image_path))
image = crop_image(original_image, 400, 5500, 400, 4200)
image = (image > 200).astype(np.uint8)*255

# 2. Load nodes and edges data
# edges
edges_path = Path('data/0_refined_edges_dict.pkl')
edges_dict = load_pickle(edges_path)

# nodes
nodes_path = Path('data/0_refined_nodes_dict.pkl')
nodes_dict = load_pickle(nodes_path)

col1, col2 = st.columns(2)
with col1:
    st.image(image, caption='Original P&ID')
with col2:
    nx_graph = cv2.imread('media/KG_networkx.png')
    nx_graph = cv2.cvtColor(nx_graph, cv2.COLOR_BGR2RGB)
    nx_graph = cv2.flip(nx_graph, 0)
    st.image(nx_graph, caption='Geometrically Aligned Graph using networkx')
image_comparison(
    img1=image,
    img2=nx_graph,
)


######################
## Create Neo4j graph
######################
# Step-1: make connection to database
# database credentials
uri = st.secrets["neo4j_uri"]
user = st.secrets["neo4j_user"]
password = st.secrets["neo4j_password"]
data_base_connection = GraphDatabase.driver(uri = uri, auth = (user, password)) 
pidKG = data_base_connection.session() 

######################
## Develop QA system
######################

# Get schema

pidKG_schema = """
Node properties:
- **Symbol**
  - `alias`: STRING Example: "symbol_11"
  - `center_x`: INTEGER Min: 643, Max: 5216
  - `center_y`: INTEGER Min: 644, Max: 3979
  - `class`: INTEGER Min: 1, Max: 32
  - `tag`: STRING Example: "SDL 101"
- **Junction**
  - `alias`: STRING Example: "J57"
  - `center_x`: INTEGER Min: 643, Max: 5204
  - `center_y`: INTEGER Min: 798, Max: 3934
  - `class`: INTEGER Min: -999, Max: -999
  - `tag`: STRING Example: "line_NN_515-line_NN_645"
Relationship properties:

The relationships:
(:Symbol)-[:CONNECTED_TO]->(:Symbol)
(:Symbol)-[:CONNECTED_TO]->(:Junction)
(:Junction)-[:CONNECTED_TO]->(:Symbol)
(:Junction)-[:CONNECTED_TO]->(:Junction)
"""


questions = ["What is total number of class 10 symbols?", "How many 10 with 2?"]

# No graph schema
cypher_generating_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0) # most-deterministic 


pidKG_schema = ''' Node properties:
- **Junction**
  - `alias`: STRING Example: "J55"
  - `tag`: STRING Example: "line_NN_513-line_NN_713"
  - `class`: INTEGER Min: -999, Max: -999
  - `center_x`: INTEGER Min: 643, Max: 5204
  - `center_y`: INTEGER Min: 798, Max: 3934
- **Symbol**
  - `alias`: STRING Example: "symbol_20"
  - `tag`: STRING Example: "OP-39294"
  - `class`: INTEGER Min: 1, Max: 32
  - `center_x`: INTEGER Min: 643, Max: 5216
  - `center_y`: INTEGER Min: 644, Max: 3979
Relationship properties:

The relationships:
(:Junction)-[:CONNECTED_TO]->(:Junction)
(:Junction)-[:CONNECTED_TO]->(:Symbol)
(:Symbol)-[:CONNECTED_TO]->(:Symbol)
(:Symbol)-[:CONNECTED_TO]->(:Junction)

Important Note - in graph, even though there are directions, the relationships are bidirectional.

'''
# import chromadb

# chromadb.api.client.SharedSystemClient.clear_system_cache()

system_prompt_for_generating_cypher = f'''You are a Neo4j expert. Given an input question, create a syntactically correct Cypher query to run. 
Here is the schema information for the underlying graph database: {pidKG_schema}.
Don't add any preambles, just return the correct cypher query with no further commentary.
Output the final Cypher query only.'''

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples, # examples to select from
    OpenAIEmbeddings(), # embedding class to produce embeddings to measure semantic similarity.
    FAISS, # Chroma (old): VectorStore class that is used to store the embeddings
    k=5, # number of examples to produce.

)

def run_query(query, session):
    result = session.run(query)
    return [record for record in result]

# get question from user
# user_question = st.text_input("Enter your question: ")
st.write("This P&ID contains 32 symbols, each labeled numerically from 1 to 32.")
st.write("Try asking questions related to counting or connections between symbols.")
questions = ["What is total number of class 10 symbols?", 
             "Count the number of 10 symbols that are directly connected to 18 symbols",
             "Are class 11 and class 28 symbols connected to one another?.", 
             "What are the tags of class 12 symbols?",
             "Can you determine if symbols of class 10 are situated between those of class 4 and class 12?",
             ]

# Let the user select or enter a custom question
user_question = st.selectbox("See example questions or enter your own:", ["Enter a new question..."] + questions)

# If the user selects "Enter a new question...", show a text input field
if user_question == "Enter a new question...":
    user_question = st.text_input("Enter your question:")


if user_question:
    selected_fewshot_examples = example_selector.select_examples({"question": user_question})

    messages = [SystemMessage(f"{system_prompt_for_generating_cypher}"),
                SystemMessage(f"Here is few examples of questions and their corresponding Cypher queries: {selected_fewshot_examples}."),
                HumanMessage(f"{user_question}")]
    cypher_generated = cypher_generating_model(messages).content #.strip()

    

    st.write(f"User query converted to: {cypher_generated}")
    # run query
    
    result = run_query(cypher_generated, pidKG)
    output_text = "\n".join(str(record) for record in result)
    st.text_area("Query Results", output_text, height=100)
    # for record in result:
    #     st.write(record)



    