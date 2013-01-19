""" clipboard.py: Provides a ProcessClipboard object for handling the gtk
clipboard

"""

from gi.repository import Gtk
from gi.repository import Gdk


class ProcessClipboard(object):
    """ Process Clipboard """

    def __init__(self, callback, user_data=None, run=False, selection_type='CLIPBOARD'):
        """ ProcessClipboard(callback) Call callback when owner changes """

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.clipboard.connect('owner-change', self.owner_change, callback, 
                user_data)
        if run:
            self.clipboard.request_text(callback, user_data)

    def owner_change(self, clipboard, event, callback, user_data):
        """ Handler owner change event """

        clipboard.request_text(callback, user_data)
