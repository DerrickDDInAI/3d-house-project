"""
Local module that 
1. Gets the **BoundingBox** (= geographic boundaries) of each of the 43 rectangles in the Belgian topographic map *NGI 1/1*.
2. Stores all the bounding boxes in a CSV file

About the NGI 1/1 map:
The Belgian National Geographic Institute (NGI) divided the Belgian topographic map in a grid of 43 rectangles.
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
import rasterio as rio

## Import local modules


# ============================================================
# Main functions
# ============================================================

geotiff_list: List = []
dsm_boundingbox_list: List = []

folder_path = os.path.abspath('assets/DSM')

for path, dirs, files in os.walk(folder_path):
    for filename in files:
        if filename.lower().endswith(".tif"):
            geotiff_list.append(filename)
            geotiff_path = f"{path}\\{filename}".replace("\\","/")
            
            # Open the GeoTiff file and get its BoundingBox
            # We open within a context manager so as to close the file after reading the info
            with rio.open(geotiff_path) as tiff_file:
                boundingbox = tiff_file.bounds
                dsm_boundingbox_list.append(boundingbox)