import pytest
from fastapi.testclient import TestClient
import viboo.server
from testcontainers.postgres import PostgresContainer
import os
import http

@pytest.fixture
def client() -> TestClient:
  return TestClient(viboo.server.app)

def setup_database(db_string: str) -> None:

  return

def test_invalid_temperature(client: TestClient) -> None:
  """
  This will test that invalid measures are not accepted.
  """
  with PostgresContainer("postgres:16") as postgres:
    os.environ["DB_STRING"] = postgres.get_connection_url()
    room = 1
    sensor_id = 1
    res = client.post("/temperature", params={
      "room": room,
      "value": -1,
      "sensor": sensor_id,
    })
    assert res.status_code == http.HTTPStatus.BAD_REQUEST
    # Todo: We could also query the database to check its state.


def test_valid_temperature(client: TestClient) -> None:
  """
  This will test the proper addition of new temperatures.
  """
  with PostgresContainer("postgres:16") as postgres:
    os.environ["DB_STRING"] = postgres.get_connection_url()
    room = 1
    values = [5, 20, 40]
    sensor_id = 1
    for temp in values:
      res = client.post("/temperature", params={
        "room_id": room,
        "value": temp,
        "sensor_type_id": sensor_id,
      })
      assert res.status_code == http.HTTPStatus.CREATED

    res = client.get("temperature")


