###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import os
import shutil

from twisted.internet.defer import Deferred
from twisted.internet.interfaces import IReactorProcess
from twisted.internet.utils import getProcessOutput

__all__ = ('get_input_from_dialog',)


def get_input_from_dialog(reactor: IReactorProcess, title: str = 'Unlock key',
                          text: str = 'Please enter passphrase to unlock key',
                          hide_text: bool = True) -> Deferred:
    """
    Show a Gnome/GTK desktop dialog asking for a passphrase.

    This is using zenity, the GNOME port of dialog which allows you to display dialog boxes
    from the commandline and shell scripts. To install (on Linux):

    .. code:: console

        sudo apt update
        sudo install zenity

    See also:

    - https://gitlab.gnome.org/GNOME/zenity
    - https://wiki.ubuntuusers.de/Zenity/
    - https://bash.cyberciti.biz/guide/Zenity:_Shell_Scripting_with_Gnome

    :param reactor: Twisted reactor to use.
    :param title: Dialog window title to show.
    :param text: Dialog text to show above text entry field.
    :param hide_text: Hide entry field text.

    :return: A deferred that resolves with the string the user entered.
    """
    exe = shutil.which('zenity')
    if not exe:
        raise RuntimeError('get_input_from_dialog(): could not find zenity (install with "apt install zenity")')
    args = ['--entry', '--title', title, '--text', text]
    if hide_text:
        args.append('--hide-text')
    d = getProcessOutput(exe, args=args, env=os.environ, reactor=reactor)

    def _consume(output):
        passphrase = output.decode('utf8').strip()
        return passphrase

    d.addCallback(_consume)
    return d


if __name__ == "__main__":
    from twisted.internet.task import react

    async def main(reactor):
        passphrase = await get_input_from_dialog(reactor)
        print(type(passphrase), len(passphrase), '"{}"'.format(passphrase))

    react(main)
