cities = [
    {"id": 1, "name": "Tokyo", "temperature": "22°C", "humidity": "60%"},
    {"id": 2, "name": "Osaka", "temperature": "24°C", "humidity": "55%"},
    {"id": 3, "name": "Kyoto", "temperature": "21°C", "humidity": "58%"},
    {"id": 4, "name": "Fukuoka", "temperature": "23°C", "humidity": "63%"},
    {"id": 5, "name": "Sapporo", "temperature": "18°C", "humidity": "65%"}
]

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>City Weather Details</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .details { margin-top: 20px; }
        label, select { font-size: 1.2em; }
        .city-info { font-size: 1.1em; margin-top: 10px; }
    </style>
    <script>
        function showCityDetails() {
            const cityData = {
"""

# JavaScript city data initialization
for city in cities:
    html_content += f'"{city["id"]}": {{"temperature": "{city["temperature"]}", "humidity": "{city["humidity"]}"}},\n'

html_content += """
            };
            const selectedCity = document.getElementById("citySelect").value;
            const cityInfo = cityData[selectedCity];

            if (cityInfo) {
                document.getElementById("temperature").innerText = "Temperature: " + cityInfo.temperature;
                document.getElementById("humidity").innerText = "Humidity: " + cityInfo.humidity;
            } else {
                document.getElementById("temperature").innerText = "";
                document.getElementById("humidity").innerText = "";
            }
        }
    </script>
</head>
<body>

    <h1>Select a City to View Weather Details</h1>
    <label for="citySelect">Choose a city:</label>
    <select id="citySelect" onchange="showCityDetails()">
        <option value="">--Select a city--</option>
"""

# Adding cities to the dropdown
for city in cities:
    html_content += f'<option value="{city["id"]}">{city["name"]}</option>\n'

html_content += """
    </select>

    <div class="details">
        <div id="temperature" class="city-info"></div>
        <div id="humidity" class="city-info"></div>
    </div>

</body>
</html>
"""

# Save HTML to a file
with open("city_weather.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTML file 'city_weather.html' has been generated.")
