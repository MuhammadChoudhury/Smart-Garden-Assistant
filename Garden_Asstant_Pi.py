import RPi.GPIO as GPIO
import Adafruit_DHT     
import time
import picamera
from datetime import datetime
import math
import spidev
from picamera import PiCamera
from time import sleep
 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000
GAIN = 1
PIN=4

L1 = 2
L2 = 3
L3 = 19
L4 = 16

# These are the four columns
C1 = 12
C2 = 17
C3 = 27
C4 = 22

GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)

GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def readLine(line, characters):
    GPIO.output(line, GPIO.HIGH)
    if(GPIO.input(C1) == 1):
        print(characters[0])
    if(GPIO.input(C2) == 1):
        print(characters[1])
    if(GPIO.input(C3) == 1):
        print(characters[2])
    if(GPIO.input(C4) == 1):
        print(characters[3])
    GPIO.output(line, GPIO.LOW)

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data
  
     
def ConverttoPercent(data):
  percent = int(round(data/10.24))
  return percent
  
# Define sensor channel
light_channel  = 0
moisture_channel  = 5
temp_channel = 2
humidity_channel = 3

camera = PiCamera()

# Define delay between readings
delay = 3
num = 1

GPIO.setup(14,GPIO.OUT)
GPIO.output(14,GPIO.LOW)

Motor1 = {'EN': 25, 'input1': 24, 'input2': 23}
Motor2 = {'EN': 5, 'input1': 6, 'input2': 13}

for x in Motor1:
    GPIO.setup(Motor1[x], GPIO.OUT)
    GPIO.setup(Motor2[x], GPIO.OUT)

EN1 = GPIO.PWM(Motor1['EN'], 100)    
EN2 = GPIO.PWM(Motor2['EN'], 100)    

EN1.start(0)
EN2.start(0)

EN2.ChangeDutyCycle(0)
EN2.ChangeDutyCycle(0)
  
fan = 0

GPIO.setup(PIN, GPIO.OUT)
GPIO.output(PIN, GPIO.HIGH)

GPIO.setup(26,GPIO.OUT)
servo1 = GPIO.PWM(26,50) #Note: 11 is pin, 50 = 50Hz pulse
servo1.start(0)

GPIO.setup(16,GPIO.OUT)
servo2 = GPIO.PWM(16,50) #Note: 11 is pin, 50 = 50Hz pulse
servo2.start(0)

GPIO.setup(21, GPIO.OUT)
GPIO.output(21, GPIO.LOW) #Blue
GPIO.setup(20, GPIO.OUT)
GPIO.output(20, GPIO.LOW) #Yellow
GPIO.setup(15, GPIO.OUT)
GPIO.output(15, GPIO.LOW) #Red
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.LOW) #Green
  

time.sleep(3)

duty = 0
  
x = 5

ans = "nothing"

pump = False
fan = False
blinds = False

pum = 10

user_temp = False
user_light = False
user_moisture = False

