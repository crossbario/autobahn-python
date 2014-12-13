###############################################################################
#
#  Copyright (c) 2014 Christian Kampka <christian@kampka.net>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###############################################################################

from twisted.python import log
from twisted.python import failure

class LogMixin:
    """
    The LogMixing to be used for logging in twisted projects.
    It wraps the twisted.python.log utilities.
    """

    def _preprocess(self, msg, args, kwargs):
        """
        Preprocess the log message and event dict.
        If exc_info should be included in the log event,
        wrap it into a Failure and place it into the event dict
        """
        if "exc_info" in kwargs:
            f = failure.Failure()
            kwargs['failure'] = f
            kwargs['isError'] = 1
            del kwargs['exc_info']
        return (msg, args, kwargs)

    def logCritical(self, msg, *args, **kwargs):
        (msg, args, kwargs) = self._preprocess(msg, args, kwargs)
        log.err(_why=msg, *args, **kwargs)

    def logError(self, msg, *args, **kwargs):
        (msg, args, kwargs) = self._preprocess(msg, args, kwargs)
        log.err(_why=msg, *args, **kwargs)

    def logWarning(self, msg, *args, **kwargs):
        (msg, args, kwargs) = self._preprocess(msg, args, kwargs)
        log.msg(msg, *args, **kwargs)

    def logInfo(self, msg, *args, **kwargs):
        (msg, args, kwargs) = self._preprocess(msg, args, kwargs)
        log.msg(msg, *args, **kwargs)

    def logDebug(self, msg, *args, **kwargs):
        (msg, args, kwargs) = self._preprocess(msg, args, kwargs)
        log.msg(msg, *args, **kwargs)

    def logException(self, msg, *args, **kwargs):
        (msg, args, kwargs) = self._preprocess(msg, args, kwargs)
        log.err(_why=msg, *args, **kwargs)
