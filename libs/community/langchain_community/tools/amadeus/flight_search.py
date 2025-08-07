import logging
from datetime import datetime as dt
from typing import Dict, Optional, Type
from amadeus import Client
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from langchain_community.tools.amadeus.base import AmadeusBaseTool

logger = logging.getLogger(__name__)


class FlightSearchSchema(BaseModel):
    """Schema for the AmadeusFlightSearch tool."""

    originLocationCode: str = Field(
        description="IATA code for the origin airport (e.g. BOM)"
    )
    destinationLocationCode: str = Field(
        description="IATA code for the destination airport (e.g. JFK)"
    )
    departureDateTimeEarliest: str = Field(
        description='Earliest departure in ISO format: "YYYY-MM-DDTHH:MM:SS"'
    )
    departureDateTimeLatest: str = Field(
        description='Latest departure in ISO format: "YYYY-MM-DDTHH:MM:SS"'
    )
    page_number: int = Field(
        default=1,
        description="Page number of results to fetch (pagination)"
    )


class AmadeusFlightSearch(AmadeusBaseTool):
    """Tool to search flights between two airports in a given datetime window."""

    name: str = "single_flight_search"
    description: str = (
        "Search for a flight between two airports between earliest and latest departure times."
    )
    args_schema: Type[FlightSearchSchema] = FlightSearchSchema

    def _run(
        self,
        originLocationCode: str,
        destinationLocationCode: str,
        departureDateTimeEarliest: str,
        departureDateTimeLatest: str,
        page_number: int = 1,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> list:
        try:
            from amadeus import ResponseError
        except ImportError:
            raise ImportError("Install with `pip install amadeus` to use this tool.")

        client = self.client
        RESULTS_PER_PAGE = 10

        earliest = dt.strptime(departureDateTimeEarliest, "%Y-%m-%dT%H:%M:%S")
        latest = dt.strptime(departureDateTimeLatest, "%Y-%m-%dT%H:%M:%S")

        if earliest.date() != latest.date():
            logger.error("Earliest and latest departure must be on the same date.")
            return []

        try:
            response = client.shopping.flight_offers_search.get(
                originLocationCode=originLocationCode,
                destinationLocationCode=destinationLocationCode,
                departureDate=latest.strftime("%Y-%m-%d"),
                adults=1,
            )
        except ResponseError as e:
            logger.error(f"Amadeus API error: {e}")
            return []

        results = []
        if response and hasattr(response, "data"):
            for offer in response.data:
                itinerary = {
                    "price": {
                        "total": offer["price"]["total"],
                        "currency": response.result["dictionaries"]["currencies"].get(
                            offer["price"]["currency"], offer["price"]["currency"]
                        )
                    },
                    "segments": []
                }

                for segment in offer["itineraries"][0]["segments"]:
                    itinerary["segments"].append({
                        "departure": segment["departure"],
                        "arrival": segment["arrival"],
                        "flightNumber": segment["number"],
                        "carrier": response.result["dictionaries"]["carriers"].get(
                            segment["carrierCode"], segment["carrierCode"]
                        )
                    })

                # Filter by latest departure
                segment_departure = dt.strptime(
                    itinerary["segments"][0]["departure"]["at"],
                    "%Y-%m-%dT%H:%M:%S"
                )
                if segment_departure <= latest:
                    results.append(itinerary)

        start_idx = (page_number - 1) * RESULTS_PER_PAGE
        return results[start_idx:start_idx + RESULTS_PER_PAGE]


AmadeusFlightSearch.model_rebuild()
