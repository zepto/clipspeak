#!/usr/bin/env python
# vim: sw=4:ts=4:sts=4:fdm=indent:fdl=0:
# -*- coding: UTF8 -*-
#
# An object for reading the clipboard.
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


""" A clipboard reader controled by a gtk status icons popup menu.

"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository.Gdk import SELECTION_CLIPBOARD

from .clipboard import ProcessClipboard
from .trayicon import TrayIcon
from .speaker import Reader


class ClipSpeak(object):
    """ Handle clipboard and trayicon events, and read the clipboard contents.

    """

    def __init__(self):
        """ Initialize stuff.

        """

        # Get the clipboard contents.
        clipboard = Gtk.Clipboard.get(SELECTION_CLIPBOARD)
        self._text = clipboard.wait_for_text()
        if not self._text:
            self._text = "The clipboard contains no text to read."

        # Create an object to handle clipboard events.
        self._clipboard = ProcessClipboard(self._get_text)

        # Create reader object.
        self._reader = Reader()

        # Create the trayicon
        self._trayicon = TrayIcon("face-monkey", self._clicked)

        icon = Gio.ThemedIcon.new_with_default_fallbacks('media-playback-start-symbolic')
        image = Gtk.Image()
        image.set_from_gicon(icon, Gtk.IconSize.MENU)
        self._trayicon.add_item('Play', image, self._read)

        icon = Gio.ThemedIcon.new_with_default_fallbacks('media-playback-pause-symbolic')
        image = Gtk.Image()
        image.set_from_gicon(icon, Gtk.IconSize.MENU)
        self._trayicon.add_item('Pause', image, self._pause)

        icon = Gio.ThemedIcon.new_with_default_fallbacks('media-playback-stop-symbolic')
        image = Gtk.Image()
        image.set_from_gicon(icon, Gtk.IconSize.MENU)
        self._trayicon.add_item('Stop', image, self._stop)

        self._trayicon.add_item('', None, None)

        icon = Gio.ThemedIcon.new_with_default_fallbacks('window-close-symbolic')
        image = Gtk.Image()
        image.set_from_gicon(icon, Gtk.IconSize.MENU)
        self._trayicon.add_item('Exit', image, self._exit)

        # Start gtk loop
        self._trayicon.run()

    def _clicked(self, button):
        """ The trayicon was clicked so toggle the items.

        """

        # Toggle the menu items.
        if self._reader.playing and not self._reader.paused:
            self._trayicon.toggle_item('Play', False)
            self._trayicon.toggle_item('Pause', True)
            self._trayicon.toggle_item('Stop', True)
        elif self._reader.paused:
            self._trayicon.toggle_item('Play', True)
            self._trayicon.toggle_item('Pause', False)
            self._trayicon.toggle_item('Stop', True)
        else:
            self._trayicon.toggle_item('Play', True)
            self._trayicon.toggle_item('Pause', False)
            self._trayicon.toggle_item('Stop', False)

    def _get_text(self, clipboard, text, userdata):
        """ Process the text.

        """

        if text:
            self._text = text
        else:
            self._text = "The clipboard contains no text to read."

    def _read(self, *args):
        """ Callback for a gtk menuitem.

        """

        if not self._reader.playing:
            self._reader.read(self._text)

        self._reader.play()

    def _pause(self, *args):
        """ Callback for a gtk menuitem.

        """

        self._reader.pause()

    def _stop(self, *args):
        """ Callback for a gtk menuitem.

        """

        self._reader.stop()

    def _exit(self, *args):
        """ Callback for a gtk menuitem.

        """

        self._stop()
        self._trayicon.exit()
