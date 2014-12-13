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


import logging


class LogMixin:
    """
    The LogMixing to be used for logging in asyncio projects.
    It wraps the python stdlib logging package.
    """

    # The named logger used by the autobahn package
    logger = logging.getLogger("autobahn")

    def logCritical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def logError(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def logWarning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def logInfo(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def logDebug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def logException(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)
