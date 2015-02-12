import quick2wire.i2c as i2c
import curses
import time

class VReader:
  """The superclass dealing with communicating with the ADC and pulling readings.

  Arguments:
  adc  -- The I2C address of the ADC chip.
  ch   -- The specific channel of the ADC chip (also sets the number of read bits).
  div  -- The divisor for voltage conversion (depends on number of bits)
  """
  def __init__(self, adc, ch, div):
    self.adc = adc
    self.ch = ch

    #Voltage conversion stuff
    self.varDiv  = div
    self.varMult = (2.4705882/self.varDiv)/1000

  def getadcreading(self, bus):
    """Returns the voltage reading for this instance after calibration.

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

    return (self.varMult * v)

class Pane:
  """docstring for Pane"""
  def __init__(self, idNum, info, instrType, LCal, x = 1, y = 1, w = 30, h = 1):
    self.x, self.y = 0, 0
    self.w, self.h = 0, 0
    self.setPos(x, y)
    self.setDim(w, h)
    self.win = None
    self.idNum = idNum
    self.info = info
    self.instrType = instrType
    self.LCal = LCal

    self.setWidthStr(info)

  def getPos(self):
    return (self.x, self.y)

  def setPos(self, y, x):
    self.x, self.y = x, y

  def getDim(self):
    return (self.w, self.h)

  def setDim(self, w, h):
    self.w, self.h = w, h

  def getInstrType(self):
    return self.instrType

  def applyCal(self, raw):
    return (self.LCal[0] * raw) + self.LCal[1]

  def setWidthStr(self, inStr):
    self.w = len(inStr[0]) + len(inStr[1]) + len(inStr[2]) + 13

  def makeWin(self):
    self.win = curses.newwin(self.h, self.w, self.y, self.x)

  def createString(self, data):
    return self.info[0] + "{} ".format(self.idNum) + self.info[1] + ": {0:02.02f} ".format(data) + self.info[2]

  def mqttPublish(self, mqttC, topic, data):
    mqttC.publish(topic + str(self.idNum), str(time.time()) + " " + str(data), 0, retain=False)

class IVIPane(Pane):
  """docstring for IVIPane"""
  def __init__(self, idNum, info, readCommand, LCal = (1, 0)):
    Pane.__init__(self, idNum, info, "ivi", LCal)

    self.readCommand = readCommand

  def update(self, iviInstr, mqttC):
    #Read from the instument
    dataRaw = iviInstr.ask(self.readCommand)
    #The instument gives the number back as a string, need a number
    data = self.applyCal(float(dataRaw))
    #Then do the normal stuff...
    dataStr = self.createString(data)

    self.mqttPublish(mqttC, "laser/sensors/ivi/", data)

    #self.win.addstr(0, 0, str(dataRaw), curses.A_BOLD)
    self.win.addstr(0, 0, str(dataStr), curses.A_BOLD)

    self.win.refresh()

class InfoPane(VReader, Pane):
  """Subclass of VReader that creates a curses windows to read diode temperatures

  Arguments:
  idNum -- Diode number for identification
  info  -- A length 3 tuple, for printing to screen.
           Order: Identifier (e.g. Diode, Driver), Reading (e.g. Temp, Current), Unit (e.g. deg, A, V)
  x     -- The x location
  y     -- The y location
  adc   -- The I2C ADC chip address
  ch    -- The channel of the ADC chip
  Lcal  -- The linear calibration/conversion, in the form 'X = Lcal[0]*Y + Lcal[1]' (default (1,0))
  avg   -- The number of times to average the reading before displaying
  """
  def __init__(self, idNum, info, adc, ch, div, LCal = (1, 0), avg = 1):
    VReader.__init__(self, adc, ch, div)
    Pane.__init__(self, idNum, info, "adc", LCal)

    self.avg = avg

  def update(self, adcBus, mqttC):
    """Updates the windows for this diode temperature window instance

    Arguments:
    adcBus   -- The quick2wire bus to use for communication with the ADC chip.
    mqttC -- The mqtt client for publishing data
    """
    #Pull the data from the ADC and deal with any averaging
    if self.avg == 1:
      rawData = self.getadcreading(adcBus)
    else:
      accum = 0  
      for i in range(1, self.avg + 1):
        accum = accum + self.getadcreading(adcBus)
      rawData = accum / self.avg
    #Convert the output to the correct units
    data = self.applyCal(rawData)
    #Create a user readable string with this data
    dataStr = self.createString(data)
    #Publish this data via mqtt
    self.mqttPublish(mqttC, "laser/sensors/adc/", data)
    #Print this readable string to the pane
    self.win.addstr(0, 0, str(dataStr), curses.A_BOLD)
    #Refresh this pane for the user to read!
    self.win.refresh()