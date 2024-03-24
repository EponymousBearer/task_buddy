from fastapi.testclient import TestClient
import pytest
from sqlmodel import Field, Session, SQLModel, create_engine, select

# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#override-a-dependency
from uitclass.main import app, get_session, Todo

from uitclass import settings

# https://fastapi.tiangolo.com/tutorial/testing/
# https://realpython.com/python-assert-statement/
# https://understandingdata.com/posts/list-of-python-assert-statements-for-unit-tests/


# postgresql://ziaukhan:oSUqbdELz91i@ep-polished-waterfall-a50jz332.us-east-2.aws.neon.tech/neondb?sslmode=require
@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_create_todo(client):
    response = client.post(
        "/todo/",
        json={
            "title": "Test Todo",
            "content": "Test Content",
            "deadline": "2023-01-01T00:00:00",  # Use a valid datetime format
            "priority": 1,  # Make sure priority is an integer if your model expects one
            "status": "pending",  # Ensure this is a valid status according to your model
            "description": "Test Todo description",
        },
    )
    assert response.status_code == 201  # Or the appropriate status code you expect
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["content"] == "Test Content"
    assert data["deadline"] == "2023-01-01T00:00:00"
    assert data["priority"] == 1
    assert data["status"] == "pending"
    assert data["description"] == "Test Todo description"

# def test_read_todo(client):
#     # Assuming an item with ID 1 exists
#     response = client.get("/todo/16")
#     assert response.status_code == 200
#     data = response.json()
#     # assert data["id"] == 16
#     # Further assertions as necessary

def test_read_all_todos(client):
    response = client.get("/todos/")
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0  # Assuming you've added items
    # Further validation of the items' contents

# def test_update_todo(client):
#     # Assuming an item with ID 1 exists and you're updating its title
#     response = client.put(
#         "/todo/19",
#         json={
#             "content": "Test Content",
#             "title": "Test Todo",
#             "deadline": "2023-01-01 00:00:00",  # Use a valid datetime format
#             "priority": 1,  # Make sure priority is an integer if your model expects one
#             "status": "pending",  # Ensure this is a valid status according to your model
#             "description": "Test Todo description",
#         },
#     )
#     assert response.status_code == 200
#     updated_item = response.json()
#     assert updated_item["title"] == "Updated Title"
#     assert updated_item["content"] == "Test Todo Content"
#     assert updated_item["deadline"] == "2023-01-01 00:00:00"
#     assert updated_item["priority"] == 1
#     assert updated_item["status"] == "pending"
#     assert updated_item["description"] == "Test Todo description"

# def test_delete_todo(client):
#     # Assuming an item with ID 1 exists
#     delete_response = client.delete("/todo/20")
#     assert delete_response.status_code == 204
#     # Verify the item no longer exists
#     fetch_response = client.get("/todo/20")
#     assert fetch_response.status_code == 404

def test_read_main(client):
    client = TestClient(app=app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


# def test_write_main():

#     connection_string = str(settings.TEST_DATABASE_URL).replace(
#         "postgresql", "postgresql+psycopg"
#     )

#     engine = create_engine(
#         connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
#     )

#     SQLModel.metadata.create_all(engine)

#     with Session(engine) as session:

#         def get_session_override():
#             return session

#         app.dependency_overrides[get_session] = get_session_override

#         client = TestClient(app=app)

#         todo_content = "buy bread"

#         response = client.post("/todos/", json={"content": todo_content})

#         data = response.json()

#         assert response.status_code == 200
#         assert data["content"] == todo_content


def test_read_list_main():

    connection_string = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg"
    )

    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override
        client = TestClient(app=app)

        response = client.get("/todos/")
        assert response.status_code == 200
