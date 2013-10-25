import quick2wire.i2c as i2c
import curses

class VReader:
  def __init__(self, adc, ch):
    self.adc = adc
    self.ch = ch

    #Voltage conversion stuff
    self.varDiv  = 16
    self.varMult = (2.4705882/varDiv)/1000

  def getadcreading(self, bus):
    #Change the ADC chip channel
    bus.transaction(i2c.writing_bytes(self.adc, self.ch))

    #Get the voltage reading
    h, l, s = bus.transaction(i2c.reading(self.adc,3))[0]
    while (s & 128):
      h, l, s = bus.transaction(i2c.reading(self.adc,3))[0]

    v = (h << 8) | l

    if (h > 128):
      v = ~(0x020000 - v)

    return v * self.varMult

class DiodePane(VReader):
  def __init__(self, idNum, (x, y), adc, ch):
    super(DiodePane, self).__init__(adc, ch)
    self.posX = x
    self.posY = y
    self.h = 1
    self.w = 30
    self.conv = 10
    self.idNum = idNum

    self.win = curses.newwin(self.h, self.y, self.posY, self.posX)

  def getTemperature(self, bus):
    v = self.getadcreading(bus)
    temp = self.conv

    return temp

  def update(self, bus):
    self.win.addstr(0, 0, "D%d Temp: %05.02f deg" % (self.idNum, self.getTemperature(bus)), curses.A_BOLD)
    self.win.refresh()