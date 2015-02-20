import curses
import InfoPanes
from PaneManager import PaneManager
import time
import quick2wire.i2c as i2c
import paho.mqtt.client as mqtt
import usbtmc
#from datetime import datetime
#from flask import Flask

try:
    #I2C ADC Reader Setup Stuff
    ADCAdd =  (0x68, 0x69) #For the two ADC chips
    Ch16 = (0x98, 0xB8, 0xD8, 0xF8) #16bit SubChannels
    Ch12 = (0x90, 0XB0, 0XD0, 0XF0) #12bit SubChannels
    Div16 = 16 #Divisor for 16bit readings
    Div12 = 1  #Divisor for 12bit readings

    #IVI Instruments Setup Stuff
    try:
        PM100D = usbtmc.Instrument("USB::0x1313::0x8078::P0004516::INSTR")
        PM100DRead = "READ?"
        PM100DCal = (1000, 0)
        PM100DConnected = 1
    except:
        PM100D = 0;
        PM100DConnected = 0

    #Calibration Stuff
    D1Cal = (10.506, -2.351)
    D2Cal = (10.688, -2.683)
    CurrentCal = (78.42, -0.059)
    CurrentAvg = 32

    #Setup screen
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    stdscr.nodelay(1)

    #Create the pane manager
    PM = PaneManager(stdscr)

    #Create info strings
    diodeInfo = ("Diode ", "temp", "deg")
    driverInfo = ("Driver ", "current", "A")
    PM100DInfo = ("Meter ", "power", "mW")

    #Create the sensor IDs
    D1Temp = "temp/d1"
    D2Temp = "temp/d2"
    Dr1Current = "current/dr1"
    PowMeter1 = "power/m1"

    #Create some info panes, first number will be the mqtt topic id
    D1Pane = InfoPanes.InfoPane(D1Temp, diodeInfo, ADCAdd[0], Ch16[0], Div16, D1Cal)
    D2Pane = InfoPanes.InfoPane(D2Temp, diodeInfo, ADCAdd[0], Ch16[1], Div16, D2Cal)
    DrPane = InfoPanes.InfoPane(Dr1Current, driverInfo, ADCAdd[1], Ch12[0], Div12, CurrentCal, CurrentAvg)

    #Add them to the manager
    PM.addPanes([D1Pane, D2Pane, DrPane])

    #Add the PM100D pane if it is plugged in
    if PM100DConnected == 1:
        PMPane = InfoPanes.IVIPane(PowMeter1, PM100DInfo, PM100DRead, PM100DCal)
        PM.addPane(PMPane)

    #Now add the new MQTT measurement publishing system
    mqttC = mqtt.Client()
    mqttC.connect("127.0.0.1", 1883, 60)
    mqttC.loop_start();

    def sensorQuery(client, userdata, message):
        payload = message.payload.decode('utf-8')

        if payload == "all":
            mqttC.publish("laser/sensors/ids", PM.getIDs(), 2, retain=False)

    queryTopic = "laser/sensors/query"

    mqttC.subscribe(queryTopic)
    mqttC.message_callback_add(queryTopic, sensorQuery)

    #Run the refresh loop
    with i2c.I2CMaster() as bus:
        while True:
            PM.updateAll((bus, PM100D), mqttC)
            
            c = stdscr.getch()
            if c == ord('q'):
                break

            time.sleep(1)

except:
    raise

finally:
    #Clean up the screen and reset to normal
    curses.nocbreak()
    curses.echo()
    stdscr.keypad(0)
    curses.endwin()
    mqttC.loop_stop()
    mqttC.disconnect()