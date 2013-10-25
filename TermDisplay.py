import curses
import InfoPanes
import time
import quick2wire.i2c as i2c

adc_address1 = 0x68
adc_address2 = 0x69

varDiv  = 16
varMult = (2.4705882/varDiv)/1000

#Setup screen
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
stdscr.nodelay(1)

#Position Stuff
maxY, maxX = stdscr.getmaxyx()
X1, Y1 = 2, maxY -2
X2, Y2 = X1+w, maxY -2

#Create some info panes
D1Pane = InfoPanes.DiodePane(1, (X1,Y1), adc_address1, 0x98)
D2Pane = InfoPanes.DiodePane(2, (X1,Y1), adc_address1, 0xB8)

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
