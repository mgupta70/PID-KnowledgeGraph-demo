import numpy as np
import pickle
import cv2
import base64
import streamlit as st

def load_pickle(file_path: str) -> dict:
    with open(file_path, 'rb') as f:
        return pickle.load(f)
    
def crop_image(image: np.ndarray, x_l, x_r, y_t, y_b) -> np.ndarray:
    return image[y_t:y_b, x_l:x_r]

def node_center(node_name: str, nodes_dict: dict) -> list:
    return nodes_dict[node_name][0]


def overlay_graph(image, edges_dict, nodes_dict):
    for edge, node_pair in edges_dict.items():
        node_1, node_2 = node_pair
        x1, y1 = node_center(node_1, nodes_dict)
        x2, y2 = node_center(node_2, nodes_dict)
        # draw nodes 
        radius = 25  
        fill_color = (0, 0, 255)
        outline_color = (0, 0, 0) 
        thickness = 5        
        cv2.circle(image, (int(x1), int(y1)), radius, fill_color, -1)
        cv2.circle(image, (int(x1), int(y1)), radius, outline_color, thickness)
        cv2.circle(image, (int(x2), int(y2)), radius, fill_color, -1)
        cv2.circle(image, (int(x2), int(y2)), radius, outline_color, thickness)
        # draw edges 
        cv2.line(image, (int(x1), int(y1)), (int(x2), int(y2)), outline_color, thickness)
    return image

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
    