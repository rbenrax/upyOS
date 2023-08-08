import machine
import utime

import array, time
from machine import Pin
import rp2
from rp2 import PIO, StateMachine, asm_pio
# LED引脚
led_onboard = machine.Pin(25, machine.Pin.OUT)


# Configure the number of WS2812 LEDs.
NUM_LEDS = 10

@asm_pio(sideset_init=PIO.OUT_LOW, out_shiftdir=PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1] 
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1] 
    jmp("bitloop")          .side(1)    [T2 - 1] 
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    
# Create the StateMachine with the ws2812 program, outputting on Pin(23).ws2812引脚
sm = StateMachine(0, ws2812, freq=8000000, sideset_base=Pin(23))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

time.sleep_ms(200)

print("red")

for j in range(0, 20): 
    for i in range(NUM_LEDS): 
        ar[i] = j<<8 
    sm.put(ar,8) 
    time.sleep_ms(50)
    
print("green")
for j in range(0, 20): 
    for i in range(NUM_LEDS): 
        ar[i] = j<<16 
    sm.put(ar,8) 
    time.sleep_ms(50)
    
print("blue")
for j in range(0, 100): 
    for i in range(NUM_LEDS): 
        ar[i] = j 
    sm.put(ar,8) 
    time.sleep_ms(5)

print("white")
for j in range(0, 100):
    for i in range(NUM_LEDS): 
        ar[i] = j<<16 + j<<8 + j 
    sm.put(ar,8) 
    time.sleep_ms(100)
    
# while True: 
    led_onboard.value(1) 
    utime.sleep(.3) 
    led_onboard.value(0) 
    utime.sleep(.3)
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                               
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                                                        
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                 
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                              
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                     
                      
                     
                     
 
  
                                                                                 
                        
                      
                                       
                          