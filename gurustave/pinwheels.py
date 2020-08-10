#!/usr/bin/env python
# NeoPixel Pinwheels
# Author: Gustave Michel III (gustave@michel.com)
#
# Create "Pinwheels", Spinning wheels of a given color, number of "spokes", spoke width, and direction
# When Spokes of two Pinwheels Intersect, the colors should "blend"

import time
from neopixel import *
import argparse
import random
# LED strip configuration:
LED_COUNT      = 103      # Number of LED pixels.
LED_PIN        = 21      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
with open('/etc/hatchan/bright.txt') as f:
    LED_BRIGHTNESS = int(f.readline().strip())
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

def colorWipe(strip, color, wait_ms=5):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

class PinWheel():
    pixel_colors = [(0,0,0) for i in range(LED_COUNT)]
    # Pixels - the NeoPixel String Object
    # start_pixel - Pixel index to start at; should be lowest index you want, regardless of reverse.
    # length - Length of the pinwheel (pinwheel range will be from start_pixel to start_pixel+length-1)
    # num_spokes - Number of points along the circle to light
    # spoke_width - Number of ADDITIONAL pixels to light behind each spoke, zero results in one light
    # color - Color TUPLE of the Pinwheel's pixels
    # ms_speed - Speed of Pinwheel in ms/movement
    # reverse - Direction of Pinwheel, default False
    def __init__(self, pixels, start_pixel, length, num_spokes, spoke_width, color, ms_speed, reverse = False):
        self.pixels = pixels
        self.start = start_pixel
        self.length = length
        self.spokes = num_spokes
        self.trail = spoke_width
        self.color = color
        self.speed = ms_speed
        self.reverse = reverse

        self.spoke_spacing = float(self.length)/self.spokes

        self.last_time = self.get_time()
        self.last_point = 0
        self.last_points = None

    def or_colors(self, first_color, second_color):
        if type(first_color) is tuple and type(second_color) is tuple:
            return tuple([a | b for a,b in zip(first_color, second_color)])
        elif type(first_color) is int and type(second_color) is int:
            return first_color | second_color
        
        # Wasn't sure the interal setup of the Color class...
        # So I used Tuples

        #default to second color
        return second_color

    # Rounds Down to nearest self.speed unit
    def get_time(self):
        return (int(round(time.time() * 1000)) // self.speed) * self.speed
    
    # (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    # DERP... ranges will always be same length, so its just a shift
    def map_pixel(self, index):
        return int(index + self.start)

    def write_pixel(self, position, color):
        PinWheel.pixel_colors[position] = color
        self.pixels.setPixelColor(position, Color(*color))

    def clear_pixels(self):
        if self.last_points is not None:
            for point in self.last_points:
                self.write_pixel(self.map_pixel(point), (0,0,0))

    def draw_pixels(self):
        if self.last_points is not None:
            for point in self.last_points:
                pixel_color = self.or_colors(PinWheel.pixel_colors[self.map_pixel(point)], self.color)
                self.write_pixel(self.map_pixel(point), pixel_color)
    
    def calc_pixels(self):
        curr_time = self.get_time()
        if curr_time == self.last_time:
            # No change yet, draw current pixels again
            self.draw_pixels()
            return
        
        if not self.reverse:
            curr_point = (self.last_point + 1) % (self.length)
        else:
            curr_point = (self.last_point - 1) % (self.length)

        points = []
        for spoke in range(self.spokes):
            spoke_point = int(round(spoke * self.spoke_spacing + curr_point) % self.length)

            trail_points = []
            for trail_point in range(self.trail+1):
                if not self.reverse:
                    point = spoke_point - trail_point
                    if point < 0:
                        point += self.length
                else:
                    point = (spoke_point + trail_point) % self.length
                trail_points.append(point)
            
            points.extend(trail_points)
        
        self.last_time = curr_time
        self.last_point = curr_point
        self.last_points = points

        self.draw_pixels()



# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        # Make sure all Pixels have been set to a value
        colorWipe(strip, Color(0,0,0), 10)

        pinwheels = [
            PinWheel(pixels, 64, 39, 3, 0, (255,0,0), 150, False),
            PinWheel(pixels, 0, 63, 4, 2, (0,255,0), 75, True),
            PinWheel(pixels, 0, 103, 4, 3, (0,0,255), 100, True)
        ]
        while True:
            # Need to clear the pixels seperatly for the color blending to work
            for pinwheel in pinwheels:
                pinwheel.clear_pixels()
            for pinwheel in pinwheels:
                pinwheel.calc_pixels()
            pixels.show()
            time.sleep(5/1000.0)
    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)
