import random
from modules.crop.schemas import SensorData


def get_simulated_sensor_data(latitude: float, longitude: float) -> SensorData:
    """
    Simulates fetching comprehensive sensor data for a given location.
    In a real-world scenario, this would involve fetching data from a database or an IoT platform.
    """
    # Simple simulation based on location, for demonstration purposes
    # The values are intentionally varied slightly
    moisture = 50.0 + (latitude % 10) * 0.5
    temperature = 30.0 + (longitude % 10) * 0.3
    ec = 2.5 + (latitude % 5) * 0.1
    ph = 7.0 + (longitude % 3) * 0.1
    humidity = 60.0 + (latitude % 10) * 0.4
    solar = 300.0 + (longitude % 10) * 20.0
    nitrate = 20.0 + (latitude % 10) * 1.5  # Simulate a value for nitrate

    return SensorData(
        soil_moisture=round(moisture, 2),
        soil_temperature=round(temperature, 2),
        electrical_conductivity=round(ec, 2),
        soil_ph=round(ph, 2),
        relative_humidity=round(humidity, 2),
        solar_radiation=round(solar, 2),
        nitrate_ppm=round(nitrate, 2),
        latitude=latitude,
        longitude=longitude
    )


# The nitrate-specific function should now just call the main one
def get_simulated_nitrate_data(latitude: float, longitude: float) -> SensorData:
    """
    Returns a comprehensive SensorData object, which includes nitrate levels.
    """
    return get_simulated_sensor_data(latitude, longitude)