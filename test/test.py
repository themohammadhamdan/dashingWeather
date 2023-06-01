import unittest
import requests, json
import numpy as np
import pandas as pd
from datetime import timedelta, datetime

# this is the list of cities used for the test. input is deliberately written in a wonky way to show that the
# function can still properly retrieve the name of the desired city
cities = ["amstErdam", "cAiro", "new york", "lOs angeles", "mOntreal", "agios dimitrios",
          "the haGue", "dar El sAlam", "hibiscus coast", "newcAstle upon tYne"]

# we'll save the sunrise and sunset times on May 29 (testing day) to make test somewhat replicable
sunrise_times = np.load("/Users/mohammadhamdan/PycharmProjects/Programming/sunrise_times.npy",
                        allow_pickle=True)
sunset_times = np.load("/Users/mohammadhamdan/PycharmProjects/Programming/sunset_times.npy",
                        allow_pickle=True)

def city_name_correct(city):
    city = city.lower().replace(" ", "+", 2)
    city_for_title = city.title().replace("+", " ", 2)
    return(city, city_for_title)

def get_coords(city):


    '''
    This function takes `city` as an input and uses the openweathermap API to fetch coordinates (latitude, longitude) of that city
    :param city:
    :return coords:
    '''

    base = 'http://api.openweathermap.org/geo/1.0/direct?q='
    api_key = '&appid=7c385ff223c5c8feec257ad30244934e'
    url = base + city_name_correct(city)[0] + api_key

    response_API = requests.get(url)
    data = response_API.text
    parse_json = json.loads(data)

    coords = dict()
    coords['lat'] = parse_json[0]['lat']
    coords['lon'] = parse_json[0]['lon']

    return(coords)

def no_rain(weather_forecast_list, times):

    '''
    In some cities it does not rain every week, so the fetched data just does not include a rain section.
    Using this function we make sure that when there is no rain section we create rain data where the values are all zeros.

    :param weather_forecast_list:
    :return:
    '''

    try:
        rain_amount = pd.DataFrame(weather_forecast_list)["rain"]
        for i in range(len(times)):
            if type(rain_amount[i]) != dict:
                rain_amount[i] = 0
            else:
                rain_amount[i] = rain_amount[i]['3h']
    except:
        rain_amount = np.zeros(len(times))

    return(rain_amount)

def get_current_weather(coords, unit):


    '''
    This function takes `coords` and `unit` as inputs and uses the openweathermap API to fetch the current weather
    :param coords:
    :param unit:
    :return current_weather:
    '''


    # getting current weather information from coordinates
    base = "https://api.openweathermap.org/data/2.5/weather?"
    lat = "lat=" + str(coords['lat'])
    lon = "&lon=" + str(coords['lon'])
    units = "&units=" + unit
    api_key = "&appid=7c385ff223c5c8feec257ad30244934e"
    url = str(base + lat + lon + units + api_key)

    response_API = requests.get(url)
    data = response_API.text
    current_weather = json.loads(data)

    return(current_weather)


def get_weather_forecast(coords, unit):

    '''
    This function fetches the temperature and rain forecast for the next five days
    :param coords:
    :param unit:
    :return weather_forecast:
    '''

    # getting forecast data
    base = 'https://api.openweathermap.org/data/2.5/forecast?'
    lat = "lat=" + str(coords['lat'])
    lon = "&lon=" + str(coords['lon'])
    units = "&units=" + unit
    api_key = "&appid=7c385ff223c5c8feec257ad30244934e"
    url = str(base + lat + lon + units + api_key)

    response_API = requests.get(url)
    data = response_API.text
    weather_forecast = json.loads(data)

    return(weather_forecast)

