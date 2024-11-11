import os
import time
import threading
from flask import Flask, Blueprint, render_template, jsonify
import paho.mqtt.client as mqtt
from flask_sqlalchemy import SQLAlchemy
from models.models import SensorData  # Assuming SensorData is in models.py

app = Flask(__name__)

# Initialize Blueprint
main_bp = Blueprint('main_controller', __name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sensor_data.db"
db = SQLAlchemy(app)

# MQTT settings
BROKER = "classpi"  # Update with your broker address
PORT = 1883


# Callback function for MQTT connection
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    if rc == 0:
        # Subscribe to individual sensor topics here
        client.subscribe("sensors/sensor1")  # Moisture sensor
        client.subscribe("sensors/sensor2")  # Temperature sensor
        client.subscribe("sensors/sensor3")  # Humidity sensor
        print("Subscribed to sensor topics")


def on_message(client, userdata, message):
    try:
        # Decode the payload and store the sensor data in the database
        sensor_id = message.topic.split('/')[-1]  # Extract sensor ID from topic
        sensor_value = float(message.payload.decode("utf-8"))  # Decode and convert to float

        # Create a new SensorData entry
        new_data = SensorData(sensor_id=sensor_id, value=sensor_value)

        # Add and commit to the database
        db.session.add(new_data)
        db.session.commit()

        print(f"Stored sensor data: {sensor_id} = {sensor_value}")

    except Exception as e:
        print(f"Error processing message: {e}")


# MQTT client setup and execution
def run_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Attempt to connect to the MQTT broker
    try:
        client.connect(BROKER, PORT, keepalive=60)  # Keepalive set for 60 seconds
        client.loop_start()  # Start the loop to process MQTT messages
        print("MQTT client is running...")
    except Exception as e:
        print(f"Error connecting to broker: {e}")
        return


# Start the MQTT client in a separate thread
mqtt_thread = threading.Thread(target=run_mqtt_client)
mqtt_thread.daemon = True  # Ensure the thread exits when the main program exits
mqtt_thread.start()

# Register the blueprint
app.register_blueprint(main_bp)

# Create the database tables if they don't exist
db.create_all()


@app.route('/')
def index():
    # You can use this route to display data or perform other actions
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)  # Set debug=True for development