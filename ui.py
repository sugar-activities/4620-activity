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
import gobject
import pygst
pygst.require('0.10')

import logging
logger = logging.getLogger('cuadraditos:ui.py')

from sugar.activity.widgets import ActivityToolbarButton
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.activity.widgets import StopButton

from constants import Constants
from capture import LiveCaptureWindow
import os


class UI:

    log = logging.getLogger('cuadraditos-ui')

    def __init__(self, pca):
        self.ca = pca
        # listen for ctrl+c & escape key
        self.ca.connect('key-press-event', self._key_press_event_cb)
        self.ACTIVE = False
        self.LAUNCHING = True
        self.ca.add_events(gtk.gdk.VISIBILITY_NOTIFY_MASK)
        self.ca.connect("visibility-notify-event", self._visible_notify_cb)

        self.control_bar_ht = 60

        # True when we're showing live video feed in the primary screen
        self.CAPTUREMODE = True

        #self.inset = self.__class__.dim_INSET

        #init
        self.mapped = False
        self.setup = False

        self.tbars = {Constants.MODE_VIDEO: 1,
                      Constants.MODE_HELP: 2}

        # Use 0.86 toolbar design
        self.toolbox = ToolbarBox()

        # Buttons added to the Activity toolbar
        activity_button = ActivityToolbarButton(self.ca)
        self.toolbox.toolbar.insert(activity_button, 0)
        activity_button.show()
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        separator.show()
        self.toolbox.toolbar.insert(separator, -1)

        # The ever-present Stop Button
        stop_button = StopButton(self)
        stop_button.props.accelerator = '<Ctrl>Q'
        self.toolbox.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.ca.set_toolbar_box(self.toolbox)
        self.toolbox.show()
        self.toolbox_ht = self.toolbox.size_request()[1]
        self.vh = gtk.gdk.screen_height() - \
                  (self.toolbox_ht + self.control_bar_ht)
        self.vw = int(self.vh / .75)

        main_box = gtk.VBox()
        self.ca.set_canvas(main_box)
        main_box.get_parent().modify_bg(gtk.STATE_NORMAL,
                                        Constants.color_black.gColor)
        main_box.show()

        self._play_button = PlayButton()
        self._play_button.connect('clicked', self._button_play_click)
        main_box.pack_start(self._play_button, expand=True)
        self._play_button.show()
        self.setup_windows()

    def _mapEventCb(self, widget, event):
        #when your parent window is ready, turn on the feed of live video
        self.capture_window.disconnect(self.MAP_EVENT_ID)
        self.mapped = True
        self.set_up()

    def set_up(self):
        if (self.mapped and not self.setup):
            self.setup = True
            gobject.idle_add(self.final_setup)

    def final_setup(self):
        self.LAUNCHING = False
        self.ACTIVE = self.ca.get_property("visible")
        self.update_video_components()

        if (self.ACTIVE):
            self.ca.capture.play()

    def setup_windows(self):
        self.window_stack = []

        self.capture_window = LiveCaptureWindow(Constants.color_black.gColor)
        self.add_to_window_stack(self.capture_window, self.ca)
        self.capture_window.set_capture(self.ca.capture)
        self.capture_window.set_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.capture_window.connect("button_release_event",
                                    self._live_button_release_cb)
        self.capture_window.add_events(gtk.gdk.VISIBILITY_NOTIFY_MASK)
        self.capture_window.connect("visibility-notify-event",
                                    self._visible_notify_cb)
        self.capture_window.connect('key-press-event',
                                    self._key_press_event_cb)
        self.hide_all_windows()
        self.MAP_EVENT_ID = self.capture_window.connect_after("map-event",
                                                              self._mapEventCb)
        for i in range(0, len(self.window_stack)):
            self.window_stack[i].show_all()

    def _visible_notify_cb(self, widget, event):

        if (self.LAUNCHING):
            return

        temp_ACTIVE = True

        if (event.state == gtk.gdk.VISIBILITY_FULLY_OBSCURED):

            if (widget == self.ca):
                temp_ACTIVE = False

        if (temp_ACTIVE != self.ACTIVE):
            self.ACTIVE = temp_ACTIVE
            if not self.ACTIVE:
                self.ca.stop_pipes()
                self.capture_window.hide()
                self._play_button.show()

    def add_to_window_stack(self, win, parent):
        self.window_stack.append(win)
        win.set_transient_for(parent)
        win.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        win.set_decorated(False)
        win.set_focus_on_map(False)
        win.set_property("accept-focus", False)
        win.props.destroy_with_parent = True

    def _key_press_event_cb(self, widget, event):

        #todo: trac #4144
        #we listen here for CTRL+C events and game keys, and pass on events to
        #gtk.Entry fields
        keyname = gtk.gdk.keyval_name(event.keyval)

        if (keyname == 'c' and event.state == gtk.gdk.CONTROL_MASK):
            self.ca.close()
        elif (keyname == 'Escape'):
            self.ca.close()

        return False

    def close(self):
        self.ca.stop_pipes()
        self.hide_all_windows()
        self.ca.close()

    def hide_all_windows(self):
        for i in range(0, len(self.window_stack)):
            self.window_stack[i].hide_all()

    def _button_play_click(self, widget):
        self.ca.capture.play()
        self.update_video_components()

    def _live_button_release_cb(self, widget, event):
        self.ca.capture.play()
        self.CAPTUREMODE = True
        self.update_video_components()

    def start_live_video(self, force):
        # We need to know which window and which pipe here

        # if returning from another activity, active won't be false and needs
        # to be to get started
        if (self.ca.capture.window == self.capture_window
            and self.ca.props.active
            and not force):
            self.ca.m.set_updating(True)
            return

        self.ca.m.set_updating(True)
        self.capture_window.set_capture(self.ca.capture)
        self.ca.capture.play()
        self.ca.m.set_updating(False)

    def set_capture_loc_dim(self, win):
        self.smart_resize(win, gtk.gdk.screen_width(),
                          gtk.gdk.screen_height() - self.toolbox_ht)
        backg_loc = self.get_background_wloc()
        self.smart_move(win, backg_loc[0], backg_loc[1])

    def smart_resize(self, win, w, h):
        win_size = win.get_size()
        if ((win_size[0] != w) or (win_size[1] != h)):
            win.resize(w, h)
            return True
        else:
            return False

    def smart_move(self, win, x, y):
        win_loc = win.get_position()
        if ((win_loc[0] != x) or (win_loc[1] != y)):
            win.move(x, y)
            return True
        else:
            return False

    def get_background_wloc(self):
        return [gtk.gdk.screen_width(), self.toolbox_ht]

    def update_video_components(self):
        pos = []
        pos.append({"position": "capture", "window": self.capture_window})
        self.hide_all_windows()
        # Update positions
        self.set_capture_loc_dim(self.capture_window)

        for i in range(0, len(self.window_stack)):
            self.window_stack[i].show_all()

    def debug_windows(self):
        for i in range(0, len(self.window_stack)):
            self.__class__.log.error('%s %s %s' % (self.window_stack[i],
                                     self.window_stack[i].get_size(),
                                     self.window_stack[i].get_position()))


class PlayButton(gtk.Button):
    def __init__(self):
        super(PlayButton, self).__init__()
        self.set_relief(gtk.RELIEF_NONE)
        self.set_focus_on_click(False)
        self.modify_bg(gtk.STATE_ACTIVE, Constants.color_black.gColor)

        path = os.path.join(Constants.GFX_PATH, 'media-play.png')
        self._play_image = gtk.image_new_from_file(path)
        self.set_image(self._play_image)
