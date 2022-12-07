import json
import plotly
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
from itertools import cycle
import plotly.express as px
import joblib
import pmdarima as pm
import datetime

def DATA_PREPARATION(maindf,minimum_model,maximum_model,commodity_name):
    maindf = maindf[::-1].reset_index()
    del maindf['index']
    closedf_min = maindf[['Date', 'Min_Price']]
    closedf_max = maindf[['Date', 'Max_Price']]
    date = maindf.iloc[-1][0]
    date=datetime.datetime.strptime(date, '%Y-%m-%d')
    # print(date)
    ed = date.strftime("%a") + ", " + date.strftime("%d") + ' ' + date.strftime("%b")+ ' ' + date.strftime("%Y")
    # print(ed)
    # deleting date column and normalizing using MinMax Scaler
    del closedf_min['Date']
    del closedf_max['Date']
    scaler_min = MinMaxScaler(feature_range=(0, 1))
    closedf_min = scaler_min.fit_transform(np.array(closedf_min).reshape(-1, 1))

    scaler_max = MinMaxScaler(feature_range=(0, 1))
    closedf_max = scaler_max.fit_transform(np.array(closedf_max).reshape(-1, 1))

    n_periods = 15
    time_step = 15
    pred_days = 15
    # Forecast -------------> minimum
    fc_min, confint_min = minimum_model.predict(n_periods=n_periods, return_conf_int=True)

    # Forecast -----------> maximum
    fc_max, confint_max = maximum_model.predict(n_periods=n_periods, return_conf_int=True)
    last_days_min = np.arange(1, time_step + 1)
    last_days_max = np.arange(1, time_step + 1)

    temp_mat_min = np.empty((len(last_days_min) + pred_days + 1, 1))
    temp_mat_min[:] = np.nan
    temp_mat_min = temp_mat_min.reshape(1, -1).tolist()[0]
    temp_mat_max = np.empty((len(last_days_max) + pred_days + 1, 1))
    temp_mat_max[:] = np.nan
    temp_mat_max = temp_mat_max.reshape(1, -1).tolist()[0]

    last_original_days_value_min = temp_mat_min
    next_predicted_days_value_min = temp_mat_min
    last_original_days_value_max = temp_mat_max
    next_predicted_days_value_max = temp_mat_max


def chanadal_price_forcasting():
    maindf = pd.read_csv('static/mandiPrice_data/Chana Dal_Price_Trends.csv')
    minimum_model = joblib.load('static/mandiPrice_models/chana_min.pkl')
    maximum_model = joblib.load('static/mandiPrice_models/chana_max.pkl')
    commodity_name = "Chana Dal"
    graphJSON, minimun_price, maximum_price,ed = DATA_PREPARATION(maindf, minimum_model, maximum_model, commodity_name)
    return graphJSON, minimun_price, maximum_price,ed
