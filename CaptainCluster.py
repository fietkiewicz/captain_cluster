#!/usr/bin/python
# -*- coding: utf-8 -*-
# Description: This program is a utility created in the lab of Dr. Chris Fietkiewicz at Case Western Reserve University. It is used to run jobs on the HPCC.
# Additional contributors: Joonsue Lee, Jess Herringer, Ethan Platt (2014)

''' Copyright 2015 Chris Fietkiewicz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import wx
import numpy as np
import sys
import os
import subprocess as sub
import re
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
		fitem1 = fileMenu.Append(wx.ID_SAVE, '&Save settings', 'Save settings')
		fitem2 = fileMenu.Append(wx.ID_OPEN, '&Load settings', 'Open settings')
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
		self.scriptName = wx.TextCtrl(self, -1, '', (self.controlWidth, 2*self.controlHeight), (self.controlWidth -5, -1), style=wx.TE_LEFT)
		self.localPath = wx.TextCtrl(self, -1, os.getcwd(),(0, 13*self.controlHeight), (self.controlWidth -5, -1), style=wx.TE_LEFT)
		self.serverPath = wx.TextCtrl(self, -1, '~',(self.controlWidth, 13*self.controlHeight), (self.controlWidth -5, -1), style=wx.TE_LEFT)
		self.runInfo = wx.TextCtrl(self, -1, '', (2*self.controlWidth, 3*2*self.controlHeight), (self.controlWidth -5, 3*2*self.controlHeight), style=wx.TE_MULTILINE | wx.TE_READONLY)
		self.runDirectory = wx.TextCtrl(self, -1, '~', (self.controlWidth, 3*self.controlHeight), (self.controlWidth -5, -1), style=wx.TE_LEFT)
		
		#Creates checklists
		self.sendInfo = wx.CheckListBox(self, -1, pos=(0, 3*2*self.controlHeight), size=(self.controlWidth -5, 3*2*self.controlHeight), style=0)
		self.receiveInfo = wx.CheckListBox(self, -1, pos=(self.controlWidth, 3*2*self.controlHeight), size=(self.controlWidth -5, 3*2*self.controlHeight), style=0)
		
		#Creates buttons
		self.runbtn = wx.Button(self, label='RUN', pos=(2*self.controlWidth, 4*self.controlHeight), size=(self.controlWidth -5, 2*self.controlHeight))
		self.runbtn.Bind(wx.EVT_BUTTON, self.RunRemotely)
		
		self.savebtn = wx.Button(self, label='Save Settings', pos=(2*self.controlWidth, 0), size=(self.controlWidth -5, 2*self.controlHeight))
		self.savebtn.Bind(wx.EVT_BUTTON, self.Save)
		
		self.loadbtn = wx.Button(self, label='Load Settings', pos=(2*self.controlWidth, 2*self.controlHeight), size=(self.controlWidth -5, 2*self.controlHeight))
		self.loadbtn.Bind(wx.EVT_BUTTON, self.Load)
		
		self.sendbtn = wx.Button(self, label='Send To Server', pos=(0, 2*2*self.controlHeight), size=(self.controlWidth -5, 2*self.controlHeight))
		self.sendbtn.Bind(wx.EVT_BUTTON, self.Send)
		
		self.receivebtn = wx.Button(self, label='Receive From Server', pos=(self.controlWidth, 2*2*self.controlHeight), size=(self.controlWidth -5, 2*self.controlHeight))
		self.receivebtn.Bind(wx.EVT_BUTTON, self.Receive)
		
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
		self.fbox.append(self.receiveInfo)
		self.fbox.append(self.runInfo)
		self.fbox.append(self.runDirectory)
		
		self.Show(True)
		
		#opens the input file with the parameter values
		if len(sys.argv) > 1:
			self.fileName.SetValue(sys.argv[1])
			self.Load_cmd()
		
	
	def OnAboutBox(self, e):
		description = """Copyright 2015 Chris Fietkiewicz. License and other information: http://filer.case.edu/cxf47/captain."""
		info = wx.AboutDialogInfo()
		info.SetName('Captain Cluster')
		info.SetVersion('1.1')
		info.SetDescription(description)
		info.AddDeveloper('Chris Fietkiewicz, Joonsue Lee, Jess Herringer, and Ethan Platt')
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
	
	#Loads settings from a text file
	def Load(self, e):
		try:
			filename = self.localPath.GetValue() + '\\' + self.fileName.GetValue()
			f = open('%s' %filename)
			self.settings = f.readlines()
			f.close()
			self.fileName.SetValue(self.settings[0].replace("\n", ""))
			self.scriptName.SetValue(self.settings[1].replace("\n", ""))
			self.runDirectory.SetValue(self.settings[2].replace("\n", ""))
			self.localPath.SetValue(self.settings[3].replace("\n", ""))
			self.serverPath.SetValue(self.settings[4].replace("\n", ""))
			self.server.SetValue(self.settings[5].replace("\n", ""))
			self.Update()
		except IOError:
			wx.wx.MessageBox('Settings file not found in local directory. Make sure the Settings file name and local directory are correct.', 'ERROR', wx.OK | wx.ICON_ERROR)
	
	#Loads settings from a text file given as an argument when running from command line
	def Load_cmd(self):
		f = open(('%s' %self.fileName.GetValue()))
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
		p = sub.Popen('%s\plink %s -l %s -pw "%s" qstat -u %s > %s\RunInfo.tmp' %(self.sshdir,self.server.GetValue(),self.user,self.pswd,self.user,self.sshdir), shell=True)
		p.wait()
		f = open('%s\RunInfo.tmp' %self.sshdir, 'r')
		pending = f.readlines()
		f.close()
		os.remove('RunInfo.tmp')
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
		

			
	def Receive(self, e):
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
		if "~" in self.serverPath.GetValue():
			self.sPath = self.serverPath.GetValue().replace("~", "")
			p = sub.Popen('%s\plink %s -l %s -pw "%s" echo $HOME > %s\Receive.tmp' %(self.sshdir,self.server.GetValue(),self.user,self.pswd,self.sshdir), shell=True)
			p.wait()
			f = open('%s\Receive.tmp' %self.sshdir, 'r')
			self.echo = f.readline()
			f.close()
			os.remove('Receive.tmp')
			self.echo.replace("\n", "")
			self.goodPath = self.echo + self.sPath
			self.goodPath = self.goodPath.replace("\n", "")
		else:
			self.goodPath = self.serverPath.GetValue()
		#Copies selected files from ReceiveInfo
		for i in range(0, len(self.receiveInfo.GetCheckedStrings())):
			p = sub.Popen('%s\pscp -l %s -pw "%s" -sftp %s:%s/%s %s' %(self.sshdir, self.user, self.pswd, self.server.GetValue(), self.goodPath, self.receiveInfo.GetCheckedStrings()[i].replace("\n", ""), self.localPath.GetValue()), shell=True)
			p.wait()
		self.RefreshDirectory(e)
		
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
		s = self.scriptName.GetValue()
		if s[-4:] == '.pbs': # for pbs script
			p = sub.Popen('%s\plink %s -l %s -pw "%s" cd %s; qsub %s > %s/Run.tmp' %(self.sshdir,self.server.GetValue(),self.user,self.pswd,self.runDirectory.GetValue(),self.scriptName.GetValue(),self.sshdir), shell=True)
			p.wait()
			f = open('%s\Run.tmp' %self.sshdir, 'r')
			# NOTE: Doesn't seem to get the sim count reliably 
			#f = open('run.sh' %self.sshdir, 'r')
			sims = f.readlines()
			f.close()
			os.remove('Run.tmp')
			self.runInfo.AppendText('%d jobs started.\n' %(len(sims)))
		elif s[-3:] == '.sh': # for shell script
			p = sub.Popen('%s\plink %s -l %s -pw "%s" cd %s; chmod +x %s; ./%s > %s/Run.tmp' %(self.sshdir,self.server.GetValue(),self.user,self.pswd,self.runDirectory.GetValue(),self.scriptName.GetValue(),self.scriptName.GetValue(),self.sshdir), shell=True)
			p.wait()
			f = open('%s\Run.tmp' %self.sshdir, 'r')
			# NOTE: Doesn't seem to get the sim count reliably 
			#f = open('run.sh' %self.sshdir, 'r')
			sims = f.readlines()
			f.close()
			self.runInfo.AppendText('%d jobs started.\n' %(len(sims)))
		else:
			wx.wx.MessageBox('The script name must end with .pbs or .sh.', 'ERROR', wx.OK | wx.ICON_ERROR)

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
		p = sub.Popen('%s\plink %s -batch -l %s -pw "%s" cd %s; ls > %s\RefreshDirectory.tmp;' %(self.sshdir,self.server.GetValue(),self.user,self.pswd,self.serverPath.GetValue(),self.sshdir), shell=True)
		p.wait()
		f = open('%s\RefreshDirectory.tmp' %self.sshdir, 'r')
		pending = f.readlines()
		f.close()
		os.remove('RefreshDirectory.tmp')
		self.receiveInfo.Destroy()
		self.receiveInfo = wx.CheckListBox(self, -1, pos=(self.controlWidth, 3*2*self.controlHeight), size=(self.controlWidth -5, 3*2*self.controlHeight), choices=pending, style=0)
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
		if "~" in self.serverPath.GetValue():
			self.sPath = self.serverPath.GetValue().replace("~", "")
			p = sub.Popen('%s\plink %s -l %s -pw "%s" echo $HOME > %s\Send.tmp' %(self.sshdir,self.server.GetValue(),self.user,self.pswd,self.sshdir), shell=True)
			p.wait()
			f = open('%s\Send.tmp' %self.sshdir, 'r')
			self.echo = f.readline()
			f.close()
			os.remove('Send.tmp')
			self.echo.replace("\n", "")
			self.goodPath = self.echo + self.sPath
			self.goodPath = self.goodPath.replace("\n", "")
		else:
			self.goodPath = self.serverPath.GetValue()
		#Copies selected files from receiveInfo
		for i in range(0, len(self.sendInfo.GetCheckedStrings())):
			p = sub.Popen('%s\pscp -l %s -pw "%s" -sftp %s\%s %s:%s' %(self.sshdir, self.user, self.pswd, self.localPath.GetValue(), self.sendInfo.GetCheckedStrings()[i].replace("\n", ""), self.server.GetValue(), self.goodPath), shell=True)
			p.wait()
		self.RefreshDirectory(e)
	
	def Quit(self, e):
		self.Close(True)
		
def main():

	ex = wx.App()
	PythonClusterControl(None)
	ex.MainLoop()
	
if __name__ == '__main__':
	main()
