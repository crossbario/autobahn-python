###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import json

from autobahn.util import newid

from twisted.web.resource import Resource, NoResource
from twisted.web.server import NOT_DONE_YET
from twisted.web import resource, http

from collections import deque

from protocol import WampProtocol

from twisted.internet import reactor


class WampHttpResourceSessionSend(Resource):
   """
   A Web resource for sending via XHR that is part of a WampHttpResourceSession.
   """

   def __init__(self, parent):
      Resource.__init__(self)
      self._parent = parent

   def render_POST(self, request):
      """
      WAMP message send.
      """
      payload = request.content.read()
      try:
         print "processing received WAMP message", payload
         self._parent.onMessage(payload, False)
      except Exception, e:
         request.setHeader('content-type', 'text/plain; charset=UTF-8')
         request.setResponseCode(http.BAD_REQUEST)
         return "could not unserialize WAMP message [%s]" % e


      request.setResponseCode(http.NO_CONTENT)
      self._parent._parent.setStandardHeaders(request)
      request.setHeader('content-type', 'application/json; charset=utf-8')
      return ""



class WampHttpResourceSessionReceive(Resource):
   """
   A Web resource for receiving via XHR that is part of a WampHttpResourceSession.
   """

   def __init__(self, parent):
      Resource.__init__(self)
      self._parent = parent

      self._queue = deque()
      self._request = None

      def printQueue():
         print "send queue", self._parent._sessionid, self._queue
         if not self._request:
            print "no poll request"
         reactor.callLater(1, printQueue)

      printQueue()


   def queue(self, data):
      self._queue.append(data)
      self._trigger()


   def _trigger(self):
      if self._request and len(self._queue):
         self._request.write('[')
         while len(self._queue) > 0:
            msg = self._queue.popleft()
            self._request.write(msg)
            if len(self._queue):
               self._request.write(',')
         self._request.write(']')
         self._request.finish()
         self._request = None


   def render_POST(self, request):

      self._parent._parent.setStandardHeaders(request)
      request.setHeader('content-type', 'application/json; charset=utf-8')

      self._request = request

      def cancel(err):
         print "cancelling, request gone"
         self._request = None

      request.notifyFinish().addErrback(cancel)

      self._trigger()

      return NOT_DONE_YET



class WampHttpResourceSession(Resource, WampProtocol):
   """
   A Web resource representing an open WAMP session.
   """

   def __init__(self, parent, sessionid):
      Resource.__init__(self)
      self._parent = parent
      self._sessionid = sessionid
      self._serializer = parent._serializers[1]

      self._send = WampHttpResourceSessionSend(self)
      self._receive = WampHttpResourceSessionReceive(self)

      self.putChild("send", self._send)
      self.putChild("receive", self._receive)

      self.onOpen()


   def sendMessage(self, bytes, isBinary):
      print "send", bytes
      self._receive.queue(bytes)



class WampHttpResourceOpen(Resource):
   """
   A Web resource for creating new WAMP sessions.
   """

   def __init__(self, parent):
      Resource.__init__(self)
      self._parent = parent

   def render_POST(self, request):
      self._parent.setStandardHeaders(request)

      payload = request.content.read()
      try:
         options = json.loads(payload)
      except Exception, e:
         return

      request.setHeader('content-type', 'application/json; charset=utf-8')

      sessionid = newid()

      self._parent._sessions[sessionid] = self._parent.protocol(self._parent, sessionid)

      ret = {'session': sessionid}

      return json.dumps(ret)



