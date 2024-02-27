from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base
import pytest
import app.models as models

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL, connect_args={
                       "check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db_item = models.DBItem(id=100, name='testing object',
                            description='testing object manually')
    db.add(db_item)
    db.commit()
    db.close()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


def test_read_root(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == "hello world"


def test_create_item(client):
    response = client.post(
        '/items/', json={'name': 'Test Item', 'description': 'This is a test item'})
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Test Item'
    assert data['description'] == 'This is a test item'
    assert 'id' in data


def test_update_item(client):
    item_id = 100
    response = client.put(
        f'/items/{item_id}', json={'name': 'updating item', 'description': 'testing updating item'})
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'updating item'
    assert data['description'] == 'testing updating item'
    assert data['id'] == item_id


def test_delete_item(client):
    item_id = 100
    response = client.delete(f'/items/{item_id}')
    assert response.status_code == 204
