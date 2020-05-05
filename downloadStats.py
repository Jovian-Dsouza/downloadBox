
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

import requests
import json
from time import sleep

###########################Settings#########################################

#Enter Pyload username and password
username = "admin"
password = "admin"

############################################################################


parameters = {"username": username, "password": password}
response = requests.post("http://127.0.0.1:8000/api/login", parameters)
session_id = response.content.decode("utf-8").replace('"','').replace("'","")
if(session_id == 'False'):
    print("Could not login! Enter correct Pyload username and password in the python file")
parameters = {"session" : session_id}


# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Beaglebone Black pin configuration:
# RST = 'P9_12'
# Note the following are only used with SPI:
# DC = 'P9_15'
# SPI_PORT = 1
# SPI_DEVICE = 0

# 128x32 display with hardware I2C:
#disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
#disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Note you can change the I2C address by passing an i2c_address parameter like:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

# Alternatively you can specify an explicit I2C bus number, for example
# with the 128x32 display you would use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)

# 128x32 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# 128x64 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# Alternatively you can specify a software SPI implementation by providing
# digital GPIO pin numbers for all the required display pins.  For example
# on a Raspberry Pi with the 128x32 display you might use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, sclk=18, din=25, cs=22)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = 0
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)

while True:

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    response = requests.post("http://127.0.0.1:8000/api/statusDownloads", parameters)
    downloadData = response.json()

    response = requests.post("http://127.0.0.1:8000/api/statusServer", parameters)
    statusServer = response.json()
    
    size = 0
    bleft = 0
    percent = 0.0
    speed = 0.0

    for d in downloadData:
        size += d['size']
        bleft += d['bleft']

    if(size != 0):
        percent = (1 - bleft/size) * 100
    
    speed = statusServer['speed']
    if(speed < 1024):
        speedtxt = str(round(speed,2)) + " B/s"
    elif(1024 <= speed and speed < 1048576):
        speedtxt = str(round(speed/1024,2)) + " KiB/s"
    else:
        speedtxt = str(round(speed/1048576,2)) + " MiB/s"

    cmd = "iwgetid -r"
    ssid = str(subprocess.check_output(cmd, shell = True)).replace("b'","").replace("\\n'",'')

    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
    Disk = str(subprocess.check_output(cmd, shell = True )).replace("b'","").replace("\\n'",'')

    cmd = "hostname -I | cut -d\' \' -f1"
    IP = str(subprocess.check_output(cmd, shell = True )).replace("b'","").replace("\\n'",'')

    # Write two lines of text.
    draw.text((x,top), ssid, font=font, fill=255)
    draw.text((x,top+15), "Percent : " + str(round(percent,2)) + "%", font=font, fill=255)
    draw.text((x,top+25), "Speed : " + speedtxt, font=font, fill=255)
    draw.text((x, top+35),       "IP: " + IP,  font=font, fill=255)
    draw.text((x, top+45),    Disk,  font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(1)
