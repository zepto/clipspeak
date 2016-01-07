#!/usr/bin/env python
# vim: sw=4:ts=4:sts=4:fdm=indent:fdl=0:
# -*- coding: UTF8 -*-
#
# Tray icon object.
# Copyright (C) 2013 Josiah Gordon <josiahg@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


""" TrayIcon:   An object that creates a simple gtk statusicon.

"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class TrayIcon(object):
    """ A trayicon that has a popup menu.

    """

    def __init__(self, imagename: str, clicked_callback: object):
        """ Create a statusicon using image imagename.

        """

        # Set the call back to notify that the icon was clicked.
        self._clicked_callback = clicked_callback

        self._status_icon = Gtk.StatusIcon.new_from_icon_name(imagename)
        self._status_icon.connect('button_press_event', self._clicked)
        self._menu = Gtk.Menu()

        self._menu_items = {}

    def run(self):
        """ Run the gtk main loop.

        """

        self._menu.show_all()
        Gtk.main()

    def exit(self):
        """ Exit the main loop.

        """

        Gtk.main_quit()

    def add_item(self, label: str, image: Gtk.Image, callback: object):
        """ Add a menu item with a callback.

        """

        if not label:
            item = Gtk.SeparatorMenuItem()
            self._menu.add(item)
            item.show()

            return

        item = Gtk.ImageMenuItem()
        item.set_image(image)
        item.set_label(label)
        item.set_use_underline(True)
        item.connect('button_release_event', callback)

        self._menu.add(item)
        item.show()

        self._menu_items[label] = item

    def toggle_item(self, label: str, value: bool=None):
        """ Toggle a menu item by label.

        """

        item = self._menu_items.get(label, None)
        if item:
            if value is None:
                item.set_sensitive(not item.get_sensitive())
            else:
                item.set_sensitive(value)
            self._menu.hide()

    def _clicked(self, status_icon, event):
        """ Called when the status icon is clicked.

        """

        button = event.button

        if button == 3:
            self._clicked_callback(button)
            self._menu.popup(None, None, None, None, button,
                             Gtk.get_current_event_time())
