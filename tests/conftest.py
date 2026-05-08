import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from main import app, get_session  # Импортируем из приложения


@pytest.fixture(name="session")
def session_fixture():
    # 1. Создаем движок, который живет ТОЛЬКО в памяти (база исчезнет после теста)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    # 2. Создаем сессию
    with Session(engine) as session:
        yield session  # Тест "берет" эту сессию

    # После теста база удалится сама
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    # 3. Переопределяем зависимость get_session для FastAPI
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    # 4. Возвращаем клиент, который "общается" с приложением
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()