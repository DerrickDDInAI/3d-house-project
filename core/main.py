"""
Main script that executes the program.
"""
# =====================================================================
# Import
# =====================================================================

# Import internal modules
import re
import sys
from typing import List, Set, Dict, TypedDict, Tuple, Optional

# Import 3rd party modules
import numpy as np
import rasterio
import rasterio.mask
from shapely.geometry.polygon import Polygon

import earthpy.plot as ep

import plotly.graph_objects as go


# Import local modules
from .house import House

# ============================================================
# Main functions
# ============================================================


def get_user_input():
    """
    Function to get the address from the user.

    To Do: make it more robust (maybe use Regex)
    """
    
    ## Loop the input session until the user enters the address in a right format
    while True:
        print("\nPlease enter the address of a building and I will plot it in 3D.")
        address_str: str = input(
        "Enter 'Streetname House_number, postal_code Town': ")
        # address_str: str = input(
        # "Enter 'Streetname House_number, postal_code, Town' | Press ENTER if you'd like to input one element at a time: ")
        # Create regex
        regex_str = re.search("^(?P<street_name>[a-zA-Z-]+)[,] (?P<house_number>[0-9]+), (?P<postal_code>[0-9]{4})[,] (?P<town>[a-zA-Z-]+$)", address_str)
        
        # if regex expression matches, get the address and break the loop
        # if re.match("^[a-zA-Z-]+ [0-9]+, [0-9]{4} [a-zA-Z-]+$", address_str):
        if regex_str:
            street_name: str = regex_str.group("street_name")
            house_number: int = regex_str.group("house_number")
            postal_code: int = regex_str.group("postal_code")
            town: str = regex_str.group("town")
            break

        # Exit the program if user enters "exit"
        elif address_str == "exit":
            print("Thank you for your visit!")
            sys.exit()

        else:
            print('Please retry or enter "exit" to quit the program')

    # else:
    #     street_name: str = input("street name: ")
    #     house_number: int = int(input("house number: "))
    #     postal_code: int = int(input("postal code: "))
    #     town: str = input("town: ")

    #     address: Tuple[str, int, str, int, str] = (
    #         street_name, house_number, postal_code, town)

    return street_name, house_number, postal_code, town


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
        tiff_image, tiff_transform = rasterio.mask.mask(
            tiff_file, [geometry], crop=True)
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
    
    # If the user wants, the program enters an address example
    show_example: bool = input(
    "\nWould you like to see an example? (yes/no): ").lower()
    if show_example in ("yes", "y"):
        street_name, house_number, postal_code, town = ("Bolivarplaats", 20, 2000, "Antwerpen")
    
    # Get the address from the user
    else:
        street_name, house_number, postal_code, town = get_user_input()

    # Create House instance
    requested_house = House(street_name, house_number, postal_code, town)

    # Get House info
    requested_house.get_address_info_from_api()
    requested_house.get_lambert72_coordinates()
    requested_house.get_house_geometry()
    requested_house.get_tiffs_path()

    # Print House info
    print("Please wait, I'm getting the necessary information to plot the building.")
    print("Address : ", requested_house)
    print("Geometric shape bounds (min_X, min_Y, max_X, max_Y): ",
          requested_house.geometry.bounds)
    print("DSM filepath: ", requested_house.dsm_filepath)
    print("DTM filepath: ", requested_house.dtm_filepath)

    # Get the Digital Surface Model (DSM) and Digital Terrain Model (DTM) images of the building
    dsm_image = read_clipped_tiff(
        requested_house.dsm_filepath, requested_house.geometry)
    dtm_image = read_clipped_tiff(
        requested_house.dtm_filepath, requested_house.geometry)

    # Compute the Canopy Height Model (CHM) image of the building
    chm_image = dsm_image - dtm_image

    # Plot the building in 3D
    fig = go.Figure(data=[go.Surface(z=chm_image[0])])
    fig.update_layout(title="3D Building")
    fig.show()


# ============================================================
# Run
# ============================================================

# Executes the main() function if this file is directly run
if __name__ == "__main__":
    main()
