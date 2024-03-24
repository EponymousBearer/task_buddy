# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from uitclass import settings
from sqlmodel import Field, Session, SQLModel, Enum, create_engine, select
from fastapi import FastAPI, Depends, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import enum
from fastapi import HTTPException

class TaskStatus(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)  # New
    content: str
    deadline: Optional[datetime] = Field(default=None)  # New
    priority: int = Field(default=1)  # New, consider using Enum for more descriptive priorities
    status: TaskStatus = Field(sa_column_kwargs={"default": TaskStatus.pending})  # New, using Enum
    description: Optional[str] = Field(default=None)  # New
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)})

# class Todo(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     content: str = Field(index=True)

# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)


# recycle connections after 5 minutes
# to correspond with the compute scale down
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Hello World API with DB",
    version="0.0.1",
    servers=[
        {
            "url": "https://bug-amusing-formally.ngrok-free.app",  # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server",
        }
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify domains you want to allow, use ["*"] for allowing all
    allow_credentials=True,
    allow_methods=["*"],  # Specify methods you want to allow, use ["*"] for allowing all
    allow_headers=["*"],  # Specify headers you want to allow, use ["*"] for allowing all
)

def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/todo/", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_todo_task(todo: Todo, session: Annotated[Session,Depends(get_session)]):
    db_todo = Todo(
        title=todo.title,
        content=todo.content,
        deadline=todo.deadline,
        priority=todo.priority,
        status=todo.status,
        description=todo.description,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)  
    )
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo

@app.put("/todo/{task_id}", response_model=Todo)
async def update_todo_task(task_id: int, task_update: Todo, session: Annotated[Session,Depends(get_session)]):
    # Fetch the existing task using SQLModel's session.exec() method
    db_task = session.exec(select(Todo).where(Todo.id == task_id)).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields if provided in the request, using model_dump() as recommended
    update_fields = task_update.model_dump(exclude_unset=True)
    for var, value in update_fields.items():
        setattr(db_task, var, value)

    db_task.updated_at = datetime.now(timezone.utc)  # Explicitly update the 'updated_at' field
    session.commit()
    return db_task

@app.delete("/todo/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_task(task_id: int, session: Annotated[Session,Depends(get_session)]):
    db_task = session.get(Todo, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(db_task)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # No content to return

@app.get("/todos/", response_model=list[Todo])
async def read_all_tasks(session: Annotated[Session,Depends(get_session)]):
    tasks = session.exec(select(Todo)).all()
    return tasks


# @app.get("/todos/", response_model=list[Todo])
# def read_todos(session: Annotated[Session, Depends(get_session)]):
#     todos = session.exec(select(Todo)).all()
#     return todos
