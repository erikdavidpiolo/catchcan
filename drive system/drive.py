from machine import Pin,PWM
import time 

driver1_in1 = Pin(1,Pin.OUT)
driver1_in2 = Pin(2,Pin.OUT)
driver1_in3 = Pin(4,Pin.OUT)
driver1_in4 = Pin(5,Pin.OUT)
driver1_enB = PWM(Pin(6))
driver1_enA = PWM(Pin(7))

while True:
    print("Turning on motor")
    driver1_in1.value(1)
    driver1_in2.value(1)  
    driver1_in3.value(1)
    driver1_in4.value(1)

    for duty in range(0,65535,100):
        print("duty:" + str(duty))
        driver1_enA.duty_u16(duty)
        driver1_enB.duty_u16(duty)
        time.sleep_ms(5)

    for duty in range(65535,0,-100):
        print("duty:" + str(duty))
        driver1_enA.duty_u16(duty)
        driver1_enB.duty_u16(duty)
        time.sleep_ms(5)
