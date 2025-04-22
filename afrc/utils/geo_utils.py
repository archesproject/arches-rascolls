import json
import uuid
from django.contrib.gis.geos import (
    GEOSGeometry,
)
from arches.app.models.system_settings import settings
from arches.app.utils.geo_utils import GeoUtils as ArchesGeoUtils


class GeoUtils(ArchesGeoUtils):

    def split_polygon_at_antimeridian(self, geom):
        if geom.dims == 2:
            geom_coords = geom.coords[0]
            max_lon = max(lon for lon, lat in geom_coords)
            min_lon = min(lon for lon, lat in geom_coords)
            east = GEOSGeometry('{"coordinates": [[[180.0, 86.0],[0.0,    86.0],[0.0,    -86.0],[180.0, -86.0],[180.0, 86.0]]],"type": "Polygon"}')
            west = GEOSGeometry('{"coordinates": [[[0.0,   86.0],[-180.0, 86.0],[-180.0, -86.0],[0.0,   -86.0],[0.0, 86.0]]],"type": "Polygon"}')
            new_coords = []

            # geom extends from eastern to western hemisphere
            if max_lon > 180:
                for coords in geom_coords:
                    lon, lat = coords
                    lon = lon - 360 if lon > 180 else -179.99
                    new_coords.append([lon, lat])
                updated_geom = GEOSGeometry(json.dumps({"coordinates": [new_coords,], "type":"Polygon"}))
                return (geom.intersection(east), updated_geom.intersection(west))

            # geom extends from western to eastern hemisphere
            if min_lon < -180:
                for coords in geom_coords:
                    lon, lat = coords
                    lon = lon + 360 if lon < 180 else 179.99
                    new_coords.append([lon, lat])
                updated_geom = GEOSGeometry(json.dumps({"coordinates": [new_coords,], "type":"Polygon"}))
                return (updated_geom.intersection(east), geom.intersection(west))
        
        return [geom]

    def buffer_feature_collection(self, feature_collection):
        """
        Takes a FeatureCollection object and a value for the buffer distance in meters,
        and returns a FeatureCollection of the original features with the buffer distance added.

        """

        unit_factors = {
            "meters": 1,
            "kilometers": 1000,
            "feet": 0.3048,
            "miles": 1609.344,
        }

        buffered_features = []

        for feature in feature_collection["features"]:
            geom = GEOSGeometry(json.dumps(feature["geometry"]))

            distance_meters = feature["properties"]["buffer_distance"] * unit_factors[feature["properties"]["buffer_units"]]

            geom.transform(settings.ANALYSIS_COORDINATE_SYSTEM_SRID)
            buffered_geom = geom.buffer(distance_meters)
            buffered_geom.transform(4326)

            buffered_feature = {
                "type": "Feature",
                "id": str(uuid.uuid4()),
                "properties": feature.get("properties", {}),
                "geometry": json.loads(buffered_geom.geojson),
            }
            buffered_features.append(buffered_feature)

        return {
            "type": "FeatureCollection",
            "features": buffered_features,
        }
