# import asyncio
# import websockets
# import json
# import random

# # Hàm giả lập dữ liệu nhiệt độ và độ ẩm
# def generate_data():
#     temperature = round(random.uniform(15.0, 30.0), 2)  # Nhiệt độ từ 15 đến 30 độ C
#     humidity = round(random.uniform(30.0, 70.0), 2)     # Độ ẩm từ 30% đến 70%
#     data = {
#         "temperature": temperature,
#         "humidity": humidity
#     }
#     return json.dumps(data)

# # Hàm xử lý kết nối WebSocket
# async def data_server(websocket, path):
#     print("Client connected")  # Thông báo khi có client kết nối
#     try:
#         while True:
#             # Gửi dữ liệu nhiệt độ và độ ẩm giả lập tới client
#             data = generate_data()
#             await websocket.send(data)
#             print(f"Sent: {data}")  # In dữ liệu đã gửi
#             await asyncio.sleep(2)  # Cập nhật mỗi 2 giây
#     except websockets.ConnectionClosed:
#         print("Client disconnected")

# # Khởi chạy WebSocket server
# async def main():
#     print("Starting WebSocket server...")  # Thông báo khi khởi động server
#     async with websockets.serve(data_server, "0.0.0.0", 8765):
#         print("Server listening on ws://0.0.0.0:8765")  # In ra khi server bắt đầu lắng nghe
#         await asyncio.Future()  # Chạy server vô hạn

# # Chạy server
# asyncio.run(main())
# import time
# import socket
# import random

# # Giả lập nhiệt độ, độ ẩm và thời gian hiện tại
# def get_sensor_data():
#     temperature = round(random.uniform(15.0, 30.0), 2)  # Nhiệt độ từ 15 đến 30 độ C
#     humidity = round(random.uniform(30.0, 70.0), 2)     # Độ ẩm từ 30% đến 70%
#     # Giờ chuẩn +9 giờ (giả lập múi giờ Nhật Bản)
#     tm = time.localtime(time.time() + 9 * 60 * 60)
#     tm_display = "{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
#         tm[0], tm[1], tm[2], tm[3], tm[4], tm[5]
#     )
#     return temperature, humidity, tm_display

# # Mẫu HTML để hiển thị dữ liệu
# html_template = """<!DOCTYPE html>
# <html>
# <head> <title>Sensor Data</title> </head>
# <body> 
#     <h1>Sensor Data</h1>
#     <p>IP Address: {ip_address}</p>
#     <p>Temperature: {temperature} °C</p>
#     <p>Humidity: {humidity} %</p>
#     <p>Date and Time: {datetime}</p>
# </body>
# </html>
# """

# # Khởi tạo socket để lắng nghe kết nối HTTP
# addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
# s = socket.socket()
# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# s.bind(addr)
# s.listen(1)
# print('Listening on', addr)

# # Lắng nghe kết nối từ client
# while True:
#     try:
#         cl, addr = s.accept()
#         print('Client connected from', addr)
#         request = cl.recv(1024)
#         print("Request:")
#         print(request)

#         # Lấy dữ liệu cảm biến
#         temperature, humidity, tm_display = get_sensor_data()
#         ip_address = addr[0]

#         # Tạo nội dung HTML với dữ liệu cảm biến
#         response_content = html_template.format(
#             ip_address=ip_address,
#             temperature=temperature,
#             humidity=humidity,
#             datetime=tm_display
#         )

#         # Tạo phản hồi HTTP hoàn chỉnh
#         full_response = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + response_content
#         cl.send(full_response.encode('utf-8'))
#         cl.close()
        
#     except OSError as e:
#         cl.close()
#         print('Connection closed')


import json
import time
import random
import asyncio
import websockets
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

# Hàm giả lập dữ liệu nhiệt độ và độ ẩm
def get_sensor_data():
    temperature = round(random.uniform(15.0, 30.0), 2)  # Nhiệt độ từ 15 đến 30 độ C
    humidity = round(random.uniform(30.0, 70.0), 2)     # Độ ẩm từ 30% đến 70%
    # Lấy thời gian hiện tại
    tm = time.localtime(time.time() + 9 * 60 * 60)
    tm_display = "{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        tm[0], tm[1], tm[2], tm[3], tm[4], tm[5]
    )
    return {
        "temperature": temperature,
        "humidity": humidity,
        "datetime": tm_display
    }

# HTTP server để phục vụ trang HTML
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Trả về trang HTML chứa mã JavaScript kết nối WebSocket
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Sensor Data</title>
            </head>
            <body>
                <h1>Sensor Data (Real-time)</h1>
                <p id="temperature">Temperature: -- °C</p>
                <p id="humidity">Humidity: -- %</p>
                <p id="datetime">Date and Time: --</p>

                <script>
                    // Kết nối tới WebSocket server
                    const socket = new WebSocket("ws://localhost:8765");

                    socket.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        document.getElementById("temperature").innerText = "Temperature: " + data.temperature + " °C";
                        document.getElementById("humidity").innerText = "Humidity: " + data.humidity + " %";
                        document.getElementById("datetime").innerText = "Date and Time: " + data.datetime;
                    };
                </script>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Page not found')

# Chạy HTTP server
def run_http_server():
    httpd = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    print("HTTP server running on http://localhost:8080")
    httpd.serve_forever()

# Chạy WebSocket server để gửi dữ liệu real-time
async def websocket_handler(websocket, path):
    while True:
        data = get_sensor_data()
        await websocket.send(json.dumps(data))
        await asyncio.sleep(2)  # Gửi dữ liệu mỗi 2 giây

async def run_websocket_server():
    async with websockets.serve(websocket_handler, "0.0.0.0", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.Future()  # Chạy vô hạn

# Khởi động cả HTTP server và WebSocket server
if __name__ == "__main__":
    # Chạy HTTP server trên một thread riêng
    http_thread = Thread(target=run_http_server)
    http_thread.start()

    # Chạy WebSocket server với asyncio
    asyncio.run(run_websocket_server())
