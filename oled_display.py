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
TXT_Y = 80
TXT_SCALE = 2

TEMP_X = 0
TEMP_Y = 6
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
        self.forecast_label1 = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=0
        )
        self.txt_group.append(self.forecast_label1)

        self.forecast_label2 = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=10
        )
        self.txt_group.append(self.forecast_label2)

        self.forecast_label3 = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=20
        )
        self.txt_group.append(self.forecast_label3)

        #temp group
        self.temp_group = displayio.Group(
            x=TEMP_X,
            y=TEMP_Y
        )
        self.temp_group.scale = 1
        
        #temp1 label
        self.temp1_label = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=0
        )
        self.temp_group.append(self.temp1_label)
        self.temp1_label.scale = 2

        #temp2 label
        self.temp2_label = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=20
        )
        self.temp_group.append(self.temp2_label)

        #temp3 label
        self.temp3_label = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=30
        )
        self.temp_group.append(self.temp3_label)

        #temp4 label
        self.temp4_label = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=40
        )
        self.temp_group.append(self.temp4_label)

        #temp5 label
        self.temp5_label = label.Label(
            terminalio.FONT,
            text="",
            color=COLOR,
            x=0,
            y=50
        )
        self.temp_group.append(self.temp5_label)
        
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

    def update_no_internet(self):
        self.w_icon_group.hidden = True
        self.temp_group.hidden = True
        self.forecast_label1.text = "no"
        self.forecast_label2.text = "internet"
        self.forecast_label3.text = ""
        self.forecast_label4.text = ""

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
        self.temp2_label.text = self.get_24_hr_temp_min(w_forecast)
        self.temp3_label.text = self.get_24_hr_temp_max(w_forecast)
        self.temp4_label.text = self.get_24_hr_rain_str(w_forecast)
        self.temp4_label.text = self.get_wind_str(w_current)
        self.refresh_temp()

        # update txt group
        desc = w_current["weather"][0]["description"]
        words = desc.split()

        self.set_forecast_labels(w_current)
        self.refresh_txt()
   
    def get_wind_str(self, w_current):
        wind = w_current["wind"]["speed"]
        gust = w_current["wind"].get("gust", wind)

        return f"{wind:.0f}; {gust:.0f} mph"

    def set_forecast_labels(self, w_current):
        desc = w_current["weather"][0]["description"]
        words = desc.split()

        # --- Step 1: build lines with max ~10 chars ---
        lines = []
        current = ""

        for word in words:
            if not current:
                current = word
            elif len(current) + 1 + len(word) <= 10:
                current += " " + word
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

        # limit to 4 lines
        lines = lines[:3]

        # --- Step 2: vertical placement logic ---
        # default: top-aligned (line1 → label1, etc)
        offset = 0

        # --- Step 3: assign to labels ---
        labels = [
            self.forecast_label1,
            self.forecast_label2,
            self.forecast_label3,
        ]

        # clear all first
        for lbl in labels:
            lbl.text = ""

        # fill with offset
        for i, line in enumerate(lines):
            if i + offset < len(labels):
                labels[i + offset].text = line

    def get_24_hr_temp_min(self, w_forecast):
        entries = w_forecast["list"][:8]  # 8 × 3h = 24h

        min_temp = min(e["main"]["temp_min"] for e in entries)

        return f"mn:{min_temp:.0f}F"

    def get_24_hr_temp_max(self, w_forecast):
        entries = w_forecast["list"][:8]  # 8 × 3h = 24h

        max_temp = max(e["main"]["temp_max"] for e in entries)

        return f"mx:{max_temp:.0f}F"

    def get_24_hr_rain_str(self, w_forecast):
        entries = w_forecast["list"][:8]  # next 24 hours

        total_r_mm = 0.0
        total_sn_mm = 0.0

        for e in entries:
            total_r_mm += e.get("rain", {}).get("3h", 0.0)
        for e in entries:
            total_sn_mm += e.get("snow", {}).get("3h", 0.0)

        # convert mm → inches
        total_r_in = total_r_mm / 25.4
        total_sn_in = total_sn_mm / 25.4

        if total_r_in == 0 and total_sn_in == 0:
            rain_str = ""
        elif total_r_in > 0 and total_sn_in == 0:
            rain_str = f"rain:{total_r_in:.01f} in"
        elif total_r_in == 0 and total_sn_in > 0:
            rain_str = f"snow:{total_sn_in:.01f} in"
        elif total_r_in > 0 and total_sn_in > 0:
            total_mix_in = total_r_in + total_sn_in
            rain_str = f"mix:{total_mix_in:.01f} in"

        return rain_str

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
