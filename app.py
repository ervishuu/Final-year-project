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

#----------------------- Model Import -----------------------------------
model_corn =load_model("models/AG_Corn_Plant_VGG19 .h5")
model_cotton =load_model("models/AG_COTTON_plant_VGG19.h5")
model_grape= load_model("models/AI_Grape.h5")
model_potato= load_model("models/AI_Potato_VGG19.h5")
model_tomato= load_model("models/AI_Tomato_model_inception.h5")
Pickled_RF_Model = joblib.load('models/RandomForest.pkl')
# --------------------ChatBot Input File---------------------------------

def IntentLabelMap():
    # Importing dataset and splitting into words and labels
    dataset = pd.read_csv('datasets/intent.csv', names=["Query", "Intent"])
    y = dataset["Intent"]
    labelencoder_intent = LabelEncoder()
    y = labelencoder_intent.fit_transform(y)
    y = np_utils.to_categorical(y)
    res = {}
    for cl in labelencoder_intent.classes_:
        res.update({cl: labelencoder_intent.transform([cl])[0]})
    intent_label_map = res
    return intent_label_map

intent_model = load_model('saved_state/intent_model.h5')
intent_label_map = IntentLabelMap()

# Load Entity model
entity_label_map = pk.load(open('saved_state/entity_model.sav', 'rb'))
loadedEntityCV = pk.load(open('saved_state/EntityCountVectorizer.sav', 'rb'))
loadedEntityClassifier = pk.load(open('saved_state/entity_model.sav', 'rb'))

with open('datasets/intents.json') as json_data:
    intents = json.load(json_data)

# Load model to predict user result
loadedIntentClassifier = load_model('saved_state/intent_model.h5')
loaded_intent_CV = pk.load(open('saved_state/IntentCountVectorizer.sav', 'rb'))
#--------------------------------------------------------------------------------

# ----------------------Admin Routes End---------------------------------------------
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(255), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    sells = db.relationship('Sells', backref='user')

    def __repr__(self) -> str:
        return f"{self.id} - {self.email}"


