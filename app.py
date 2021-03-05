#import dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement= Base.classes.measurement
Station= Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
#home page route with clickable links
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>tobs</a><br/>"
        f"<a href='/api/v1.0/<start>'>starting temperature</a><br/>"
        f"<a href='/api/v1.0/<start>/<end>'>starting/ending temperature range</a><br/>"
    )
#display json for prcp
@app.route("/api/v1.0/precipitation")
def precipitation():
     # Create our session (link) from Python to the DB
    session = Session(engine)
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    results = session.query(Measurement.prcp, Measurement.date).order_by(Measurement.date.desc()).all()
    session.close()
      # Create a dictionary from the row data and append to a list of all_results
    all_results = []
    for item in results:
        item_dict = {}
        item_dict["date"] = item[1]
        item_dict["prcp"] = item[0]
        all_results.append(item_dict)

    return jsonify(all_results)
#display station json data
@app.route('/api/v1.0/stations')  
def stations():
    session = Session(engine)
    
    results= session.query(Station.station).order_by(Station.station.desc()).all()
    session.close()
    return jsonify(results)
#display temperature observed (tobs) at the most active station in the previous year
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    prev_year= dt.date(2017,8,23) - dt.timedelta(days=365)
    results=session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281')\
.filter(Measurement.date >= prev_year).all()
    return jsonify(results)
    session.close()
#display average to the end of the data set given a start date in the url    
@app.route('/api/v1.0/<start>/')
def calc_temp(start):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    session=Session(engine)
    results= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()    
    session.close()
    return jsonify(results)
#display average between a given range of dates in the url
@app.route('/api/v1.0/<start>/<end>')    
def calc_temps(start, end):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    session=Session(engine)
    results= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()    
    session.close()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)  