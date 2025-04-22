import json
import uuid
from django.contrib.gis.geos import (
    GEOSGeometry,
)
from arches.app.models.system_settings import settings
from arches.app.utils.geo_utils import GeoUtils as ArchesGeoUtils


class GeoUtils(ArchesGeoUtils):

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
