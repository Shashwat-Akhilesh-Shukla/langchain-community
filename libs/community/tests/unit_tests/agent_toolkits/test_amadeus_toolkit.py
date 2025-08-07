from unittest.mock import patch
from langchain_community.agent_toolkits.amadeus.toolkit import AmadeusToolkit

@patch("langchain_community.agent_toolkits.amadeus.toolkit.AmadeusClosestAirport")
@patch("langchain_community.agent_toolkits.amadeus.toolkit.AmadeusFlightSearch")
def test_amadeus_toolkit_init(mock_flight_search, mock_closest_airport):
    toolkit = AmadeusToolkit()
    tools = toolkit.get_tools()

    assert mock_flight_search.called
    assert mock_closest_airport.called
    assert len(tools) == 2
