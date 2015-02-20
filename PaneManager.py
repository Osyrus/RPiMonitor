import curses

class PaneManager:
    """docstring for PaneManager"""
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.sizeY, self.sizeX = stdscr.getmaxyx()
        self.panes = []
        self.linePos = 1
        self.spacingX = 1
        self.spacingY = 1

    def getIDs(self):
        sensorIds = "sensors"

        for pane in self.panes:
            sensorIds = sensorIds + "," + pane.getID()

        return sensorIds

    def addPane(self, pane):
        if len(self.panes) == 0:
            pane.setPos(self.sizeY - self.linePos, self.spacingX)
        else:
            while True:
                yPos = self.sizeY - self.linePos

                if self.panes[-1].getPos()[1] == yPos:
                    usedX = self.panes[-1].getPos()[0] + self.panes[-1].getDim()[0] + self.spacingX

                    if (usedX + pane.getPos()[0]) <= self.sizeX:
                        pane.setPos(yPos, usedX)
                        break
                    else:
                        self.linePos = self.linePos + 1 + self.spacingY
                        
                else:
                    pane.setPos(yPos, self.spacingX)
                    break

        pane.makeWin()
        self.panes.append(pane)

    def addPanes(self, panes):
        for pane in panes:
            self.addPane(pane)

    def updateAll(self, instr, mqttC):
        for pane in self.panes:
            if pane.getInstrType() == "adc":
                pane.update(instr[0], mqttC)
            elif pane.getInstrType() == "ivi":
                pane.update(instr[1], mqttC)