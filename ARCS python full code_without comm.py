import serial
import time
import RPi.GPIO as GPIO
import sys
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1306 ##, ssd1325, ssd1331, sh1106
from time import sleep
from hx711 import HX711
from socket import *
from PIL import Image, ImageDraw, ImageFont
import os

class QRCode_reader:
    def __init__(self):
        self.ser = serial.Serial("/dev/ttyAMA0",
                    baudrate = 9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1
                    )
    def read(self):
        self.rsv = str(self.ser.readline())
        self.qrcode = self.rsv[0:-1]
        self.rsv_hex = self.rsv.encode("utf-8")
        self.ter = self.rsv_hex[-2:]

    def closeser(self):
        self.ser.close()

    def openser(self):
        self.ser.open()

class id_check:
    def __init__(self):
        pass

    def verify(self):
        if QR.qrcode == 'wxp://f2f0zuxxgJFzeF4GzXExe47MqSZ9egDOvGX':
            return True
        else:
            return False

class oled:
    def __init__(self):
        self.serial = spi(device=0, port=0)
        self.device = ssd1306(self.serial)
        self.font = ImageFont.truetype("ukai.ttc",16)
        

    def display(self, msg, msg2):
        self.msg = msg
        self.msg2 = msg2
        with canvas(self.device) as self.draw:
            self.draw.rectangle(self.device.bounding_box, outline="white", fill="black")
            self.draw.text((30, 15), msg.decode("UTF-8"), fill="white", font=self.font)
            self.draw.text((20, 40), msg2.decode("UTF-8"), fill="white")


class actuator:
    def __init__(self):
        self.gpio = GPIO
        self.gpio.setmode(GPIO.BCM)

        self.dlpin1 = 4
        self.dlpin2 = 17
        self.drpin1 = 6
        self.drpin2 = 13
        self.dlenpin = 5
        self.drenpin = 22

        self.hlpin1 = 19
        self.hlpin2 = 26
        self.henpin = 27
        self.gpio.setup(self.dlpin1, self.gpio.OUT)
        self.gpio.setup(self.dlpin2, self.gpio.OUT)
        self.gpio.setup(self.drpin1, self.gpio.OUT)
        self.gpio.setup(self.drpin2, self.gpio.OUT)
        self.gpio.setup(self.dlenpin, self.gpio.OUT)
        self.gpio.setup(self.drenpin, self.gpio.OUT)
        self.gpio.output(self.dlpin1, 0)
        self.gpio.output(self.dlpin2, 0)
        self.gpio.output(self.drpin1, 0)
        self.gpio.output(self.drpin2, 0)
        self.gpio.output(self.dlenpin, 0)
        self.gpio.output(self.drenpin, 0)
        self.gpio.setup(self.hlpin1, self.gpio.OUT)
        self.gpio.setup(self.hlpin2, self.gpio.OUT)
        self.gpio.setup(self.henpin, self.gpio.OUT)
        self.gpio.output(self.hlpin1, 0)
        self.gpio.output(self.hlpin2, 0)
        self.gpio.output(self.henpin, 0)
        #self.gpio.setup(self.doorupcheck, self.gpio.IN) #GPIO23 input setting

        
    def doorup(self):
            self.gpio.output(self.dlenpin, 1)
            self.gpio.output(self.dlpin1, 1)
            self.gpio.output(self.dlpin2, 0)
        
    def doorupstop(self):
        print("Stopped")
        self.gpio.output(self.dlpin1, 0)
        self.gpio.output(self.dlpin2, 0)
        self.gpio.output(self.dlenpin, 0)
        sleep(0.5)
        

    def doordown(self):
        self.gpio.output(self.dlenpin, 1)
        self.gpio.output(self.dlpin1, 0)
        self.gpio.output(self.dlpin2, 1)
        sleep(5) # speed of door up
        self.gpio.output(self.dlpin1, 0)
        self.gpio.output(self.dlpin2, 0)
        self.gpio.output(self.dlenpin, 0)  
        
    def dooropenrot(self):
        self.gpio.output(self.drenpin, 1)
        self.gpio.output(self.drpin1, 1)
        self.gpio.output(self.drpin2, 0)
        sleep(5) # speed of door up
        self.gpio.output(self.drpin1, 0)
        self.gpio.output(self.drpin2, 0)
        self.gpio.output(self.drenpin, 0)

    def doorcloserot(self):
        self.gpio.output(self.drenpin, 1)
        self.gpio.output(self.drpin1, 0)
        self.gpio.output(self.drpin2, 1)
        sleep(5) # speed of door up
        self.gpio.output(self.drpin1, 0)
        self.gpio.output(self.drpin2, 0)
        self.gpio.output(self.drenpin, 0)

    def hopperopen(self):
        self.gpio.output(self.henpin, 1)
        self.gpio.output(self.hlpin1, 0)
        self.gpio.output(self.hlpin2, 1)
        sleep(5) # speed of door up
        self.gpio.output(self.hlpin1, 0)
        self.gpio.output(self.hlpin2, 0)
        self.gpio.output(self.henpin, 0)

    def hopperclose(self):
        self.gpio.output(self.henpin, 1)
        self.gpio.output(self.hlpin1, 1)
        self.gpio.output(self.hlpin2, 0)
        sleep(5) # speed of door up
        self.gpio.output(self.hlpin1, 0)
        self.gpio.output(self.hlpin2, 0)
        self.gpio.output(self.henpin, 0)