class WampHttpResource(Resource):
   """
   A WAMP Web base resource.
   """
   protocol = WampHttpResourceSession

   def __init__(self, serializers, debug = False):
      Resource.__init__(self)
      self._serializers = serializers
      self._debug = debug
      self._sessions = {
         'foo': 23      
      }
      #self._options = {
      #}
      #if options is not None:
      #   self._options.update(options)

      print self.protocol

      self.putChild("open", WampHttpResourceOpen(self))

   def getChild(self, name, request):

      print "getChild", name, request.postpath

      if name not in self._sessions:
         return NoResource("No WAMP session '%s'" % name)

      if len(request.postpath) != 1 or request.postpath[0] not in ['send', 'receive']:
         return NoResource("Invalid WAMP session operation '%s'" % request.postpath[0])

      sessionid = name
      op = request.postpath[0]

      print sessionid, op
      print self._sessions
      res = self._sessions[sessionid]
      print res

      return res

   def setStandardHeaders(self, request):
      origin = request.getHeader("Origin")
      if origin is None or origin == "null":
         origin = "*"
      request.setHeader('access-control-allow-origin', origin)
      request.setHeader('access-control-allow-credentials', 'true')
      request.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

      headers = request.getHeader('Access-Control-Request-Headers')
      if headers is not None:
         request.setHeader('Access-Control-Allow-Headers', headers)


   # def putChild(self, path, child):
   #    child.parent = self
   #    Resource.putChild(self, path, child)
    

    #     # Just in case somebody wants to mess with these
    #     self._methods = {
    #         'xhr': XHR,
    #         'xhr_send': XHRSend,
    #         'xhr_streaming': XHRStream,
    #         'eventsource': EventSource,
    #         'htmlfile': HTMLFile,
    #         'jsonp': JSONP,
    #         'jsonp_send': JSONPSend,
    #     }
    #     self._writeMethods = ('xhr_send','jsonp_send')
    #     # Static Resources
    #     self.putChild("info",Info())
    #     self.putChild("iframe.html",IFrame())
    #     self.putChild("websocket",RawWebSocket())
    #     # Since it's constant, we can declare the websocket handler up here
    #     self._websocket = WebSocket()
    #     self._websocket.parent = self
    
    # def getChild(self, name, request):
    #     # Check if it is the greeting url
    #     if not name and not request.postpath:
    #         return self
    #     # Hacks to resove the iframe even when people are dumb
    #     if len(name) > 10 and name[:6] == "iframe" and name[-5:] == ".html":
    #         return self.children["iframe.html"]
    #     # Sessions must have 3 parts, name is already the first. Also, no periods in the loadbalancer
    #     if len(request.postpath) != 2 or "." in name or not name:
    #         return resource.NoResource("No such child resource.")
    #     # Extract session & request type. Discard load balancer
    #     session, name = request.postpath
    #     # No periods in the session
    #     if "." in session or not session:
    #         return resource.NoResource("No such child resource.")
    #     # Websockets are a special case
    #     if name == "websocket":
    #         return self._websocket
    #     # Reject invalid methods
    #     if name not in self._methods:
    #         return resource.NoResource("No such child resource.")
    #     # Reject writes to invalid sessions, unless just checking options
    #     if name in self._writeMethods and session not in self._sessions and request.method != "OPTIONS":
    #         return resource.NoResource("No such child resource.")
    #     # Generate session if doesn't exist, unless just checking options
    #     if session not in self._sessions and request.method != "OPTIONS":
    #         self._sessions[session] = Stub(self, session)
    #     # Delegate request to appropriate handler
    #     return self._methods[name](self, self._sessions[session] if request.method != "OPTIONS" else None)
    
    # def setBaseHeaders(self, request, cookie=True):
    #     origin = request.getHeader("Origin")
    #     headers = request.getHeader('Access-Control-Request-Headers')
    #     if origin is None or origin == "null":
    #         origin = "*"
    #     request.setHeader('access-control-allow-origin', origin)
    #     request.setHeader('access-control-allow-credentials', 'true')
    #     request.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    #     if headers is not None:
    #         request.setHeader('Access-Control-Allow-Headers', headers)
    #     if self._options["cookie_needed"] and cookie:
    #         cookie = request.getCookie("JSESSIONID") if request.getCookie("JSESSIONID") else "dummy"
    #         request.addCookie("JSESSIONID", cookie, path="/")
    
   def render_GET(self, request):
#      self.setBaseHeaders(request,False)
      request.setHeader('content-type', 'text/plain; charset=UTF-8')
      return "Welcome to SockJS!\n"

   def render_POST(self, request):
      #return "Hello"
      try:
         payload = request.content.read()
         options = json.loads(payload)
      except Exception, e:
         return

      print options

      def finish():
         request.write("Hello delayed")
         request.finish()

      def cancel(err, call):
         print "cancelling, request gone"
         call.cancel()

      call = reactor.callLater(1, finish)
      request.notifyFinish().addErrback(cancel, call)

      return NOT_DONE_YET
