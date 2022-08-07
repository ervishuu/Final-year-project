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

    last_original_days_value_min[0:time_step + 1] = \
    scaler_min.inverse_transform(closedf_min[len(closedf_min) - time_step:]).reshape(1, -1).tolist()[0]
    next_predicted_days_value_min[time_step + 1:] = \
    scaler_min.inverse_transform(np.array(fc_min).reshape(-1, 1)).reshape(1, -1).tolist()[0]

    last_original_days_value_max[0:time_step + 1] = \
    scaler_max.inverse_transform(closedf_max[len(closedf_max) - time_step:]).reshape(1, -1).tolist()[0]
    next_predicted_days_value_max[time_step + 1:] = \
    scaler_max.inverse_transform(np.array(fc_max).reshape(-1, 1)).reshape(1, -1).tolist()[0]

    new_pred_plot = pd.DataFrame({
        'last_days_min_value': last_original_days_value_min,
        'predicted_min_value': next_predicted_days_value_min,
        'last_days_max_value': last_original_days_value_max,
        'predicted_max_value': next_predicted_days_value_max
    })
    names = cycle(['Last 15 days Min price', 'Predicted next 15 days Min price', 'Last 15 days max price',
                   'Predicted next 15 days max price'])
    min_point = round(new_pred_plot['predicted_min_value'][15:].min())
    max_point = round(new_pred_plot['predicted_max_value'][15:].max())

    y_axis_min_point = round(new_pred_plot['predicted_min_value'].min())
    y_axis_max_point = round(new_pred_plot['predicted_max_value'].max())

    title ="Compare last 15 days vs next 15 days {} Minimum/Maximum price forcasting".format(commodity_name)
    legend_title = '{} Min/Max Price'.format(commodity_name)
    fig = px.line(new_pred_plot, x=new_pred_plot.index, y=[new_pred_plot['last_days_min_value'],
                                                           new_pred_plot['predicted_min_value'],
                                                           new_pred_plot['last_days_max_value'],
                                                           new_pred_plot['predicted_max_value']],
                  labels={'value': 'price', 'index': 'Timestamp'}, template='plotly_dark', markers=True,width=1000, height=400)
    fig.update_layout(title_text=title,yaxis_range=[y_axis_min_point-1000, y_axis_max_point+2000], font_size=10, font_color='white',
                      legend_title_text=legend_title)
    fig.add_vline(x=15, line_width=3, line_dash="dash", line_color="green")
    fig.add_hrect(y0=int(min_point), y1=int(max_point), line_width=0, fillcolor="red", opacity=0.2)
    fig.for_each_trace(lambda t: t.update(name=next(names)))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON,min_point,max_point,ed

def bajra_price_forcasting():
    maindf = pd.read_csv('static/mandiPrice_data/Bajra_Price_Trends.csv')
    minimum_model = joblib.load('static/mandiPrice_models/bajra_min.pkl')
    maximum_model = joblib.load('static/mandiPrice_models/bajra_max.pkl')
    commodity_name = "Bajra"
    # header = "Compare last 15 days vs next 30 days Bajra Minimum/Maximum price forcasting"
    graphJSON, minimun_price, maximum_price,ed = DATA_PREPARATION(maindf, minimum_model, maximum_model, commodity_name)
    return graphJSON, minimun_price, maximum_price,ed

def arhar_price_forcasting():
    maindf = pd.read_csv('static/mandiPrice_data/Arhar_Dal_TurDal.csv')
    minimum_model = joblib.load('static/mandiPrice_models/arhar_min.pkl')
    maximum_model = joblib.load('static/mandiPrice_models/arhar_max.pkl')
    commodity_name = "Arhar"
    graphJSON, minimun_price, maximum_price,ed = DATA_PREPARATION(maindf, minimum_model, maximum_model, commodity_name)
    return graphJSON, minimun_price, maximum_price,ed

def greenBanana_price_forcasting():
    maindf = pd.read_csv('static/mandiPrice_data/Banana _Green_Price_Trends.csv')
    minimum_model = joblib.load('static/mandiPrice_models/banana_min.pkl')
    maximum_model = joblib.load('static/mandiPrice_models/banana_max.pkl')
    commodity_name = "Green Banana"
    graphJSON, minimun_price, maximum_price,ed = DATA_PREPARATION(maindf, minimum_model, maximum_model, commodity_name)
    return graphJSON, minimun_price, maximum_price,ed

def bhendi_price_forcasting():
    maindf = pd.read_csv('static/mandiPrice_data/Bhindi_Ladies_Finger_ Price_Trends.csv')
    minimum_model = joblib.load('static/mandiPrice_models/bhendi_min.pkl')
    maximum_model = joblib.load('static/mandiPrice_models/bhendi_max.pkl')
    commodity_name = "Bhindi (Ladies Finger)"
    graphJSON, minimun_price, maximum_price,ed = DATA_PREPARATION(maindf, minimum_model, maximum_model, commodity_name)
    return graphJSON, minimun_price, maximum_price,ed

def cabbage_price_forcasting():
    maindf = pd.read_csv('static/mandiPrice_data/Cabbage_Price_Trends.csv')
    minimum_model = joblib.load('static/mandiPrice_models/cabbage_min.pkl')
    maximum_model = joblib.load('static/mandiPrice_models/cabbage_max.pkl')
    commodity_name = "Cabbage"
    graphJSON, minimun_price, maximum_price,ed = DATA_PREPARATION(maindf, minimum_model, maximum_model, commodity_name)
    return graphJSON, minimun_price, maximum_price,ed

def brinjal_price_forcasting():
    maindf = pd.read_csv('static/mandiPrice_data/Brinjal_Price_Trends.csv')
    minimum_model = joblib.load('static/mandiPrice_models/brinjal_min.pkl')
    maximum_model = joblib.load('static/mandiPrice_models/brijal_max.pkl')
    commodity_name = "Brinjal"
    graphJSON, minimun_price, maximum_price,ed = DATA_PREPARATION(maindf, minimum_model, maximum_model, commodity_name)
    return graphJSON, minimun_price, maximum_price,ed

def chanadal_price_forcasting():
    maindf = pd.read_csv('static/mandiPrice_data/Chana Dal_Price_Trends.csv')
    minimum_model = joblib.load('static/mandiPrice_models/chana_min.pkl')
    maximum_model = joblib.load('static/mandiPrice_models/chana_max.pkl')
    commodity_name = "Chana Dal"
    graphJSON, minimun_price, maximum_price,ed = DATA_PREPARATION(maindf, minimum_model, maximum_model, commodity_name)
    return graphJSON, minimun_price, maximum_price,ed
