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

TXT_X = 0
TXT_Y = 60
TXT_SCALE = 2

TEMP_X = 0
TEMP_Y = 5
TEMP_SCALE = 2

ICON_X = 30
ICON_Y = -40
ICON_SIZE = 130
ICON_COLORS = 4

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
        self.txt_group = displayio.Group(
            x=TXT_X,
            y=TXT_Y
        )
        self.txt_group.scale = TXT_SCALE
        
        #short forecast
        self.forecast_label = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=0
        )
        self.txt_group.append(self.forecast_label)

        #txt group
        self.temp_group = displayio.Group(
            x=TEMP_X,
            y=TEMP_Y
        )
        self.temp_group.scale = TEMP_SCALE
        
        #temp1 label
        self.temp1_label = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=0
        )
        self.temp_group.append(self.temp1_label)
        
        #temp2 label
        self.temp2_label = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=10
        )
        self.temp_group.append(self.temp2_label)

        #icon group
        self.w_icon_group = displayio.Group(
            x=ICON_X,
            y=ICON_Y
        )

        #icon tile grid
        self.w_icon_bitmap = displayio.Bitmap(ICON_SIZE, ICON_SIZE, ICON_COLORS)

        self.w_icon_palette = displayio.Palette(ICON_COLORS)
        for i in range(ICON_COLORS):
            gray = int(i * 255 / (ICON_COLORS - 1)) if ICON_COLORS > 1 else 255
            self.w_icon_palette[i] = (gray << 16) | (gray << 8) | gray

        self.w_icon_tilegrid = displayio.TileGrid(
            self.w_icon_bitmap,
            pixel_shader=self.w_icon_palette,
        )
        self.w_icon_group.append(self.w_icon_tilegrid)

        # Determines group order, later groups render on top
        self.root.append(self.w_icon_group)
        self.root.append(self.txt_group)
        self.root.append(self.temp_group)

    def update_weather(self):
        # current weather
        w_current = self.dw.get_current_weather()
        self.w_current = w_current

        # daily weather
        w_forecast = self.dw.get_forecast_weather()
        self.w_forecast = w_forecast

        # update icon group
        icon_code = w_current["weather"][0]["icon"]
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
        self.update_w_icon(icon_url)

        # update temp group
        self.temp1_label.text = f"{w_current['main']['temp']:.01f} F"
        self.refresh_temp()

        # update txt group
        desc = w_current["weather"][0]["description"]
        multiline = "\n".join(desc.split())
        self.forecast_label.text = multiline
        self.refresh_txt()

    def refresh_temp(self):
        self.temp_group.hidden = True
        self.temp_group.hidden = False

    def refresh_txt(self):
        self.txt_group.hidden = True
        self.txt_group.hidden = False

    def update_w_icon(self, icon_url):
        img = self.dw.icon_to_bitmap(
            icon_url,
            ICON_SIZE,
            ICON_SIZE,
            ICON_COLORS
        )

        pixels = img.load()
        
        self.w_icon_tilegrid.hidden = True

        for y in range(ICON_SIZE):
            for x in range(ICON_SIZE):
                self.w_icon_bitmap[x,y] = pixels[x,y]

        self.w_icon_tilegrid.hidden = False


if __name__ == "__main__":
    d = OledDisplay()
    d.update_current_weather()
    while(1):
        pass
