#!/home/pi/env/bin/python

import board
import displayio
import terminalio
import i2cdisplaybus
from adafruit_display_text import label
import adafruit_ssd1327
from PIL import Image, ImageDraw
from DevensWeather import DevensWeather

WIDTH = 128
HEIGHT = 128
BORDER = 8
FONTSCALE = 1

COLOR=0xFFFFFF

class OledDisplay:

    def __init__(self):
        displayio.release_displays()

        i2c = board.I2C()
        display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3D)
        self.display = adafruit_ssd1327.SSD1327(display_bus, width=WIDTH, height=HEIGHT)

        self.root = displayio.Group()
        self.display.root_group = self.root

        self.dw = DevensWeather()

        #txt group
        self.txt_group = displayio.Group(y=90)
        self.txt_group.scale = 1
        
        #temp label
        self.temp_label = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=0
        )
        self.txt_group.append(self.temp_label)

        #short forecast
        self.forecast_label = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=10
        )
        self.txt_group.append(self.forecast_label)

        #precip forecast
        self.precip_label = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=30
        )
        self.txt_group.append(self.precip_label)

        self.w_icon_group = displayio.Group()
        self.w_icon_group.y = 0

        self.w_icon_width = 130
        self.w_icon_height = 130
        self.w_icon_colors = 4
        self.w_icon_bitmap = displayio.Bitmap(self.w_icon_width, self.w_icon_height, self.w_icon_colors)

        self.w_icon_palette = displayio.Palette(self.w_icon_colors)
        for i in range(self.w_icon_colors):
            gray = int(i * 255 / (self.w_icon_colors - 1)) if self.w_icon_colors > 1 else 255
            self.w_icon_palette[i] = (gray << 16) | (gray << 8) | gray

        self.w_icon_tilegrid = displayio.TileGrid(
            self.w_icon_bitmap,
            pixel_shader=self.w_icon_palette,
            x=0,
            y=-40,
        )
        self.w_icon_group.append(self.w_icon_tilegrid)

        # Determines group order, later groups render on top
        self.root.append(self.w_icon_group)
        self.root.append(self.txt_group)

    def update_current_weather(self):
        wx = self.dw.get_current_weather()
        self.current_wx = wx

        icon_code = wx["weather"][0]["icon"]
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

        self.update_w_icon(icon_url)

        self.update_temp(
            f"{wx['main']['temp']:.01f}, [{wx['main']['temp_min']:.01f} - {wx['main']['temp_max']:.01f}] F"
        )
        self.update_forecast(wx["weather"][0]["description"])
        gust = wx["wind"].get("gust", 0)
        self.update_precip(
            f"{wx['wind']['speed']}, [{gust} gusts] mph"
        )

    def update_temp(self, value):
        self.txt_group.hidden = True
        self.temp_label.text = value
        self.txt_group.hidden = False

    def update_forecast(self, value: str):
        self.txt_group.hidden = True
        self.forecast_label.text = value
        self.txt_group.hidden = False

    def update_precip(self, value:str):
        self.txt_group.hidden = True
        self.precip_label.text = value
        self.txt_group.hidden = False

    def update_w_icon(self, icon_url):
        img = self.dw.icon_to_bitmap(
            icon_url,
            self.w_icon_width,
            self.w_icon_height,
            self.w_icon_colors
        )

        pixels = img.load()
        
        self.w_icon_tilegrid.hidden = True

        for y in range(self.w_icon_height):
            for x in range(self.w_icon_width):
                self.w_icon_bitmap[x,y] = pixels[x,y]

        self.w_icon_tilegrid.hidden = False


if __name__ == "__main__":
    d = OledDisplay()
    d.update_current_weather()
    while(1):
        pass
