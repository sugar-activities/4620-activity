# -*- coding: UTF-8 -*-
# Copyright (c) 2012, Miguel Paolino <mpaolino@ideal.com.uy>
# This file is part of Cuadraditos.
#
# Cuadraditos is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cuadraditos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cuadraditos.  If not, see <http://www.gnu.org/licenses/>.
import gobject
import logging
import pygst
pygst.require('0.10')
import gst

logger = logging.getLogger('cuadraditos:cuadraditos.py')

from sugar.activity import activity

from model import Model
from ui import UI
from capture import Capture
from constants import Constants


gst.debug_set_active(True)
gst.debug_set_colored(False)

if logging.getLogger().level <= logging.DEBUG:
    gst.debug_set_default_threshold(gst.LEVEL_WARNING)
else:
    gst.debug_set_default_threshold(gst.LEVEL_ERROR)


class Cuadraditos(activity.Activity):

    log = logging.getLogger('cuadraditos-activity')

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        #flags for controlling the writing to the datastore
        self.I_AM_CLOSING = False
        self.I_AM_SAVED = False
        self.props.enable_fullscreen_mode = False
        self.ui = None
        Constants(self)
        #self.modify_bg(gtk.STATE_NORMAL, Constants.color_black.gColor)

        #wait a moment so that our debug console capture mistakes
        gobject.idle_add(self._initme, None)

    def _initme(self, userdata=None):
        #the main classes
        self.m = Model(self)
        self.capture = Capture(self)
        self.ui = UI(self)

        return False

    def stop_pipes(self):
        self.capture.stop()

    def restart_pipes(self):
        self.capture.stop()
        self.capture.play()

    def close(self):
        self.I_AM_CLOSING = True
        self.m.UPDATING = False
        if (self.ui != None):
            self.ui.hide_all_windows()
        if (self.capture != None):
            self.capture.stop()

        #this calls write_file
        activity.Activity.close(self)

    def destroy(self):
        if self.I_AM_SAVED:
            activity.Activity.destroy(self)
