import numpy as np
import pickle

def load_pickle(file_path: str) -> dict:
    with open(file_path, 'rb') as f:
        return pickle.load(f)
    
def node_center(node_name: str, nodes_dict: dict) -> list:
    return nodes_dict[node_name][0]