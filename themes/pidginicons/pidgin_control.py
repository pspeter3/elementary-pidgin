#!/usr/bin/env python

#  
#  Copyright (C) 2009-2010 Jason Smith, Rico Tzschichholz
#                2010 Lukasz Piepiora, Robert Dyer
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import atexit
import gobject
import dbus
import dbus.glib
import glib
import sys
import os

try:
	from dockmanager.dockmanager import DockManagerItem, DockManagerSink, DOCKITEM_IFACE
	from signal import signal, SIGTERM
	from sys import exit
except ImportError, e:
	exit()


pidginbus = "im.pidgin.purple.PurpleService"
pidginpath = "/im/pidgin/purple/PurpleObject"
pidginitem = "im.pidgin.purple.PurpleInterface"


class PidginDBus():
	def __init__(self):
		bus = dbus.SessionBus()
		obj = bus.get_object (pidginbus, pidginpath)
		self.iface = dbus.Interface (obj, pidginitem)
		
	def IsConnected(self):
		status = self.iface.PurpleSavedstatusGetCurrent()	
		return not self.iface.PurpleSavedstatusGetType(status) == 1

	def IsAway(self):
		status = self.iface.PurpleSavedstatusGetCurrent()	
		return not self.iface.PurpleSavedstatusGetType(status) == 5

	def getStatus(self):
		status = self.iface.PurpleSavedstatusGetCurrent()	
		return self.iface.PurpleSavedstatusGetType(status)
		
	def Available(self):
		new_status = self.iface.PurpleSavedstatusNew("", 2)
		self.iface.PurpleSavedstatusActivate(new_status)
	
	def Disconnect(self):
		new_status = self.iface.PurpleSavedstatusNew("", 1)
		self.iface.PurpleSavedstatusActivate(new_status)	
	
	def Away(self):
		new_status = self.iface.PurpleSavedstatusNew("", 5)
		self.iface.PurpleSavedstatusActivate(new_status)

	def Busy(self):
		new_status = self.iface.PurpleSavedstatusNew("", 3)
		self.iface.PurpleSavedstatusActivate(new_status)

	def Invisible(self):
		new_status = self.iface.PurpleSavedstatusNew("", 4)
		self.iface.PurpleSavedstatusActivate(new_status)


class PidginItem(DockManagerItem):
	def __init__(self, sink, path):
		DockManagerItem.__init__(self, sink, path)
		self.pidgin = None

		#Menu Items

		self.add_menu_item ("Available", "/usr/share/pixmaps/pidgin/status/16/available.png","Status")
		self.add_menu_item ("Away", "/usr/share/pixmaps/pidgin/status/16/away.png","Status")
		self.add_menu_item ("Busy", "/usr/share/pixmaps/pidgin/status/16/busy.png","Status")
		self.add_menu_item ("Invisible", "/usr/share/pixmaps/pidgin/status/16/invisible.png","Status")
		self.add_menu_item ("Disconnect", "/usr/share/pixmaps/pidgin/status/16/offline.png","Status")
		
		self.bus.add_signal_receiver(self.name_owner_changed_cb,
				dbus_interface='org.freedesktop.DBus',
				signal_name='NameOwnerChanged')
		
		obj = self.bus.get_object ("org.freedesktop.DBus", "/org/freedesktop/DBus")
		self.bus_interface = dbus.Interface(obj, "org.freedesktop.DBus")
		
		self.bus_interface.ListNames (reply_handler=self.list_names_handler, error_handler=self.list_names_error_handler)
		
		self.bus.add_signal_receiver(self.status_changed, "AccountStatusChanged", pidginitem, pidginbus, pidginpath)
		self.bus.add_signal_receiver(self.conversation_updated, "ConversationUpdated", pidginitem, pidginbus, pidginpath)

	def list_names_handler(self, names):
		if pidginbus in names:
			self.init_pidgin_objects()
#			self.set_menu_buttons()
			self.update_badge()

	def list_names_error_handler(self, error):
		print "error getting bus names - %s" % str(error)
	
	def name_owner_changed_cb(self, name, old_owner, new_owner):
		if name == pidginbus:
			if new_owner:
				self.init_pidgin_objects()
			else:
				self.pidgin = None
#			self.set_menu_buttons()
			self.update_badge()
	
	def init_pidgin_objects(self):
		self.pidgin = PidginDBus()
		self.update_icon()

	def status_changed(self, account, old, new):
#		self.set_menu_buttons()
		self.update_icon()
		self.update_badge()

	def update_icon(self):
		status = self.pidgin.getStatus()
		if status == 2:
			status_image = '/usr/share/pixmaps/pidgin/status/48/available.svg'
		elif status == 5:
			status_image = '/usr/share/pixmaps/pidgin/status/48/away.svg'
		elif status == 3:
			status_image = '/usr/share/pixmaps/pidgin/status/48/busy.svg'
		elif status == 4:
			status_image = '/usr/share/pixmaps/pidgin/status/48/invisible.svg'
		elif status == 1:
			status_image = '/usr/share/pixmaps/pidgin/status/48/offline.svg'
		self.set_icon(status_image)
		return True		

	
	def conversation_updated(self, conv, type):
		self.update_badge()

#	def clear_menu_buttons(self):
#		for k in self.id_map.keys():
#			self.remove_menu_item(k)

#	def set_menu_buttons(self):
#		self.clear_menu_buttons()
#				
#		if not self.pidgin or not self.iface:
#			return
#
#		if self.pidgin.IsConnected():
#			if self.pidgin.IsAway():
#				self.add_menu_item ("Set Away", "/usr/share/pixmaps/pidgin/status/16/away.png")
#			else:
#				self.add_menu_item ("Set Available", "/usr/share/pixmaps/pidgin/status/16/available.png")
#			self.add_menu_item ("Disconnect", "/usr/share/pixmaps/pidgin/status/16/offline.png")
#		else:
#			self.add_menu_item ("Connect", "/usr/share/pixmaps/pidgin/status/16/available.png")
		
	def update_badge(self):
		if not self.pidgin:
			self.reset_badge()
			return False
		
		convs = self.pidgin.iface.PurpleGetConversations()
		count = 0
		for conv in convs:
			count = count + self.pidgin.iface.PurpleConversationGetData(conv, "unseen-count")
		if count:
			self.set_badge("%s" % count)
		else:
			self.reset_badge()
		return True
	
	def menu_pressed(self, menu_id):
		menu_id = self.id_map[menu_id]
		
		if menu_id == "Disconnect":
			self.pidgin.Disconnect()
		elif menu_id == "Away":
			self.pidgin.Away()
		elif menu_id == "Invisible":
			self.pidgin.Invisible()
		elif menu_id == "Busy":
			self.pidgin.Busy()
		else:
			self.pidgin.Available()
		
	
class PidginSink(DockManagerSink):
	def item_path_found(self, pathtoitem, item):
		if item.Get(DOCKITEM_IFACE, "DesktopFile", dbus_interface="org.freedesktop.DBus.Properties").endswith ("pidgin.desktop"):
			self.items[pathtoitem] = PidginItem(self, pathtoitem)


pidginsink = PidginSink()

def cleanup ():
	pidginsink.dispose ()

if __name__ == "__main__":
	mainloop = gobject.MainLoop(is_running=True)

	atexit.register (cleanup)
	signal(SIGTERM, lambda signum, stack_frame: exit(1))

	mainloop.run()
