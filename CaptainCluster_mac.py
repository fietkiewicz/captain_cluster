#!/usr/bin/python
# -*- coding: utf-8 -*-
# Description: This program is a utility created in the lab of Dr. Chris Fietkiewicz at Case Western Reserve University. It is used to access, copy and run jobs on the HPCC.
# Contributors: Joonsue Lee (2012), Jess Herringer (2013), Ethan Platt (2014)

import wx
import sys
import os
import subprocess as sub
import re
import pexpect
from wx.lib.buttons import GenBitmapTextButton
		
class PythonClusterControl(wx.Frame):

	def __init__(self, *args, **kw):
		super(PythonClusterControl, self).__init__(*args, **kw)
		
		#Goes Through Main program
		self.InitUI()
		
	def InitUI(self):
		
		#Sets the size
		windowWidth = 600
		windowHeight = 460
		self.controlWidth = windowWidth / 3
		self.controlHeight = 25
		self.SetTitle('Captain Cluster')
		self.SetSize((windowWidth + 10, windowHeight))
		self.Centre()
		
		#Sets up directory variables
		self.sshdir = os.getcwd()
		
		#Creates a Menubar
		menubar = wx.MenuBar()
		fileMenu = wx.Menu()
		fitem1 = fileMenu.Append(wx.ID_SAVE, '&Save', 'Save settings')
		fitem2 = fileMenu.Append(wx.ID_OPEN, '&Open', 'Open settings')
		fitem3 = fileMenu.Append(wx.ID_EXIT, '&Quit', 'Quit application')
		menubar.Append(fileMenu, '&File')
		self.SetMenuBar(menubar)
		self.Bind(wx.EVT_MENU, self.Save, fitem1)
		self.Bind(wx.EVT_MENU, self.Load, fitem2)
		self.Bind(wx.EVT_MENU, self.Quit, fitem3)
		
		#Creates About Box in Menu
		help = wx.Menu()
		help.Append(100, '&About')
		self.Bind(wx.EVT_MENU, self.OnAboutBox, id=100)
		menubar.Append(help, '&Help')
		self.SetMenuBar(menubar)
		
		#Creates necessary StaticTexts
		self.stxt = []
		self.stxt.append(wx.StaticText(self, -1, 'Settings', (0, 0)))
		self.stxt.append(wx.StaticText(self, -1, 'Server', (0, self.controlHeight)))
		self.stxt.append(wx.StaticText(self, -1, 'Script', (0, 2*self.controlHeight)))
		self.stxt.append(wx.StaticText(self, -1, 'Run Directory', (0, 3*self.controlHeight)))
		self.stxt.append(wx.StaticText(self, -1, 'Local Directory', (0, 12*self.controlHeight)))
		self.stxt.append(wx.StaticText(self, -1, 'Server Directory', (self.controlWidth, 12*self.controlHeight)))
		
		self.dscrptn = []
				
		#Creates textboxes
		self.fileName = wx.TextCtrl(self, -1, 'Settings.txt', (self.controlWidth, 0), (self.controlWidth -5, -1), style=wx.TE_LEFT)
		self.server = wx.TextCtrl(self, -1, 'hpclogin.case.edu',(self.controlWidth, self.controlHeight), (self.controlWidth -5, -1), style=wx.TE_LEFT)
		self.scriptName = wx.TextCtrl(self, -1, 'run.sh', (self.controlWidth, 2*self.controlHeight), (self.controlWidth -5, -1), style=wx.TE_LEFT)
		self.localPath = wx.TextCtrl(self, -1, os.getcwd(),(0, 13*self.controlHeight), (self.controlWidth -5, -1), style=wx.TE_LEFT)
		self.serverPath = wx.TextCtrl(self, -1, '~',(self.controlWidth, 13*self.controlHeight), (self.controlWidth -5, -1), style=wx.TE_LEFT)
		self.runInfo = wx.TextCtrl(self, -1, '', (2*self.controlWidth, 3*2*self.controlHeight), (self.controlWidth -5, 3*2*self.controlHeight), style=wx.TE_MULTILINE | wx.TE_READONLY)
		self.runDirectory = wx.TextCtrl(self, -1, '~', (self.controlWidth, 3*self.controlHeight), (self.controlWidth -5, -1), style=wx.TE_LEFT)
		
		#Creates checklists
		self.sendInfo = wx.CheckListBox(self, -1, pos=(0, 3*2*self.controlHeight), size=(self.controlWidth -5, 3*2*self.controlHeight), style=0)
		self.recieveInfo = wx.CheckListBox(self, -1, pos=(self.controlWidth, 3*2*self.controlHeight), size=(self.controlWidth -5, 3*2*self.controlHeight), style=0)
		
		#Creates buttons
		self.runbtn = wx.Button(self, label='RUN', pos=(2*self.controlWidth, 4*self.controlHeight), size=(self.controlWidth -5, 2*self.controlHeight))
		self.runbtn.Bind(wx.EVT_BUTTON, self.RunRemotely)
		
		self.savebtn = wx.Button(self, label='Save Settings', pos=(2*self.controlWidth, 0), size=(self.controlWidth -5, 2*self.controlHeight))
		self.savebtn.Bind(wx.EVT_BUTTON, self.Save)
		
		self.loadbtn = wx.Button(self, label='Load Settings', pos=(2*self.controlWidth, 2*self.controlHeight), size=(self.controlWidth -5, 2*self.controlHeight))
		self.loadbtn.Bind(wx.EVT_BUTTON, self.Load)
		
		self.sendbtn = wx.Button(self, label='Send', pos=(0, 2*2*self.controlHeight), size=(self.controlWidth -5, 2*self.controlHeight))
		self.sendbtn.Bind(wx.EVT_BUTTON, self.Send)
		
		self.recievebtn = wx.Button(self, label='Recieve', pos=(self.controlWidth, 2*2*self.controlHeight), size=(self.controlWidth -5, 2*self.controlHeight))
		self.recievebtn.Bind(wx.EVT_BUTTON, self.Recieve)
		
		self.refreshDirectorybtn = wx.Button(self, label='Refresh Directories', pos=(0, 14*self.controlHeight), size=(2*self.controlWidth -5, 2*self.controlHeight))
		self.refreshDirectorybtn.Bind(wx.EVT_BUTTON, self.RefreshDirectory)
		
		self.runInfobtn = wx.Button(self, label='Run Information', pos=(2*self.controlWidth, 12*self.controlHeight), size=(self.controlWidth -5, 2*self.controlHeight))
		self.runInfobtn.Bind(wx.EVT_BUTTON, self.RunInfo)
		
		self.loginbtn = wx.Button(self, label='Login', pos=(2*self.controlWidth, 14*self.controlHeight), size=(self.controlWidth -5, 2*self.controlHeight))
		self.loginbtn.Bind(wx.EVT_BUTTON, self.Login)
		
		self.fbox = []
		self.fbox.append(self.scriptName)
		self.fbox.append(self.localPath)
		self.fbox.append(self.fileName)
		self.fbox.append(self.serverPath)
		self.fbox.append(self.sendInfo)
		self.fbox.append(self.recieveInfo)
		self.fbox.append(self.runInfo)
		self.fbox.append(self.runDirectory)
		
		self.Show(True)
		
		#opens the input file with the parameter values
		if len(sys.argv) > 1:
			self.fileName.SetValue(sys.argv[1])
			self.Load_cmd()
		
	
	def OnAboutBox(self, e):
	
		description = """This program is a utility created in the lab of Dr. Chris Fietkiewicz at Case Western Reserve University. It is used to access, copy and run jobs on the HPCC."""
		info = wx.AboutDialogInfo()
		
		info.SetName('Cluster Control')
		info.SetVersion('1.0')
		info.SetDescription(description)
		info.AddDeveloper('Chris Fietkiewicz, Joonsue Lee (2012), Jess Herringer (2013), Ethan Platt (2014)')
		
		wx.AboutBox(info)
		
	def Save(self, e):
	#Saves specified settings in a separate file
		f = open(self.fileName.GetValue(), 'w')
		f.write(self.fileName.GetValue() + '\n')
		f.write(self.scriptName.GetValue() + '\n')
		f.write(self.runDirectory.GetValue() + '\n')
		f.write(self.localPath.GetValue() + '\n')
		f.write(self.serverPath.GetValue() + '\n')
		f.write(self.server.GetValue() + '\n')
		f.close()
	
	def Login(self, e):
	#changes the username and password
		dlg = wx.TextEntryDialog(self, 'Please Enter Username: ', 'User', '')
		if dlg.ShowModal() == wx.ID_OK:
			self.user = dlg.GetValue()
		dlg.Destroy()
		dlg = wx.PasswordEntryDialog(self, 'Please Enter Password: ', 'Password', '')
		if dlg.ShowModal() == wx.ID_OK:
			self.pswd = dlg.GetValue()
		dlg.Destroy()
		
	def Load(self, e):
	#Loads settings from a text file
		#the file dialog
		style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
		dialog = wx.FileDialog(None, 'Open', style=style)
		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPath()
		else:
			path = self.fileName.GetValue()
		dialog.Destroy()
		#end of dialog
		self.fileName.SetValue(path)
		f = open('%s' %self.fileName.GetValue())
		self.settings = f.readlines()
		f.close()
		self.fileName.SetValue(self.settings[0].replace("\n", ""))
		self.scriptName.SetValue(self.settings[1].replace("\n", ""))
		self.runDirectory.SetValue(self.settings[2].replace("\n", ""))
		self.localPath.SetValue(self.settings[3].replace("\n", ""))
		self.serverPath.SetValue(self.settings[4].replace("\n", ""))
		self.server.SetValue(self.settings[5].replace("\n", ""))
		self.Update()
	
	def Load_cmd(self):
	#Loads settings from a text file
		f = open('%s' %self.fileName.GetValue())
		self.settings = f.readlines()
		f.close()
		self.fileName.SetValue(self.settings[0].replace("\n", ""))
		self.scriptName.SetValue(self.settings[1].replace("\n", ""))
		self.runDirectory.SetValue(self.settings[2].replace("\n", ""))
		self.localPath.SetValue(self.settings[3].replace("\n", ""))
		self.serverPath.SetValue(self.settings[4].replace("\n", ""))
		self.server.SetValue(self.settings[5].replace("\n", ""))
		self.Update()
	
	def RunInfo(self,e):
		#Tries to access the username variable and prompts dialog boxes if no username is stored
		try:
			a = self.user
		except AttributeError:
			dlg = wx.TextEntryDialog(self, 'Please Enter Username: ', 'User', '')
			if dlg.ShowModal() == wx.ID_OK:
				self.user = dlg.GetValue()
			dlg.Destroy()
			dlg = wx.PasswordEntryDialog(self, 'Please Enter Password: ', 'Password', '')
			if dlg.ShowModal() == wx.ID_OK:
				self.pswd = dlg.GetValue()
			dlg.Destroy()
		
		#Checks how many simulations are still running
		p = sub.Popen('%s\plink %s -l %s -pw "%s" qstat -u %s > %s\log.txt' %(self.sshdir,self.server.GetValue(),self.user,self.pswd,self.user,self.sshdir), shell=True)
		p.wait()
		
		child = pexpect.spawn('ssh %s -l %s qstat -u %s > %s/log.txt' %(self.server.GetValue(),self.user,self.user,self.serverPath.GetValue()))
		child.expect('%s@%s\'s password: ' %(self.user,self.server.GetValue()))
		child.sendline('%s' %(self.pswd))
		child.interact()
		child2 = pexpect.spawn('scp %s@%s:%s/log.txt %s/log.txt' %(self.user,self.server.GetValue(),self.serverPath.GetValue(),self.sshdir))
		child2.expect('%s@%s\'s password: ' %(self.user,self.server.GetValue()))
		child2.sendline('%s' %(self.pswd))
		child2.interact()
		child3 = pexpect.spawn('ssh %s -l %s cd %s; rm log.txt' %(self.server.GetValue(),self.user,self.serverPath.GetValue()))
		child3.expect('%s@%s\'s password: ' %(self.user,self.server.GetValue()))
		child3.sendline('%s' %(self.pswd))
		child3.interact()
		
		f = open('%s/log.txt' %self.sshdir, 'r')
		pending = f.readlines()
		f.close()
		completed = 0
		total = len(pending)
		for i in range(0,total-1):
			if (" C " in pending.pop()):
				completed = completed + 1
		running = total - completed
		
		if running > 0:
			self.runInfo.AppendText('%d jobs running. \n' %((running -5)))
		else:
			self.runInfo.AppendText('%d jobs running. \n' %(running))
		

			
	def Recieve(self, e):
		#Tries to access the username variable and prompts dialog boxes if no username is stored
		try:
			a = self.user
		except AttributeError:
			dlg = wx.TextEntryDialog(self, 'Please Enter Username: ', 'User', '')
			if dlg.ShowModal() == wx.ID_OK:
				self.user = dlg.GetValue()
			dlg.Destroy()
			dlg = wx.PasswordEntryDialog(self, 'Please Enter Password: ', 'Password', '')
			if dlg.ShowModal() == wx.ID_OK:
				self.pswd = dlg.GetValue()
			dlg.Destroy()
		#Copies selected files from recieveInfo
		for i in range(0, len(self.recieveInfo.GetCheckedStrings())):
			child = pexpect.spawn('scp %s@%s:%s/%s %s' %(self.user,self.server.GetValue(),self.serverPath.GetValue(),self.recieveInfo.GetCheckedStrings()[i].replace("\n", ""),self.localPath.GetValue()))
			child.expect('%s@%s\'s password: ' %(self.user,self.server.GetValue()))
			child.sendline('%s' %(self.pswd))
			child.interact()
		
		
	def RunRemotely(self,e):
		#Tries to access the username variable and prompts dialog boxes if no username is stored
		try:
			a = self.user
		except AttributeError:
			dlg = wx.TextEntryDialog(self, 'Please Enter Username: ', 'User', '')
			if dlg.ShowModal() == wx.ID_OK:
				self.user = dlg.GetValue()
			dlg.Destroy()
			dlg = wx.PasswordEntryDialog(self, 'Please Enter Password: ', 'Password', '')
			if dlg.ShowModal() == wx.ID_OK:
				self.pswd = dlg.GetValue()
			dlg.Destroy()
		
		#Submits run.sh to be run on the HPCC
		child = pexpect.spawn('ssh %s -l %s cd %s; chmod +x %s; ./%s > log.txt' %(self.server.GetValue(),self.user,self.runDirectory.GetValue(),self.scriptName.GetValue(),self.scriptName.GetValue()))
		child.expect('%s@%s\'s password: ' %(self.user,self.server.GetValue()))
		child.sendline('%s' %(self.pswd))
		child.interact()
		child2 = pexpect.spawn('scp %s@%s:%s/log.txt %s/log.txt' %(self.user,self.server.GetValue(),self.runDirectory.GetValue(),self.sshdir))
		child2.expect('%s@%s\'s password: ' %(self.user,self.server.GetValue()))
		child2.sendline('%s' %(self.pswd))
		child2.interact()
		child3 = pexpect.spawn('ssh %s -l %s cd %s; rm log.txt' %(self.server.GetValue(),self.user,self.runDirectory.GetValue()))
		child3.expect('%s@%s\'s password: ' %(self.user,self.server.GetValue()))
		child3.sendline('%s' %(self.pswd))
		child3.interact()
		
		f = open('%s/log.txt' %self.sshdir, 'r')
		# NOTE: Doesn't seem to get the sim count reliably 
		#f = open('run.sh' %self.sshdir, 'r')
		sims = f.readlines()
		f.close()
		self.runInfo.AppendText('%d jobs started.\n' %(len(sims)))
			
	
	def RefreshDirectory(self, e):
		#Tries to access the username variable and prompts dialog boxes if no username is stored
		try:
			a = self.user
		except AttributeError:
			dlg = wx.TextEntryDialog(self, 'Please Enter Username: ', 'User', '')
			if dlg.ShowModal() == wx.ID_OK:
				self.user = dlg.GetValue()
			dlg.Destroy()
			dlg = wx.PasswordEntryDialog(self, 'Please Enter Password: ', 'Password', '')
			if dlg.ShowModal() == wx.ID_OK:
				self.pswd = dlg.GetValue()
			dlg.Destroy()
		child = pexpect.spawn('ssh %s -l %s cd %s; ls > ls.txt' %(self.server.GetValue(),self.user,self.serverPath.GetValue()))
		child.expect('%s@%s\'s password: ' %(self.user,self.server.GetValue()))
		child.sendline('%s' %(self.pswd))
		child.interact()
		child2 = pexpect.spawn('scp %s@%s:%s/ls.txt %s/ls.txt' %(self.user,self.server.GetValue(),self.serverPath.GetValue(),self.sshdir))
		child2.expect('%s@%s\'s password: ' %(self.user,self.server.GetValue()))
		child2.sendline('%s' %(self.pswd))
		child2.interact()
		child3 = pexpect.spawn('ssh %s -l %s cd %s; rm ls.txt' %(self.server.GetValue(),self.user,self.serverPath.GetValue()))
		child3.expect('%s@%s\'s password: ' %(self.user,self.server.GetValue()))
		child3.sendline('%s' %(self.pswd))
		child3.interact()		
		
		f = open('%s/ls.txt' %self.sshdir, 'r')
		pending = f.readlines()
		f.close()
		self.recieveInfo.Destroy()
		self.recieveInfo = wx.CheckListBox(self, -1, pos=(self.controlWidth, 3*2*self.controlHeight), size=(self.controlWidth -5, 3*2*self.controlHeight), choices=pending, style=0)
		local = os.listdir('%s' %self.localPath.GetValue())
		self.sendInfo.Destroy()
		self.sendInfo = wx.CheckListBox(self, -1, pos=(0, 3*2*self.controlHeight), size=(self.controlWidth -5, 3*2*self.controlHeight), choices=local, style=0)
	
	
	def Send(self, e):
		#Tries to access the username variable and prompts dialog boxes if no username is stored
		try:
			a = self.user
		except AttributeError:
			dlg = wx.TextEntryDialog(self, 'Please Enter Username: ', 'User', '')
			if dlg.ShowModal() == wx.ID_OK:
				self.user = dlg.GetValue()
			dlg.Destroy()
			dlg = wx.PasswordEntryDialog(self, 'Please Enter Password: ', 'Password', '')
			if dlg.ShowModal() == wx.ID_OK:
				self.pswd = dlg.GetValue()
			dlg.Destroy()
		#Copies selected files from recieveInfo
		for i in range(0, len(self.sendInfo.GetCheckedStrings())):
			child = pexpect.spawn('scp %s/%s %s@%s:%s' %(self.localPath.GetValue(),self.sendInfo.GetCheckedStrings()[i].replace("\n", ""),self.user,self.server.GetValue(),self.serverPath.GetValue()))
			child.expect('%s@%s\'s password: ' %(self.user,self.server.GetValue()))
			child.sendline('%s' %(self.pswd))
			child.interact()
		
	
	def Quit(self, e):
		self.Close(True)
		
def main():

	ex = wx.App()
	PythonClusterControl(None)
	ex.MainLoop()
	
if __name__ == '__main__':
	main()
