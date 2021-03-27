# https://python-gtk-3-tutorial.readthedocs.io/en/latest/
# https://twistedmatrix.com/documents/current/core/howto/choosing-reactor.html

import os
import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository.Gdk import Color

from twisted.internet import gtk3reactor
gtk3reactor.install()

import txaio
txaio.use_twisted()

from twisted.internet.task import react

import click
import web3

from autobahn.util import parse_activation_code
from autobahn.wamp.types import ComponentConfig
from autobahn.wamp.serializer import CBORSerializer
from autobahn.twisted.wamp import ApplicationRunner
from autobahn.xbr import account_from_seedphrase, generate_seedphrase
from autobahn.xbr._config import UserConfig
from autobahn.xbr._cli import Client


class SelectNewProfile(Gtk.Assistant):
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

    SELECTED_NONE = 0
    SELECTED_NEW = 1
    SELECTED_SYNCRONIZE = 2
    SELECTED_RECOVER = 3

    def __init__(self, reactor, client, config_path, profile_name, onboard_member_submitted):
        Gtk.Assistant.__init__(self)

        self.reactor = reactor
        self.client = client
        self.onboard_member_submitted = onboard_member_submitted

        self.input_seedphrase = None
        self.input_email = None
        self.input_password = None

        # configure assistant window/widget
        self.set_title("XBR Network")
        self.set_default_size(600, 600)
        self.set_border_width(50)
        self.set_resizable(False)

        # assistant window/widget actions
        self.connect("cancel", self.on_cancel_clicked)
        self.connect("close", self.on_close_clicked)
        self.connect("apply", self.on_apply_clicked)

        # setup assistant pages
        self._setup_page1()
        self._setup_page2()
        self._setup_page3()
        self._setup_page4()

        # start on page 1
        self.set_current_page(0)

    def on_apply_clicked(self, *args):
        print("The 'Apply' button has been clicked")

    def on_close_clicked(self, *args):
        print("The 'Close' button has been clicked")
        Gtk.main_quit()

    def on_cancel_clicked(self, *args):
        print("The Assistant has been cancelled.")
        Gtk.main_quit()

    def on_complete_toggled(self, checkbutton):
        self.set_page_complete(self.complete, checkbutton.get_active())

    def _setup_page1(self):
        """
        Setup page shown when no config/profile could be found. Allows to select from:

        * new account
        * synchronize device
        * recover account
        """
        grid1 = Gtk.Grid()
        grid1.set_row_spacing(20)
        grid1.set_column_spacing(20)
        grid1.set_margin_top(20)
        grid1.set_margin_bottom(20)
        grid1.set_margin_start(20)
        grid1.set_margin_end(20)

        image1 = Gtk.Image()
        image1.set_from_file('xbr_white.svg')
        grid1.attach(image1, 0, 0, 2, 1)

        label0 = Gtk.Label(label='Initial configuration, please select:\n')
        label0.set_alignment(0, 0)
        grid1.attach(label0, 0, 1, 1, 1)

        label1 = Gtk.Label(label='Create a new account or start from fresh')
        label1.set_alignment(0, 0.5)
        label1.set_justify(Gtk.Justification.LEFT)
        grid1.attach(label1, 1, 2, 1, 1)

        button1 = Gtk.Button.new_with_label('New account')
        def on_button1(res):
            self.log.info('SELECTED_NEW: {res}', res=res)
            self.set_current_page(1)

        button1.connect('clicked', on_button1)
        grid1.attach(button1, 0, 2, 1, 1)

        label2 = Gtk.Label(label='Synchronize device with account in other device')
        label2.set_alignment(0, 0.5)
        label2.set_justify(Gtk.Justification.LEFT)
        grid1.attach(label2, 1, 3, 1, 1)

        button2 = Gtk.Button.new_with_label('Synchronize account')
        def on_button2(res):
            self.log.info('SELECTED_SYNCRONIZE: {res}', res=res)
            self.set_current_page(2)

        button2.connect('clicked', on_button2)
        grid1.attach(button2, 0, 3, 1, 1)

        label3 = Gtk.Label(label='Recover account from account seed phrase')
        label3.set_alignment(0, 0.5)
        label3.set_justify(Gtk.Justification.LEFT)
        grid1.attach(label3, 1, 4, 1, 1)

        button3 = Gtk.Button.new_with_label('Recover account')
        def on_button3(res):
            self.log.info('SELECTED_RECOVER: {res}', res=res)
            self.set_current_page(3)

        button3.connect('clicked', on_button3)
        grid1.attach(button3, 0, 4, 1, 1)

        self.append_page(grid1)

    def _setup_page2(self):
        """
        Setup page shown to generate a new seed phrase.
        """
        box2_1 = Gtk.VBox()

        box2_2 = Gtk.HBox()
        image2_1 = Gtk.Image()
        image2_1.set_from_file('xbr_white.svg')
        box2_2.add(image2_1)
        box2_1.add(box2_2)

        button2_1 = Gtk.Button.new_with_label('Generate seedphrase')

        def on_button2_1(_):
            sp = generate_seedphrase(strength=256, language='english')
            textbuffer2_1.set_text(sp)
            checkbutton2_1.set_sensitive(True)

        button2_1.connect('clicked', on_button2_1)
        box2_1.add(button2_1)

        label2_1 = Gtk.Label(label='Backup your new seed phrase in a secure offline location (e.g. on printed paper):')
        label2_1.set_alignment(0, 0.5)
        label2_1.set_justify(Gtk.Justification.LEFT)
        box2_1.add(label2_1)

        textview2_1 = Gtk.TextView()
        textbuffer2_1 = textview2_1.get_buffer()
        textbuffer2_1.set_text('\n' * 5)
        textview2_1.set_editable(False)
        textview2_1.set_justification(Gtk.Justification.CENTER)
        textview2_1.set_monospace(True)
        textview2_1.set_wrap_mode(Gtk.WrapMode.WORD)
        box2_1.add(textview2_1)

        box2_3 = Gtk.HBox()

        checkbutton2_1 = Gtk.CheckButton(label="I have backed up my seed phrase")
        checkbutton2_1.set_active(False)
        checkbutton2_1.set_sensitive(False)

        def on_checkbutton2_1(_):
            button2_2.set_sensitive(True)

        checkbutton2_1.connect("toggled", on_checkbutton2_1)
        box2_3.add(checkbutton2_1)

        button2_2 = Gtk.Button.new_with_label('Continue')
        button2_2.set_sensitive(False)

        def on_button2_2(_):
            account = account_from_seedphrase(textbuffer2_1.get_text(), index=0)
            ethadr = web3.Web3.toChecksumAddress(self._ethkey.public_key.to_canonical_address())

            self.input_seedphrase = textbuffer2_1.get_text()
            self.set_current_page(2)

        button2_2.connect('clicked', on_button2_2)
        box2_3.add(button2_2)

        box2_1.add(box2_3)

        self.append_page(box2_1)

    def _setup_page3(self):
        """

        :return:
        """
        box1 = Gtk.VBox()

        box2 = Gtk.HBox()
        image1 = Gtk.Image()
        image1.set_from_file('xbr_white.svg')
        box2.add(image1)
        box1.add(box2)

        grid1 = Gtk.Grid()
        grid1.set_row_spacing(20)
        grid1.set_column_spacing(20)
        grid1.set_margin_top(20)
        grid1.set_margin_bottom(20)
        grid1.set_margin_start(20)
        grid1.set_margin_end(20)

        label1 = Gtk.Label(label='Your email address:')
        grid1.attach(label1, 0, 0, 1, 1)

        entry1 = Gtk.Entry()
        entry1.set_text('')
        entry1.set_max_length(255)
        entry1.set_max_width_chars(40)
        grid1.attach(entry1, 1, 0, 1, 1)

        checks = {
            'email': None,
            'password': None,
            'eula': None,
        }
        def check_all():
            print('check_all')
            for c in checks:
                if checks[c] is None:
                    print('check failed', c)
                    button2.set_sensitive(False)
                    return
            button2.set_sensitive(True)

        def check_email(email):
            if '@' in email:
                return email
            else:
                return None

        def check_password(password):
            return True

        def on_entry1(entry):
            # joe.doe@example.com
            checks['email'] = check_email(entry.get_text())
            if checks['email']:
                entry1.modify_fg(Gtk.StateFlags.NORMAL, None)
            else:
                entry1.modify_fg(Gtk.StateFlags.NORMAL, Color(50000, 0, 0))
            check_all()

        entry1.connect('changed', on_entry1)

        label2 = Gtk.Label(label='New password:')
        grid1.attach(label2, 0, 1, 1, 1)

        entry2 = Gtk.Entry()
        entry2.set_text('')
        entry2.set_max_length(20)
        entry2.set_max_width_chars(20)
        entry2.set_visibility(False)
        grid1.attach(entry2, 1, 1, 1, 1)

        label2 = Gtk.Label(label='Repeat new password:')
        grid1.attach(label2, 0, 2, 1, 1)

        entry3 = Gtk.Entry()
        entry3.set_text('')
        entry3.set_max_length(20)
        entry3.set_max_width_chars(20)
        entry3.set_visibility(False)
        grid1.attach(entry3, 1, 2, 1, 1)

        label3 = Gtk.Label(label='EULA:')
        grid1.attach(label3, 0, 3, 1, 1)

        def on_entry23(_):
            checks['password'] = entry2.get_text() == entry3.get_text() and check_password(entry2.get_text())
            if check_password(entry2.get_text()):
                entry2.modify_fg(Gtk.StateFlags.NORMAL, None)
            else:
                entry2.modify_fg(Gtk.StateFlags.NORMAL, Color(50000, 0, 0))
            if check_password(entry3.get_text()):
                entry3.modify_fg(Gtk.StateFlags.NORMAL, None)
            else:
                entry3.modify_fg(Gtk.StateFlags.NORMAL, Color(50000, 0, 0))
            check_all()

        entry2.connect('changed', on_entry23)
        entry3.connect('changed', on_entry23)

        button1 = Gtk.CheckButton(label='I accept the EULA and terms of use')
        button1.set_active(False)
        button1.set_sensitive(True)

        def on_button1(button):
            if button.get_active():
                checks['eula'] = True
            else:
                checks['eula'] = False
            check_all()

        button1.connect('toggled', on_button1)
        grid1.attach(button1, 1, 3, 1, 1)

        button2 = Gtk.Button.new_with_label('Register account')
        button2.set_sensitive(False)

        def on_button2(_):
            self.input_email = checks['email']
            self.input_password = checks['password']
            self.set_current_page(3)

        button2.connect('clicked', on_button2)
        grid1.attach(button2, 2, 4, 1, 1)

        box1.add(grid1)

        self.append_page(box1)

    def _setup_page4(self):
        """
        Page shown when member registration request was submitted, a verification email
        sent, and the verification request ID returned.
        The user now should check the email inbox for the received verification code,
        and continue verifying the code.

        :return:
        """
        box1 = Gtk.VBox()

        box2 = Gtk.HBox()
        image1 = Gtk.Image()
        image1.set_from_file('xbr_white.svg')
        box2.add(image1)
        box1.add(box2)

        box3 = Gtk.HBox()
        label1 = Gtk.Label(label='Member registration submitted, verification request:')
        label2 = Gtk.Label(label='8d5d7ffd-23d9-45a0-a686-00a49f29d3cd')
        box3.add(label1)
        box3.add(label2)
        box1.add(box3)

        label3 = Gtk.Label(label='Please check your email inbox, and enter the verification code received here:')
        box1.add(label3)

        entry1 = Gtk.Entry()
        entry1.set_text('')
        entry1.set_max_length(255)
        entry1.set_max_width_chars(40)
        box1.add(entry1)

        def on_entry1(entry):
            # "RWCN-94NV-CEHR" -> ("RWCN", "94NV", "CEHR") | None
            code = parse_activation_code(entry.get_text())
            if code:
                entry1.modify_fg(Gtk.StateFlags.NORMAL, None)
                button1.set_sensitive(True)
            else:
                entry1.modify_fg(Gtk.StateFlags.NORMAL, Color(50000, 0, 0))
                button1.set_sensitive(False)

        entry1.connect('changed', on_entry1)

        button1 = Gtk.Button.new_with_label('Verify')
        button1.set_sensitive(False)

        def on_button1(res):
            print('1' * 100, res)
        button1.connect('clicked', on_button1)
        box1.add(button1)

        self.append_page(box1)

    def _setup_page5(self):
        print('ONBOARDED!')


