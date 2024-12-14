"""
This module will contain the required endpoints.
Note that if the project was bigger, we would be using a router, and dispatching the routes in different files.
"""
import fastapi
import http
from typing import *
import pydantic
import sqlalchemy
import os
import datetime
app = fastapi.FastAPI()

# region: Types
SensorTypeId = int
RoomId = int
BuildingId = int
Temperature = float
# endregion: Types


def setup_database() -> None:
    """
    This will build the tables required for this project.
    We do not put it in a .sh or another script for simplicity.
    """
    if "DB_STRING" not in os.environ:
        raise RuntimeError(
            "Please provide a DB_STRING env var before trying to setup the database.")
    engine = sqlalchemy.create_engine(os.environ["DB_STRING"])
    with engine.begin() as connection:
        # Only putting the tables we will use in this example. No additional tests are done here since we already test that in the unit tests.
        connection.execute(
            sqlalchemy.text("""
                          CREATE TABLE IF NOT EXISTS Capture(
                            building_id integer,
                            room_id integer,
                            sensor_type_id integer,
                            value float,
                            ts timestamp
                          );

                          """)
        )
    return


@app.post("/temperature")
def add_temperature(room_id: RoomId, building_id: BuildingId, sensor_type_id: SensorTypeId, value: Temperature, timestamp: datetime.datetime) -> fastapi.Response:
    """Adds a temperature to the database.

    Args:
        room_id (RoomId): room identifier
        building_id (BuildingId): building identifier
        sensor_type_id (SensorTypeId): type of sensor
        value (Temperature): value in kelvin
        timestamp (datetime.datetime): date of capture

    Returns:
        fastapi.Response: Http response.
    """
    # Note: We will ignore timezones.
    # Here is an example of preprocessing of the temperature. Example: if we can break
    # all physical laws and go below (as said in assumptions, we will pretend they are all in kelvin)
    if value < 0:
        return fastapi.Response(
            content="Invalid temperature. Kelvins cannot be negative.",
            status_code=http.HTTPStatus.BAD_REQUEST,
        )

    # TODO: Add here the authorization and authentication.
    # TODO: Aditionally, do some sql sanitization to avoid sql injections.
    # TODO: How do we want to handle upsertions ?
    # Here we have a very basic version of that.
    engine = sqlalchemy.create_engine(os.environ["DB_STRING"])

    with engine.begin() as connection:
        # Only putting the tables we will use in this example. No additional tests are done here since we already test that in the unit tests.
        insert_query = sqlalchemy.text("""
                        INSERT INTO Capture (
                          building_id,
                          room_id,
                          sensor_type_id,
                          value,
                          ts
                        )
                        VALUES(
                          :building_id,
                          :room_id,
                          :sensor_type_id,
                          :value,
                          :ts
                          )
                        """)

        connection.execute(
            insert_query,
            {
                "building_id": building_id,
                "room_id": room_id,
                "sensor_type_id": sensor_type_id,
                "value": value,
                "ts": timestamp,
            }
        )

    return fastapi.Response(
        status_code=http.HTTPStatus.CREATED,
    )


class GetTemperatureResponse(pydantic.BaseModel):
    value: float
    # We might have more data in the future.


@app.get("/temperature")
def get_temperature(room_id: RoomId, building_id: BuildingId, sensor_type_id: SensorTypeId) -> GetTemperatureResponse:
    """Aggregates the temperature on the specified interval for a specific room in a specific building.


    Args:
        room_id (RoomId): Room to compute the average for.
        building_id (BuildingId): Building containing the room.
        sensor_type_id (SensorTypeId): Type of sensor to aggregate on.

    Returns:
        GetTemperatureResponse: Aggregated value over 15min.
    """
    # TODO: Here we should do authorization checks, or add a layer of abstraction for the data fetching.

    # Hard coded interval to match the requirements.

    engine = sqlalchemy.create_engine(os.environ["DB_STRING"])

    with engine.begin() as connection:
        # Only putting the tables we will use in this example. No additional tests are done here since we already test that in the unit tests.
        result = connection.execute(
            sqlalchemy.text("""
                        SELECT AVG(value) as result
                        FROM Capture
                        WHERE ts >= NOW()- INTERVAL '15min'
                          AND room_id=:room_id
                          AND building_id=:building_id
                          AND sensor_type_id=:sensor_type_id
                        """),
            {
                "room_id": room_id,
                "building_id": building_id,
                "sensor_type_id": sensor_type_id,
            }
        )
        avg = result.first()[0]
    return GetTemperatureResponse(
        value=avg,
    )
