import cv2
from math import perm
import os
import pickle
from email.policy import default
from tkinter import SEL_LAST
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, flash, session, redirect, url_for,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from DailySeed_scrapper import *
from weather_forcasting_app import *
from weather import Weather, WeatherException
from mandiprice_forcasting_app import *
from datetime import datetime
from sqlalchemy import any_
import pandas as pd
import numpy as np
import pickle as pk
from sklearn.preprocessing import LabelEncoder
import re
from nltk.stem.porter import PorterStemmer
from keras.utils import np_utils
from keras.models import load_model
import json
import random
import joblib
import sqlite3



app = Flask(__name__)
app.config['SECRET_KEY'] = "abc"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///artificial_agriculture.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ANIMALS_SELL_IMAGES'] = "./static/img/animals_sell_images/"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)
app.config.from_pyfile('config/config.cfg')
w = Weather(app.config)

IMG_COUNT = 1


@app.route('/cotton_prediction', methods=['POST'])
def cotton_prediction():
    global IMG_COUNT
    if request.files['image'].filename == '':
        print('No file was uploaded')
        return render_template('classification_cotton.html')
    else:
        img = request.files['image']
        img.save('static/uploaded/classification-{}.jpg'.format(IMG_COUNT))
        img_arr = cv2.imread('static/uploaded/classification-{}.jpg'.format(IMG_COUNT))

        img_arr = cv2.resize(img_arr, (224, 224))
        img_arr = img_arr / 255.0
        img_arr = img_arr.reshape(1, 224, 224, 3)
        predictions = model_cotton.predict(img_arr)
        prediction = np.argmax(predictions, axis=1)
        print(prediction[0])
        IMG_COUNT = IMG_COUNT + 1
        file_path = load_saved_img()
        print(IMG_COUNT)
        print(file_path)
        if prediction[0] == 0:
            return render_template('result_classification.html', data=["diseased cotton leaf"],user_image = file_path)
        elif prediction[0] == 1:
            return render_template('result_classification.html', data=["diseased cotton plant"],user_image = file_path)
        elif prediction[0] == 2:
            return render_template('result_classification.html', data=["fresh cotton leaf"],user_image = file_path)
        else:
            return render_template('result_classification.html', data=["fresh cotton plant"],user_image = file_path)

@app.route('/grapes_prediction', methods=['POST'])
def grapes_prediction():
    global IMG_COUNT
    if request.files['image'].filename == '':
        print('No file was uploaded')
        return render_template('classification_grapes.html')
    else:
        img = request.files['image']
        img.save('static/uploaded/classification-{}.jpg'.format(IMG_COUNT))
        img_arr = cv2.imread('static/uploaded/classification-{}.jpg'.format(IMG_COUNT))

        img_arr = cv2.resize(img_arr, (224, 224))
        img_arr = img_arr / 255.0
        img_arr = img_arr.reshape(1, 224, 224, 3)
        predictions = model_grape.predict(img_arr)
        prediction = np.argmax(predictions, axis=1)
        print(prediction[0])
        IMG_COUNT = IMG_COUNT + 1
        file_path = load_saved_img()
        if prediction[0] == 0:
            return render_template('result_classification.html', data=["Grape___Black_rot'"],user_image = file_path)
        elif prediction[0] == 1:
            return render_template('result_classification.html', data=["Grape___Esca_(Black_Measles)"],user_image = file_path)
        elif prediction[0] == 2:
            return render_template('result_classification.html', data=["Grape___Leaf_blight_(Isariopsis_Leaf_Spot)"],user_image = file_path)
        else:
            return render_template('result_classification.html', data=["Grape___healthy", 'red'],user_image = file_path)


@app.route('/potato_prediction', methods=['POST'])
def potato_prediction():
    global IMG_COUNT
    if request.files['image'].filename == '':
        print('No file was uploaded')
        return render_template('classification_potato.html')
    else:
        img = request.files['image']
        img.save('static/uploaded/classification-{}.jpg'.format(IMG_COUNT))
        img_arr = cv2.imread('static/uploaded/classification-{}.jpg'.format(IMG_COUNT))

        img_arr = cv2.resize(img_arr, (224, 224))
        img_arr = img_arr / 255.0
        img_arr = img_arr.reshape(1, 224, 224, 3)
        predictions = model_potato.predict(img_arr)
        prediction = np.argmax(predictions, axis=1)
        print(prediction[0])
        IMG_COUNT = IMG_COUNT + 1
        file_path = load_saved_img()
        if prediction[0] == 0:
            return render_template('result_classification.html', data=["Potato_Early_blight"],user_image = file_path)
        elif prediction[0] == 1:
            return render_template('result_classification.html', data=["Potato_Late_blight"],user_image = file_path)
        else:
            return render_template('result_classification.html', data=["Potato_healthy "],user_image = file_path)

