import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)


Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

#List all routes that are available

@app.route("/")
def homepage():
    return (
        f"Available Routes:<br/>"

        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

#`/api/v1.0/precipitation`
#Convert the query results to a Dictionary using `date` as the key 
#and `prcp` as the value.

@app.route("/api/v1.0/precipitation")
def precipitation():

    """Return the prcp data for the last year"""

    last_year = dt.date(2017, 1, 1) - dt.timedelta(days=365)

    prec_query = session.query(Measurement.date, Measurement.prcp).\

        filter(Measurement.date >= last_year).all()

    prec_dict = {date: prcp for date, prcp in prec_query}

#Return the JSON representation of your dictionary.
    return jsonify(prec_dict)

#`/api/v1.0/stations`

@app.route("/api/v1.0/stations")
def stations():

    """Return a list of stations."""

    stations_q = session.query(Station.station).all()

# Return a JSON list of stations from the dataset.
    stations = list(np.ravel(stations_q))
    return jsonify(stations)

# `/api/v1.0/tobs`

@app.route("/api/v1.0/tobs")
def temp_monthly():

    """Return the Temperature Observations (tobs) for the previous year."""

#query for the dates and temperature observations from a year from the 
#last data point.
    last_year = dt.date(2017, 1, 1) - dt.timedelta(days=365)

    tobs_q = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= last_year).all()

    tobs = list(np.ravel(tobs_q))

#Return a JSON list of Temperature Observations (tobs) for the 
#previous year.
    return jsonify(tobs)

#`/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):

    """Return TMIN, TAVG, TMAX."""

sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

#Return a JSON list of the minimum temperature, the average temperature,
#and the max temperature for a given start or start-end range.

#When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all
#dates greater than and equal to the start date.

if not end:
    temps_q = session.query(*sel).filter(Measurement.date >= start).all()

    temps = list(np.ravel(temps_q))

    return jsonify(temps)

#When given the start and the end date, calculate the `TMIN`, `TAVG`, 
#and `TMAX` for dates between the start and end date inclusive.

    temps_q = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temps = list(np.ravel(temps_q))

    return jsonify(temps)

#run flask app
if __name__ == '__main__':
    app.run()