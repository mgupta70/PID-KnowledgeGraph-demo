import os, cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

from helpers import *
from few_shot import examples
import streamlit as st

os.environ["OPENAI_API_KEY"] = st.secrets["openai_api_key"]

#############
## Load data
#############
# 1. Load image
image_path = Path('data/0.jpg')
image = cv2.imread(str(image_path))

# 2. Load nodes and edges data
# edges
edges_path = Path('data/0_refined_edges_dict.pkl')
edges_dict = load_pickle(edges_path)

# nodes
nodes_path = Path('data/0_refined_nodes_dict.pkl')
nodes_dict = load_pickle(nodes_path)

######################
## Create Neo4j graph
######################
from neo4j import GraphDatabase
# Step-1: make connection to database
# database credentials

uri = st.secrets["neo4j_uri"]
user = st.secrets["neo4j_user"]
password = st.secrets["neo4j_password"]
data_base_connection = GraphDatabase.driver(uri = uri, auth = (user, password)) 
pidKG = data_base_connection.session() 

# # Step-2: create nodes
# nodes_to_add = []
# for edge, node_pair in edges_dict.items():
#     for node in node_pair:
#         if node not in nodes_to_add:
#             if node.startswith('J'):
#                 node_type = 'Junction'
#             else:
#                 node_type = 'Symbol'
#             center_x, center_y = node_center(node, nodes_dict)
#             _, class_name, tag = nodes_dict[node]
#             pidKG.run(
#                 f"CREATE (n:{node_type} {{class: {class_name}, tag: '{tag}', center_x: {center_x}, center_y: {center_y}, alias: '{node}'}})"
#             )
#             nodes_to_add.append(node)
            
# # Step-3: create edges
# # Note: this step could be combined with the Step-2. But there can be chances that some nodes are not created and
# # we are trying to create edges between them. So, it is better to create nodes first and then create edges.

# for edge, node_pair in edges_dict.items():
#     node1, node2 = node_pair
#     pidKG.run(
#         "MATCH (n1), (n2) WHERE n1.alias = $n1_alias AND n2.alias = $n2_alias CREATE (n1)-[:CONNECTED_TO]->(n2)",
#         n1_alias=node1, n2_alias=node2
#     )

# Note: directions above are arbitrary because arrows are not shown on the given P&ID. 
# However, Neo4j requires a direction for each edge so we have chosen an arbitrary direction.
# In later stage, when querying into the Graph, we can ignore the direction of the edge.

######################
## Develop QA system
######################
from langchain_community.graphs import Neo4jGraph #-> Old but works # New: from langchain_neo4j import Neo4jGraph (I found new to be troublesome for me)
from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import OpenAIEmbeddings
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

system_prompt_for_generating_cypher = f'''You are a Neo4j expert. Given an input question, create a syntactically correct Cypher query to run. 
Here is the schema information for the underlying graph database: {pidKG_schema}.
Don't add any preambles, just return the correct cypher query with no further commentary.
Output the final Cypher query only.'''

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples, # examples to select from
    OpenAIEmbeddings(), # embedding class to produce embeddings to measure semantic similarity.
    Chroma, # VectorStore class that is used to store the embeddings
    k=2, # number of examples to produce.

)

for q in questions:
    selected_fewshot_examples = example_selector.select_examples({"question": q})
    
    messages = [SystemMessage(f"{system_prompt_for_generating_cypher}"),
                SystemMessage(f"Here is few examples of questions and their corresponding Cypher queries: {selected_fewshot_examples}."),
                HumanMessage(f"{q}")]
    cypher_generated = cypher_generating_model(messages).content #.strip()
    print(cypher_generated)
    st.write(cypher_generated)
    
    