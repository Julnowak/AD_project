import socket
import threading            

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.sql import text
import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
import datetime



Base = declarative_base()

class Sensor(Base):
    __tablename__ = 'sensors'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    location = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    measurements = relationship("Measurement", back_populates="sensor")

# Define the Measurement class
class Measurement(Base):
    __tablename__ = 'measurements'
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensors.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    sensor = relationship("Sensor", back_populates="measurements")
    temperature_measurements = relationship("TemperatureMeasurement", back_populates="measurement")
    precipitation_measurements = relationship("PrecipitationMeasurement", back_populates="measurement")
    pressure_measurements = relationship("PressureMeasurement", back_populates="measurement")
    cloud_measurements = relationship("CloudMeasurement", back_populates="measurement")
    weather_code_measurements = relationship("WeatherCodeMeasurement", back_populates="measurement")
    wind_measurements = relationship("WindMeasurement", back_populates="measurement")

# Define the TemperatureMeasurement class
class TemperatureMeasurement(Base):
    __tablename__ = 'temperature_measurements'
    id = Column(Integer, primary_key=True)
    measurement_id = Column(Integer, ForeignKey('measurements.id'), nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    apparent_temperature = Column(Float)
    is_day = Column(Boolean)
    measurement = relationship("Measurement", back_populates="temperature_measurements")

# Define the PrecipitationMeasurement class
class PrecipitationMeasurement(Base):
    __tablename__ = 'precipitation_measurements'
    id = Column(Integer, primary_key=True)
    measurement_id = Column(Integer, ForeignKey('measurements.id'), nullable=False)
    precipitation = Column(Float)
    rain = Column(Float)
    showers = Column(Float)
    snowfall = Column(Float)
    measurement = relationship("Measurement", back_populates="precipitation_measurements")

# Define the PressureMeasurement class
class PressureMeasurement(Base):
    __tablename__ = 'pressure_measurements'
    id = Column(Integer, primary_key=True)
    measurement_id = Column(Integer, ForeignKey('measurements.id'), nullable=False)
    sealevel_pressure = Column(Float)
    surface_pressure = Column(Float)
    measurement = relationship("Measurement", back_populates="pressure_measurements")

# Define the CloudMeasurement class
class CloudMeasurement(Base):
    __tablename__ = 'cloud_measurements'
    id = Column(Integer, primary_key=True)
    measurement_id = Column(Integer, ForeignKey('measurements.id'), nullable=False)
    cloud_cover_total = Column(Float)
    measurement = relationship("Measurement", back_populates="cloud_measurements")

# Define the WeatherCodeMeasurement class
class WeatherCodeMeasurement(Base):
    __tablename__ = 'weather_code_measurements'
    id = Column(Integer, primary_key=True)
    measurement_id = Column(Integer, ForeignKey('measurements.id'), nullable=False)
    weather_code = Column(Integer)
    measurement = relationship("Measurement", back_populates="weather_code_measurements")

# Define the WindMeasurement class
class WindMeasurement(Base):
    __tablename__ = 'wind_measurements'
    id = Column(Integer, primary_key=True)
    measurement_id = Column(Integer, ForeignKey('measurements.id'), nullable=False)
    wind_speed_10m = Column(Float)
    wind_direction_10m = Column(Float)
    wind_gusts_10m = Column(Float)
    measurement = relationship("Measurement", back_populates="wind_measurements")

class SensorConnection(threading.Thread):
    def __init__(self, port, ip_address='localhost') -> None:
        threading.Thread.__init__(self)
        self.port = port
        self.ip_address = ip_address
        self.sensor_socket = socket.socket()
        self.buffer = []
    
    def run(self):
        try:
            self.sensor_socket.connect((self.ip_address, self.port))
            while True:
                self.buffer.append(self.sensor_socket.recv(1024).decode())
        except:
            self.sensor_socket.close()


def add_sensor(name, loc, lat, long):
    from sqlalchemy.sql import text
    stmt = text('select * from sensors')

    results = session.execute(stmt).fetchall()

    print(results)
    sensor = Sensor(name=name, location=loc, latitude=lat, longitude=long)
    return sensor


def add_combined_measurement(sensor_name, act_time, temperature, humidity, apparent_temperature, is_day,
                             precipitation, rain, showers, snowfall, sealevel_pressure, surface_pressure,
                             cloud_cover_total, weather_code, wind_speed_10m, wind_direction_10m, wind_gusts_10m):
    sensor = session.query(Sensor).filter_by(name=sensor_name).first()
    if not sensor:
        # Handle the case where the sensor is not found
        return
    
    # Create a new measurement entry
    new_measurement = Measurement(sensor_id=sensor.id, timestamp=act_time)
    
    # Add temperature and humidity measurements
    temperature_measurement = TemperatureMeasurement(
        measurement=new_measurement,
        temperature=temperature,
        humidity=humidity,
        apparent_temperature=apparent_temperature,
        is_day=is_day
    )
    
    # Add precipitation measurements
    precipitation_measurement = PrecipitationMeasurement(
        measurement=new_measurement,
        precipitation=precipitation,
        rain=rain,
        showers=showers,
        snowfall=snowfall
    )
    
    # Add pressure measurements
    pressure_measurement = PressureMeasurement(
        measurement=new_measurement,
        sealevel_pressure=sealevel_pressure,
        surface_pressure=surface_pressure
    )
    
    # Add cloud measurements
    cloud_measurement = CloudMeasurement(
        measurement=new_measurement,
        cloud_cover_total=cloud_cover_total
    )
    
    # Add weather code measurements
    weather_code_measurement = WeatherCodeMeasurement(
        measurement=new_measurement,
        weather_code=weather_code
    )
    
    # Add wind measurements
    wind_measurement = WindMeasurement(
        measurement=new_measurement,
        wind_speed_10m=wind_speed_10m,
        wind_direction_10m=wind_direction_10m,
        wind_gusts_10m=wind_gusts_10m
    )
    
    # Add and commit the new measurement and its related measurements to the session
    session.add(new_measurement)
    session.add(temperature_measurement)
    session.add(precipitation_measurement)
    session.add(pressure_measurement)
    session.add(cloud_measurement)
    session.add(weather_code_measurement)
    session.add(wind_measurement)
    session.commit()

db_string = "mysql+pymysql://szyszka1:reiUvwMb9qAjpyiN@mysql.agh.edu.pl/szyszka1"

engine = create_engine(db_string)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

if __name__ == '__main__':
    counter = 10000000 # Czas
    c = 0
    while True:
        list_of_values = []
        while c <= counter:
            # print(c)
            if c < counter:
                pass
            else:
                ##### WAŻNE #####
                Session = sessionmaker(bind=engine)
                session = Session()
                stmt = text('select * from sensors')
                results = session.execute(stmt).fetchall()
                print(results)


                #######################
                # Setup the Open-Meteo API client with cache and retry on error
                cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
                retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
                openmeteo = openmeteo_requests.Client(session = retry_session)

                # Make sure all required weather variables are listed here
                # The order of variables in current or daily is important to assign them correctly below
                url = "https://api.open-meteo.com/v1/gfs"
                params = {
                    "latitude": 40.730610,
                    "longitude": -73.935242,
                    "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "is_day", "precipitation", \
                                "rain", "showers", "snowfall", "weather_code", "cloud_cover", "pressure_msl", "surface_pressure", \
                                "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
                    "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "is_day", "precipitation", \
                                "rain", "showers", "snowfall", "weather_code", "cloud_cover", "pressure_msl", "surface_pressure", \
                                "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
                    "past_days": 7,
                    "forecast_days": 0,
                }
                responses = openmeteo.weather_api(url, params=params)

                # Process first location. Add a for-loop for multiple locations or weather models
                response = responses[0]
                print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
                print(f"Elevation {response.Elevation()} m asl")
                print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
                print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

                # Current values. The order of variables needs to be the same as requested.
                current = response.Current()
                current_temperature_2m = current.Variables(0).Value()
                current_relative_humidity_2m = current.Variables(1).Value()
                current_apparent_temperature = current.Variables(2).Value()
                current_is_day = current.Variables(3).Value()
                current_precipitation = current.Variables(4).Value()
                current_rain = current.Variables(5).Value()
                current_showers = current.Variables(6).Value()
                current_snowfall = current.Variables(7).Value()
                current_weather_code = current.Variables(8).Value()
                current_cloud_cover = current.Variables(9).Value()
                current_pressure_msl = current.Variables(10).Value()
                current_surface_pressure = current.Variables(11).Value()
                current_wind_speed_10m = current.Variables(12).Value()
                current_wind_direction_10m = current.Variables(13).Value()
                current_wind_gusts_10m = current.Variables(14).Value()


                date_range_with_tz = pd.date_range(
                    start=pd.to_datetime(current.Time(), unit="s", utc=True),
                    end=pd.to_datetime(current.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=current.Interval()),
                    inclusive="left"
                )

                date_range_naive = date_range_with_tz.tz_convert(None)

                current_data = {
                    "date": date_range_naive,
                    "temperature_2m": current_temperature_2m,
                    "relative_humidity_2m": current_relative_humidity_2m,
                    "apparent_temperature": current_apparent_temperature,
                    "precipitation": current_precipitation,
                    "rain": current_rain,
                    "is_day": current_rain,
                    "showers": current_showers,
                    "snowfall": current_snowfall,
                    "weather_code": current_weather_code,
                    "pressure_msl": current_pressure_msl,
                    "surface_pressure": current_surface_pressure,
                    "cloud_cover": current_cloud_cover,
                    "wind_speed_10m": current_wind_speed_10m,
                    "wind_direction_10m": current_wind_direction_10m,
                    "wind_gusts_10m": current_wind_gusts_10m,
                }

                current_dataframe = pd.DataFrame(data=current_data)
                sensor_1 = add_sensor("Sensor", "New York", response.Latitude(), response.Longitude())
                stmt = text(f'select * from sensors where latitude = {response.Latitude()} && longitude = {response.Longitude()} ')
                results = session.execute(stmt).fetchall()

                if results[0][3] == round(response.Latitude(), 4) and results[0][4] == round(response.Longitude(), 4):
                    pass
                else:
                    session.add(sensor_1)

                for index, row in current_dataframe.iterrows():
                    act_time = row['date']
                    add_combined_measurement(
                    sensor_1.name,
                    act_time,
                    row['temperature_2m'],
                    row['relative_humidity_2m'],
                    row['apparent_temperature'],
                    row['is_day'],
                    row['precipitation'],
                    row['rain'],
                    row['showers'],
                    row['snowfall'],
                    row['pressure_msl'],
                    row['surface_pressure'],
                    row['cloud_cover'],
                    row['weather_code'],
                    row['wind_speed_10m'],
                    row['wind_direction_10m'],
                    row['wind_gusts_10m']
                )
                stmt = text(f'select count(*) from measurements')
                results = session.execute(stmt).fetchall()
                print(results)
            c += 1
            

        # Insert do bazy wszystkich z list_of_values
        c = 0

    