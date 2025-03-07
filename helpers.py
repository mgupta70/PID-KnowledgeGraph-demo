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
    