class loadcell:
    def __init__(self):
        self.referenceUnit = 15000
        self.hx_right = HX711(21, 20)
        self.hx_left = HX711(16, 12)
        self.hx_right.set_reading_format("MSB", "MSB")
        self.hx_left.set_reading_format("MSB", "MSB")
        self.hx_right.set_reference_unit(self.referenceUnit)
        self.hx_left.set_reference_unit(self.referenceUnit)
        self.hx_right.reset()
        self.hx_left.reset()
        self.hx_right.tare()
        self.hx_left.tare()

    def weighing(self):
        self.val_right = self.hx_right.get_weight(5)
        self.val_left = self.hx_left.get_weight(5)
        self.val_avg = (self.val_right + self.val_left) / 2
        self.hx_right.power_down()
        self.hx_left.power_down()
        self.hx_right.power_up()
        self.hx_left.power_up()
        time.sleep(0.1)
        return self.val_avg

class socketprog:
    def __init__(self):
        self.tcpClitSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClitSocket.connect(('3.133.100.99', 8000))

    def sending(self, data):
        self.data = data
        self.tcpClitSocket.send(self.data.encode('utf-8'))
        ret = self.tcpClitSocket.recv(1024)
        return ret
 
machineno = 'AEL-001'
stx = '['
etx = ']'


QR = QRCode_reader()
lcd = oled()
check = id_check()
display_msg = '欢迎使用'
display_msg2 = '  Welcome'
door = actuator()
scale = loadcell()
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN)

while 1:
        lcd.display(display_msg, display_msg2)
        print("Ready")
        QR.read()
        verification = check.verify()
        if QR.rsv !='':
            print(QR.qrcode)
            if verification == True:
                QR.closeser()
                os.system('mpg321 /home/pi/tts/door_is_opening_ch.mp3 &')
                lcd.display('盖门打开', 'Door is Opening')
                inputsensor = GPIO.input(23)
                while inputsensor == True:
                    inputsensor = GPIO.input(23)
                    print("Door is up")
                    door.doorup()
                    sleep(0.5)
                    if inputsensor == False:
                        door.doorupstop()
                print("Door is rotating")
                door.dooropenrot()
                os.system('mpg321 /home/pi/tts/please_input_your_waste_cn.mp3 &')
                lcd.display('请投放垃圾', 'Please Input Waste')
                print("Input Waste")
                #detecting waste input-+++++++++++++++++++++++++++++++++++
                sleep(0.5)
                door.doorup()
                door.dooropenrot()
                lcd.display('盖门关闭', 'Door is Closing')
                os.system('mpg321 /home/pi/tts/door_is_closing_cn.mp3 &')
                print("Door is Closing")
                sleep(0.5)
                door.doorcloserot()
                door.doordown()
                weight = scale.weighing()*0.001
                lcd.display('您的垃圾为', "  %0.2f"%weight +'kg')
                print("Your waste is", "%0.2f"%weight +"kg")
                sleep(1)
                door.hopperopen()
                sleep(1)
                door.hopperclose()
                #sock = socketprog()
                #dataset = stx+machineno+","+QR.qrcode+","+"W"+"%0.2f"%weight+","+"GGG"+etx
                #recvsig = sock.sending(dataset)
                #recvveri = recvsig.decode('utf-8')
                #print(recvveri)
                lcd.display('感谢使用', '  Thank you')
                os.system('mpg321 /home/pi/tts/thank_you_for_using_cn.mp3 &')
                print("Thank you")
                sleep(2)
                #if (recvveri == '200'):
                #    sleep(2)
                #else:
                #    lcd.display('Data sending', 'Failed')
                #    sleep(2)
                print(stx+machineno+","+QR.qrcode+","+"W"+"%0.2f"%weight+","+"GGG"+etx)
                QR.openser()
            elif verification == False:
                display_msg = 'Sorry!'
                display_msg2 = 'Bye'

"""
except KeyboardInterrupt:
    lcd.device.cleanup()
    GPIO.cleanup()
"""


    

    
        
