from setuptools import setup, find_packages

setup(
    name='dashingWeather',
    version='1.0.0',
    author='Mohammad Hamdan',
    author_email='mohammad.hamdan@student.uva.nl',
    description='dashingWeather is an up and coming weather app built using Dash for Python.'
                'The allows the user to access weather data from every city in the world. '
                'All they need to do is type a city name and they are instantenously '
                'shown a plethora of weather information: the current conditions'
                'in real time, the temperature and rain forecasts for the next five days, '
                'and the forecast for tomorrows weather. They are also presented with a'
                'colourful world map which has the capability to display various informative'
                'metrics about the weather today.',
    packages=['dashingWeather'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=[],  # Add any dependencies your package requires
)
