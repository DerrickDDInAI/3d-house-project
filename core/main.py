"""
Main script that executes the program.
"""
# =====================================================================
# Import
# =====================================================================

## Import internal modules
# import os.path
import json
from matplotlib.pyplot import title
import requests
from typing import List, Set, Dict, TypedDict, Tuple, Optional

## Import 3rd party modules
import numpy as np

# import geopandas as gpd

import rasterio
import rasterio.mask
from rasterio.plot import show
from rasterio.plot import show_hist
from shapely.geometry.polygon import Polygon

import earthpy.plot as ep

import plotly.graph_objects as go
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

    example_yes_no: bool = input("\nWould you like to see an example? (yes/no): ").lower()
    if example_yes_no in ("yes", "y"): 
        address: Tuple[str, int, str, int, str] = ("Bolivarplaats", 20, None, 2000, "Antwerpen")
    else:
        print("\nPlease enter the address of a building and I will plot it in 3D.")
        street_name = input("street name: ")
        # if not isinstance(street_name, str):
        house_number = int(input("house number: "))
        box_number = input("box number (just press enter if no box): ")
        postal_code = int(input("postal code: "))
        town = input("town: ")

        address: Tuple[str, int, str, int, str] = (street_name, house_number, box_number, postal_code, town)
    
    return address

def read_clipped_tiff(filepath: str, geometry: Polygon) -> np.ndarray:
    """
    Function to read the GeoTiff file 
    and clip it with the house geometric shape.

    Return: raster data (= image) of the building
    """
    # We open the GeoTiff within a context manager 
    # so as to close it after reading the info and save memory.
    with rasterio.open(filepath) as tiff_file:
        # Read the data into a numpy array:
        tiff_image, tiff_transform = rasterio.mask.mask(tiff_file, [geometry], crop=True)
        #tiff_image_bounds = rasterio.plot.plotting_extent(tiff_file)
        #tiff_image_bounds_meta = tiff_file.meta

    return tiff_image

def main() -> None:
    # Welcoming message
    print("""Hello!
    Welcome to the 3D House Project!
    I can plot a building in 3D provided it is in my database.
    Currently, any building in Flanders (Belgium).
    """)

    # Get the address from the user
    street_name, house_number, box_number, postal_code, town = get_user_input()

    # Create House instance
    requested_house = House(street_name, house_number, postal_code, town, box_number=box_number)

    requested_house.get_address_info_from_api()
    requested_house.get_lambert72_coordinates()
    requested_house.get_house_geometry()
    requested_house.get_tiffs_path()
    print("Please wait, I'm getting the necessary information to plot the building.")
    print("Address : ", requested_house)
    print("Geometric shape bounds: ", requested_house.geometry.bounds)
    print("DSM filepath: ", requested_house.dsm_filepath)
    print("DTM filepath: ", requested_house.dtm_filepath)

    # Get the Digital Surface Model (DSM) and Digital Terrain Model (DTM) images of the building
    dsm_image = read_clipped_tiff(requested_house.dsm_filepath, requested_house.geometry)
    dtm_image = read_clipped_tiff(requested_house.dtm_filepath, requested_house.geometry)

    # Compute the Canopy Height Model (CHM) image of the building
    chm_image = dsm_image - dtm_image

    # Plot the building CHM in 2D
    # ep.plot_bands(chm_image,
    #           cmap='terrain',
    #           title="Building CHM")
    # plt.show()

    # Plot the building in 3D
    fig = go.Figure(data=[go.Surface(z=chm_image[0])])
    fig.update_layout(title="3D Building")
    fig.show()


# ============================================================
# Run
# ============================================================

## Executes the main() function if this file is directly run
if __name__ == "__main__":
    main()