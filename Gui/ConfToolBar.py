import wx
from xml.etree.ElementTree import ElementTree

class ConfToolBar(wx.ToolBar):

	def __init__(self, parent, configPath):
		wx.ToolBar.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_FLAT | wx.TB_NODIVIDER)

		self._parent = parent
		
		configTree = ElementTree(file=configPath)
		self._config = configTree.getroot()
		
		confToolBar = self._config.find("ToolBar")
		width = int(confToolBar.get('width'))
		height = int(confToolBar.get('height'))
		self._size = wx.Size(width, height) 
		self.SetToolBitmapSize(self._size)

		for configItem in confToolBar:
			self._creatItem(configItem)
			
		self.Realize()
	
	def _creatItem(self, configItem):
		itemName = configItem.get('name')
		if not itemName:
			self.AddSeparator()	
			return 

		itemId = wx.NewId()
		bitmapId = getattr(wx, configItem.get('bitmap'))
		if not bitmapId:
			bitmapId = wx.ART_INFORMATION

		bitmap = wx.ArtProvider_GetBitmap(bitmapId, wx.ART_OTHER, self._size)
		self.AddLabelTool(itemId, itemName, bitmap, shortHelp=itemName, longHelp=configItem.get('longHelp')) 
		self._bindCommand(itemId, configItem)
	
	def _bindCommand(self, itemId, configItem):
		commandName = configItem.get('action')	
		if commandName:
			exec 'import ' + commandName
			exec 'command = ' + commandName + '.' + commandName + '()'

			self._parent.Bind(wx.EVT_MENU, command.svc, id=itemId)
		
