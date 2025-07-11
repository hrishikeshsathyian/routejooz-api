import googlemaps.client
import numpy as np
import pandas as pd 
from numpy import sin, cos, sqrt, arctan2
import googlemaps
from datetime import datetime
import os 

key = os.environ.get("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=key)

def haversine_matrix(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    # at this point all 4 shapes are (361, )
    # after converting the arrays to 2D, they become (361, 1) and now with subtraction dlat and dlon become (361, 361)
    # the pairwise difference of distances is calculated between each point 
    dlat = lat2[:, None] - lat1[None, :] 
    dlon = lon2[:, None] - lon1[None, :]

    # all the terms here are of shape (361, 361)
    a = sin(dlat / 2.0)**2 + cos(lat2[:, None]) * cos(lat1[None, :]) * sin(dlon / 2.0)**2
    c = 2 * arctan2(sqrt(a), sqrt(1 - a))

    return R * c


# converts a CSV file into pandas dataframe and generates distance matrix using haversine formula
def generate_haversine_distance_matrix(filename: str = "preprocessing/locations_rows.csv") -> tuple[pd.DataFrame, dict, dict]:
    df = pd.read_csv(filename)
    index_to_qrcode = dict(zip(df.index, df['qr_code'].values))
    qrcode_to_index = {v: k for k, v in index_to_qrcode.items()}
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        raise ValueError("CSV file values must contain 'latitude' and 'longitude' columns")
    lat_rad = np.radians(df['latitude'].values)
    lon_rad = np.radians(df['longitude'].values)   
    distance_matrix = haversine_matrix(lat_rad, lon_rad, lat_rad, lon_rad)
    distance_df = pd.DataFrame(distance_matrix, index=df.index, columns=df.index)
    return distance_df, index_to_qrcode, qrcode_to_index

# returns a dictionary of id to the a list of tuples of (neighbor_index, distance)
# 360: [(358, 0.0), (348, 0.0), (177, 0.42029514223399395), (128, 0.4248738719492289), (20, 0.5274286067933707), (86, 0.5274286067933707), (343, 0.5355846232047573), (349, 0.5355846232047573), (174, 0.5430170348560918), (235, 2.2968920826002712), (171, 2.301869839818027)]
def get_k_closest_locations(distance_df: pd.DataFrame, k:int = 10) -> dict: 
    closest = {} 
    for i in distance_df.index: 
        sorted_neighbors = distance_df.loc[i].sort_values()
        nearest = sorted_neighbors[sorted_neighbors.index != i][: k + 1]
        # Store: key = source location index, value = list of (neighbor_index, distance)
        closest[i] = list(nearest.items())
    return closest 


def update_k_closest_locations(distance_df: pd.DataFrame,index_to_qr: dict, k:int = 10, ) -> pd.DataFrame:
    closest = get_k_closest_locations(distance_df, k)
    for k, v in closest.items():
        root_qr = index_to_qr[k]
        neighbours = [index_to_qr[neighbor_index] for neighbor_index, _ in v]
        print(f"Location {root_qr} closest neighbors: {neighbours}")
   