while True:
    


  camera.resolution = (640, 480)
  camera.framerate = 15



  # Read the moisture sensor data
  moisture_level = ReadChannel(moisture_channel)
  moisture_percent = ConverttoPercent(moisture_level)
  moisture_level /= 2
  moisture_percent /= 2  

  # Print out results
  print ("--------------------------------------------")
  print("Moisture : {} ({}%)".format(moisture_level,moisture_percent))
  
  if user_moisture == True:
      if moisture_percent < moisture:
          pump = True
          GPIO.setup(PIN, GPIO.OUT)
          GPIO.output(PIN, GPIO.LOW)
          GPIO.output(21, GPIO.HIGH) #Blue
          print("Pump ON")
          pumping = moisture - moisture_percent
          print("Pumping for ", pum, " seconds")
          pumping = pumping 
          time.sleep(pum)
      else:
          pump = False
          GPIO.setup(PIN, GPIO.OUT)
          GPIO.output(PIN, GPIO.HIGH)
          GPIO.output(21, GPIO.LOW) #Blue
          print("Pump OFF")
          time.sleep(3)
  else:
      if moisture_percent >= 90 and moisture_percent <= 95:
          print("pump deadzone")
      elif moisture_percent < 80:
          pump = True
          GPIO.setup(PIN, GPIO.OUT)
          GPIO.output(PIN, GPIO.LOW)
          GPIO.output(21, GPIO.HIGH) #Blue
          print("Pump ON")
          pumping = 100 - moisture_percent

          print("Pumping for ", pum, " seconds")
          time.sleep(pum)
      else:   #moisture over 95
          pump = False
          GPIO.setup(PIN, GPIO.OUT)
          GPIO.output(PIN, GPIO.HIGH)
          GPIO.output(21, GPIO.LOW) #Blue
          print("Pump OFF")
          time.sleep(3)
          
  pump = False
  GPIO.output(21, GPIO.LOW) #Blue
  GPIO.setup(PIN, GPIO.OUT)
  GPIO.output(PIN, GPIO.HIGH)
  time.sleep(3)
  # Read the moisture sensor data
  light_level = ReadChannel(light_channel)
  light_percent = ConverttoPercent(light_level)

  # Print out results
  print("Light : {} ({}%)".format(light_level,light_percent))
  
  # Set pin 11 as an output, and set servo1 as pin 11 as PWM
  
  time.sleep(3)
 
  if user_light == True:
      if light_percent < light:
          print("Blinds are now opening")
          while duty <= 12:
              blinds = True
              GPIO.output(15, GPIO.HIGH) #Red
              servo1.ChangeDutyCycle(duty)
              servo2.ChangeDutyCycle(duty)
              EN2.ChangeDutyCycle(x)
              GPIO.output(Motor2['input1'], GPIO.HIGH)
              GPIO.output(Motor2['input2'], GPIO.LOW)
              time.sleep(1)
              duty = duty + 1
              x = x + 3
              count = 0
      else:
          print("Blinds are now closing")
          while duty >= 1:
              blinds = False
              GPIO.output(15, GPIO.LOW) #Red
              servo1.ChangeDutyCycle(duty)
              servo2.ChangeDutyCycle(duty)
              EN2.ChangeDutyCycle(x)
              GPIO.output(Motor2['input1'], GPIO.LOW)
              GPIO.output(Motor2['input2'], GPIO.HIGH)
              time.sleep(1)
              duty = duty - 1
              x = x - 3
              count = 0
  else:
      if light_percent <= 95 and light_percent >= 85:
          print("light deadzone")
      elif light_percent < 85:
          print("Blinds are now opening")
          stop = light_percent / 10
          stop = math.floor(stop)
          print(stop)
          time.sleep(5)
          while duty <= stop:
              blinds = True
              GPIO.output(15, GPIO.HIGH) #Red
              servo1.ChangeDutyCycle(duty)
              servo2.ChangeDutyCycle(duty)
              EN2.ChangeDutyCycle(x)
              GPIO.output(Motor2['input1'], GPIO.HIGH)
              GPIO.output(Motor2['input2'], GPIO.LOW)
              time.sleep(0.5)
              duty = duty + 1
              x = x + 3
              count = 0
              print(duty,"  ", x)
      else:
          print("Blinds are now opening")
          stop = light_percent / 10
          stop = math.floor(stop)
          print(stop)
          time.sleep(5)
          print("Blinds are now closing")
          while duty >= 1:
              blinds = False
              GPIO.output(15, GPIO.LOW) #Red
              servo1.ChangeDutyCycle(duty)
              servo2.ChangeDutyCycle(duty)
              EN2.ChangeDutyCycle(x)
              GPIO.output(Motor2['input1'], GPIO.LOW)
              GPIO.output(Motor2['input2'], GPIO.HIGH)
              time.sleep(1)
              duty = duty - 1
              x = x - 3
              count = 0

  servo1.stop()
  servo2.stop()
  EN1.ChangeDutyCycle(0)
  EN2.ChangeDutyCycle(0)
  time.sleep(5)
    


