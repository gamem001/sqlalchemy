import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    #This finds the last date of the 'year'
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    #This will give the first date of the 'year'
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #This is a query that gives the precipitation results for any date greater than the first date of the year defined.
    result = session.query(Measurement.prcp, Measurement.date).\
    filter(Measurement.date >= query_date).\
    group_by(Measurement.date).\
    order_by(Measurement.date).all()
    #This is a dictionary comprehension that will create a dictionary from the list result of the query
    precip_dictionary = {date: prcp for prcp, date in result}
    return jsonify(precip_dictionary)

    session.close()


@app.route("/api/v1.0/stations")
def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Find list of all stations
    station_data = session.query(Station.station).all()
    stations = list(np.ravel(station_data))
    return jsonify(stations=stations)

    session.close()

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query for beginning and ending dates for the last year of data.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for temps and dates from the most active station for the last year of data.
    tobs_info = session.query(Measurement.tobs, Measurement.date).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= query_date).\
    filter(Measurement.date <= last_date).\
    order_by(Measurement.date).all()
    tobs = list(np.ravel(tobs_info))
    return jsonify(tobs)

    session.close()


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):

    session = Session(engine)

    """Return TMIN, TAVG, TMAX."""
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if end is None:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)
    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)
    
    session.close()


if __name__ == '__main__':
    app.run()

