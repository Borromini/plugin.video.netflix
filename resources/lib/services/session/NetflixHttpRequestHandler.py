# -*- coding: utf-8 -*-
# Author: asciidisco
# Module: NetflixHttpRequestHandler
# Created on: 07.03.2017
# License: MIT https://goo.gl/5bMj3H

"""Oppionionated internal proxy that dispatches requests to Netflix"""
from __future__ import unicode_literals

import json
import BaseHTTPServer
from SocketServer import TCPServer
from urlparse import urlparse, parse_qs
import resources.lib.common as common
from resources.lib.services.session.NetflixSession import NetflixSession
from resources.lib.services.session.NetflixHttpSubRessourceHandler import \
    NetflixHttpSubRessourceHandler


# get list of methods & instance form the sub ressource handler
METHODS = common.get_class_methods(class_item=NetflixHttpSubRessourceHandler)


class NetflixHttpRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Oppionionated internal proxy that dispatches requests to Netflix"""

    # pylint: disable=invalid-name
    def do_GET(self):
        """
        GET request handler
        (we only need this, as we only do GET requests internally)
        """
        url = urlparse(self.path)
        params = parse_qs(url.query)
        method = params.get('method', [None])[0]

        # not method given
        if method is None:
            self.send_error(500, 'No method declared')
            return

        # no existing method given
        if method not in METHODS:
            error_msg = 'Method "'
            error_msg += str(method)
            error_msg += '" not found. Available methods: '
            error_msg += str(METHODS)
            return self.send_error(404, error_msg)

        # call method & get the result
        result = getattr(self.server.res_handler, method)(params)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        return self.wfile.write(json.dumps({
            'method': method,
            'result': result}))

    def log_message(self, *args):
        """Disable the BaseHTTPServer Log"""
        pass


##################################


class NetflixTCPServer(TCPServer):
    """Override TCPServer to allow shared struct sharing"""

    def __init__(self, server_address):
        """Initializes NetflixTCPServer"""
        common.log('Constructing netflixTCPServer')
        self.res_handler = NetflixHttpSubRessourceHandler(NetflixSession())

        TCPServer.__init__(self, server_address, NetflixHttpRequestHandler)

    def esn_changed(self):
        """Return if the esn has changed on Session initialization"""
        return common.set_esn(self.res_handler.netflix_session.esn)
