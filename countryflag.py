import os
import requests
country_code_map = {
    "India": "in",
    "United States": "us",
    "China": "cn",
    "Germany": "de",
    "Australia": "au",
    "Canada": "ca",
    "Japan": "jp",
    "France": "fr",
    "Brazil": "br",
    "Great Britain": "gb",
    "pakistan": "pk",
    "New Zealand": "nz",
    "russia": "ru",
    "Italy": "it",
    "South Korea": "kr",
    "north korea": "kk",
    "Netherlands": "nl",
    "Ukraine": "ua",
    "Norway": "no",
    "Denmark": "dm",
    "Switzerland": "sw",
    "Spain": "sp",
    "Sweden": "se",
    "United Kingdom": "kk",
    "Turkey": "tr",
    "Greece": "gr",
    "Mexico": "mx",
    "Iran": "ia",
    "Iraq": "iaq",
    "Afghanistan": "af",
    "Qatar": "qat"
}

# Create flags folder
os.makedirs("flags", exist_ok=True)

# Download flags
for country, code in country_code_map.items():
    url = f"https://flagcdn.com/w320/{code}.png"
    response = requests.get(url)
    if response.status_code == 200:
        with open(f"flags/{country}.png", "wb") as f:
            f.write(response.content)
        print(f"Downloaded flag for {country}")
    else:
        print(f"Failed to download flag for {country}")
