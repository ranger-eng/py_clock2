import io
import math
from dataclasses import dataclass
from typing import Optional

import requests
from PIL import Image, ImageOps


@dataclass
class WeatherSnapshot:
    short_forecast: str
    precip_probability: Optional[int]
    temperature_f: float
    icon_code: str
    icon_url: str


class DevensWeather:
    """
    Current-weather printer for Devens, MA using OpenWeather.
    Downloads the weather icon and renders it as ASCII art.
    """
    DEVENS_LAT = 42.5447
    DEVENS_LON = -71.6132

    def __init__(self, user_agent: str = "devens-weather-ascii/1.0"):
        self.api_key = "2a3ad76e8924625c08d3856cbe687f08"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.params = {
            "lat": self.DEVENS_LAT,
            "lon": self.DEVENS_LON,
            "appid": self.api_key,
            "units": "imperial"
        }

    def _get_json(self, url: str, params: Optional[dict] = None) -> dict:
        resp = self.session.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _get_bytes(self, url: str) -> bytes:
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        return resp.content

    def get_current_weather(self):
        """Current weather."""
        url = "https://api.openweathermap.org/data/2.5/weather"
        data = self._get_json(url, params=self.params)

        return data

    def get_forecast_weather(self):
        """5 day forecast is 3 hour chunks."""
        url = "https://api.openweathermap.org/data/2.5/forecast"
        data = self._get_json(url, params=self.params)

        return data

    def get_hourly_weather(self):
        """Hourly forecast for 4 days (96 timestamps)."""
        url = "https://api.openweathermap.org/data/2.5/hourly"
        data = self._get_json(url, params=self.params)

        return data

    def get_daily_weather(self):
        """Daily forecast for 16 days."""
        url = "https://api.openweathermap.org/data/2.5/daily"
        data = self._get_json(url, params=self.params)

        return data

    def icon_to_bitmap(
            self, icon_url: str, width: int = 32, height: int = 32, colors: int = 4,
    ) -> Image.Image:
        img_bytes = self._get_bytes(icon_url)

        # Open with Pillow
        img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")

        # Compose transparent pixels onto black
        bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
        img = Image.alpha_composite(bg, img)

        img = img.convert("L")

        # Resize to desired display size
        img = img.resize((width, height), Image.Resampling.LANCZOS)

        img = ImageOps.invert(img)
        img = ImageOps.autocontrast(img)

        # Quantize grayscale image down to N colors
        # Pillow gives us palette indices 0..colors-1
        img = img.quantize(colors=colors)
        
        pixels = img.load()

        return img

    def print_current_weather(self) -> None:
        wx = self.get_current_weather()
        print(self.icon_to_ascii(wx.icon_url))
        print(f"Forecast : {wx.short_forecast}")
        print(
            "Precip   : "
            f"{str(wx.precip_probability) + '%' if wx.precip_probability is not None else 'N/A'}"
        )
        print(f"Temp     : {wx.temperature_f:.1f} F")
        print(f"Icon     : {wx.icon_code}")


if __name__ == "__main__":
    # Replace with your real OpenWeather API key
    weather = DevensOpenWeather()
    weather.print_current_weather()
