import pytest
from fastapi.testclient import TestClient
import viboo.server
from testcontainers.postgres import PostgresContainer
import os
import http
import datetime
from typing import *


@pytest.fixture
def client() -> TestClient:
    return TestClient(viboo.server.app)


class TemperatureTestCase(TypedDict, total=True):
    room_id: int
    building_id: int
    sensor_type_id: int
    timestamp: datetime.datetime
    value: float


def test_invalid_temperature(client: TestClient) -> None:
    """
    This will test that invalid measures are not accepted.
    """
    with PostgresContainer("postgres:16") as postgres:
        os.environ["DB_STRING"] = postgres.get_connection_url()
        room_id = 1
        sensor_id = 1
        building_id = 1
        res = client.post("/temperature", params=TemperatureTestCase(
            value=-1,
            sensor_type_id=1,
            building_id=1,
            room_id=1,
            timestamp=datetime.datetime(2024, 1, 1, 0, 0),
        )
        )
        assert res.status_code == http.HTTPStatus.BAD_REQUEST
        # Todo: We could also query the database to check its state.


def test_valid_temperature(client: TestClient) -> None:
    """
    This will test the proper addition of new temperatures.
    """

    with PostgresContainer("postgres:16") as postgres:
        os.environ["DB_STRING"] = postgres.get_connection_url()
        viboo.server.setup_database()
        now = datetime.datetime.now()

        temperatures: List[TemperatureTestCase] = [
            # First value should be ignored as it will be outside of the timezone of 15min.
            {"building_id": 1, "room_id": 1, "sensor_type_id": 1,
                "timestamp": now-datetime.timedelta(minutes=20), "value": 10.0},
            {"building_id": 1, "room_id": 1, "sensor_type_id": 1,
                "timestamp": now-datetime.timedelta(minutes=10), "value": 20.0},
            {"building_id": 1, "room_id": 1, "sensor_type_id": 1,
                "timestamp": now, "value": 30.0},
            # Adding some noise
            {"building_id": 2, "room_id": 1, "sensor_type_id": 1,
                "timestamp": now, "value": 90.0},
        ]
        for entry in temperatures:
            update = client.post("/temperature", params=entry)
            assert update.status_code == http.HTTPStatus.CREATED

        res = client.get("/temperature", params={
            "room_id": 1,
            "building_id": 1,
            "sensor_type_id": 1,
        })

        response = viboo.server.GetTemperatureResponse(**res.json())
        assert response.value == (20.0+30.0) / \
            2, "Average not computed properly."
