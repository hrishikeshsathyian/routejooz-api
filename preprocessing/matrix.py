import numpy as np
import pandas as pd 
from numpy import sin, cos, sqrt, arctan2
import googlemaps
from datetime import datetime
import os 
from ortools.constraint_solver import pywrapcp


key = os.environ.get("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=key)

"""
    Generates mappings to use as utils in later functions.
"""
def generate_util_mappings(filename: str = "preprocessing/locations_rows.csv") -> tuple[dict, dict, dict]:
    df = pd.read_csv(filename)
    index_to_postal = dict(zip(df.index, df['postal_code'].values))
    postal_to_index = {v: k for k, v in index_to_postal.items()}
    postal_to_coords = {
        row['postal_code']: (row['latitude'], row['longitude'])
        for _, row in df.iterrows()
    }
    return index_to_postal, postal_to_index, postal_to_coords


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


"""
    Generates N x N distance matrix using the Haversine formula where N is the number of locations
"""
# converts a CSV file into pandas dataframe and generates distance matrix using haversine formula
def generate_haversine_distance_matrix(filename: str = "preprocessing/locations_rows.csv") -> tuple[pd.DataFrame, dict, dict]:
    df = pd.read_csv(filename)
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        raise ValueError("CSV file values must contain 'latitude' and 'longitude' columns")
    lat_rad = np.radians(df['latitude'].values)
    lon_rad = np.radians(df['longitude'].values)   
    distance_matrix = haversine_matrix(lat_rad, lon_rad, lat_rad, lon_rad)
    distance_df = pd.DataFrame(distance_matrix, index=df.index, columns=df.index)
    return distance_df

"""
returns a dictionary of id to the a list of tuples of (neighbor_index, distance)
e.g 0: [(32, 0.19794328712164175), (2, 1.1317483539456736), (61, 1.3865118665248717), (78, 1.4101382433925465), (212, 1.6828427820623364), (171, 1.9375821738299372), (18, 1.9906685558795476), (53, 2.07898249726828), (66, 2.128008342644582), (40, 2.2895403073831537), (170, 2.3130388914913)]
"""
def get_k_closest_locations(distance_df: pd.DataFrame, k:int = 25) -> dict: 
    closest = {} 
    for i in distance_df.index: 
        sorted_neighbors = distance_df.loc[i].sort_values()
        nearest = sorted_neighbors[sorted_neighbors.index != i][: k]
        closest[i] = list(nearest.items())
    return closest, k 


"""
    Takes a estimated Haversine distance matrix and converts it into a time matrix.
    Then updates each node's closest k locations with actual traffic data from Google Maps API.
    Hardcoded to use 25 because it is the maximum API request without batching needed
"""
def update_k_closest_locations(distance_df: pd.DataFrame,index_to_postal: dict, postal_to_coords: dict) -> pd.DataFrame:
    closest, k = get_k_closest_locations(distance_df, k=25)
    
    # convert distance matrix into time matrix
    avg_speed_kmph = 20  # Conservative estimate of average speed of travel 
    for i in distance_df.index:
        for j in distance_df.columns:
            if i != j:
                haversine_km = distance_df.iat[i, j]
                est_time_min = (haversine_km / avg_speed_kmph) * 60
                distance_df.iat[i, j] = est_time_min
            else:
                distance_df.iat[i, j] = 0.0  # defensively ensure diagonal is 0


    for origin_id, neighbours in closest.items(): 
        origin_postal = index_to_postal[origin_id]
        origin_coords = postal_to_coords[origin_postal]

        destination_coords = list(map(lambda x: postal_to_coords[index_to_postal[x[0]]], neighbours))
       
        if len(destination_coords) > k: 
            destination_coords = destination_coords[:k]
        try:
            result = gmaps.distance_matrix(
                origins=[origin_coords],
                destinations=destination_coords,
                mode="driving",
                departure_time="now",
                traffic_model="best_guess",
                units="metric",
                region="SG"
            )
            data = result["rows"][0]["elements"] 
            #uncomment to visualise data returned
            #print(data) 
            if len(data) != len(neighbours):
                print(f"Warning: Mismatch in number of neighbours and data returned for origin {origin_id}. Expected {len(neighbours)}, got {len(data)}")
                continue

            for i in range(len(neighbours)): 
                neighbour_index = neighbours[i][0]
                if data[i]["status"] == "OK":
                    time_taken = data[i]["duration_in_traffic"]["value"]  
                    distance_df.iat[origin_id, neighbour_index] = time_taken / 60.0 
                    distance_df.iat[neighbour_index, origin_id] = time_taken / 60.0  
                else:
                    print(f"Skipping {origin_id} ||| {neighbour_index}, status: {data[i]['status']}")

            
        except googlemaps.exceptions.ApiError as e:
            print(f"Error fetching distance matrix Google Maps API Error: {e}")
            continue

    
    return distance_df 








