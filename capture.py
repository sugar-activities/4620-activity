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
import pygtk
pygtk.require('2.0')
import pygst
pygst.require('0.10')
import gst
import gst.interfaces
import gobject
gobject.threads_init()
import logging
from constants import Constants
import aplay
import urlparse
from sugar.graphics.alert import ConfirmationAlert, TimeoutAlert


logger = logging.getLogger('cuadraditos:capture.py')


def _is_camera_present():
    v4l2src = gst.element_factory_make('v4l2src')
    if v4l2src.props.device_name is None:
        return False, False

    # Figure out if we can place a framerate limit on the v4l2 element, which
    # in theory will make it all the way down to the hardware.
    # ideally, we should be able to do this by checking caps. However, I can't
    # find a way to do this (at this time, XO-1 cafe camera driver doesn't
    # support framerate changes, but gstreamer caps suggest otherwise)
    pipeline = gst.Pipeline()
    caps = gst.Caps("video/x-raw-yuv")
    fsink = gst.element_factory_make("fakesink")
    pipeline.add(v4l2src, fsink)
    v4l2src.link(fsink, caps)
    pipeline.set_state(gst.STATE_NULL)
    return True

camera_presents = _is_camera_present()


class Capture:
    log = logging.getLogger('cuadraditos-capture')

    def __init__(self, pca):
        self.window = None
        self.ca = pca
        self._eos_cb = None

        self.playing = False

        self.VIDEO_WIDTH = 352
        self.VIDEO_HEIGHT = 288
        self.VIDEO_FRAMERATE = 5
        self.recognized_schemes = ['file', 'ftp', 'gopher', 'http', 'https',
                                   'imap', 'mailto', 'mms', 'news', 'nntp',
                                   'prospero', 'rsync', 'rtsp', 'rtspu',
                                   'sftp', 'shttp', 'sip', 'sips', 'snews',
                                   'svn', 'svn+ssh', 'telnet', 'wais']

        self.pipeline = gst.Pipeline("my-pipeline")
        self.createPipeline()

        self.last_detection = None
        bus = self.pipeline.get_bus()
        bus.enable_sync_message_emission()
        bus.add_signal_watch()
        self.SYNC_ID = bus.connect('sync-message::element',\
                                   self._onSyncMessageCb)
        self.MESSAGE_ID = bus.connect('message', self._onMessageCb)

    def createPipeline(self):
        src = gst.element_factory_make("v4l2src", "camsrc")
        srccaps = gst.Caps('video/x-raw-yuv, width=%s, height=%s' %\
                           (self.VIDEO_WIDTH, self.VIDEO_HEIGHT))
        zbar = gst.element_factory_make("zbar")

        self.pipeline.add(src, zbar)
        src.link(zbar, srccaps)

        xvsink = gst.element_factory_make("xvimagesink", "xvsink")
        xv_available = xvsink.set_state(gst.STATE_PAUSED) != \
                       gst.STATE_CHANGE_FAILURE
        xvsink.set_state(gst.STATE_NULL)

        if not xv_available:
            self.__class__.log.error('xv not available cannot capture video')
            return

        xvsink.set_property("sync", False)
        self.pipeline.add(xvsink)
        zbar.link(xvsink)

    def play(self):
        if not camera_presents:
            return

        self.pipeline.set_state(gst.STATE_PLAYING)
        self.playing = True

    def pause(self):
        self.pipeline.set_state(gst.STATE_PAUSED)
        self.playing = False

    def stop(self):
        self.pipeline.set_state(gst.STATE_NULL)
        self.playing = False

    def is_playing(self):
        return self.playing

    def idlePlayElement(self, element):
        element.set_state(gst.STATE_PLAYING)
        return False

    def blockedCb(self, x, y, z):
        pass

    def _onSyncMessageCb(self, bus, message):
        if message.structure is None:
            return
        if message.structure.get_name() == 'prepare-xwindow-id':
            self.window.set_sink(message.src)
            message.src.set_property('force-aspect-ratio', True)

    def _clipboardGetFuncCb(self, clipboard, selection_data, info, data):
        selection_data.set("text/uri-list", 8, data)

    def _clipboardClearFuncCb(self, clipboard, data):
        pass

    def _copyURIToClipboard(self):
        gtk.Clipboard().set_with_data([('text/uri-list', 0, 0)],
                                      self._clipboardGetFuncCb,
                                      self._clipboardClearFuncCb,
                                      self.last_detection)
        return True

    def _alert_uri_response_cb(self, alert, response_id):
        self.ca.remove_alert(alert)

    def _alert_text_response_cb(self, alert, response_id):
        if response_id is gtk.RESPONSE_OK:
            gtk.Clipboard().set_text(self.last_detection)
        self.ca.remove_alert(alert)

    def _onMessageCb(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            if self._eos_cb:
                cb = self._eos_cb
                self._eos_cb = None
                cb()
        elif t == gst.MESSAGE_ELEMENT:
            s = message.structure
            if s.has_name("barcode"):
                self.stop()
                self.window.hide()
                aplay.play(Constants.sound_click)
                self.last_detection = s['symbol']
                parsedurl = urlparse.urlparse(s['symbol'])
                if parsedurl.scheme in self.recognized_schemes:
                    alert = TimeoutAlert(60)
                    alert.remove_button(gtk.RESPONSE_CANCEL)
                    alert.props.title = 'Direccion detectada!'
                    alert.props.msg = 'La dirección fue copiada al ' +\
                                      'portatapeles. Acceda al ' +\
                                      'marco de Sugar y haga click sobre ' +\
                                      'ella para abrirla en el navegador.'
                    alert.connect('response', self._alert_uri_response_cb)
                    self.ca.add_alert(alert)
                    self._copyURIToClipboard()
                    self.ca.alert.show()
                else:
                    alert = ConfirmationAlert()
                    alert.props.title = 'Texto detectado. ' +\
                                        '¿Desea copiarlo al portapapeles?'
                    alert.props.msg = s['symbol']
                    alert.connect('response', self._alert_text_response_cb)
                    self.ca.add_alert(alert)
                    self.ca.alert.show()

        elif t == gst.MESSAGE_ERROR:
            #todo: if we come out of suspend/resume with errors, then get us
            #      back up and running...
            #todo: handle "No space left on the resource.gstfilesink.c"
            #err, debug = message.parse_error()
            pass


class LiveCaptureWindow(gtk.Window):

    def __init__(self, bgd):
        gtk.Window.__init__(self)

        self.imagesink = None
        self.capture = None

        self.modify_bg(gtk.STATE_NORMAL, bgd)
        self.modify_bg(gtk.STATE_INSENSITIVE, bgd)
        self.unset_flags(gtk.DOUBLE_BUFFERED)
        self.set_flags(gtk.APP_PAINTABLE)

    def set_capture(self, pcapture):
        self.capture = pcapture
        self.capture.window = self

    def set_sink(self, sink):
        if (self.imagesink != None):
            assert self.window.xid
            self.imagesink = None
            del self.imagesink

        self.imagesink = sink
        self.imagesink.set_xwindow_id(self.window.xid)
