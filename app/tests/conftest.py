"""

pytest fixtures — uses DATABASE_URL when set (CI/Docker), otherwise in-memory SQLite.

"""

import os



import pytest

from fastapi.testclient import TestClient

from sqlalchemy.orm import sessionmaker



# In-memory SQLite for local runs; CI/Docker inject DATABASE_URL for PostgreSQL

if "DATABASE_URL" not in os.environ:

    os.environ["DATABASE_URL"] = "sqlite:///:memory:"



from app.main import app

from app.database import Base, engine

from app.main import get_db



TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)





def override_get_db():

    db = TestingSessionLocal()

    try:

        yield db

    finally:

        db.close()





@pytest.fixture(scope="session", autouse=True)

def setup_db():

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)





@pytest.fixture()

def client():

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:

        yield c

    app.dependency_overrides.clear()


