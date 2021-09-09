# Brent Lee Johnson ==> Class 1
# Final End Of Module Project
# All imports
import hmac
import sqlite3
import datetime
import sys
import logging
import cloudinary
from cloudinary import uploader

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

# Containing information that is compulsory for allowing the email to work /
# API Setup
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.debug = True
app.config["SECRET_KEY"] = "super-secret"
# This allows for the token key to have an extended time limit
# app.config["JWT_EXPIRATION_DELTA"] = datetime.timedelta(seconds=4000)
CORS(app)


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
            all_products = cursor.fetchall()

        response["status_code"] = 200
        response["data"] = all_products
        return response

    # ADDS A PRODUCT
    if request.method == "POST":
        try:
            user_id = request.json["user_id"]
            image = request.json["image"]
            name = request.json["name"]
            description = request.json["description"]
            price = request.json["price"]

            # Upload image to cloudinary
            cloudinary.config(cloud_name="dlmtwdavm", api_key="263954874477652",
                              api_secret="SKaOWOepasPrCPdE--p8NQhRd9w")
            upload_result = None

            app.logger.info("%s file_to_upload", image)
            if image:
                upload_result = cloudinary.uploader.upload(image)  # Upload results
                app.logger.info(upload_result)

            with sqlite3.connect("pos.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO product("
                               "user_id,"
                               "image,"
                               "name,"
                               "description,"
                               "price) VALUES(?, ?, ?, ?, ?)", (user_id, upload_result["url"], name, description,
                                                                price))
                conn.commit()
                response["message"] = "Successfully added new product into database"
                response["status_code"] = 201
            return response
        except ValueError:
            response["message"] = "Failed to create product"
            response["status_code"] = 209
            return response


@app.route("/product/<int:user_id>/", methods=["GET"])
def get_user_product(user_id):
    response = {}

    # GETS ALL PRODUCTS
    if request.method == "GET":
        with sqlite3.connect("pos.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM product WHERE user_id=" + str(user_id))
            user_products = cursor.fetchall()

        response["status_code"] = 200
        response["data"] = user_products
        return response


if __name__ == "__main__":
    app.debug = True
    app.run()