for city in cities:

    class MyTestCase(unittest.TestCase):

        '''
        in these tests we check whether our input conversion, geolocator and rain checker functions work
        1. when a user inputs a city name (e.g., "new york"), it needs to be converted into a plotting format
        ("New York"), and a url format ("new+york").
        2. weather retrieval can only be done using coordinates, but users will input city names, so we need
        to check that our coordinate retrieval works
        3. when fetching rain data, if it will not rain in the 5 day forecast, the API call does not return anything.
        however this is a problem when plotting this data, so we test our function that then generates an array with
        0 values which can be used for plotting.
        4. we retrieve data in a datetime format, then convert it to string for plotting, so for each city
        we check where the year and month after manipulation correspond to May or June 2023.
        5. we retrieve sunrise/sunset data in a utc format, and when we convert it to a string it's presented in GMT,
        which is *not* the right format universally (e.g., why would we want to see sunrise time in new york in UK
        winter time?) so we have to apply a correction. this test is based on (saved) data from May 29 and tests to see
        if the difference between retrieved data and actual information corresponds to the timezone difference reported
        in the api retrieval. i actually discovered that some data was presented incorrectly using this test :) i was
        using a country-based correction function which meant that for some cities in countries with multiple time zones,
        these times were a few hours off
        '''

        def test_city_names_coords(self):

            test = city_name_correct(city)
            coords = get_coords(city)
            forecast = pd.DataFrame(get_weather_forecast(coords, "metric")["list"])
            times = pd.to_datetime(forecast["dt_txt"])
            rain_amount = no_rain(get_weather_forecast(coords, "metric")["list"], times)
            current_weather = get_current_weather(coords, "metric")

            if city == "amstErdam":
                self.assertEqual(test[0], "amsterdam")
                self.assertEqual(test[1], "Amsterdam")

                self.assertAlmostEqual(coords['lat'], 52.3676, places=1)
                self.assertAlmostEqual(coords['lon'], 4.9041, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"]) # the app will only be used tested in may/june 2023

                self.assertEqual(datetime(2023,5,29,5,26) - sunrise_times[0], timedelta(seconds = current_weather["timezone"]))
                self.assertEqual(datetime(2023,5,29,21,49) - sunset_times[0], timedelta(seconds = current_weather["timezone"]))

            elif city == "cAiro":
                self.assertEqual(test[0], "cairo")
                self.assertEqual(test[1], "Cairo")

                self.assertAlmostEqual(coords['lat'], 30.0444, places=1)
                self.assertAlmostEqual(coords['lon'], 31.2357, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

                self.assertEqual(datetime(2023, 5, 29, 5, 55) - sunrise_times[1], timedelta(seconds = current_weather["timezone"]))
                self.assertEqual(datetime(2023,5,29,21,49) - sunset_times[1], timedelta(seconds = current_weather["timezone"]))

            elif city == "new york":
                self.assertEqual(test[0], "new+york")
                self.assertEqual(test[1], "New York")

                self.assertAlmostEqual(coords['lat'], 40.7128, places=1)
                self.assertAlmostEqual(coords['lon'], -74.0060, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

                self.assertEqual(datetime(2023, 5, 29, 5, 29) - sunrise_times[2], timedelta(seconds = current_weather["timezone"]))
                self.assertEqual(datetime(2023,5,29,20,19) - sunset_times[2], timedelta(seconds = current_weather["timezone"]))

            elif city == "lOs angeles":
                self.assertEqual("los+angeles", test[0])
                self.assertEqual("Los Angeles", test[1])

                self.assertAlmostEqual(coords['lat'], 34.0522, places=1)
                self.assertAlmostEqual(coords['lon'], 118.2437, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

                self.assertEqual(datetime(2023, 5, 29, 5, 44) - sunrise_times[3], timedelta(seconds = current_weather["timezone"]))
                self.assertEqual(datetime(2023,5,29,19,47) - sunset_times[3], timedelta(seconds = current_weather["timezone"]))

            elif city == "mOntreal":
                self.assertEqual("montreal", test[0])
                self.assertEqual("Montreal", test[1])

                self.assertAlmostEqual(coords['lat'], 45.5019, places=1)
                self.assertAlmostEqual(coords['lon'], 73.5674, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

                self.assertEqual(datetime(2023, 5, 29, 5, 11) - sunrise_times[4], timedelta(seconds = current_weather["timezone"]))
                self.assertEqual(datetime(2023,5,29,20,33) - sunset_times[4], timedelta(seconds = current_weather["timezone"]))

            elif city == "agios dimitrios":
                self.assertEqual("agios+dimitrios", test[0])
                self.assertEqual("Agios Dimitrios", test[1])

                self.assertAlmostEqual(coords['lat'], 37.9357, places=1)
                self.assertAlmostEqual(coords['lon'], 23.7295, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

                self.assertEqual(datetime(2023, 5, 29, 6, 5) - sunrise_times[5], timedelta(seconds = current_weather["timezone"]))
                self.assertEqual(datetime(2023,5,29,20,39) - sunset_times[5], timedelta(seconds = current_weather["timezone"]))

            elif city == "the haGue":
                self.assertEqual("the+hague", test[0])
                self.assertEqual("The Hague", test[1])

                self.assertAlmostEqual(coords['lat'], 52.0705, places=1)
                self.assertAlmostEqual(coords['lon'], 4.3007, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

                self.assertEqual(datetime(2023, 5, 29, 5, 30) - sunrise_times[6], timedelta(seconds = current_weather["timezone"]))
                self.assertEqual(datetime(2023,5,29,21,50) - sunset_times[6], timedelta(seconds = current_weather["timezone"]))

            elif city == "dar El sAlam":
                self.assertEqual("dar+el+salam", test[0])
                self.assertEqual("Dar El Salam", test[1])

                self.assertAlmostEqual(coords['lat'], 6.7924, places=1)
                self.assertAlmostEqual(coords['lon'], 39.2083, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

                self.assertEqual(datetime(2023, 5, 29, 6, 28) - sunrise_times[7], timedelta(seconds = current_weather["timezone"]))
                self.assertEqual(datetime(2023,5,29,18,13) - sunset_times[7], timedelta(seconds = current_weather["timezone"]))

            elif city == "hibiscus coast":
                self.assertEqual("hibiscus+coast", test[0])
                self.assertEqual("Hibiscus Coast", test[1])

                self.assertAlmostEqual(coords['lat'], -36.6058, places=1)
                self.assertAlmostEqual(coords['lon'], 174.6978, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

                self.assertEqual(datetime(2023, 5, 29, 7, 22) - sunrise_times[8], timedelta(seconds = current_weather["timezone"]))
                self.assertEqual(datetime(2023,5,29,17,13) - sunset_times[8], timedelta(seconds = current_weather["timezone"]))

            elif city == "newcAstle upon tYne":
                self.assertEqual("newcastle+upon+tyne", test[0])
                self.assertEqual("Newcastle Upon Tyne", test[1])

                self.assertAlmostEqual(coords['lat'], 54.9783, places=1)
                self.assertAlmostEqual(coords['lon'], -1.6178, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

                self.assertEqual(datetime(2023, 5, 29, 4, 41, 10) - sunrise_times[9], timedelta(seconds = current_weather["timezone"]))
                self.assertEqual(datetime(2023,5,29,21,28, 57) - sunset_times[9], timedelta(seconds = current_weather["timezone"]))

if __name__ == '__main__':
    unittest.main()
