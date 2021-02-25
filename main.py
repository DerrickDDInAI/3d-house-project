"""
Python program to plot in 3D any house located in Flanders.
See README file for more information.
"""
# =====================================================================
# Import
# =====================================================================

# Import internal modules
import re
import sys
from typing import List, Set, Dict, Tuple

# Import 3rd party modules
import numpy as np
import rasterio
import rasterio.mask
from shapely.geometry.polygon import Polygon
import plotly.graph_objects as go


# Import local modules
from core.house import House

# ============================================================
# Main functions
# ============================================================


def get_user_input() -> House:
    """
    Function to get the address from the user.

    To Do: make it more robust (maybe use Regex)
    """

    print("\nPlease enter the address of a house and I will plot it in 3D.")

    # Loop the input session until the user enters the address in a right format
    while True:
        address_str: str = input(
            "Enter 'Streetname House_number, postal_code Town': ")

        # Create regex
        regex_str = re.search(
            "^(?P<street_name>[a-zA-Z- ]+)[,-]* (?P<house_number>[0-9]+)[,-]* (?P<postal_code>[0-9]{4})[,-]* (?P<town>[a-zA-Z- ]+$)", address_str)

        # if regex expression matches, get the address and break the loop
        if regex_str:
            street_name: str = regex_str.group("street_name")
            house_number: int = regex_str.group("house_number")
            postal_code: int = regex_str.group("postal_code")
            town: str = regex_str.group("town")

            # Create House instance
            requested_house = House(
                street_name, house_number, postal_code, town)

            # Request info from *basisregisters.vlaanderen* API
            requested_house.get_address_info_from_api()

            # If info contains "Onbekende" (= "unknown" in Dutch), continue loop to ask for user input
            if re.search("[Oo]nbekende", str(requested_house.address_info_json)):
                print("""Sorry, I couldn't find the address.
                If this is an address in Flanders, please check for typos.
                """)
                print('Please retry or enter "exit" to quit the program')
                continue

            break

        # Exit the program if user enters "exit"
        elif address_str == "exit":
            print("Thank you for your visit!")
            sys.exit()

        # If the address requested is not in a right format, ask user to retry or quit the program
        else:
            print('Please retry or enter "exit" to quit the program')

    return requested_house


def read_clipped_tiff(filepath: str, geometry: Polygon) -> np.ndarray:
    """
    Function to read the GeoTiff file
    and clip it with the house geometric shape.

    Return: raster data (= image) of the house
    """
    # We open the GeoTiff within a context manager
    # so as to close it after reading the info and save memory.
    with rasterio.open(filepath) as tiff_file:
        # Read the data into a numpy array:
        tiff_image, tiff_transform = rasterio.mask.mask(
            tiff_file, [geometry], crop=True)
        # tiff_image_bounds = rasterio.plot.plotting_extent(tiff_file)
        # tiff_image_bounds_meta = tiff_file.meta

    return tiff_image, tiff_transform


def main() -> None:
    # Welcoming message
    print("""Hello!
    Welcome to the 3D House Project!
    I can plot a house in 3D provided it is in my database.
    Currently, any house in Flanders (Belgium).
    """)

    # If the user wants, the program enters an address example
    show_example: bool = input(
        "\nWould you like to see an example? (yes/no): ").lower()
    if show_example in ("yes", "y"):
        requested_house = House("Bolivarplaats", 20, 2000, "Antwerpen")
        # Request info from API
        requested_house.get_address_info_from_api()

    # Get the address from the user
    else:
        requested_house = get_user_input()

    # Get house info
    requested_house.get_lambert72_coordinates()
    requested_house.get_house_geometry()

    # Get the corresponding GeoTiff files for the house
    requested_house.get_tiffs_path()

    # Print House info
    print("Please wait, I'm getting the necessary information to plot the house.")
    print("Address: ", requested_house)
    print(
        f"X and Y coordinates (Lambert 72 system): [{requested_house.X_Lambert72}, {requested_house.Y_Lambert72}]")
    print("Geometric shape bounds (min_X, min_Y, max_X, max_Y): ",
          requested_house.geometry.bounds)
    print("\nDSM filepath: ", requested_house.dsm_filepath)
    print("DTM filepath: ", requested_house.dtm_filepath)

    # Get the Digital Surface Model (DSM) and Digital Terrain Model (DTM) images of the house
    dsm_image: np.ndarray
    dsm_transform: rasterio.affine.Affine
    dsm_image, dsm_transform = read_clipped_tiff(
        requested_house.dsm_filepath, requested_house.geometry)
    dtm_image, dtm_transform = read_clipped_tiff(
        requested_house.dtm_filepath, requested_house.geometry)

    # Print the affine transformation used in the raster data (= image)
    print("\nDSM affine transformation in X direction: (meter, pixel)")
    print(dsm_transform[:2])
    print("DSM affine transformation in Y direction: (meter, pixel)")
    print(dsm_transform[-2:])

    # Compute the Canopy Height Model (CHM) image of the house
    chm_image = dsm_image - dtm_image

    # Plot the house in 3D
    ## Create 3D plot
    fig = go.Figure(data=[go.Surface(z=chm_image[0])])

    ## Reverse the y-axis
    fig.update_scenes(yaxis_autorange="reversed")

    ## Update title and axis labels
    fig.update_layout(
        title={
            'text': f"""<b>3D House</b><br><b>{requested_house}</b>
            <br>X and Y coordinates (Lambert 72 system):
            <br>[{requested_house.X_Lambert72}, {requested_house.Y_Lambert72}]""",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
            )
    fig.update_layout(
        scene=dict(
            xaxis_title='X: Distance (meter)',
            yaxis_title='Y: Distance (meter)',
            zaxis_title='Z: Height (meter)'
        ),
        legend_title="Height",
        font=dict(
            family="Roboto, monospace",
            size=17,
            color="black"
        )
    )
    fig.show()


# ============================================================
# Run
# ============================================================

# Executes the main() function if this file is directly run
if __name__ == "__main__":
    main()
