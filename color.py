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
import gtk


class Color:

    def __init__(self):
        pass

    def init_rgba(self, r, g, b, a):
        self._ro = r
        self._go = g
        self._bo = b
        self._ao = a
        self._r = self._ro / 255.0
        self._g = self._go / 255.0
        self._b = self._bo / 255.0
        self._a = self._ao / 255.0

        self._opaque = False
        if (self._a == 1):
            self.opaque = True

        rgb_tup = (self._ro, self._go, self._bo)
        self.hex = self.rgb_to_hex(rgb_tup)
        self.gColor = gtk.gdk.color_parse(self.hex)

    def init_gdk(self, col):
        self.init_hex(col.get_html())

    def init_hex(self, hex):
        cTup = self.hex_to_rgb(hex)
        self.init_rgba(cTup[0], cTup[1], cTup[2], 255)

    def get_int(self):
        return int(self._a * 255) + (int(self._b * 255) << 8) + \
              (int(self._g * 255) << 16) + (int(self._r * 255) << 24)

    def rgb_to_hex(self, rgb_tup):
        hexcolor = '#%02x%02x%02x' % rgb_tup
        return hexcolor

    def hex_to_rgb(self, h):
        c = eval('0x' + h[1:])
        r = (c >> 16) & 0xFF
        g = (c >> 8) & 0xFF
        b = c & 0xFF
        return (int(r), int(g), int(b))
