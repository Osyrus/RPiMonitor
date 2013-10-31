import quick2wire.i2c as i2c
import curses

class VReader:
  """The superclass dealing with communicating with the ADC and pulling readings.

  Arguments:
  adc  -- The I2C address of the ADC chip.
  ch   -- The specific channel of the ADC chip.
  Lcal -- The linear calibration, in the form 'Y = (X - Lcal[1])/Lcal[0]' (default (1,0)).
  conv -- The linear conversion from voltage, in the form 'Y = conv * X'.
  """
  def __init__(self, adc, ch, Lcal = (1,0), conv = 1):
    self.adc = adc
    self.ch = ch

    #Voltage conversion stuff
    self.varDiv  = 16
    self.varMult = (2.4705882/self.varDiv)/1000
    self.Lcal = Lcal
    self.conv = conv

  def getadcreading(self, bus):
    """Returns the voltage reading for this instance after calibration and conversion.

    Arguments:
    bus -- The quick2wire bus to use for communication with the ADC chip.
    """

    #Change the ADC chip channel
    bus.transaction(i2c.writing_bytes(self.adc, self.ch))

    #Get the voltage reading
    h, l, s = bus.transaction(i2c.reading(self.adc,3))[0]
    while (s & 128):
      h, l, s = bus.transaction(i2c.reading(self.adc,3))[0]

    v = (h << 8) | l

    if (h > 128):
      v = ~(0x020000 - v)

    return ((self.varMult * self.conv * v) - self.Lcal[1]) / self.Lcal[0]

class Pane:
  """docstring for Pane"""
  def __init__(self, x = 1, y = 1, w = 30, h = 1):
    self.x, self.y = 0, 0
    self.w, self.h = 0, 0
    self.setPos(x, y)
    self.setDim(w, h)

  def getPos(self):
    return (self.x, self.y)

  def setPos(self, x, y):
    self.x, self.y = x, y

  def getDim(self):
    return (self.w, self.h)

  def setDim(self, w, h):
    self.w, self.h = w, h
    

class DiodePane(VReader, Pane):
  """Subclass of VReader that creates a curses windows to read diode temperatures

  Arguments:
  idNum -- Diode number for identification
  x     -- The x location
  y     -- The y location
  adc   -- The I2C ADC chip address
  ch    -- The channel of the ADC chip
  Lcal  -- The linear calibration, in the form 'Y = (X - Lcal[1])/Lcal[0]' (default (1,0))
  """
  def __init__(self, idNum, adc, ch, Lcal = (1, 0)):
    self.conv = 10 #100mv per degree conversion
    self.setDim(30, 1) #Definition for this module, width = 30, height = 1
    self.idNum = idNum

    super(DiodePane, self).__init__(adc, ch, Lcal, self.conv)

    self.win = curses.newwin(self.h, self.w, self.y, self.x)

  def update(self, bus):
    """Updates the windows for this diode temperature window instance

    Arguments:
    bus -- The quick2wire bus to use for communication with the ADC chip.
    """
    self.win.addstr(0, 0, "D%d Temp: %05.02f deg" % (self.idNum, self.getadcreading(bus)), curses.A_BOLD)
    self.win.refresh()