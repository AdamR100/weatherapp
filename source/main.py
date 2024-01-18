from flask import *
from flask_sqlalchemy import SQLAlchemy
import requests
import os
import json
from config import appid
app = Flask('weather_app')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pytdb.sqlite'
app.config['SECRET_KEY'] = os.urandom(30)
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

def get_weather_by_name(city_name):
    # country_numeric = pycountry.countries.get(name='Poland')
    params = {'q': '{}'.format(city_name), 'appid': appid, 'units': 'metric', 'lang': 'pl'}
    obj = requests.get('https://api.openweathermap.org/data/2.5/weather?', params).json()
    return obj


def get_weather_by_id(id):
    params = {'id' : id, 'appid': appid, 'units': 'metric', 'lang': 'pl'}
    obj = requests.get('https://api.openweathermap.org/data/2.5/weather?', params).json()
    return obj


@app.route('/', methods=['GET'])
def main_page():
    return render_template('index.html', weather_list=[get_weather_by_id(id) for id in db.session.query(City.id)], abs=abs)


@app.route('/del', methods=['POST'])
def delete_card():
    City.query.filter(City.id == request.form['id']).delete()
    db.session.commit()
    return redirect(url_for('main_page'))


@app.route('/add', methods=['POST'])
def add_city():
    city_name = request.form['city_name']
    weather = get_weather_by_name(city_name)
    if weather.get('cod') != 200:
        flash('City not found')
    elif db.session.query(City.id).filter(City.id == weather['id']).count() == 0:
        db.session.add(City(id=weather['id'], name=weather['name']))
        db.session.commit()
    else:
        flash('The city has already been added to the list!')
    return redirect(url_for('main_page'))


app.run()
