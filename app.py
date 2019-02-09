import numpy as np
import datetime as dt
from matplotlib import style
import matplotlib.pyplot as plt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
inspector = inspect(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        "Welcome to Hawaii Weather API:<br/>"
        "Available Routes:<br/>"
        "Precipitation Information: /api/v1.0/precipitation<br/>"
        "Station Information: /api/v1.0/stations<br/>"
        "Temp information: /api/v1.0/tobs<br/>"
        "Date: /api/v1.0/Insert Date as YYYY-MM-DD<br/>"
        "Start to End Date: /api/v1.0/Insert Start Date as YYYY-MM-DD/Insert End Date as YYYY-MM-DD<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
#Query for dates from a year from the last data point
    last_date = dt.datetime.strptime('2016-08-23','%Y-%m-%d')

    precip_year = session.query(Measurement.date, Measurement.prcp).\
        filter(func.strftime(Measurement.date)>= last_date).\
        order_by(Measurement.date).all()

#Query date and prcp values to a dictionary
    prcp_dict = {}
    for prcp in precip_year:
        prcp_dict[prcp.date] = prcp.prcp
#Return JSON of prcp dictionary
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def station():
   # Query all stations from Station
    stations = session.query(Station.name).all()
    
    # Create list of station names
    station_list = []
    
    #Add stations to list
    
    for station in stations:
        station_list.append(station.name)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tempertature():
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    tobs= session.query(Measurement.date, Measurement.tobs).\
        filter(func.strftime(Measurement.date)>= last_date).\
        order_by(Measurement.date).all()

    tobs=[]
    for temperature in tobs:
        tobs_dict = {}
        tobs_dict["date"] = temperature.date
        tobs_dict["tobs"] = temperature.tobs
        tobs.append(tobs_dict)

    return jsonify(tobs)

@app.route("/api/v1.0/start")
def start():
    def temps_start(start_date):
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    start_date = dt.date('%Y-%m-%d')
    start_temps = temps_start(start_date)
    return jsonify(start_temps)

@app.route("/api/v1.0/avgtemp/<start_date>/<end_date>")
def between_dates(start_date, end_date):

    start_end_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    start_end_temps=[]
    for temps in start_end_temps:
        dict = {}
        dict["Temp Min"] = temps[0]
        dict["Temp Avg"] = temps[1]
        dict["Temp Max"] = temps[2]
        dict["Start Date"] = start_date
        dict["End Date"] = end_date
        start_end_temps.append(dict)
    
    return jsonify(start_end_temps)

if __name__ == "__main__":
    app.run(debug=True)
