# Brent Lee Johnson ==> Class 1
# Final End Of Module Project
# All imports
import hmac
import sqlite3
import datetime
import sys
import logging

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail, Message


# This function creates dictionaries out of SQL rows, so that the data follows JSON format
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# User class
class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# Fetching the information from the user table in the database
# def fetch_users():
#     with sqlite3.connect("pos.db") as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM user")
#         users = cursor.fetchall()
#
#         new_data = []
#
#         for data in users:
#             print(f"{data[0]}, {data[2]}, {data[3]}")
#             new_data.append(User(data[0], data[2], data[3]))
#     return new_data


# Creating the USER table
def init_user_table():
    conn = sqlite3.connect("pos.db")
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "full_name TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("User table created successfully.")


# Creating the PRODUCT table
def init_product_table():
    conn = sqlite3.connect("pos.db")
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS product(product_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "user_id INTEGER NOT NULL,"
                 "image TEXT NOT NULL,"
                 "name TEXT NOT NULL,"
                 "description TEXT NOT NULL,"
                 "price INTEGER NOT NULL,"
                 "FOREIGN KEY (user_id) REFERENCES user (user_id))")
    print("Product table created successfully.")
    conn.close()


# Calling the tables from the database
init_user_table()
init_product_table()
# users = fetch_users()

# username_table = { u.username: u for u in users }
# userid_table = { u.id: u for u in users }


# # Authentication
# def authenticate(username, password):
#     user = username_table.get(username, None)
#     if user and hmac.compare_digest(user.password.encode("utf-8"), password.encode("utf-8")):
#         return user


# def identity(payload):
#     user_id = payload["identity"]
#     return userid_table.get(user_id, None)


# Containing information that is compulsory for allowing the email to work /
# API Setup
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.debug = True
app.config["SECRET_KEY"] = "super-secret"
# This allows for the token key to have an extended time limit
app.config["JWT_EXPIRATION_DELTA"] = datetime.timedelta(seconds=4000)
CORS(app)
# For the mail
# app.config["MAIL_SERVER"] = "smtp.gmail.com"
# app.config["MAIL_PORT"] = 465
# app.config["MAIL_USERNAME"] = "huntermoonspear@gmail.com"
# app.config["MAIL_PASSWORD"] = "dianadragonheart"
# app.config["MAIL_USE_TLS"] = False
# app.config["MAIL_USE_SSL"] = True
# mail = Mail(app)

# jwt = JWT(app, authenticate, identity)


@app.route("/", methods=["GET"])
def welcome():
    response = {}

    if request.method == "GET":
        response["message"] = "Welcome"
        response["status_code"] = 201
        return response


# Registration
@app.route("/users/", methods=["GET", "POST", "PATCH"])
def user_registration():
    response = {}

    # FETCH ALL USERS
    if request.method == "GET":
        with sqlite3.connect("pos.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user")

            users = cursor.fetchall()

            response["status_code"] = 200
            response["data"] = users
            return response

    # LOGIN
    if request.method == "PATCH":
        email = request.json["email"]
        password = request.json["password"]

        with sqlite3.connect("pos.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email=? AND password=?", (email, password))

            user = cursor.fetchone()

        response["status_code"] = 200
        response["data"] = user
        return response

    # REGISTER
    if request.method == "POST":
        try:
            full_name = request.json["full_name"]
            email = request.json["email"]
            password = request.json["password"]

            with sqlite3.connect("pos.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user("
                               "full_name,"
                               "email,"
                               "password) VALUES(?, ?, ?)", (full_name, email, password))
                conn.commit()
                response["message"] = "Successfully added new user into database"
                response["status_code"] = 201
            return response
        except ValueError:
            response["message"] = "Failed"
            response["status_code"] = 209
            return response


# GETS A SPECIFIC USER
@app.route("/users/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    response = {}

    with sqlite3.connect("pos.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE user_id=" + str(user_id))
        user = cursor.fetchone()

    response["status_code"] = 200
    response["data"] = user
    return response


# PRODUCTS
@app.route("/product/", methods=["GET", "POST"])
def products():
    response = {}
    # GET ALL PRODUCTS
    if request.method == "GET":
        with sqlite3.connect("pos.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM product")
            products = cursor.fetchall()

        response["status_code"] = 200
        response["data"] = products
        return response

    # ADDS A PRODUCT
    if request.method == "POST":
        try:
            user_id = request.json["user_id"]
            image = request.json["image"]
            name = request.json["name"]
            description = request.json["description"]
            price = request.json["price"]

            with sqlite3.connect("pos.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO product("
                               "user_id,"
                               "image,"
                               "name,"
                               "description,"
                               "price) VALUES(?, ?, ?, ?, ?)", (user_id, image, name, description, price))
                conn.commit()
                response["message"] = "Successfully added new product into database"
                response["status_code"] = 201
            return response
        except ValueError:
            response["message"] = "Failed to create product"
            response["status_code"] = 209
            return response


if __name__ == "__main__":
    app.debug = True
    app.run()
