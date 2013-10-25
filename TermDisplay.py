import curses
import curses.textpad as textpad
import time
import quick2wire.i2c as i2c

adc_address1 = 0x68
adc_address2 = 0x69

varDiv  = 16
varMult = (2.4705882/varDiv)/1000

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()

stdscr.keypad(1)
stdscr.nodelay(1)

maxY, maxX = stdscr.getmaxyx()

h = 1
w = 30

X1, Y1 = 2, maxY -2
X2, Y2 = X1+w, maxY -2

win1 = curses.newwin(h, w, Y1, X1)
win2 = curses.newwin(h, w, Y2, X2)

def printDTemp(win, num, v):
	temp = v * 10
	win.addstr(0, 0, "D%d Temp: %05.02f deg" % (num, temp), curses.A_BOLD)
	win.refresh()

with i2c.I2CMaster() as bus:
	def changechannel(address, adcConfig):
		bus.transaction(i2c.writing_bytes(address, adcConfig))

	def getadcreading(address):
		h, l, s = bus.transaction(i2c.reading(address,3))[0]
		while (s & 128):
			h, l, s = bus.transaction(i2c.reading(address,3))[0]

		v = (h << 8) | l

		if (h > 128):
			v = ~(0x020000 - v)

		return v * varMult

	while True:
		changechannel(adc_address1, 0x98)
		printDTemp(win1, 1, getadcreading(adc_address1))
		changechannel(adc_address1, 0xB8)
		printDTemp(win2, 2, getadcreading(adc_address1))
		
		c = stdscr.getch()
		if c == ord('q'):
			break

		time.sleep(1)

curses.nocbreak()
curses.echo()
stdscr.keypad(0)
curses.endwin()
