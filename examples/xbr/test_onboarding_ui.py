# https://python-gtk-3-tutorial.readthedocs.io/en/latest/
# https://twistedmatrix.com/documents/current/core/howto/choosing-reactor.html

import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from twisted.internet import gtk3reactor
gtk3reactor.install()

from twisted.internet import reactor

import txaio
txaio.use_twisted()

import click

from autobahn.xbr._config import UserConfig



class MainWindow(Gtk.Window):
    """
    local user profile config there?
    if no, show:
        - button "new account"
        - button "synchronize account"
        - button "recover account"
    if yes, unlock profile (ask for password)
    check account online: does account exist?
        if yes, show account details + button "synchronize other device"
        if no, start or continue registration ..
    """
    log = txaio.make_logger()

    DOTDIR = os.path.abspath(os.path.expanduser('~/.xbrnetwork'))
    DOTFILE = 'config.ini'

    def __init__(self, profile_name: str='default'):
        Gtk.Window.__init__(self, title='Register with XBR network')

        if not os.path.isdir(self.DOTDIR):
            os.mkdir(self.DOTDIR)
            self.log.info('dotdir created: "{dotdir}"', dotdir=self.DOTDIR)

        config_path = os.path.join(self.DOTDIR, self.DOTFILE)
        if not os.path.isfile(config_path):
            pass

        self._config = UserConfig(config_path)
        self._profile = config.profiles.get(profile_name, None)

        if not self._profile:
            raise click.ClickException('no such profile: "{}"'.format(profile_name))
        else:
            self.log.info('user profile "{profile_name}" loaded from "{config_path}"',
                          config_path=config_path, profile_name=profile_name)

        self._win_grid = Gtk.Grid()
        self._win_grid.set_row_spacing(20)
        self._win_grid.set_column_spacing(20)
        self._win_grid.set_margin_top(20)
        self._win_grid.set_margin_bottom(20)
        self._win_grid.set_margin_start(20)
        self._win_grid.set_margin_end(20)
        self.add(self._win_grid)

        self._win_user_email_label = Gtk.Label(label='Your email address:')
        self._win_grid.attach(self._win_user_email_label, 0, 0, 1, 1)

        self._win_user_email = Gtk.Entry()
        self._win_user_email.set_text(profile.email)
        self._win_user_email.set_max_length(255)
        self._win_user_email.set_max_width_chars(40)
        self._win_grid.attach(self._win_user_email, 1, 0, 1, 1)

        self._win_eula_accept_label = Gtk.Label(label='XBR network EULA:')
        self._win_grid.attach(self._win_eula_accept_label, 0, 1, 1, 1)

        self._win_check_eula = Gtk.CheckButton(label='accept')
        self._win_check_eula.connect('toggled', self.on_eula_toggled)
        self._win_check_eula.set_active(False)
        self._win_grid.attach(self._win_check_eula, 1, 1, 1, 1)

    def on_eula_toggled(self, button):
        value = button.get_active()
        self._win_check_eula.set_editable(value)


txaio.start_logging(level='info')

win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

reactor.run()
