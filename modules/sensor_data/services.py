from modules.crop.schemas import RecommendationRequest, SensorData
import random

def get_simulated_sensor_data(latitude: float, longitude: float) -> SensorData:
    """
    Simulates real-time sensor data from a specific location (latitude, longitude).
    This function can be replaced with a real data fetching service later.
    """
    # These values are generated to be plausible for an agricultural setting.
    # You can adjust these ranges to better reflect conditions in Zambia.
    soil_moisture = round(random.uniform(20.0, 60.0), 2)
    soil_temperature = round(random.uniform(15.0, 35.0), 2)
    electrical_conductivity = round(random.uniform(0.5, 3.0), 2) # dS/m
    soil_ph = round(random.uniform(5.5, 7.5), 2)
    relative_humidity = round(random.uniform(40.0, 95.0), 2)
    solar_radiation = round(random.uniform(100.0, 1000.0), 2) # W/m^2

    return SensorData(
        latitude=latitude,
        longitude=longitude,
        soil_moisture=soil_moisture,
        soil_temperature=soil_temperature,
        electrical_conductivity=electrical_conductivity,
        soil_ph=soil_ph,
        relative_humidity=relative_humidity,
        solar_radiation=solar_radiation,
    )