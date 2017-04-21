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
import os
from gettext import gettext as gt

import sugar.graphics.style
from sugar.activity import activity

from color import Color


class Constants:

    VERSION = 1

    SERVICE = "org.laptop.Cuadraditos"
    IFACE = SERVICE
    PATH = "/org/laptop/Cuadraditos"
    activityId = None

    keyName = "name"
    keyMime = "mime"
    keyExt = "ext"
    keyIstr = "istr"

    color_black = Color()
    color_black.init_rgba(0, 0, 0, 255)
    color_white = Color()
    color_white.init_rgba(255, 255, 255, 255)
    color_red = Color()
    color_red.init_rgba(255, 0, 0, 255)
    color_green = Color()
    color_green.init_rgba(0, 255, 0, 255)
    color_blue = Color()
    color_blue.init_rgba(0, 0, 255, 255)
    color_button = Color()
    color_button.init_gdk(sugar.graphics.style.COLOR_BUTTON_GREY)

    GFX_PATH = os.path.join(activity.get_bundle_path(), "gfx")
    sound_click = os.path.join(GFX_PATH, 'photoShutter.wav')

    MODE_VIDEO = 1
    MODE_HELP = 2

    #defensive method against variables not translated correctly
    def _(s):
        #todo: permanent variable
        i_strs_test = {}
        for i in range(0, 4):
            i_strs_test[str(i)] = str(i)

        i = s
        try:
            #test translating the string with many replacements
            i = gt(s)
            test = i % i_strs_test
        except:
            #if it doesn't work, revert
            i = s

        return i

    i_str_activity_name = _('Cuadraditos')

    dim_CONTROLBAR_HT = 55

    def __init__(self, ca):
        self.__class__.activityId = ca._activity_id
