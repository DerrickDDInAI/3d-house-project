# =====================================================================
# Import
# =====================================================================

## Import internal modules
import os
import json
import requests
from typing import List, Set, Dict, TypedDict, Tuple, Optional

## Import 3rd party modules
import pandas as pd
from shapely.geometry import Polygon

from tiff_boundingbox import get_all_tiff_boundingbox


# ============================================================
# Classes Definition
# ============================================================

class House:
    """
    Address has 3 attributes: street_name, house_number, box_number, postal_code, town, X_Lambert72, Y_Lambert72
    * street_name: string = the street name
    * house_number: int = the house number
    * box_number: int = the box number
    * postal_code: int = the postal code
    * town: string = the town
    * X_Lambert72: float = X coordinate in the *Belgian Lambert 72* system (EPSG:31370)
    * Y_Lambert72: float = Y coordinate in the *Belgian Lambert 72* system (EPSG:31370)
    * geometry: geometric shape of the house
    """
    def __init__(self, street_name, house_number, postal_code, town, box_number=None, XY_Lambert72=None) -> None: 
        """
        Function to create an instance of Address class
        By default:
        * caption is "game" if no caption is provided
        """
        self.street_name: str = street_name
        self.house_number: int = house_number
        self.box_number: str =  box_number
        self.postal_code: int = postal_code
        self.town: str = town

        # Unpack the x and y coordinates tuple
        self.X_Lambert72: float
        self.Y_Lambert72: float
        if XY_Lambert72 is not None:
            self.X_Lambert72, self.Y_Lambert72 = XY_Lambert72
        else:
            self.X_Lambert72 = None
            self.Y_Lambert72 = None

        self.geometry = None

    def __str__(self) -> str:
        """
        Function to print the address of the house and its X and Y coordinates in the *Belgian Lambert 72* system
        """
        return f"{self.street_name} {self.house_number}, {self.postal_code} {self.town}\nX and Y coordinates (Lambert 72 system): [{self.X_Lambert72}, {self.Y_Lambert72}]"
    
    def get_address_info_from_api(self) -> None:
        """
        Function to get the info of an address in json syntax
        from the Basisregisters Vlaanderen API: https://docs.basisregisters.vlaanderen.be/docs/api-documentation.html#tag/api-documentation.html
        """
        address_url: str = "https://api.basisregisters.vlaanderen.be/v1/adresmatch"
        address_request = requests.get(address_url, params={"straatnaam":self.street_name, "huisnummer":self.house_number, "postcode":self.postal_code, "gemeentenaam":self.town})
        self.address_info_json: Dict[str, List[TypedDict]] = json.loads(address_request.content)

    def get_lambert72_coordinates(self):
        """
        Function to get the house X and Y coordinates in the *Belgian Lambert 72* system
        """
        self.X_Lambert72, self.Y_Lambert72 = self.address_info_json["adresMatches"][0]["adresPositie"]["point"]["coordinates"]
    
    def get_house_geometry(self):
        """
        Function to get the geometry of the house.
        Process: 
        Each house has a building unit ID and each building unit ID has a building ID.
        In the API, we can get the geometry from the building ID.
        """
        # 1. Get the url of the building unit ID
        building_unit_id_url: str = self.address_info_json["adresMatches"][0]["adresseerbareObjecten"][0]["detail"]

        # 2. Request the info for this building unit ID
        building_unit_id_request: requests.models.Response = requests.get(building_unit_id_url)
        building_unit_id_json: dict = json.loads(building_unit_id_request.content)

        # 3. Get the url of the building ID
        building_id_url: str = building_unit_id_json["gebouw"]["detail"]

        # 4. Request the info for this building unit ID
        building_id_request: requests.models.Response = requests.get(building_id_url)
        building_id_json: dict = json.loads(building_id_request.content)

        # 5. Get the geometry of the house as a Polygon object
        self.geometry: Polygon = Polygon(building_id_json["geometriePolygoon"]["polygon"]["coordinates"][0])


    def get_map_rectangle_id(self):
        """
        Function to check in which grid rectangle the house is located on the Flanders topographic map *NGI 1/1*.
        Process:
        As the coordinates of both the house and the map uses the Lambert 72 system, 
        we can directly compute if the house is in the **BoundingBox** (= geographic boundaries) of a rectangle.

        About the NGI 1/1 map:
        The Belgian National Geographic Institute (NGI) divided the Flanders topographic map in a grid of 43 rectangles.
        Each rectangle covers an area of 640 km² (32 km in X direction, 20 km in Y direction).
        """
        # Get the DataFrame containing the **BoundingBox** of a each rectangle
        tiff_boundingbox_df: pd.DataFrame = get_all_tiff_boundingbox()

        # Find in which rectangle **BoundingBox** the house is located
        map_rectangle_id_np: pd.core.series.Series = tiff_boundingbox_df.GeoTiff_ID[tiff_boundingbox_df.BoundingBox.apply(lambda bb_tuple: (bb_tuple[0] <= self.X_Lambert72 <= bb_tuple[2]) and (bb_tuple[1] <= self.Y_Lambert72 <= bb_tuple[3]))]

        # Get the id from the map_rectangle_id_np (which is a numpy representation)
        self.map_rectangle_id: str = map_rectangle_id_np.values[0]