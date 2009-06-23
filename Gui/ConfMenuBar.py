import wx
from xml.etree.ElementTree import ElementTree

class ConfMenuBar(wx.MenuBar):

	def __init__(self, parent, configPath):
		wx.MenuBar.__init__(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)
		self._parent = parent
		
		configTree = ElementTree(file=configPath)
		self._config = configTree.getroot()
		
		confMenuBar = self._config.find("MenuBar")
		for configMenu in confMenuBar:
			self._creatMenu(configMenu)
			
	def _creatMenu(self, configMenu):
		menu = wx.Menu()
		for confItem in configMenu:
			self._creatItem(menu, confItem)	
		self.Append(menu, configMenu.get('name'))
	
	def _creatItem(self, menu, configItem):
		itemId = wx.NewId()
		itemName = configItem.get('name')
		if itemName:
			menu.Append(itemId, itemName) 
		else:
			menu.AppendSeparator()
			return 
		self._bindCommand(itemId, configItem)
	
	def _bindCommand(self, itemId, configItem):
		commandName = configItem.get('action')	
		if commandName:
			exec 'import ' + commandName
			exec 'command = ' + commandName + '.' + commandName + '()'

			self._parent.Bind(wx.EVT_MENU, command.svc, id=itemId)
		
