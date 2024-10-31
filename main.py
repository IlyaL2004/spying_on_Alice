from pydantic import BaseModel

from fastapi import FastAPI, Depends

from typing import Union, Annotated
from fastapi_users import fastapi_users, FastAPIUsers
from auth.auth import auth_backend
from auth.database import Users
from auth.menager import get_user_manager
from auth.schemas import UserRead, UserCreate
import joblib
from ml_model.preprocessing import preprocess
model = joblib.load("C:/Users/79853/Desktop/ptml/spying_on_Alice/ml_model/modell.joblib")

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


@app.post("/predict")
def predict():
    # Выполнение препроцессинга данных из файла `one_str.csv`
    features_sparse = preprocess()

    # Получение предсказания
    pred = model.predict(features_sparse).tolist()
    return {"predictions": pred}







