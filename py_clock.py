import time
from datetime import datetime
import board
import subprocess
from adafruit_ht16k33.segments import BigSeg7x4
from oled_display import OledDisplay

# Initialize I2C and display 
i2c = board.I2C() 
display = BigSeg7x4(i2c, address=0x70, auto_write=False) 
display.brightness = 0.0 
display.blink_rate = 0  # turn off hardware blink 

def blink_bottom_left(display, mod): 
    now = time.localtime() 
    if (now.tm_sec % mod) == 0: 
        display.bottom_left_dot = True 
    else: 
        display.bottom_left_dot = False

def rtc_time() -> time.struct_time:
    # Read Linux RTC device via hwclock
    result = subprocess.run(
        ["sudo", "hwclock", "-r"],
        capture_output=True,
        text=True,
        check=True,
    )
    s = result.stdout.strip()
    dt = datetime.fromisoformat(s)

    return dt.timetuple()


import subprocess

def ntp_synced():
    result = subprocess.run(
        ["timedatectl", "show", "-p", "NTPSynchronized", "--value"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip() == "yes"

wdisplay = OledDisplay()
last_hour = None

while True:

    if not ntp_synced():
        now = rtc_time()
    else:
        now = time.localtime()
    hour = now.tm_hour
    minute = now.tm_min

    if now.tm_hour != last_hour:
        wdisplay.update_current_weather()
        last_hour = now.tm_hour

    disp_hour = hour

    # 12-hour format
    if hour == 0:
        disp_hour = 12
    elif hour > 12:
        disp_hour -= 12

    # Display as HH:MM
    display.print(f"{disp_hour:02d}:{minute:02d}")

    # pm indicator
    if hour >= 12:
        display.top_left_dot = True
    else:
        display.top_left_dor = False

    # time based brightness
    if hour < 8 or hour >= 19:
        display.brightness = 0.0
    else:
        display.brightness = 0.3

    # ntp status
    if not ntp_synced():
        blink_bottom_left(display, 5)

    display.show()

    time.sleep(.1)
