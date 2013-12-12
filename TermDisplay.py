import curses
import InfoPanes
import exceptions.Exception as Exception
from PaneManager import PaneManager
import time
import quick2wire.i2c as i2c

try:
  #I2C Setup Stuff
  ADCAdd =  (0x68, 0x69)
  Ch16 = (0x98, 0xB8 ,0xD8, 0xF8) #16bit Channels

  #Calibration Stuff
  D1Cal = (10.506, 2.351)
  D2Cal = (10.688, 2.683)
  CurrentCal = (78.42, -0.059)

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

  #Create some info panes
  D1Pane = InfoPanes.InfoPane(1, diodeInfo, ADCAdd[0], Ch16[0], D1Cal)
  D2Pane = InfoPanes.InfoPane(2, diodeInfo, ADCAdd[0], Ch16[1], D2Cal)
  DrPane = InfoPanes.InfoPane(1, driverInfo, ADCAdd[1], Ch16[0], CurrentCal)

  #Add them to the manager
  PM.addPanes([D1Pane, D2Pane])

  #Run the refresh loop
  with i2c.I2CMaster() as bus:
    while True:
      PM.updateAll(bus)
      
      c = stdscr.getch()
      if c == ord('q'):
        break

      time.sleep(1)

except Exception, e:
  raise e

finally:
  #Clean up the screen and reset to normal
  curses.nocbreak()
  curses.echo()
  stdscr.keypad(0)
  curses.endwin()