# Wait before repeating loop
  temp_level = ReadChannel(temp_channel)
  temp_percent = ConverttoPercent(temp_level)
  
  temp_percent = (9/5)*temp_percent + 32

  # Print out results
  print("Temp : {} ({} F)".format(temp_level,temp_percent))
  
  time.sleep(3)

  
  if user_temp == True:
      if temp_percent > temp:
          fan = True
          GPIO.output(18, GPIO.HIGH) #Green
          GPIO.setup(14,GPIO.OUT)
          print ("Fan on. User temp")
          GPIO.output(14,GPIO.HIGH)
          for x in range(1, 40):
              
              EN1.ChangeDutyCycle(x)
       #     EN2.ChangeDutyCycle(x)
              time.sleep(0.2)

              GPIO.output(Motor1['input1'], GPIO.HIGH)
              GPIO.output(Motor1['input2'], GPIO.LOW)
            
        #    GPIO.output(Motor2['input1'], GPIO.HIGH)
        #    GPIO.output(Motor2['input2'], GPIO.LOW
      else:
          fan = False
          GPIO.output(18, GPIO.LOW) #Green
          GPIO.setup(14,GPIO.OUT)
          print ("Fan off")
          GPIO.output(14,GPIO.LOW)
          
          EN1.ChangeDutyCycle(0)
  else:
      
      if (temp_percent >= 50 and temp_percent <= 60):
          print("deadzone")
      elif temp_percent < 50 :
          fan = False
          GPIO.output(18, GPIO.LOW) #Green
          GPIO.setup(14,GPIO.OUT)
          print ("Fan off")
          GPIO.output(14,GPIO.LOW)
          
          EN1.ChangeDutyCycle(0)
          
      elif temp_percent > 60 and temp_percent < 70:
          fan = True
          GPIO.output(18, GPIO.HIGH) #Green
          GPIO.setup(14,GPIO.OUT)
          print ("Fan ON")
          GPIO.output(14,GPIO.HIGH)
          
          EN1.ChangeDutyCycle(0)
          
      else: #temp > 70
          
          fan = True
          GPIO.output(18, GPIO.HIGH) #Green
          GPIO.setup(14,GPIO.OUT)
          print ("Fan on")
          GPIO.output(14,GPIO.HIGH)
          
          for i in range(10, 40):
              EN1.ChangeDutyCycle(i)
       #     EN2.ChangeDutyCycle(x)
              time.sleep(0.2)

              GPIO.output(Motor1['input1'], GPIO.HIGH)
              GPIO.output(Motor1['input2'], GPIO.LOW)
            
        #    GPIO.output(Motor2['input1'], GPIO.HIGH)
        #    GPIO.output(Motor2['input2'], GPIO.LOW
  GPIO.setup(14,GPIO.OUT)
  GPIO.output(14,GPIO.LOW)
  #GPIO.output(18, GPIO.LOW) #Green
 # EN1.ChangeDutyCycle(0)
  #EN2.ChangeDutyCycle(0)
  time.sleep(5)
          

  def capture_photo(file_capture, text):
      # Add date as timestamp on the generated files.
      camera.annotate_text = text
      # Capture an image as the thumbnail.
      camera.start_preview()
      sleep(5)
      camera.capture(file_capture)
      camera.stop_preview()
      print("\r\nImage Captured! \r\n")
    
  # Get the current date as the timestamp to generate unique file names.
  
 # date = datetime.datetime.now().strftime('%m-%d-%Y_%H.%M.%S')
  camera.start_preview()
  time.sleep(5)
  camera.stop_preview()
  print("iteration", num)
  num += 1
  
  
  # Wait before repeating loop
  print("You can turn of the pump, fan, or blinds.")
  print("Or you can set your own optimal temperature moisture, or light settings for plant")
  ans = input("What do you want to do?")
  print("Your answer is : ", ans)
  time.sleep(1)
  
  
  if ans == "fan":
      if fan == True:
          fan = False
          GPIO.setup(14,GPIO.OUT)
          print ("Fan off")
          GPIO.output(14,GPIO.LOW)
          EN1.ChangeDutyCycle(0)
      else:
          GPIO.setup(14,GPIO.OUT)
          print ("Fan on")
          GPIO.output(14,GPIO.HIGH)
          EN1.ChangeDutyCycle(0)
  elif ans == "pump":
      if pump == True:
          pump = False
          GPIO.setup(PIN, GPIO.OUT)
          GPIO.output(PIN, GPIO.HIGH)
          print("OFF")
          time.sleep(5)
      else:
          pump = True
          GPIO.setup(PIN, GPIO.OUT)
          GPIO.output(PIN, GPIO.LOW)
          print("Pump ON")
          time.sleep(5)
  elif ans == "blinds":
      if blinds == True:
          print("Blinds are now closing")
          while duty >= 1:
              blinds = False
              GPIO.output(15, GPIO.LOW) #Red
              servo1.ChangeDutyCycle(duty)
              servo2.ChangeDutyCycle(duty)
              EN2.ChangeDutyCycle(x)
              GPIO.output(Motor2['input1'], GPIO.LOW)
              GPIO.output(Motor2['input2'], GPIO.HIGH)
              time.sleep(1)
              duty = duty - 1
              x = x - 3
              count = 0
      else:
          print("Blinds are now opening")
          while duty <= 12:
              blinds = True
              GPIO.output(15, GPIO.HIGH) #Red
              servo1.ChangeDutyCycle(duty)
              servo2.ChangeDutyCycle(duty)
              EN2.ChangeDutyCycle(x)
              GPIO.output(Motor2['input1'], GPIO.HIGH)
              GPIO.output(Motor2['input2'], GPIO.LOW)
              time.sleep(1)
              duty = duty + 1
              x = x + 3
              count = 0
  elif ans == "manual":
      temp = input("What temperature value do you want to set it to?")
      temp = int(temp)
      user_temp = True
      light = input("What light value do you want to set it to?")
      light = int(light)
      user_light = True
      moisture = input("What moisture value do you want to set it to?")
      moisture = int(moisture)
      user_moisture = True
  elif ans == "default settings":
      user_temp = False
      user_moisure = False
      user_light = False
  else:
      continue
      
      
          
      
          
      

 