from parser import parse_price
import json

url = "https://www.tophifi.pl/glosniki/glosniki-podstawkowe/bowers-wilkins-606-s3.html"
print(f"Testing TopHiFi URL: {url}")
result = parse_price(url)
print(json.dumps(result, indent=2))