class Application(object):
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

    def start(self, reactor, profile_name):
        txaio.start_logging(level='info')

        if not os.path.isdir(self.DOTDIR):
            os.mkdir(self.DOTDIR)
            self.log.info('dotdir created: "{dotdir}"', dotdir=self.DOTDIR)

        config_path = os.path.join(self.DOTDIR, self.DOTFILE)
        if not os.path.isfile(config_path):
            self.log.info('no config exist under "{config_path}"', config_path=config_path)
            self._config = UserConfig(config_path)
            self._profile = None
        else:
            self._config = UserConfig(config_path)
            self._profile = self._config.profiles.get(profile_name, None)

            if not self._profile:
                raise click.ClickException('no such profile "{}" in config "{}"'.format(profile_name, config_path))
            else:
                self.log.info('user profile "{profile_name}" loaded from "{config_path}"',
                            config_path=config_path, profile_name=profile_name)

        assert self._config and self._profile

        extra = {
            'profile': self._profile,
        }
        runner = ApplicationRunner(url=self._profile.network_url,
                                   realm=self._profile.network_realm,
                                   extra=extra,
                                   serializers=[CBORSerializer()])
        client = runner.run(Client, auto_reconnect=True, start_reactor=False)

        d = txaio.create_future()
        if False and self._config:
            # if we have a config/profile, go on with ..
            raise NotImplementedError()
        else:
            # if we don't have a config yet,
            win = SelectNewProfile(reactor, client, config_path, 'default', d)

        win.show_all()

        return d


async def main(reactor, profile):
    log = txaio.make_logger()
    app = Application()
    d = app.start(reactor, profile)

    def done(selected):
        log.info('Selected action: {selected}', selected=selected)
        Gtk.main_quit()

    def error(err):
        log.error('{err}', err=err)
        sys.exit(1)

    txaio.add_callbacks(d, done, error)
    Gtk.main()


react(main, ('default',))
