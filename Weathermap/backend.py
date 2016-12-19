import django_pyowm
from pyowm import OWM
from django_pyowm import models
from django_pyowm import *


def save_city_weather(city_name='Kiev,UA'):
    api_key = '46f37ceccd8eccfe06f6f7d6d9128f50'
    # получаем елемент класса OWM25, с которым будет работать
    owm = OWM(api_key)
    # сохраняем тек погоду и возвращаем
    save_last_weather(owm, city_name)
    last_weather = get_weather()
    # сохраняем прогноз на 14 дней и возвращаем
    save_weather_forecast(owm, city_name)
    last_weather_sect = get_weather(14)
    # формируем прогноз с периодом в 3 часа и формируем список температур
    list_temp = get_temperature_forecast(owm, city_name)
    # формируем словари из нужных нам показателей
    weather_dict = weather_to_dict(last_weather)
    forecast_pressure_dict = weather_qs_to_dict(last_weather_sect)

    return {'last_weather': weather_dict, 'forecast_pressure_dict': forecast_pressure_dict, 'list_temp': list_temp}


def get_temperature_forecast(owm, city_name='Kiev,UA'):
    fc = owm.three_hours_forecast(city_name)
    f = fc.get_forecast()
    list_temp = []
    i = 0
    for weather in f:
        date_w = weather.get_reference_time(timeformat='date')
        date_s = date_w.strftime("%h.%d %H:%M")
        temp = weather.get_temperature(unit='celsius')
        list_temp.append([date_s, temp['temp']])
        i += 1
        if i == 8:
            break
    return list_temp


def weather_qs_to_dict(forecast):
    weather_model = models.Weather
    list_pressure = []

    for w in forecast:
        weather = weather_model.to_entity(w)
        press = weather.get_pressure()
        date_w = weather.get_reference_time(timeformat='date')
        date_s = date_w.strftime("%d.%m.%Y")
        # print(type(date_s))
        list_pressure.append([date_s, press['press']])
    list_pressure = sorted(list_pressure)
    return list_pressure


def weather_to_dict(weather):
    weather = models.Weather.to_entity(weather)
    wind = weather.get_wind()
    temp = weather.get_temperature('celsius')
    pressure = weather.get_pressure()
    cloudy = weather.get_clouds()
    status = weather.get_detailed_status()
    date_w = weather.get_reference_time(timeformat='date')
    date_s = date_w.strftime("%d.%m.%Y")
    weather_dict = {
        'temperature': temp,
        'wind': wind,
        'pressure': pressure,
        'date': date_s,
        'cloudy': cloudy,
        'status': status,
    }
    return weather_dict


def save_weather_forecast(owm, place='Kiev,UA', limit=14):
    if not owm:
        return None
    forecaster = owm.daily_forecast(place, limit)
    fc = forecaster.get_forecast()
    m_forecast = models.Forecast.from_entity(fc)
    weather_class = models.Weather
    for w in fc.get_weathers():
        wobj = weather_class.from_entity(w)
        wobj.save()


def save_last_weather(owm, place='Kiev,UA'):
    if not owm:
        return None

    obs = owm.weather_at_place(place)
    m = models.Observation.from_entity(obs)
    m.weather.save()


def get_weather(section=None):
    model_weath = models.Weather
    if section:
        w = model_weath.objects.order_by("-id")[0:section]
    else:
        w = model_weath.objects.last()
    return w
