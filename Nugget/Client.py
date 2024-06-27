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
import time
import pytz



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



def add_sensor(name, loc, lat, long):
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

db_string = "mysql+pymysql://szewczyk:hbe2m7tZmX56ectN@mysql.agh.edu.pl/szewczyk"

engine = create_engine(db_string)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

used_sensors = [{'name':"sensor_1", 'location':"New York", 'latitude':40.7296, 'longitude':-73.9497}, 
           {'name':"sensor_2", 'location':"San Francisco", 'latitude':37.7893, 'longitude':-122.422},
           {'name':"sensor_3", 'location':"Phoenix", 'latitude':33.4484, 'longitude':-112.074},
           {'name':"sensor_4", 'location':"Dallas", 'latitude':32.7792, 'longitude':-96.8089},
           {'name':"sensor_5", 'location':"Miami", 'latitude':25.7617, 'longitude':-80.1918}]


if __name__ == '__main__':
    
    # Dodawanie sensorow do bazy danych
    for sen in used_sensors:
        stmt = text(f'select * from sensors')
        results = session.execute(stmt).fetchall()

        if any(el[3] == sen['latitude'] for el in results) and any(el[4] == sen['longitude'] for el in results):
            pass
        else:
            sensor = add_sensor(sen['name'], sen['location'], sen['latitude'], sen['longitude'])
            session.add(sensor)
            session.commit()
            print('aaaa')


    #TODO: przerobić dodawanie danych (co godzinę)
    stmt = text(f'SELECT timestamp FROM measurements ORDER BY timestamp DESC LIMIT 1')
    result = session.execute(stmt).fetchone()

    if result:
        last_appended_time = result[0]
    else:
        temp = datetime.datetime.now(datetime.UTC)
        last_appended_time = temp.replace(tzinfo=None)
    
    while True:

        current_time = datetime.datetime.now(datetime.UTC)
        naive_current_time = current_time.replace(tzinfo=None)
 
        if (naive_current_time - last_appended_time) > datetime.timedelta(hours=1, minutes=16):

            Session = sessionmaker(bind=engine)
            session = Session()
            stmt = text('select * from sensors')
            results = session.execute(stmt).fetchall()
            print(results)

            cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
            retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
            openmeteo = openmeteo_requests.Client(session = retry_session)

            url = "https://api.open-meteo.com/v1/gfs"

            act_time = 0
            for sen in used_sensors:

                params = {
                    "latitude": sen['latitude'],
                    "longitude": sen['longitude'],
                    "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "is_day", "precipitation", \
                                "rain", "showers", "snowfall", "weather_code", "cloud_cover", "pressure_msl", "surface_pressure", \
                                "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
                }

                responses = openmeteo.weather_api(url, params=params)

                response = responses[0]

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

                unix_timestamp = current.Time()
                act_time = datetime.datetime.utcfromtimestamp(unix_timestamp)
                print(act_time)

                add_combined_measurement(
                    sen['name'],
                    act_time,
                    current_temperature_2m,
                    current_relative_humidity_2m,
                    current_apparent_temperature,
                    current_is_day,
                    current_precipitation,
                    current_rain,
                    current_showers,
                    current_snowfall,
                    current_pressure_msl,
                    current_surface_pressure,
                    current_cloud_cover,
                    current_weather_code,
                    current_wind_speed_10m,
                    current_wind_direction_10m,
                    current_wind_gusts_10m,
                )

                stmt = text(f'select count(*) from measurements')
                results = session.execute(stmt).fetchall()
                print(results)

            last_appended_time = act_time
            session.close()

    