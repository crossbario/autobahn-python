###############################################################################
##
##  Copyright 2011-2012 Tavendo GmbH
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

import re
UA_FIREFOX = re.compile(".*Firefox/(\d*).*")
UA_CHROME = re.compile(".*Chrome/(\d*).*")
UA_CHROMEFRAME = re.compile(".*chromeframe/(\d*).*")
UA_WEBKIT = re.compile(".*AppleWebKit/([0-9+\.]*)\w*.*")

# FIXME:

# HP Touchpad: has Qt-WebKit browser with old WS, but has Flash
# Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.5; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/234.83 Safari/534.6 TouchPad/1.0
# current mapping => True True True SUPPORTED
# This is correct, but mapped from the "wrong" code ("Safari")


def _lookupWsSupport(ua):
   """
   Lookup if browser supports WebSocket Hybi-10 or higher natively,
   and if not, whether the web-socket-js Flash bridge works to
   polyfill that.

   Returns a tuple of booleans

      (ws_supported, needs_flash, detected)

      ws_supported = WebSocket is supported
      needs_flash = Flash Bridge is needed for support
      detected = the code has explicitly mapped the support/nosupport

   Params:

      ua = user agent string, i.e. flask.request.user_agent.string
   """

   ## Internet Explorer
   ##
   ## FIXME: handle Windows Phone
   ##
   if ua.find("MSIE") >= 0:
      # IE10 has native support
      if ua.find("MSIE 10") >= 0:
         return (True, False, True)

      # first, check for Google Chrome Frame
      if ua.find("chromeframe") >= 0:
         # Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; chromeframe/11.0.660.0)
         # http://www.chromium.org/developers/how-tos/chrome-frame-getting-started/understanding-chrome-frame-user-agent
         r = UA_CHROMEFRAME.match(ua)
         try:
            v = int(r.groups()[0])
            if v >= 14:
               return (True, False, True)
         except:
            return (False, False, False)

      # Flash fallback
      if ua.find("MSIE 8") >= 0 or ua.find("MSIE 9") >= 0:
         return (True, True, True)

      return (False, False, True)


   ## Firefox
   ##
   if ua.find("Firefox") >= 0:
      # Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0a2) Gecko/20120227 Firefox/12.0a2
      r = UA_FIREFOX.match(ua)
      try:
         v = int(r.groups()[0])
         if v >= 7:
            return (True, False, True)
         elif v >= 3:
            return (True, True, True)
         else:
            return (False, False, True)
      except:
         return (False, False, True)


   ## Safari
   ##
   if ua.find("Safari") >= 0 and not ua.find("Chrome") >= 0:

      ## FIXME: when Apple ships Safari with 6455, fix this total hack!

      # RFC6455:
      # Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534+ (KHTML, like Gecko) Version/5.1.2 Safari/534.52.7
      # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.24+ (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10

      # Hybi-00
      # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.53.11 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10

      # Hixie-76?
      # # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_5_8) AppleWebKit/534.50.2 (KHTML, like Gecko) Version/5.0.6 Safari/533.22.3

      r = UA_WEBKIT.match(ua)
      try:
         v = r.groups()[0]
         if ua.find("Windows") >= 0 and v in ["534+"]:
            return (True, False, True)
         if ua.find("Macintosh") >= 0:
            vv = v.replace('+', '').split('.')
            if (int(vv[0]) == 535 and int(vv[1]) >= 24) or int(vv[0]) > 535:
               return (True, False, True)
      except:
         return (False, False, False)

      return (True, True, True)


   ## Chrome
   ##
   if ua.find("Chrome") >= 0:
      # Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11
      r = UA_CHROME.match(ua)
      try:
         v = int(r.groups()[0])
         if v >= 14:
            return (True, False, True)
         elif v >= 4:
            return (True, True, True)
         else:
            return (False, False, True)
      except:
         return (False, False, False)


   ## Android
   ##
   if ua.find("Android") >= 0:

      ## Firefox Mobile
      ##
      if ua.find("Firefox") >= 0:
         # Mozilla/5.0 (Android; Linux armv7l; rv:10.0.2) Gecko/20120215 Firefox/10.0.2 Fennec/10.0.2
         return (True, False, True)

      ## Chrome for Android
      ##
      if ua.find("CrMo") >= 0:
         # Mozilla/5.0 (Linux; U; Android-4.0.3; en-us; Galaxy Nexus Build/IML74K) AppleWebKit/535.7 (KHTML, like Gecko) CrMo/16.0.912.75 Mobile Safari/535.7
         # http://code.google.com/chrome/mobile/docs/faq.html
         return (True, False, True)

      ## Opera Mobile
      ##
      if ua.find("Opera") >= 0:
         # Opera/9.80 (Android 2.2; Linux; Opera Tablet/ADR-1202231246; U; en) Presto/2.10.254 Version/12.00

         # no native support, Flash bridge does not seem to work
         return (False, False, True)

      ## Android Browser
      ##
      if ua.find("AppleWebKit") >= 0:

         # Samsung Galaxy Tab 1
         # Mozilla/5.0 (Linux; U; Android 2.2; de-de; GT-P1000 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1

         # Samsung Galaxy S
         # Mozilla/5.0 (Linux; U; Android 2.3.3; de-de; GT-I9000 Build/GINGERBREAD) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1

         # Samsung Galaxy Note
         # Mozilla/5.0 (Linux; U; Android 2.3.6; de-de; GT-N7000 Build/GINGERBREAD) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1
         return (True, True, True)

         # Though we return WS = True, and Flash = True here, when the device has no actual Flash support, that
         # will get later detected in JS. This applies to i.e.

         # Samsung Galaxy ACE (no Flash since ARM)
         # Mozilla/5.0 (Linux; U; Android 2.2.1; de-de; GT-S5830 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1

      ## unidentified browser
      ##
      return (False, False, False)


   ## iOS
   ##
   if ua.find("iPhone") >= 0 or ua.find("iPad") >= 0 or ua.find("iPod") >= 0:
      # https://developer.apple.com/library/ios/DOCUMENTATION/AppleApplications/Reference/SafariWebContent/OptimizingforSafarioniPhone/OptimizingforSafarioniPhone.html#//apple_ref/doc/uid/TP40006517-SW3

      ## no native support, no flash, no alternative browsers => no support
      return (False, False, True)


   ## Unidentified / No support
   ##
   return (False, False, False)


UA_DETECT_WS_SUPPORT_DB = {}

def lookupWsSupport(ua, debug = True):
   ws = _lookupWsSupport(ua)
   if debug:
      if not UA_DETECT_WS_SUPPORT_DB.has_key(ua):
         UA_DETECT_WS_SUPPORT_DB[ua] = ws

      if not ws[2]:
         msg = "UNDETECTED"
      elif ws[0]:
         msg = "SUPPORTED"
      elif not ws[0]:
         msg = "UNSUPPORTED"
      else:
         msg = "ERROR"

      print "DETECT_WS_SUPPORT", ua, ws[0], ws[1], ws[2], msg

   return ws
