from fastapi import Body, FastAPI

import uvicorn
import psycopg2
import sqllex as sx
from typing import Union
from datetime import date
from datetime import datetime
import re

app = FastAPI()

db = sx.PostgreSQLx(
    engine=psycopg2,  # Postgres engine
    dbname="fastapi",  # database name
    user="fastapi",  # username
    password="fastapi",  # user's password
    host="db",  # psql host address
    port="5432",  # connection port

    # Optional parameters
    template={
        'users': {
            'name': [sx.TEXT, sx.NOT_NULL, sx.UNIQUE],
            'birthday': [sx.DATE, sx.NOT_NULL]
        }
    },

    # Create connection to database with database class object initialisation
    init_connection=True
)

USERS = db["users"]


def calculate_dates(original_date, now):
    delta1 = datetime(now.year, original_date.month, original_date.day)
    delta2 = datetime(now.year + 1, original_date.month, original_date.day)

    return ((delta1 if delta1 > now else delta2) - now).days


@app.get("/{user}")
def get_user_birthday(user: str):
    if re.match(r'^[a-zA-Z]+$', user):
        bd = USERS.select("birthday", WHERE=(USERS["name"] == user), )
        if bd:
            now = datetime.now()
            if not bd[0][0] == datetime.today().date():
                n = calculate_dates(bd[0][0], now)
                return f'Hello, {user} Your birthday is in {n} day'
            else:
                return f'Hello {user} Happy birthday'


@app.put("/hellousername/{user}", status_code=204)
def put_birthday(user: str,
                 payload: Union[date, None] = Body(default=None)
                 ):
    if re.match(r'^[a-zA-Z]+$', user):

        if not USERS.select("name", WHERE=(USERS["name"] == user), ):

            if payload < date.today():

                if payload == "1970-01-01":
                    print("wrong date, will use default 1970-01-01")

                print(f'insert {user} with {payload}')

                USERS.insert(user, payload)
            else:
                print(f'must be a date before the today date')
        else:
            print(f'exist {user} in db')

    else:
        print("user have non alpha letters")


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
