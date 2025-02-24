import aiohttp

BASE_URL = "https://wttr.in/{city}?format=j1"

async def get_weather_data(city: str) -> dict:
    """
    Fetch weather data for a given city using wttr.in API

    Args:
        city (str): Name of the city to get weather data for

    Returns:
        dict: Weather data for the specified city
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL.format(city=city)) as response:
                if response.status == 200:
                    return await response.json()
                return {'cod': '404', 'message': 'City not found'}
    except Exception as e:
        return {'cod': '500', 'message': f'Error fetching weather data: {str(e)}'}