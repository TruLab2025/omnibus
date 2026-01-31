from parser import parse_price
import json

url = "https://www.euro.com.pl/telewizory-led-lcd-plazmowe/lg-telewizor-oled77b56la.bhtml"
print(f"Testing URL: {url}")
result = parse_price(url)
print(json.dumps(result, indent=2))
