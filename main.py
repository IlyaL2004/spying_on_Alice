from pydantic import BaseModel

from fastapi import FastAPI, Depends

from typing import Union, Annotated
from fastapi_users import fastapi_users, FastAPIUsers
from auth.auth import auth_backend
from auth.database import Users
from auth.menager import get_user_manager
from auth.schemas import UserRead, UserCreate
import joblib

model = joblib.load("/home/vadim/spying_on_Alice/ml_model/model.joblib")

app = FastAPI(
    title="App"
)

fastapi_users = FastAPIUsers[Users, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)


app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

current_user = fastapi_users.current_user()

@app.get("/protected-route")
def protected_route(users: Users = Depends(current_user)):
    return f"Hello, {users.username}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"

class Session(BaseModel):
    time1: int
    site1: int
    time2: int
    site2: int


@app.post("/predict")
def predict(session: Session):
    features = [[
        session.time1,
        session.site1,
        session.time2,
        session.site2,
    ]]

    pred = model.predict(features).tolist()[0]
    return {
        "prediction": pred
    }

