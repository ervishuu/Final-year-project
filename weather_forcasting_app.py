import datetime
import pandas as pd
import json
import plotly
import plotly.express as px

def weather_forcast(location,w):
    w.set_location(location.get('location'))
    try:
        weather_data = w.get_forecast_data()
        x_axis = []
        y_axis_temp = []
        for i in range(15):
            date = datetime.datetime.now() + datetime.timedelta(days=i)
            x_axis.append(date.strftime("%a") + ", " + date.strftime("%d") + ' ' + date.strftime("%b"))
        for tem in weather_data[1:]:
            y_axis_temp.append(float(tem[1]))

        title = weather_data[0] + ' - ' + weather_data[1][0]
        df = pd.DataFrame({'Date': x_axis, 'Temperature': y_axis_temp})
        fig1 = px.line(df, x="Date", y="Temperature", title=title, width=1000,
                       height=400,
                       color_discrete_sequence=['red'], markers=True, template="plotly_dark").update_layout(
            xaxis_title="Date", yaxis_title="")
        fig1.update_traces(textposition="bottom right", line=dict(width=2), showlegend=True, name='Temperature °C')
        graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        y_axis_humidity = []
        for tem in weather_data[1:]:
            y_axis_humidity.append(float(tem[2]))
        df1 = pd.DataFrame({'Date': x_axis, 'Humidity': y_axis_humidity})
        fig2 = px.line(df1, x="Date", y="Humidity", width=1000, height=400,
                       color_discrete_sequence=['orange'], markers=True, template="plotly_dark")
        fig2.update_traces(textposition="bottom right", line=dict(width=2), showlegend=True, name="Humidity %")
        graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

        y_axis_speed = []
        for tem in weather_data[1:]:
            y_axis_speed.append(float(tem[3]))
        df3 = pd.DataFrame({'Date': x_axis, 'Speed': y_axis_speed})
        fig3 = px.line(df3, x="Date", y="Speed", width=1000, height=400,
                       color_discrete_sequence=['blue'], markers=True, template="plotly_dark")
        fig3.update_traces(textposition="bottom right", line=dict(width=2), showlegend=True, name='Windspeed km/h')
        graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON1,graphJSON2,graphJSON3,title
    except:
        return "someting is wrong"