@app.route('/tomato_prediction', methods=['POST'])
def tomato_prediction():
    global IMG_COUNT
    if request.files['image'].filename == '':
        print('No file was uploaded')
        return render_template('classification_tomato.html')
    else:
        img = request.files['image']
        img.save('static/uploaded/classification-{}.jpg'.format(IMG_COUNT))
        img_arr = cv2.imread('static/uploaded/classification-{}.jpg'.format(IMG_COUNT))

        img_arr = cv2.resize(img_arr, (224, 224))
        img_arr = img_arr / 255.0
        img_arr = img_arr.reshape(1, 224, 224, 3)
        predictions = model_tomato.predict(img_arr)
        prediction = np.argmax(predictions, axis=1)
        print(prediction[0])
        IMG_COUNT = IMG_COUNT + 1
        file_path = load_saved_img()
        if prediction[0] == 0:
            return render_template('result_classification.html', data=["Bacterial_spot"],user_image = file_path)
        elif prediction[0] == 1:
            return render_template('result_classification.html', data=["Early_blight"],user_image = file_path)
        elif prediction[0] == 2:
            return render_template('result_classification.html', data=["Late_blight"],user_image = file_path)
        elif prediction[0] == 3:
            return render_template('result_classification.html', data=["Leaf_Mold"],user_image = file_path)
        elif prediction[0] == 4:
            return render_template('result_classification.html', data=["Septoria_leaf_spot"],user_image = file_path)
        elif prediction[0] == 5:
            return render_template('result_classification.html', data=["Spider_mites Two-spotted_spider_mite"],user_image = file_path)
        elif prediction[0] == 6:
            return render_template('result_classification.html', data=["Target_Spot"],user_image = file_path)
        elif prediction[0] == 7:
            return render_template('result_classification.html', data=["Tomato_Yellow_Leaf_Curl_Virus"],user_image = file_path)
        elif prediction[0] == 8:
            return render_template('result_classification.html', data=["Tomato_mosaic_virus"],user_image = file_path)
        else:
            return render_template('result_classification.html', data=["Healthy"],user_image = file_path)

# ------------------------- Recomnadation system ------------------------------------------------

@app.route('/recommendation')
def recommendation():
    return render_template('recommendation_system.html')

