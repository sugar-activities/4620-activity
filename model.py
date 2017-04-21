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
import pygtk
pygtk.require('2.0')
import gobject

import logging
logger = logging.getLogger('cuadraditos:cuadraditos.py')

from constants import Constants


class Model:
    def __init__(self, pca):
        self.ca = pca
        self.MODE = Constants.MODE_VIDEO
        self.UPDATING = True
        self.CAPTURING = False

    def is_video_mode(self):
        return self.MODE == Constants.MODE_VIDEO

    def is_help_mode(self):
        return self.MODE == Constants.MODE_HELP

    def setup_mode(self, type, update):
        if (not type == self.MODE):
            return

        self.set_updating(True)
        if (update):
            self.ca.ui.updateModeChange()
        self.set_updating(False)

    def set_updating(self, upd):
        self.UPDATING = upd

    def do_video_mode(self):
        if (self.MODE == Constants.MODE_VIDEO):
            return

        self.MODE = Constants.MODE_VIDEO
        self.set_updating(True)
        gobject.idle_add(self.setup_mode, self.MODE, True)

    def do_help_mode(self):
        if (self.MODE == Constants.MODE_HELP):
            return

        self.MODE = Constants.MODE_HELP
        self.set_updating(True)
        gobject.idle_add(self.setup_mode, self.MODE, True)
