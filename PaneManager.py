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

  def addPane(self, pane):
    if len(self.panes) == 0:
      pane.setPos(self.sizeY - self.linePos, self.spacingX)
    else:
      while True:
        if self.panes[-1].getPos()[1] == self.linePos:
          usedX = self.panes[-1].getPos()[0] + self.panes[-1].getDim()[0] + self.spacingX

          if (usedX + pane.getPos()[0]) <= self.sizeX:
            pane.setPos(self.sizeY - self.linePos, usedX)
            break
          else:
            self.linePos = self.linePos + 1 + self.spacingY

        else:
          pane.setPos(self.sizeY - self.linePos, self.spacingX)
          break

    self.panes.append(pane)

  def addPanes(self, panes):
    for pane in panes:
      self.addPane(pane)

  def updateAll(self, bus):
    for pane in self.panes:
      pane.update(bus)