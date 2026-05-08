from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


class TaskBase(SQLModel):
    title: str = Field(index=True)
    description: str | None = None
    is_done: bool = False


class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    is_done: bool | None = None


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
        with Session(engine) as session:
            yield session

SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/task/")
def create_task(task: TaskCreate, session: SessionDep) -> Task:
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.get("/taskes/")
def read_taskes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Task]:
    taskes = session.exec(select(Task).offset(offset).limit(limit)).all()
    return taskes


@app.get("/taskes/{task_id}")
def read_task(task_id: int, session: SessionDep) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.patch("/taskes/{task_id}", response_model=TaskUpdate)
def update_task(task_id: int, task: TaskUpdate, session: SessionDep):
    task_db = session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=404, detail="task not found")
    task_data = task.model_dump(exclude_unset=True)
    task_db.sqlmodel_update(task_data)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db


@app.delete("/taskes/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}