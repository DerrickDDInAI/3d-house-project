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
    pass




def main() -> None:
    house_test = House("Smeyerspad", 24, 2910, "Essen")
    house_test.get_address_info_from_api()
    house_test.get_lambert72_coordinates()
    house_test.get_house_geometry()
    print(house_test)

# ============================================================
# Run
# ============================================================

## Executes the main() function if this file is directly run
if __name__ == "__main__":
    main()