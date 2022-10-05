import json
from http.client import HTTPException
from fastapi import FastAPI, Depends, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uvicorn

app = FastAPI()
oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with open("userdb.json", "r") as json_file:
        json_data = json.load(json_file)
        if json_data:
            password = json_data.get(form_data.username)
            if not password:
                raise HTTPException()

    return {"access_token": form_data.username, "token_type": "bearer"}


@app.post("/send_coin")
def transfer_money(token: str = Depends(oauth_scheme), destination_user: str = Body(...),
                   amount_to_transfer: float = Body(...)):
    user_balance = None
    with open("userbalance.json", "r") as user_balance_file:
        user_balance = json.load(user_balance_file)
        curr_user_balance = user_balance.get(token)['curr_balance']
        dest_user = user_balance.get(destination_user)
        if not dest_user:
            raise HTTPException()
        dest_user_bal = dest_user['curr_balance']
        print(f"destination user balance:{dest_user_bal}")
        if curr_user_balance - amount_to_transfer < 0:
            raise HTTPException()
    user_balance[token]['curr_balance'] -= amount_to_transfer
    user_balance[destination_user]['curr_balance'] += amount_to_transfer
    with open("userbalance.json", "w") as user_balance_write:
        json.dump(user_balance, user_balance_write)
        return {
            "username": token,
            "message": f"money success{amount_to_transfer}"
        }


@app.get("/user_balance")
def get_user_balance(token: str = Depends(oauth_scheme)):
    with open("userbalance.json", "r") as file:
        user_balance = json.load(file)
    if not user_balance.get(token):
        raise HTTPException()
    return {
        "username": token,
        "current_balance": user_balance.get(token)['curr_balance']
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
