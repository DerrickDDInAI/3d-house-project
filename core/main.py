"""
Main script that executes the program.
"""
# =====================================================================
# Import
# =====================================================================

## Import internal modules
# import os.path
import json
import requests

## Import 3rd party modules
# import numpy as np

# import geopandas as gpd

# import rasterio as rio
# import rasterio.mask
# from rasterio.plot import show
# from rasterio.plot import show_hist

# import earthpy as et
# import earthpy.spatial as es
# import earthpy.plot as ep

# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

## Import local modules
from house import House

# ============================================================
# Main functions
# ============================================================

def get_user_input():
    """
    Function to get the address from the user.

    To Do: make it more robust (maybe use Regex)
    """
    # Loop the input session until the user enters the address in a right format
    # waiting_for_user_input = True
    # while waiting_for_user_input:
    print("\nPlease enter the address of a building and I will plot it in 3D.")
    street_name = input("street name: ")
    # if not isinstance(street_name, str):
    house_number = int(input("house number: "))
    box_number = input("box number (just press enter if no box): ")
    postal_code = int(input("postal code: "))
    town = input("town: ")
        
    return (street_name, house_number, box_number, postal_code, town)

def main() -> None:
    # Welcoming message
    print("Hello!")
    print("I'm happy to see you!")
    print("Well, I don't really see you! ;)")
    print('Anyway, welcome to the 3D House Project!')
    print("I can plot a house in 3D providing it is in my database:")
    print("Currently, any house in Flanders (Belgium).")

    # Get the address from the user
    street_name, house_number, box_number, postal_code, town = get_user_input()
    house_test = House(street_name, house_number, postal_code, town, box_number=box_number)
    house_test.get_address_info_from_api()
    house_test.get_lambert72_coordinates()
    house_test.get_house_geometry()
    house_test.get_map_rectangle_id()
    print(house_test)
    print(house_test.map_rectangle_id)

# ============================================================
# Run
# ============================================================

## Executes the main() function if this file is directly run
if __name__ == "__main__":
    main()