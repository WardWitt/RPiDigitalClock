import pygame
import time
import os
import socket
import configparser
import logging
import datetime
import pygame.gfxdraw


logging.basicConfig(
    level = logging.WARNING,
    filename="RPiDClock.log",
    filemode="w",
    format="%(name)s - %(levelname)s - %(message)s - %(asctime)s",
)

# get our base path
base_dir = os.path.dirname(os.path.realpath(__file__))

# Load configuration
config = configparser.ConfigParser()
config.read(base_dir + "/RPiDClock.ini")

# NTP status
timeStatus = False

counter = 0

# Initialize the pygame class
logging.warning("Start RPiclock")
pygame.display.init()
pygame.font.init()

# Figure out our IP Address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# connect() for UDP doesn't send packets
s.connect(("8.8.8.8", 0))
ipAddress = socket.gethostname() + ' ' + s.getsockname()[0]

bg = pygame.display.set_mode(
    tuple(map(int, config["Display"]["Resolution"].split(",")))
)
pygame.mouse.set_visible(False)
BGimage = pygame.image.load(config["Image"]["Background_Image"])
LogoImage = pygame.image.load(config["Image"]["Logo_Image"])

white = (255, 255, 255, 255)
black = (0, 0, 0, 255)
yellow = (255, 255, 0, 255)

ipTxtColor = tuple(map(int, config["Color"]["IP_Address_Color"].split(",")))
NTP_GoodColor = tuple(map(int, config["Color"]["NTP_Good_Color"].split(",")))
NTP_BadColor = tuple(map(int, config["Color"]["NTP_Bad_Color"].split(",")))

# Scaling to the right size for the clock display
displayHeight = bg.get_height()
displayWidth = bg.get_width()
digiclocksize = int(displayHeight / 1.6)
dotsize = int(displayHeight / 90)

# Coordinates of items on display
xclockpos = int(displayWidth / 2)
ycenter = int(displayHeight / 2)
xcenter = int(displayWidth / 2)

txthmy = int(ycenter)

# Fonts
clockfont = pygame.font.SysFont(None, digiclocksize)
ipFont = pygame.font.SysFont(None, 30)

ipTxt = ipFont.render(ipAddress, True, ipTxtColor)

# Logo position
imageXY = LogoImage.get_rect(
    centerx=xclockpos, centery=ycenter + int(displayHeight * 0.36))

######################### Main program loop. ####################################

clock = pygame.time.Clock()

while True:
    pygame.display.update()

    current_time = datetime.datetime.now()
    string_time = current_time.strftime("%I:%M:%S")

    # Display the logo and background image
    bg.blit(BGimage, [0, 0])
    bg.blit(LogoImage, imageXY)

    # Display IP address
    bg.blit(ipTxt, ipTxt.get_rect())

    # NTP warning flag
    counter += 1
    if counter == 1800:
        chronyc = os.popen("chronyc -c tracking").read().split(",")
        lastTimeUpdate = time.time() - float(chronyc[3])
        if lastTimeUpdate < 4000:
            timeStatus = True
            logging.info("Last valad time update %f seconds ago",
                         lastTimeUpdate)
        else:
            timeStatus = False
            logging.warning(
                "!!! - Last valad time update %f seconds ago - !!!", lastTimeUpdate
            )
        counter = 0

    if timeStatus:
        pygame.gfxdraw.aacircle(
            bg, dotsize + 5, displayHeight - dotsize - 5, dotsize, NTP_GoodColor
        )
        pygame.gfxdraw.filled_circle(
            bg, dotsize + 5, displayHeight - dotsize - 5, dotsize, NTP_GoodColor
        )
    else:
        pygame.gfxdraw.aacircle(
            bg, dotsize + 5, displayHeight - dotsize - 5, dotsize, NTP_BadColor
        )
        pygame.gfxdraw.filled_circle(
            bg, dotsize + 5, displayHeight - dotsize - 5, dotsize, NTP_BadColor
        )

    # Render our digital clock
    digital_clock = clockfont.render(string_time, True, white)
    # Digital clock with a drop shadow
    digital_clock_ds = clockfont.render(string_time, True, black)
    txtposhm = digital_clock.get_rect(centerx=xclockpos, centery=txthmy / 2)

    # Display the normal screen
    # Insert our drop shadow first
    bg.blit(digital_clock_ds, txtposhm.move(+4, +4))
    bg.blit(digital_clock, txtposhm)  # Now add the digital clock

    # # This sets the frame rate
    clock.tick(15)
    # print(clock.get_fps())

    
