"""
Local module that gets the **BoundingBox** (= geographic boundaries) of the 43 grid rectangles in the Flanders topographic map *NGI 1/1*.
In "assets/DSM" or "assets/DTM" directory, we have 43 GeoTiff files. Each GeoTiff file contains the raster data (= image) of each rectangle,
with its BoundingBox info.

About the NGI 1/1 map:
The Belgian National Geographic Institute (NGI) divided the Flanders topographic map in a grid of 43 rectangles.
Each rectangle covers an area of 640 km² (32 km in X direction, 20 km in Y direction).
The map uses the Lambert 72 system.
"""
# =====================================================================
# Import
# =====================================================================

## Import internal modules
import os.path
from typing import List, Set, Dict, TypedDict, Tuple, Optional

## Import 3rd party modules
import pandas as pd
import rasterio as rio

## Import local modules


# ============================================================
# Main function
# ============================================================

def get_all_tiff_boundingbox() -> pd.DataFrame:
    """
    Function to get the **BoundingBox** of all the geoTiff files.

    Return: a DataFrame with the GeoTiff filenames
    and their corresponding BoundingBox's as columns
    """
    # Create empty lists:
    geotiff_id_list: List = [] # will contain the rectangle number of each GeoTiff
    geotiff_list: List = []  # will contain all GeoTiff filenames
    geotiff_path_list: List = [] # will contain the GeoTiff's filepaths
    dsm_boundingbox_list: List = [] # will contain the BoundingBox of each GeoTiff

    # Get the relative path of the directory that contains all the GeoTiff files
    folder_path = os.path.join("assets","DSM")

    # Get all the filenames within the directory
    for path, dirs, files in os.walk(folder_path):
        for filename in files:
            # Search only filenames with the extension ".tif"
            if filename.lower().endswith(".tif"):

                # Get the rectangle number of each GeoTiff
                geotiff_id = filename.replace(".tif", "").split("_k")[1]
                geotiff_id_list.append(geotiff_id)

                # Get the filename
                geotiff_list.append(filename)

                # Get the filepath
                geotiff_path = os.path.join(path, filename)
                geotiff_path_list.append(geotiff_path)
                
                # Open the GeoTiff file and get its BoundingBox
                # We open within a context manager so as to close the file after reading the info
                with rio.open(geotiff_path) as tiff_file:
                    boundingbox = tiff_file.bounds
                    dsm_boundingbox_list.append(boundingbox)

    # Create a DataFrame from geotiff_list and dsm_boundingbox_list
    return pd.DataFrame(list(zip(geotiff_id_list, geotiff_list, geotiff_path_list, dsm_boundingbox_list)), columns=["GeoTiff_ID", "GeoTiff", "Filepath", "BoundingBox"])

# ============================================================
# Run
# ============================================================

## Executes the main() function if this file is directly run
if __name__ == "__main__":
    tiff_boundingbox_df: pd.DataFrame = get_all_tiff_boundingbox()
    print(tiff_boundingbox_df)