@app.route('/crop_recommendation' , methods = ['POST','GET'])
def crop_recommendation():
    if request.method == 'POST':
        try:
            Nitrogen = float(request.form['nitrogen_level'])
            Phosphorus = float(request.form['phosphorus_level'])
            Potassium = float(request.form['pottasium_level'])
            temperature =float(request.form['temperature'])
            humidity =float(request.form['humidity'])
            ph =float(request.form['ph_level'])
            rainfall =float(request.form['rain_fall'])
            print(Nitrogen,Phosphorus,Potassium,temperature,humidity,ph,rainfall)
            result = Pickled_RF_Model.predict([[Nitrogen,Phosphorus,Potassium,temperature,humidity,ph,rainfall]])
            print(result)
            if result[0] == "rice":
                return render_template('recommendation_system.html', data=["rice",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "maize":
                return render_template('recommendation_system.html', data=["maize",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "chickpea":
                return render_template('recommendation_system.html', data=["chickpea",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "kidneybeans":
                return render_template('recommendation_system.html', data=["kidneybeans",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "pigeonpeas":
                return render_template('recommendation_system.html', data=["pigeonpeas",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "mothbeans":
                return render_template('recommendation_system.html', data=["mothbeans",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "mungbean":
                return render_template('recommendation_system.html', data=["mungbean",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "blackgram":
                return render_template('recommendation_system.html', data=["blackgram",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "lentil":
                return render_template('recommendation_system.html', data=["lentil",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "pomegranate":
                return render_template('recommendation_system.html', data=["pomegranate",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "banana":
                return render_template('recommendation_system.html', data=["banana",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "mango":
                return render_template('recommendation_system.html', data=["mango",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "grapes":
                return render_template('recommendation_system.html', data=["grapes",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "watermelon":
                return render_template('recommendation_system.html', data=["watermelon",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "muskmelon":
                return render_template('recommendation_system.html', data=["muskmelon",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "apple":
                return render_template('recommendation_system.html', data=["apple",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "orange":
                return render_template('recommendation_system.html', data=["orange",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "papaya":
                return render_template('recommendation_system.html', data=["papaya",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "coconut":
                return render_template('recommendation_system.html', data=["coconut",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "cotton":
                return render_template('recommendation_system.html', data=["cotton",'It would be best for you to take the following crop based on the information you have provided'])
            elif result[0] == "jute":
                return render_template('recommendation_system.html', data=["jute",'It would be best for you to take the following crop based on the information you have provided'])
            else:
                return render_template('recommendation_system.html', data=['coffee','It would be best for you to take the following crop based on the information you have provided'])
        except:
            render_template("error.html")
    else :
        return render_template('recommendation_system.html')

#----------------------- scrap Daily prices ---------------------------------------------------#
@app.route('/scrap_daily_prices')
def scrapDailyPrices():
    output= scrapeData()
    return output
    # return render_template('classification_potato.html')

#----------------- weather forcasting ---------------------------------------------
@app.route('/weather_forcasting')
def weather_forcasting():
    return render_template('weather_forcasting.html')

@app.route('/weather_forcasting_result', methods=['POST', 'GET'])
def weather_forcasting_result():
    if request.method == 'POST':
        location = request.form
        graphJSON1,graphJSON2,graphJSON3,title= weather_forcast(location,w)
        return render_template('weather_forcast_result.html', graphJSON=[graphJSON1,graphJSON2,graphJSON3], header=title)
    else:
        return render_template("error.html")

# ----------------------mandi price forcasting-------------------------------

@app.route('/mandi_price_forcasting')
def mandi_price_forcasting():
    return render_template('mandi_price_forcasting.html')

@app.route('/commodity_price_forcasting', methods = ['POST','GET'])
def commodity_price_forcasting():
    if request.method == 'POST':
        commodity = request.form['commodity']
        if commodity == "Arhar":
            graphJSON, minimun_price, maximum_price,ed = arhar_price_forcasting()
            return render_template('commodity_price_forcasting.html', graphJSON=graphJSON, minimun_price=minimun_price,
                                   maximum_price=maximum_price,ed=ed)
        elif commodity == "Bajra":
            graphJSON, minimun_price, maximum_price,ed = bajra_price_forcasting()
            return render_template('commodity_price_forcasting.html', graphJSON=graphJSON,minimun_price=minimun_price,maximum_price=maximum_price,ed=ed)
        elif commodity == "Green Banana":
            graphJSON, minimun_price, maximum_price,ed = greenBanana_price_forcasting()
            return render_template('commodity_price_forcasting.html', graphJSON=graphJSON, minimun_price=minimun_price,
                                   maximum_price=maximum_price,ed=ed)
        elif commodity == "Bhindi":
            graphJSON, minimun_price, maximum_price,ed = bhendi_price_forcasting()
            return render_template('commodity_price_forcasting.html', graphJSON=graphJSON, minimun_price=minimun_price,
                                   maximum_price=maximum_price,ed=ed)
        elif commodity == "Cabbage":
            graphJSON, minimun_price, maximum_price,ed = cabbage_price_forcasting()
            return render_template('commodity_price_forcasting.html', graphJSON=graphJSON, minimun_price=minimun_price,
                                   maximum_price=maximum_price,ed=ed)
        elif commodity == "Brinjal":
            graphJSON, minimun_price, maximum_price,ed = brinjal_price_forcasting()
            return render_template('commodity_price_forcasting.html', graphJSON=graphJSON, minimun_price=minimun_price,
                                   maximum_price=maximum_price)
        elif commodity == "chanadal":
            graphJSON, minimun_price, maximum_price,ed = chanadal_price_forcasting()
            return render_template('commodity_price_forcasting.html', graphJSON=graphJSON, minimun_price=minimun_price,
                                   maximum_price=maximum_price,ed=ed)

if __name__ == "__main__":
    app.run()
