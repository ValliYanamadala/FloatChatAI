from datetime import datetime
import math
from typing import Any, Dict, List, Optional, Union

from ai.schemas.contracts import MCPToolName, QueryPlan
from app.schemas.query import QueryRequest, SpatialBoundingBox
from app.schemas.spatial import NearestFloatsRequest
from app.services.ai.deterministic_parser import KNOWN_REGIONS

# Mapping of ai.schemas.OceanParameter enum strings to canonical backend parameters
AI_PARAM_TO_BACKEND = {
    "temperature": "temperature_C",
    "salinity": "salinity",
    "pressure": "pressure_dbar",
    "oxygen": "dissolved_oxygen_umol_kg",
    "chlorophyll": "chlorophyll_mg_m3",
    "nitrate": "nitrate_umol_kg",
    "ph": "pH",
}


class QueryPlanAdapter:
    """
    Adapter layer translating validated AI QueryPlan contracts (ai.schemas.QueryPlan)
    into backend Pydantic request models (app.schemas.QueryRequest, NearestFloatsRequest).
    """

    @classmethod
    def to_query_request(cls, plan: QueryPlan) -> QueryRequest:
        """
        Convert a QueryPlan with tool QUERY_MEASUREMENTS or SEARCH_FLOATS into a QueryRequest.
        """
        args = plan.arguments or {}

        # 1. Float ID(s)
        float_ids: Optional[List[str]] = None
        if "float_ids" in args and isinstance(args["float_ids"], list):
            float_ids = [str(fid) for fid in args["float_ids"]]
        elif "float_id" in args and args["float_id"]:
            float_ids = [str(args["float_id"])]
        elif "platform_number" in args and args["platform_number"]:
            float_ids = [str(args["platform_number"])]

        # 2. Parameters
        parameters: Optional[List[str]] = None
        raw_params = args.get("parameters") or args.get("variables") or args.get("parameter")
        if raw_params:
            if isinstance(raw_params, str):
                raw_params = [raw_params]
            parameters = [AI_PARAM_TO_BACKEND.get(p.lower(), p) for p in raw_params]

        # 3. Depth range
        depth_range: Optional[Dict[str, float]] = None
        raw_depth = args.get("depth_range_m") or args.get("depth_range")
        if isinstance(raw_depth, dict):
            min_d = raw_depth.get("min_depth_m", raw_depth.get("min"))
            max_d = raw_depth.get("max_depth_m", raw_depth.get("max"))
            d_dict = {}
            if min_d is not None:
                d_dict["min"] = float(min_d)
            if max_d is not None:
                d_dict["max"] = float(max_d)
            if d_dict:
                depth_range = d_dict
        elif isinstance(raw_depth, (list, tuple)) and len(raw_depth) == 2:
            depth_range = {"min": float(raw_depth[0]), "max": float(raw_depth[1])}

        # 4. Dates
        start_date: Optional[datetime] = None
        end_date: Optional[datetime] = None
        raw_dates = args.get("date_range")
        if isinstance(raw_dates, dict):
            s_raw = raw_dates.get("start_date")
            e_raw = raw_dates.get("end_date")
            if s_raw:
                start_date = datetime.fromisoformat(str(s_raw)) if isinstance(s_raw, str) else s_raw
            if e_raw:
                end_date = datetime.fromisoformat(str(e_raw)) if isinstance(e_raw, str) else e_raw
        if "start_date" in args and args["start_date"]:
            s = args["start_date"]
            start_date = datetime.fromisoformat(str(s)) if isinstance(s, str) else s
        if "end_date" in args and args["end_date"]:
            e = args["end_date"]
            end_date = datetime.fromisoformat(str(e)) if isinstance(e, str) else e

        # 5. Spatial bounding box
        bounding_box: Optional[SpatialBoundingBox] = None
        if "bounding_box" in args and isinstance(args["bounding_box"], dict):
            bbox_dict = args["bounding_box"]
            bounding_box = SpatialBoundingBox(
                min_lat=float(bbox_dict["min_lat"]),
                max_lat=float(bbox_dict["max_lat"]),
                min_lon=float(bbox_dict["min_lon"]),
                max_lon=float(bbox_dict["max_lon"]),
            )
        elif "location" in args and isinstance(args["location"], dict):
            loc = args["location"]
            if "latitude" in loc and "longitude" in loc and loc["latitude"] is not None and loc["longitude"] is not None:
                lat = float(loc["latitude"])
                lon = float(loc["longitude"])
                radius_km = float(loc.get("radius_km") or 500.0)
                delta_lat = radius_km / 111.0
                cos_lat = max(0.1, math.cos(math.radians(lat)))
                delta_lon = radius_km / (111.0 * cos_lat)
                bounding_box = SpatialBoundingBox(
                    min_lat=max(-90.0, round(lat - delta_lat, 4)),
                    max_lat=min(90.0, round(lat + delta_lat, 4)),
                    min_lon=max(-180.0, round(lon - delta_lon, 4)),
                    max_lon=min(180.0, round(lon + delta_lon, 4)),
                )
            elif "name" in loc and loc["name"]:
                region_name = str(loc["name"]).lower()
                bounding_box = KNOWN_REGIONS.get(region_name)
        elif "region" in args and args["region"]:
            region_name = str(args["region"]).lower()
            bounding_box = KNOWN_REGIONS.get(region_name)

        # 6. Pagination
        limit = int(args.get("limit", 50))
        offset = int(args.get("offset", 0))

        return QueryRequest(
            float_ids=float_ids,
            bounding_box=bounding_box,
            start_date=start_date,
            end_date=end_date,
            parameters=parameters,
            depth_range=depth_range,
            limit=limit,
            offset=offset,
        )

    @classmethod
    def to_nearest_floats_request(cls, plan: QueryPlan) -> NearestFloatsRequest:
        """
        Convert a QueryPlan with tool NEAREST_FLOATS into a NearestFloatsRequest.
        """
        args = plan.arguments or {}
        lat = args.get("latitude")
        lon = args.get("longitude")

        # Fallback to location dictionary if nested
        if (lat is None or lon is None) and "location" in args and isinstance(args["location"], dict):
            lat = args["location"].get("latitude")
            lon = args["location"].get("longitude")

        max_dist = args.get("max_distance_km") or (
            args.get("location", {}).get("radius_km") if isinstance(args.get("location"), dict) else None
        ) or 500.0
        limit = int(args.get("limit", 5))

        return NearestFloatsRequest(
            latitude=float(lat),
            longitude=float(lon),
            max_distance_km=float(max_dist),
            limit=limit,
        )
