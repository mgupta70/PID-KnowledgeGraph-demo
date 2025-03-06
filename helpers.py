import numpy as np
import pickle

def load_pickle(file_path: str) -> dict:
    with open(file_path, 'rb') as f:
        return pickle.load(f)
    
def node_center(node_name: str, nodes_dict: dict) -> list:
    return nodes_dict[node_name][0]

def crop_image(image: np.ndarray, x_l, x_r, y_t, y_b) -> np.ndarray:
    return image[y_t:y_b, x_l:x_r]