class Sells(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    first_image = db.Column(db.String(500), nullable=False)
    second_image = db.Column(db.String(500), nullable=False)
    breed_name = db.Column(db.String(255), nullable=False)
    animal_type = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Enquiries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sells_id = db.Column(db.Integer, db.ForeignKey('sells.id'))
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    contact_number = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    message = db.Column(db.String(500), nullable=True)
    status = db.Column(db.Integer, nullable=False, default="submitted")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RatesData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    rate = db.Column(db.String(500), nullable=True)


def checkUserAuthUser():
    access = True
    if session and session['isLoggedIn'] and session['email'] and session['user_type'] == 'user':
        return access
    else:
        access = False
        return access


def checkUserAuthAdmin():
    access = True
    if session and session['isLoggedIn'] and session['email'] and session['user_type'] == 'admin':
        return access
    else:
        access = False
        return access


def userDetails(id):
    data = Users.query.filter_by(id=id).first()
    if data:
        return data
    else:
        return "not found"


def loginUserDetails():
    if session and session['isLoggedIn'] and session['email'] and session['user_type'] == 'user':
        email = session['email']
        data = Users.query.filter_by(email=email).first()
        if data:
            return data
    else:
        return False


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/shop")
def shop():
    loggedinuser = loginUserDetails()
    if loggedinuser:

        sell = Sells.query.filter_by(
            status="accepted").filter(Sells.users_id != loggedinuser.id)

    else:
        sell = Sells.query.filter_by(
            status="accepted")

    return render_template('shop.html', sell=sell)


@app.route("/shopDetails/<int:id>")
def shop_details(id):
    login_user = loginUserDetails()
    if login_user:
        sell = Sells.query.filter_by(id=id).first()
        enquiry = Enquiries.query.filter_by(
            sells_id=id).filter_by(users_id=login_user.id).first()
        if enquiry:
            show = False
        else:
            show = True
        first_image = sell.first_image[9:]
        second_image = sell.second_image[9:]
        return render_template('shopDetails.html', sell=sell, first_image=first_image, second_image=second_image, show=show)
    else:
        return redirect('/login')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        data = Users.query.filter_by(email=email).first()

        if data:
            msg_type = 'warning'
            msg = 'Email is already used'
            return render_template('register.html', msg_type=msg_type, msg=msg)
        else:

            user = Users(email=email, password=password,
                         first_name=first_name, last_name=last_name)
            db.session.add(user)
            db.session.commit()

            msg_type = 'success'
            msg = 'Successfully Registered'
            return render_template('register.html', msg_type=msg_type, msg=msg)

    return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        data = Users.query.filter_by(email=email).first()
        if data and data.password == password:
            session['isLoggedIn'] = True
            session['email'] = data.email
            session['user_type'] = data.user_type

            if data.user_type == 'user':
                return redirect('/')
            else:
                return redirect('/admin')

        else:
            msg_type = 'warning'
            msg = 'wrong username password'

            return "wrong username password"

    if checkUserAuthAdmin():
        return redirect('/admin')
    if checkUserAuthUser():
        return redirect('/')
    return render_template('login.html')


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if checkUserAuthAdmin() or checkUserAuthUser():
        session['isLoggedIn'] = False
        session['user'] = ""
        session['user_type'] = ''
        loginemail = session['email']
        msg_type = 'success'
        msg = 'sucessfully loggedout'
        return render_template('login.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(file):

    # check if the post request has the file part
    try:
        if file not in request.files:
            flash('No file part')
            return redirect('/sell')
        file = request.files[file]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect('/sell')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save = file.save(os.path.join(
                app.config['ANIMALS_SELL_IMAGES'], filename))
            path = os.path.join(app.config['ANIMALS_SELL_IMAGES'], filename)
            return path
    except Exception as e:
        return(str(e))


@app.route('/sell', methods=['GET', 'POST'])
def sell():
    access = checkUserAuthUser()
    if access:
        data = Users.query.filter_by(email=session['email']).first()
        if request.method == 'POST':
            first_path = upload_file('image_first')
            second_path = upload_file('image_second')
            breed_name = request.form['breed_name']
            animal_type = request.form['animal_type']
            age = request.form['age']
            price = request.form['price']

            sell = Sells(users_id=data.id, firlst_image=first_path, second_image=second_path,
                         breed_name=breed_name, animal_type=animal_type, age=age,  price=price)
            db.session.add(sell)
            db.session.commit()

            msg_type = 'success'
            msg = 'Successfully Submitted'

            flash('Successfully Submitted')
            return redirect('/sell')
        all_sells = Sells.query.filter_by(users_id=data.id).all()
        return render_template('sell.html', all_sells=all_sells)
    else:
        return redirect('/login')


@app.route('/enquiries', methods=['GET', 'POST'])
def my_enquiries():
    permission = checkUserAuthUser()
    # print(permission)
    login_Details = loginUserDetails()
    if permission:
        # my_sells_tuple = Sells.query.filter_by(users_id=login_Details.id).all()
        # sells_id_list = [r.id for r in my_sells_tuple]
        # enquiries = Enquiries.query.filter(
        #     Enquiries.sells_id.in_(sells_id_list)).all()

        new = Sells.query.join(Enquiries, Sells.id == Enquiries.sells_id).join(Users, Enquiries.users_id == Users.id).add_columns(Users.first_name, Enquiries.contact_number, Enquiries.address, Enquiries.message,  Enquiries.address, Sells.first_image).filter(
            Sells.users_id == login_Details.id).all()

        # print(new)
        return render_template('enquiries.html', enquiries=new)

    else:
        return redirect('/login')


@app.route('/submit_enquiry', methods=['GET', 'POST'])
def submit_enquiry():
    permission = checkUserAuthUser()

    if permission and request.method == 'POST':

        loginUserDeatails = loginUserDetails()
        users_id = loginUserDeatails.id
        sells_id = request.form['sells_id']
        contact_number = request.form['contact_number']
        address = request.form['address']
        message = request.form['message']
        enquiry = Enquiries(sells_id=sells_id, users_id=users_id,
                            contact_number=contact_number, address=address, message=message)
        db.session.add(enquiry)
        db.session.commit()
        return redirect('/shop')
    else:
        return redirect('/login')

        # ---------------------- Admin Routes Start ----------------------------------------------


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if checkUserAuthAdmin():
        users_list = Users.query.filter_by(user_type='user').count()
        all_sells = Sells.query.count()
        return render_template('admin/index.html', all_sells=all_sells, users_list=users_list)
    return redirect('/login')


@app.route('/users', methods=['GET', 'POST'])
def users_list():
    if checkUserAuthAdmin():
        users_list = Users.query.filter_by(user_type='user').all()
        return render_template('admin/users.html', users_list=users_list)
    else:
        return redirect('/login')


@app.route('/admin_sell', methods=['GET', 'POST'])
def admin_sell():
    if checkUserAuthAdmin():
        # all_sells = Sells.query.all()
        all_sells = Sells.query.join(Users, Sells.users_id == Users.id).add_columns(Users.id.label("user_id"), Users.first_name, Users.last_name, Users.email, Sells.id.label(
            "sell_id"), Sells.first_image, Sells.second_image,  Sells.breed_name, Sells.animal_type, Sells.age, Sells.price, Sells.status).all()
        # print(all_sells)

        return render_template('admin/sell.html', all_sells=all_sells)
    return redirect('/login')


@app.route('/admin_sell_status_change/<string:type>/<int:id>', methods=['GET', 'POST'])
def admin_sell_status_change(type, id):
    if checkUserAuthAdmin():
        sell = Sells.query.filter_by(id=id).first()
        sell.status = type
        db.session.add(sell)
        db.session.commit()
        return redirect('/admin_sell')
    return redirect('/login')


@app.route('/sell_details/<int:id>', methods=['GET', 'POST'])
def sell_details(id):
    if checkUserAuthAdmin():
        # sellDetails = Sells.query.filter_by(id=id).first()

        sellDetails = Sells.query.join(Users, Sells.users_id == Users.id).add_columns(Users.id.label("user_id"), Users.first_name, Users.last_name, Users.email, Sells.id.label(
            "sell_id"), Sells.first_image, Sells.second_image,  Sells.breed_name, Sells.animal_type, Sells.age, Sells.price, Sells.status).filter(
            Sells.id == id).first()

        if sellDetails:
            first_image = sellDetails.first_image[9:]
            second_image = sellDetails.second_image[9:]
        else:
            first_image = ''
            second_image = ''

        return render_template('admin/sell_details.html', sellDetails=sellDetails, first_image=first_image, second_image=second_image)

    return redirect('./login')


@app.route('/user_details/<int:id>', methods=['GET', 'POST'])
def user_details(id):
    if checkUserAuthAdmin():
        userDetails = Users.query.filter_by(id=id).first()
        sellDetails = Sells.query.filter_by(users_id=id)
        enquiryDetails = Enquiries.query.filter_by(users_id=id)
        return render_template('admin/user_details.html', userDetails=userDetails, sellDetails=sellDetails, enquiryDetails=enquiryDetails)

    return redirect('./login')


@app.route('/import_rate_data', methods=['GET', 'POST'])
def import_rate_data():
    if checkUserAuthAdmin():
        connection = sqlite3.connect('artificial_agriculture.db')
        cursor = connection.cursor()

        with open('data.csv', 'r') as file:
            records = 0
            for row in file:
                cursor.execute(
                    "INSERT INTO rates_data VALUES (?,?,?)", row.split(","))
                connection.commit()
                records += 1

        connection.close()
        print('\n Records Transfer Completed'. format(records))
        return redirect('/admin_sell')

    return redirect('/login')


# ----------------------ChatBot start----------------------------------------------

@app.route("/get")
def get_bot_response():
    USER_INTENT = ""
    while True:
        try:
            user_query = request.args.get('msg')
            print(user_query)
            query = re.sub('[^a-zA-Z]', ' ', user_query)
            query = query.split(' ')
            ps = PorterStemmer()
            tokenized_query = [ps.stem(word.lower()) for word in query]
            processed_text = ' '.join(tokenized_query)
            processed_text = loaded_intent_CV.transform([processed_text]).toarray()
            predicted_Intent = loadedIntentClassifier.predict(processed_text)
            result = np.argmax(predicted_Intent, axis=1)
            for key, value in intent_label_map.items():
                if value == result[0]:
                    USER_INTENT = key
                    break
            for i in intents['intents']:
                if i['tag'] == USER_INTENT:
                    responce = random.choice(i['responses'])
                    print("AgroBot: ", responce)
            return str(responce)

        except:
            pass
# ----------------------ChatBot END----------------------------------------------
def load_saved_img():
    global IMG_COUNT
    print(IMG_COUNT)
    img_path = "static/uploaded/classification-{}.jpg".format(IMG_COUNT-1)
    return img_path

#-----------------Prediction Pages --------------------------#
@app.route('/classification_corn')
def classification_corn():
    return render_template('classification_corn.html')

@app.route('/classification_cotton')
def classification_cotton():
    return render_template('classification_cotton.html')

@app.route('/classification_grapes')
def classification_grapes():
    return render_template('classification_grapes.html')

@app.route('/classification_potato')
def classification_potato():
    return render_template('classification_potato.html')

@app.route('/classification_tomato')
def classification_tomato():
    return render_template('classification_tomato.html')

#-----------------result Page --------------------------#
@app.route('/corn_prediction', methods=['POST'])
def corn_prediction():
    global IMG_COUNT
    if request.files['image'].filename == '':
        print('No file was uploaded')
        return render_template('classification_corn.html')
    else:
        img = request.files['image']
        img.save('static/uploaded/classification-{}.jpg'.format(IMG_COUNT))
        img_arr = cv2.imread('static/uploaded/classification-{}.jpg'.format(IMG_COUNT))

        img_arr = cv2.resize(img_arr, (224, 224))
        img_arr = img_arr / 255.0
        img_arr = img_arr.reshape(1, 224, 224, 3)
        predictions = model_corn.predict(img_arr)
        prediction = np.argmax(predictions, axis=1)
        print(prediction[0])
        IMG_COUNT = IMG_COUNT + 1
        file_path = load_saved_img()
        if prediction[0] == 0:
            return render_template('result_classification.html', data=["Blight"],user_image = file_path)
        elif prediction[0] == 1:
            return render_template('result_classification.html', data=["Common_Rust"],user_image = file_path)
        elif prediction[0] == 2:
            return render_template('result_classification.html', data=["Gray_Leaf_Spot"],user_image = file_path)
        else:
            return render_template('result_classification.html', data=["Healthy"],user_image = file_path)

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

        return render_template('mandi_price_forcasting.html')
    else:
        return render_template("error.html")


# ---------------------mandi price ----------------------------

@app.route('/seeds_rate', methods=['GET', 'POST'])
def seeds_rate():
    connection, cursor_mandi = mandidb()
    cursor_mandi.execute("SELECT * from rates_data")
    rows = []
    for row in cursor_mandi:
        rows.append(row)
    cursor_mandi.close()
    return render_template('seeds_rate.html',data = rows)


@app.route('/feachMandiData', methods = ['POST','GET'])
def feachMandiData():
    connection , cursor_mandi = mandidb()
    if request.method == 'POST':
        commodity = request.form['commodity']
        sql="SELECT * FROM rates_data WHERE commidity = '{}'".format(commodity)
        cursor_mandi.execute(sql)
        feachedData = []
        for row in cursor_mandi:
            feachedData.append(row)
    cursor_mandi.close()
    return render_template("scrapped_seeds_rate.html",data = feachedData)

if __name__ == "__main__":
    app.run()
