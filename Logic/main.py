# Green_box
# Created at 2018-12-06 18:59:52.765684

import streams
import adc

from wireless import wifi
from espressif.esp32net import esp32wifi as wifi_driver
from zerynthapp import zerynthapp
from servo import servo

streams.serial()

#Info of ADM
uid='ZrMb3OGfTl6HRmXfVNgNrg'
token='BJ9Pp0KCReyv_ib2EThT4g'

#network infos
network_name = 'Francesco'
password = 'franco12'

#definition of pins
pin_temp = A0
pin_hum = A4
pin_bright = A3
enable_irrigation = D16

#setting of pin modes
pinMode(pin_temp, INPUT_ANALOG)
pinMode(pin_hum, INPUT_ANALOG)
pinMode(pin_bright, INPUT_ANALOG)
pinMode(enable_irrigation, OUTPUT)

#opening parameters
servo_motor = servo.Servo(D2.PWM, min_width=600, max_width=2500, default_width=600, period=100000)
door_status = 0   #means closed door 
door_open = 'OPEN DOOR'
door_close = 'CLOSE DOOR'
max_degree = 40
min_degree = 3

#irrigation parameters
valve_status = 0   #means closed valve 
irrigation_start = 'IRRIGATE'
irrigation_stop = 'STOP'

#Function defined to get the value of thermistor and transform it in centigrades
def temperature(*args):
    row_temp = analogRead(pin_temp)
    temp = row_temp*25/750
    temp = "%.1f" % temp
    print (row_temp)
    return temp

#Function defined to get the value of moisture sensor and transform it in a percentage value
max_humidity_value = 4096 
def humidity(*args):
    row_hum = analogRead(pin_hum)
    hum = row_hum *100 / max_humidity_value
    hum = "%.1f" % hum
    print (hum)
    return hum
    
#Function defined to get the value of the brightness sensor and than establish what's the level of light in the ambient
def brightness(*args):
    row_bright = analogRead(pin_bright)
    if row_bright <= 2500:
        bright = 2 #means very bright
    if row_bright > 2500 and row_bright <= 3100:
        bright = 1 #means normal brightness
    if row_bright > 3100:
        bright = 0 #means very dark
    print (row_bright)
    return bright

#Function defined to open the gate of the GreenBox, this function menage a servo motor used to move the door
servo_motor.attach()
def opening(*args): 
    if door_status:
        door_status = 0
        servo_motor.moveToDegree(min_degree)
        return door_open
    else:
        door_status = 1
        servo_motor.moveToDegree(max_degree)
        return door_close
        
#Function defined to menage the solenoid valve, this make possible the irrigation function on the app
def irrigation(*args):
    if valve_status:
        valve_status = 0
        digitalWrite(enable_irrigation,LOW)
        return irrigation_start
    else:
        valve_status = 1
        digitalWrite(enable_irrigation,HIGH)
        return irrigation_stop
        

# A 3 seconds delay for easing the connection
for i in range(3):
    sleep(1000)
    print('...', 3-i)
    

print('Start')
try:
    #initializing the wifi driver
    wifi_driver.auto_init()
    sleep(3000)
    
    #connecting to the network, this depends on network_name and password defined at the top of the code
    print('Connecting...')
    wifi.link(network_name, wifi.WIFI_WPA2, password)
    print('Connected to wifi')
    sleep(1000)
    
    #connecting to the zerynth App, this depend on uid and token defined at the top of the code
    print('Connecting to Zerynth App...')
    zapp = zerynthapp.ZerynthApp(uid, token)
    print('zapp object created!')
    
    # Associate the app methods to the python functions 
    zapp.on('temperature',temperature )
    zapp.on('humidity',humidity)
    zapp.on('brightness',brightness)
    zapp.on('irrigation',irrigation)
    zapp.on('opening',opening)
    
    
    print('Start the app instance...')
    zapp.run()
    print('Instance started.')
    
    while True:
        print('.')
        sleep(1000)
    
except Exception as e:
    print(e)