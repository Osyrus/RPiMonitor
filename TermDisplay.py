import curses
import InfoPanes
import time
import quick2wire.i2c as i2c

#I2C Setup Stuff
adc_address1 = 0x68
adc_address2 = 0x69
D1Ch = 0x98
D2Ch = 0xB8

#Calibration Stuff
D1Cal = (0.9518, 2.238)
D2Cal = (0.9356, 2.51)

#Setup screen
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
curses.curs_set(0)
stdscr.keypad(1)
stdscr.nodelay(1)

#Position Stuff
maxY, maxX = stdscr.getmaxyx()
w = 30
X1, Y1 = 2, maxY -2
X2, Y2 = X1+w, maxY -2

#Create some info panes
D1Pane = InfoPanes.DiodePane(1, X1, Y1, adc_address1, D1Ch, D1Cal)
D2Pane = InfoPanes.DiodePane(2, X2, Y2, adc_address1, D2Ch, D2Cal)

#Run the refresh loop
with i2c.I2CMaster() as bus:
	while True:
		D1Pane.update(bus)
		D2Pane.update(bus)
		
		c = stdscr.getch()
		if c == ord('q'):
			break

		time.sleep(1)

#Clean up the screen and reset to normal
curses.nocbreak()
curses.echo()
stdscr.keypad(0)
curses.endwin()
