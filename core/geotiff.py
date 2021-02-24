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


# ============================================================
# Main functions
# ============================================================

def get_tiffs(folder: str) -> pd.DataFrame:
    """
    Function to get all GeoTiff files within the DSM or DTM folder.
    Param: `folder` is either "DSM" or "DTM" folder    
    Return: a DataFrame with the GeoTiff filenames, paths
    and their corresponding BoundingBox's as columns    
    """
    # Create empty lists
    geotiff_id_list: List = [] # will contain the rectangle number of each GeoTiff
    geotiff_list: List = []  # will contain all GeoTiff filenames
    geotiff_path_list: List = [] # will contain the GeoTiff's filepaths
    boundingbox_list: List = [] # will contain the BoundingBox of each GeoTiff

    # Get the relative path of the directory that contains all the GeoTiff files
    folder_path = os.path.join("assets", folder)

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
                # We open within a context manager 
                # so as to close the file after reading the info and save memory
                with rio.open(geotiff_path) as tiff_file:
                    boundingbox = tiff_file.bounds
                    boundingbox_list.append(boundingbox)

    # Create a DataFrame from the lists
    return pd.DataFrame(list(zip(geotiff_id_list, geotiff_list, geotiff_path_list, boundingbox_list)), columns=["GeoTiff_ID", f"{folder}_GeoTiff", f"{folder}_Filepath", f"{folder}_BoundingBox"])


def get_dsm_dtm_tiffs() -> pd.DataFrame:
    """
    Function to get all DSM and DTM GeoTiff files.
  
    Return: a DataFrame with the GeoTiff filenames, paths
    and their corresponding BoundingBox's as columns    
    """

    # Get DSM and DTM GeoTiff files
    dsm_tiffs_df: pd.DataFrame = get_tiffs("DSM")
    dtm_tiffs_df: pd.DataFrame = get_tiffs("DTM")

    # Join both DataFrames on their "GeoTiff_ID" as index
    return dsm_tiffs_df.set_index("GeoTiff_ID").join(dtm_tiffs_df.set_index("GeoTiff_ID"))

# ============================================================
# Run
# ============================================================

## Executes the get_dsm_dtm_tiffs() function if this file is directly run
if __name__ == "__main__":
    dsm_dtm_tiffs_df: pd.DataFrame = get_dsm_dtm_tiffs()
    print(dsm_dtm_tiffs_df)

    # Test if DSM and DTM GeoTiff files have the same BoundingBox
    print(all(dsm_dtm_tiffs_df.DSM_BoundingBox == dsm_dtm_tiffs_df.DTM_BoundingBox))
