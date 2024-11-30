from flask import Flask, jsonify
import websocket
import json
app = Flask(__name__)


import os
import dotenv
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import time as time_module  # To avoid confusion with your 'time' field
from datetime import datetime, timedelta  # For time calculations
import threading

load_dotenv()

finhub_api_key = os.environ.get("FINHUB_API_KEY")
mongo_db_password = os.environ.get("MONGO_DB_PASSWORD")

"""Connect to mongo DB"""

uri = f"mongodb+srv://stock:{mongo_db_password}@cluster1.n7nkbzx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"
from pymongo import MongoClient

   # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
client = MongoClient(uri)
db = client['stocks']
collection = db["stock_prices_historical"]
# result = collection.insert_one({"item": "card", "qty": 15})

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

"""Set up websockets"""

def on_message(ws, message):
    res = json.loads(message)
    if res["type"] == "trade":
        data = res["data"][0]
        time = data['t']
        stock = data['s']
        price = data['p']
        collection.insert_one({"time": time, "stock": stock, "price": price})
        # print(f"Data is: {data}")
        print(f"Price is {price}")

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"AAPL"}')
    ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')


"""Define app routes for post and get requests"""

@app.route('/')
def index():
    return "Hello, World!"



@app.route('/get_past_30_minutes')
def get_past_30_minutes():
    print("Endpoint /get_past_30_minutes called")
    thirty_minutes_ago = int((time_module.time() - 30 * 60) * 1000)  # Convert to milliseconds
    recent_data = collection.find({"time": {"$gte": thirty_minutes_ago}})
    data_list = [{"time": doc["time"], "stock": doc["stock"], "price": doc["price"]} for doc in recent_data]
    return jsonify(data_list)


def run_websocket():
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={finhub_api_key}",
                                 on_message=on_message,
                                 on_error=on_error,
                                 on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

def run_flask():
    app.run(debug=False)

if __name__ == "__main__":

    websocket_thread = threading.Thread(target=run_websocket)
    flask_thread = threading.Thread(target=run_flask)

    websocket_thread.start()
    flask_thread.start()

    websocket_thread.join()
    flask_thread.join()

    # TODO add to backend when it is recieved