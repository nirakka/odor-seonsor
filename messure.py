# coding: utf-8

import spidev
import RPi.GPIO as GPIO
import time
import sqlite3
import datetime
from fluent import sender
threshold = 500 #閾値を変えるときはここを変更

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)

spi = spidev.SpiDev()

spi.open(0,0)

spi.max_speed_hz=1000000

spi.bits_per_word=8

dummy = 0xff
start = 0x47
sgl = 0x20

ch0 = 0x00

msbf = 0x08
dbname = "/home/pi/test.db"
dbtable = "odor"



def measure(ch):
    ad = spi.xfer2( [ (start + sgl + ch + msbf), dummy ] )
    val = ((ad[0] & 0x03) << 8) + ad[1]
    return val

try:

    logger = sender.FluentSender('sqlite3')
    max_value = 0
     
    while 1:
        time.sleep(0.237)

        GPIO.output(22,True)
        time.sleep(0.003)

        ch0_val = measure(ch0)
        Val = 1023 - ch0_val
        if max_value < Val:
            max_value = Val
        time.sleep(0.002)
        GPIO.output(22,False)
        
        GPIO.output(17,True)
        time.sleep(0.008)
        GPIO.output(17,False)
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.emit('odor', {'cur_time':cur_time,'odor':Val})
        
        print(cur_time, Val)

        if Val > threshold:
            print("kussa")

except KeyboardInterrupt:
    print(max_value) 
    pass

spi.close()
