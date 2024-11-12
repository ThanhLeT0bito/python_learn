import time
import network
import ntptime
import socket

# from machine import I2C, Pin
# import ssd1306
# from dht20 import DHT20

#Wi-FiのSSIDとパスワードを入力 
ssid = 'joho'
password = 'Np7chi85'

# HTML
html = """<!DOCTYPE html>
<html>
<head> <title>Pico W</title> </head>
<body> <h1>Pico W HTTP Server</h1>
<p>Hello, World!</p>
<p>%s</p>
</body>
</html>
"""

# Wi-Fi設定 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('接続待ち...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('ネットワーク接続失敗')
else:
    print('接続完了')
    status = wlan.ifconfig()
    ipAddress = status[0]
    print( 'IPアドレス = ' + ipAddress )

# NTPサーバーとして"ntp.nict.jp"を指定
ntptime.host = "ntp.nict.jp"

# 時間の同期を試みる
try:
    # NTPサーバーから取得した時刻でPico WのRTCを同期
    ntptime.settime()
except:
    print("時間の同期に失敗しました。")
    raise

# 世界標準時に9時間加算し日本時間を算出
tm = time.localtime(time.time() + 9 * 60 * 60)
# 現在の日付と時刻を「月/日 時:分:秒」の形式で表示
tm_display = "02-11-2024" #"{1:02d}/{2:02d} {3:02d}:{4:02d}:{5:02d}".format(tm[0], tm[1], tm[2], tm[3], tm[4], tm[5])

# I2C 設定
#i2c = I2C(0, scl=Pin(13), sda=Pin(12))

#dht20 = DHT20(i2c)
#display = ssd1306.SSD1306_I2C(128, 64, i2c)

# 温度と湿度
temperature = 30 #dht20.dht20_temperature()
humidity = 28 #dht20.dht20_humidity()

# シェルに表示
print("温度 : " + str(temperature))
print("湿度 : " + str(humidity))
print("時刻 : " + tm_display)


# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
s.bind(addr)
s.listen(1)
print('listening on', addr)

def fetch_weather(city_ID):
    url = "https://weather.tsukumijima.net/api/forecast/city/" + city_ID
    response = requests.get(url)
    return response.json()

def create_web_page(weather_data, city_ID):
    # Extract data from API response
    rain_probability = weather_data['forecasts'][0]['chanceOfRain']['T12_18']
    # temperature = dht20.dht20_temperature()
    # humidity = dht20.dht20_humidity()
    
    # Update display
    #update_display(rain_probability, temperature, humidity)
    
    # HTML for web interface
    html = f"""
    <html>
    <head>
        <title>Weather Station</title>
    </head>
    <body>
        <h2>Weather Station</h2>
        <form action="/city">
            <label for="city_ID">Choose a city:</label>
            <select name="city_ID">
                <option value="016010" {'selected' if city_ID == '016010' else ''}>Sapporo</option>
                <option value="270000" {'selected' if city_ID == '270000' else ''}>Osaka</option>
                <option value="130010" {'selected' if city_ID == '130010' else ''}>Tokyo</option>
            </select>
            <input type="submit" value="Get Weather">
        </form>
        <h3>Weather Information</h3>
        <p>Rain Probability: {rain_probability}</p>
        <p>Temperature: {temperature} °C</p>
        <p>Humidity: {humidity} %</p>
    </body>
    </html>
    """
    return html

# Listen for connections, serve client
while True:
    try:       
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        print("request:")
        print(request)
        request = str(request)


        ##
        if '/city?city_ID=' in request:
                city_ID = request.split('/city?city_ID=')[1].split(' ')[0]
                print("New city ID selected:", city_ID)
            
        weather_data = fetch_weather(city_ID)
        html = create_web_page(weather_data, city_ID)
        
        # Create and send response
#         stateis = f"""
# IP Address: {ipAddress}<br>
# Temperature: {str(temperature)}<br>
# Humidity: {str(humidity)}<br>
# Date and Time: {tm_display}
# """
        # response = html % stateis
        full_response = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + html
        cl.send(full_response)
        cl.close()
        
    except OSError as e:
        cl.close()
        print('connection closed')


# SSD1306 に表示
    display.fill(0)
    display.text('temp:' + str(temperature), 5, 2, 1)
    display.text('humid:' + str(humidity), 5, 18, 1)
    display.text(ipAddress, 5, 34, 1)
    display.text(tm_display, 5, 50, 1)

    display.show()
