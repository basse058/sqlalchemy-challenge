import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# Database Setup
database_path = "Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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

        f'<br/>'
        f'Welcome to the SurfsUp API!<br/>'
        f'<br/>'
        f'Find dates in the precipitation route so you can look up data on a date or between a range of dates. <br/>'
        f'<br/>'
        f'Available Routes:<br/>'
        f'<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'<br/>'
        f'Data from a specific date (adjust date):<br/>'
        f'/api/v1.0/2017-08-23<br/>'
        f'<br/>'
        f'Data between a range of dates (adjust dates):<br/>'
        f'/api/v1.0/2010-01-01/2017-08-23<br/>'
    )

#precipitation route
@app.route("/api/v1.0/precipitation")
def precip_date():
    session = Session(engine)
    res=session.query(Measurement.date, Measurement.prcp)
    session.close()

    results=[]
    for date,precip in res:
        precip_dic={}
        precip_dic["date"]=date
        precip_dic["prcp"]=precip
        results.append(precip_dic)
    return jsonify(results)

#Stations route
@app.route("/api/v1.0/stations")
def station_list():
    session = Session(engine)
    result=session.query(Station.name).all()
    session.close()
    all_names = list(np.ravel(result))
    return jsonify(all_names)

#tobs route
@app.route("/api/v1.0/tobs")
def tob():
    session = Session(engine)
    recent_date=dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.date.desc())\
        .first()[0], '%Y-%m-%d')
    last_12_months=recent_date - dt.timedelta(days=365)
    last_12_months=last_12_months.date()

    top_station = session.query(Measurement.station).filter(Measurement.date >= last_12_months)\
       .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0] 

    tobs_j =session.query(Measurement.tobs).filter(Measurement.station == top_station).all()
    session.close()
    tobs = list(np.ravel(tobs_j))
    return jsonify(tobs)

# For a specified start
@app.route("/api/v1.0/<start>")
def start_day(start):
    session = Session(engine)
    query_ = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    start_list=list(np.ravel(query_))
    session.close()
    return jsonify(start_list)

# For a specified start date and end date
@app.route("/api/v1.0/<start>/<end>")
def start_end_day(start,end):
    session = Session(engine)
    query_ = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start,Measurement.date<= end).all()
    start_list=list(np.ravel(query_))
    session.close()
    return jsonify(start_list)        

if __name__ == '__main__':
    app.run(debug=True)