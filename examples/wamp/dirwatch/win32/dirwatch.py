###############################################################################
##
##  Copyright 2013 Tavendo GmbH
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

import os
import os.path

import pywintypes

import win32file
import win32con
import win32event

import ntsecuritycon



class DirWatcher:
   """
   Watches a directory (optional recursively) for file system changes.

   Infos:
     * http://msdn.microsoft.com/en-us/library/windows/desktop/aa365465%28v=vs.85%29.aspx
     * http://www.themacaque.com/?p=859
     * http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
   """

   _ACTIONS = {1: 'CREATE',
               2: 'DELETE',
               3: 'MODIFY',
               4: 'MOVEFROM',
               5: 'MOVETO'}

   def __init__(self, dir = '.', recurse = True, asynch = True, timeout = 200):
      """
      Directory change watcher. After creation, you will call loop() providing
      a callback that fires when changes are detected. If running asynch == True,
      you can stop() the loop, even when no change events happen (which is generally,
      desirable!).

      To use this class with Twisted, you should deferToThread the loop().

      :param dir: Directory to watch.
      :type dir: str
      :param recurse: Watch all subdirectories also - recursively.
      :type recurse: bool
      :param asynch: Iff true, use IOCP looping, which can be interrupted by calling stop().
      :type asynch: bool
      :param timeout: Iff asynch, timeout for the event loop.
      :type timeout: int
      """

      self.dir = os.path.abspath(dir)
      self.recurse = recurse
      self.stopped = False
      self.asynch = asynch
      self.timeout = timeout

      ## listening filter
      self.filter = win32con.FILE_NOTIFY_CHANGE_FILE_NAME | \
                    win32con.FILE_NOTIFY_CHANGE_DIR_NAME | \
                    win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES | \
                    win32con.FILE_NOTIFY_CHANGE_SIZE | \
                    win32con.FILE_NOTIFY_CHANGE_LAST_WRITE | \
                    win32con.FILE_NOTIFY_CHANGE_SECURITY | \
                    0

      fflags = win32con.FILE_FLAG_BACKUP_SEMANTICS
      if self.asynch:
         fflags |= win32con.FILE_FLAG_OVERLAPPED
         self.loop = self.loop_asynchronous
      else:
         self.loop = self.loop_synchronous

      ## base directory object watched
      self.hdir = win32file.CreateFile(self.dir,
                                       ntsecuritycon.FILE_LIST_DIRECTORY,
                                       win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                                       None,
                                       win32con.OPEN_EXISTING,
                                       fflags,
                                       None)

   def stop(self):
      self.stopped = True


   def loop_synchronous(self, callback):

      print "loop_synchronous"
      while not self.stopped:
         ##
         ## This will block until notification.
         ##
         results = win32file.ReadDirectoryChangesW(self.hdir,
                                                   8192,
                                                   self.recurse,
                                                   self.filter,
                                                   None,
                                                   None)
         print results
         r = [(DirWatcher._ACTIONS.get(x[0], "UNKNOWN"), x[1]) for x in results]
         if len(r) > 0:
            callback(r)



   def loop_asynchronous(self, callback):
      print "loop_asynchronous"

      buf = win32file.AllocateReadBuffer(8192)
      overlapped = pywintypes.OVERLAPPED()
      overlapped.hEvent = win32event.CreateEvent(None, 0, 0, None)

      while not self.stopped:

         win32file.ReadDirectoryChangesW(self.hdir,
                                         buf,
                                         self.recurse,
                                         self.filter,
                                         overlapped)

         ##
         ## This will block until notification OR timeout.
         ##
         rc = win32event.WaitForSingleObject(overlapped.hEvent, self.timeout)
         if rc == win32event.WAIT_OBJECT_0:
            ## got event: determine data length ..
            n = win32file.GetOverlappedResult(self.hdir, overlapped, True)
            if n:
               ## retrieve data
               results = win32file.FILE_NOTIFY_INFORMATION(buf, n)
               print results
               r = [(DirWatcher._ACTIONS.get(x[0], "UNKNOWN"), x[1]) for x in results]
               if len(r) > 0:
                  callback(r)
            else:
               # directory handled was closed
               self.stopped = True
         else:
            #print "timeout"
            pass


if __name__ == '__main__':
   dw = DirWatcher(asynch = False)
   def log(r):
      print r
   dw.loop(log)
