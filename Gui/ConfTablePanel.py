import wx
from wx.grid import Grid as wxGrid
from xml.etree.ElementTree import ElementTree

class ConfTablePanel(wx.Panel):

	def __init__(self, parent):
		wx.Panel.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)
		self._parent = parent

		self._grid = wxGrid(parent, -1, parent.GetStartPosition(), wx.Size(150, 250), wx.NO_BORDER | wx.WANTS_CHARS)

		self._grid.CreateGrid(2, 3)
	
	def getPanelInfo(self):
		return wx.aui.AuiPaneInfo().Name("test1").Caption("Pane Caption").Top().CloseButton(True).MaximizeButton(True)

