from unittest.mock import patch
from langchain_community.agent_toolkits.amadeus.toolkit import AmadeusToolkit

@patch("langchain_community.agent_toolkits.amadeus.toolkit.AmadeusClosestAirport")
@patch("langchain_community.agent_toolkits.amadeus.toolkit.AmadeusFlightSearch")


def test_amadeus_toolkit_init(mock_flight_search, mock_closest_airport):
    """Test that AmadeusToolkit initializes correctly and returns expected tools.
    
    Args:
        mock_flight_search: Mock for the flight search functionality.
        mock_closest_airport: Mock for the closest airport functionality.
    """
    toolkit = AmadeusToolkit()
    tools = toolkit.get_tools()

    assert mock_flight_search.called
    assert mock_closest_airport.called
    assert len(tools) == 2


