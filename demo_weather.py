from machine import Pin, I2C
import time
import network
import urequests as requests
import ssd1306
from dht20 import DHT20
import socket

# Setup for I2C and OLED display
i2c = I2C(0, sda=Pin(12), scl=Pin(13))
dht20 = DHT20(i2c)
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# Connect to Wi-Fi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Waiting for connection...')
        time.sleep(1)
    if wlan.status() != 3:
        raise RuntimeError('Network connection failed')
    else:
        print('Connected')
        status = wlan.ifconfig()
        print('IP address = ' + status[0])

# Your Wi-Fi credentials
ssid = 'Your_SSID'
password = 'Your_PASSWORD'
connect_to_wifi(ssid, password)

# Global city ID (Sapporo)
city_ID = "016010"

# Start a web server to allow city ID selection
def start_server():
    global city_ID
    # Open socket
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print('Server is listening on', addr)

    while True:
        try:
            # Accept a client connection
            cl, addr = s.accept()
            print('Client connected from', addr)

            # Receive the request from the client
            request = cl.recv(1024)
            request = request.decode('utf-8')
            print("Received request:")
            print(request)

            # Extract city ID if provided in the request
            if '/city?city_ID=' in request:
                # Parse the city ID from the request
                params = request.split(' ')[1]
                if '/city?city_ID=' in params:
                    city_ID = params.split('/city?city_ID=')[1].split('&')[0]
                    print("New city ID selected:", city_ID)

            # Fetch weather data and generate HTML response
            weather_data = fetch_weather(city_ID)
            html = create_web_page(weather_data, city_ID)

            # Send full HTTP response to client
            full_response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + html
            cl.send(full_response.encode('utf-8'))
            cl.close()

        except OSError as e:
            cl.close()
            print('Connection closed due to error:', e)

def fetch_weather(city_ID):
    url = "https://weather.tsukumijima.net/api/forecast/city/" + city_ID
    response = requests.get(url)
    return response.json()

def create_web_page(weather_data, city_ID):
    # Extract data from API response
    rain_probability = weather_data['forecasts'][0]['chanceOfRain']['T12_18'] or '0'
    temperature = dht20.dht20_temperature()
    humidity = dht20.dht20_humidity()
    
    # Update display
    update_display(rain_probability, temperature, humidity)
    
    # HTML for web interface with JavaScript button click handlers
    html = f"""
    <html>
    <head>
        <title>Weather Station</title>
        <style>
            .city-button {{
                padding: 10px 20px;
                margin: 5px;
                font-size: 16px;
                cursor: pointer;
                border: none;
                border-radius: 5px;
            }}
            .city-button.selected {{
                background-color: #4CAF50;
                color: white;
            }}
            .city-button:not(.selected) {{
                background-color: #f0f0f0;
                color: black;
            }}
        </style>
        <script>
            function selectCity(cityID) {{
                window.location.href = '/city?city_ID=' + cityID;
            }}
            function highlightButton(selectedID) {{
                // Remove selected class from all buttons
                var buttons = document.querySelectorAll('.city-button');
                buttons.forEach(button => button.classList.remove('selected'));
                
                // Add selected class to the clicked button
                document.getElementById(selectedID).classList.add('selected');
            }}
        </script>
    </head>
    <body onload="highlightButton('{city_ID}')">
        <h2>Weather Station</h2>
        <div>
            <button id="016010" class="city-button" onclick="selectCity('016010'); highlightButton('016010');">
                Sapporo
            </button>
            <button id="270000" class="city-button" onclick="selectCity('270000'); highlightButton('270000');">
                Osaka
            </button>
            <button id="130010" class="city-button" onclick="selectCity('130010'); highlightButton('130010');">
                Tokyo
            </button>
        </div>
        <h3>Weather Information</h3>
        <p>Rain Probability: {rain_probability}</p>
        <p>Temperature: {temperature} °C</p>
        <p>Humidity: {humidity} %</p>
    </body>
    </html>
    """
    return html


def update_display(rain_probability, temperature, humidity):
    display.fill(0)
    display.text('Chance of rain:', 5, 2, 1)
    display.text(rain_probability, 5, 18, 1)
    display.text('Temp: ' + str(temperature), 5, 34, 1)
    display.text('Humid: ' + str(humidity), 5, 50, 1)
    display.show()

# Run the server
start_server()
