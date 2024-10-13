from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI(
    title="AliceApp"
)

fake_users = [
    {"id" : 1, "role": "admin", "name": "Bob"},
    {"id" : 2, "role": "developer", "name": "Jack", "hobbies" : [{"id": "1", "appeared": "2024-10-10", "hobbie" : "football"}]},
    {"id" : 3, "role": "HR", "name": "Mary", "hobbies" : [{"id": "1", "appeared": "2024-10-10", "hobbie" : "music"}]},
]

@app.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    return [user for user in fake_users if user.get("id") == user_id]

class HobbieType(Enum):
    football = "football"
    music = "music"
    fishing = "fishing"

class Hobbie(BaseModel):
    id: int
    appeared: str
    hobbie: HobbieType

class User(BaseModel):
    id: int
    role: str
    name: str
    hobbies: Optional[List[Hobbie]]



@app.post("/auth/sign-up")
def user_sign_up(new_user: List[User]):
    fake_users.extend(new_user)
    return {"status": 200, "users": fake_users}



