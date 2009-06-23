

from xml.etree.ElementTree import ElementTree

import wx
import wx.grid
import wx.html
import wx.aui

from os import path
from ConfMenuBar import ConfMenuBar
from ConfToolBar import ConfToolBar
from ConfTablePanel import ConfTablePanel

class MainWin(wx.Frame):
	def __init__ (self, parent, id=-1, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE |
                                            wx.SUNKEN_BORDER |
                                            wx.CLIP_CHILDREN):
		wx.Frame.__init__(self, parent, id, title, pos, size, style)
		self.x = 0
		
		# tell FrameManager to manage this frame        
		self._mgr = wx.aui.AuiManager()
		self._mgr.SetManagedWindow(self)
		
		curPath = path.dirname (path.realpath(__file__)) + '/test.xml'
		configTree = ElementTree(file=curPath)
		self._config = configTree.getroot()

		self._mb = ConfMenuBar(self, curPath)
		self.SetMenuBar(self._mb)

		self._tb = ConfToolBar(self, curPath)

		self._creatStatusBar()

		self._panel = ConfTablePanel(self)
		self._mgr.AddPane(self._panel, self._panel.getPanelInfo())
		self._mgr.Update()

	def _creatStatusBar(self):
		confStatusBar = self._config.find('StatusBar')
		self._statusBar = self.CreateStatusBar(len(confStatusBar), wx.ST_SIZEGRIP)
		statusWidth = []	
		for i, confItem in enumerate(confStatusBar):
			statusWidth.append(int(confItem.get('size')))
		self._statusBar.SetStatusWidths(statusWidth)

		for i, confItem in enumerate(confStatusBar):
			self._statusBar.SetStatusText(confItem.get('text'), i)

	def GetStartPosition(self):

		self.x = self.x + 20
		x = self.x
		pt = self.ClientToScreen(wx.Point(0, 0))

		return wx.Point(pt.x + x, pt.y + x)
	
if __name__ == '__main__':
	app = wx.App(0)
	frame = MainWin(None, title='test')	
	app.SetTopWindow(frame)
	frame.Show()

	app.MainLoop()
