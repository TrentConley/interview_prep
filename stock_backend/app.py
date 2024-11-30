from flask import Flask
import websocket
import json
app = Flask(__name__)


import os
import dotenv
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

finhub_api_key = os.environ.get("FINHUB_API_KEY")
mongo_db_password = os.environ.get("MONGO_DB_PASSWORD")

"""Connect to mongo DB"""

uri = f"mongodb+srv://stock:{mongo_db_password}@cluster1.n7nkbzx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

"""Set up websockets"""

def on_message(ws, message):
    res = json.loads(message)
    print(str(res))
    if res["type"] == "trade":
        print(res["data"])

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"AAPL"}')

"""Define app routes for post and get requests"""

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == "__main__":


    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={finhub_api_key}",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
    app.run(debug=True)