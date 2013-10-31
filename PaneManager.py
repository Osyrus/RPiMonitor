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
    if len(panes) == 0:
      pane.setPos(self.sizeY - linePos, spacingX)
    else:
      while True:
        if panes[end].getPos()[1] == linePos:
          usedX = panes[end].getPos()[0] + panes[end].getDim[0] + spacingX

          if (usedX + pane.getPos()[0]) <= self.sizeX:
            pane.setPos(self.sizeY - linePos, usedX)
            break
          else:
            linePos = linePos + 1 + spacingY

        else:
          pane.setPos(self.sizeY - linePos, spacingX)
          break

    panes.append(pane)

  def addPanes(self, panes):
    for pane in panes:
      self.addPane(pane)

  def updateAll(self, bus):
    for pane in self.panes:
      pane.update(bus)