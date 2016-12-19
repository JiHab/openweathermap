
from django.http import HttpResponse

from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy
from Weathermap import backend
from django.template import loader


def home(request):

    if request.GET:
        city_name = request.GET.get('cityName', '')
        weather_d = backend.save_city_weather(city_name)
    else:
        weather_d = backend.save_city_weather()

    weather = weather_d['last_weather']
    weather_set = weather_d['forecast_pressure_dict']
    temperature = weather_d['list_temp']

    template_gc = loader.get_template("g_charts.html")

    context ={
        'values': weather_set,
        'weather': weather,
        'temp': temperature,
        'csrf_input': csrf_input_lazy(request),
        'csrf_token': csrf_token_lazy(request),
        'city': 'in '+city_name
    }

    # return HttpResponse(template.render(context))
    return HttpResponse(template_gc.render(context))


