import datetime

from flask import Blueprint, jsonify, request, render_template
from app import db
import time
from models.models import SensorData

main_bp = Blueprint('main_controller', __name__)


@main_bp.route('/')
def home_func():
    return render_template('home.html', title="Home")

# Live Data Route (Chart for live data)
@main_bp.route('/live')
def live_func():
    # Query live data from the database
    live_data = {
        'humidity': SensorData.query.filter(SensorData.sensor_id == 'sensor1').order_by(SensorData.timestamp.desc()).first(),
        'temperature': SensorData.query.filter(SensorData.sensor_id == 'sensor2').order_by(SensorData.timestamp.desc()).first(),
        'moisture': SensorData.query.filter(SensorData.sensor_id == 'sensor3').order_by(SensorData.timestamp.desc()).first()
    }
    return render_template('live.html', title="Live Data", live_data=live_data)

# Historical Data Route (Chart for historical data)
@main_bp.route('/historical')
def historical_func():
    # Get historical data from the database
    end_time = datetime.utcnow()
    start_time = end_time - datetime.timedelta(days=7)  # Get data for the last 7 days

    humidity_data = SensorData.query.filter(SensorData.sensor_id == 'sensor1', SensorData.timestamp >= start_time).all()
    temperature_data = SensorData.query.filter(SensorData.sensor_id == 'sensor2', SensorData.timestamp >= start_time).all()
    moisture_data = SensorData.query.filter(SensorData.sensor_id == 'sensor3', SensorData.timestamp >= start_time).all()

    # Passing data to the template
    return render_template('historical.html', title="Historical Data", humidity_data=humidity_data, temperature_data=temperature_data, moisture_data=moisture_data)



