# https://python-gtk-3-tutorial.readthedocs.io/en/latest/
# https://twistedmatrix.com/documents/current/core/howto/choosing-reactor.html

import os
import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from twisted.internet import gtk3reactor
gtk3reactor.install()

import txaio
txaio.use_twisted()

import click

from twisted.internet.task import react

from autobahn.xbr._config import UserConfig
from autobahn.xbr import generate_seedphrase


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

    def __init__(self, config_path, profile_name, selected):
        Gtk.Assistant.__init__(self)

        self.set_title("XBR Network")
        self.set_default_size(600, 600)
        self.set_border_width(50)
        self.set_resizable(False)

        self.connect("cancel", self.on_cancel_clicked)
        self.connect("close", self.on_close_clicked)
        self.connect("apply", self.on_apply_clicked)

        ##
        ## page 1: select top-level action
        ##
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
            # self.destroy()
            # txaio.resolve(selected, self.SELECTED_NEW)
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
            self.destroy()
            txaio.resolve(selected, self.SELECTED_SYNCRONIZE)

        button2.connect('clicked', on_button2)
        grid1.attach(button2, 0, 3, 1, 1)

        label3 = Gtk.Label(label='Recover account from account seed phrase')
        label3.set_alignment(0, 0.5)
        label3.set_justify(Gtk.Justification.LEFT)
        grid1.attach(label3, 1, 4, 1, 1)

        button3 = Gtk.Button.new_with_label('Recover account')
        def on_button3(res):
            self.log.info('SELECTED_RECOVER: {res}', res=res)
            self.destroy()
            txaio.resolve(selected, self.SELECTED_RECOVER)

        button3.connect('clicked', on_button3)
        grid1.attach(button3, 0, 4, 1, 1)

        self.append_page(grid1)

        ##
        ## page 2: select top-level action
        ##
        box2_1 = Gtk.VBox()

        box2_2 = Gtk.HBox()
        image2_1 = Gtk.Image()
        image2_1.set_from_file('xbr_white.svg')
        box2_2.add(image2_1)
        box2_1.add(box2_2)

        button2_1 = Gtk.Button.new_with_label('Generate seedphrase')
        def on_button2_1(res):
            sp = generate_seedphrase(strength=256, language='english')
            textbuffer2_1.set_text(sp)
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

        self.append_page(box2_1)

        ##
        ## start on page 0
        ##
        # self.set_show_tabs(False)
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

        self.set_resizable(False)
        self.set_default_size(600, 600)

        self.set_border_width(3)

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        self.page1 = Gtk.Box()
        self.page1.set_border_width(10)
        self.page1.add(Gtk.Label(label="Default Page!"))
        self.notebook.append_page(self.page1, Gtk.Label(label="Plain Title"))

        self.page2 = Gtk.Box()
        self.page2.set_border_width(10)
        self.page2.add(Gtk.Label(label="A page with an image for a Title."))
        self.notebook.append_page(
            self.page2, Gtk.Image.new_from_icon_name("help-about", Gtk.IconSize.MENU)
        )

        sp = generate_seedphrase(strength=256, language='english')
        print(sp)

    def actions(self):

        self.set_border_width(50)

        grid1 = Gtk.Grid()
        grid1.set_row_spacing(20)
        grid1.set_column_spacing(20)
        grid1.set_margin_top(20)
        grid1.set_margin_bottom(20)
        grid1.set_margin_start(20)
        grid1.set_margin_end(20)
        self.add(grid1)

        label1 = Gtk.Label(label='Create a new account')
        grid1.attach(label1, 0, 0, 1, 1)

        button1 = Gtk.Button.new_with_label('New account')
        button1.connect('clicked', self.on_click_me_clicked)
        grid1.attach(button1, 1, 0, 1, 1)

        label2 = Gtk.Label(label='Synchronize with other device in account')
        grid1.attach(label2, 0, 1, 1, 1)

        button2 = Gtk.Button.new_with_label('Synchronize account')
        button2.connect('clicked', self.on_click_me_clicked)
        grid1.attach(button2, 1, 1, 1, 1)

        label3 = Gtk.Label(label='Recover account from account seed phrase')
        grid1.attach(label3, 0, 2, 1, 1)

        button3 = Gtk.Button.new_with_label('Recover account')
        button3.connect('clicked', self.on_click_me_clicked)
        grid1.attach(button3, 1, 2, 1, 1)

    def on_click_me_clicked(self, button):
        print('"Click me" button was clicked')

    def on_open_clicked(self, button):
        print('"Open" button was clicked')

    def on_close_clicked(self, button):
        print("Closing application")
        Gtk.main_quit()

    def _show_create_new_config(self):
        self._win_grid = Gtk.Grid()
        self._win_grid.set_row_spacing(20)
        self._win_grid.set_column_spacing(20)
        self._win_grid.set_margin_top(20)
        self._win_grid.set_margin_bottom(20)
        self._win_grid.set_margin_start(20)
        self._win_grid.set_margin_end(20)
        self.add(self._win_grid)

    def _test(self):
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


class Assistant(Gtk.Assistant):
    """
    https://developer.gnome.org/pygtk/stable/gtk-constants.html#gtk-assistant-page-type-constants
    """
    def __init__(self):
        Gtk.Assistant.__init__(self)
        self.set_title("Assistant")
        self.set_default_size(400, -1)
        self.connect("cancel", self.on_cancel_clicked)
        self.connect("close", self.on_close_clicked)
        self.connect("apply", self.on_apply_clicked)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.INTRO)
        self.set_page_title(box, "Page 1: Introduction")
        label = Gtk.Label(label="An 'Intro' page is the first page of an Assistant. It is used to provide information about what configuration settings need to be configured. The introduction page only has a 'Continue' button.")
        label.set_line_wrap(True)
        box.pack_start(label, True, True, 0)
        self.set_page_complete(box, True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.CONFIRM)
        self.set_page_title(box, "Page 2: Confirm")
        label = Gtk.Label(label="The 'Confirm' page may be set as the final page in the Assistant, however this depends on what the Assistant does. This page provides an 'Apply' button to explicitly set the changes, or a 'Go Back' button to correct any mistakes.")
        label.set_line_wrap(True)
        box.pack_start(label, True, True, 0)
        self.set_page_complete(box, True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.CONTENT)
        self.set_page_title(box, "Page 3: Content")
        label = Gtk.Label(label="The 'Content' page provides a place where widgets can be positioned. This allows the user to configure a variety of options as needed. The page contains a 'Continue' button to move onto other pages, and a 'Go Back' button to return to the previous page if necessary.")
        label.set_line_wrap(True)
        box.pack_start(label, True, True, 0)
        self.set_page_complete(box, True)

        self.complete = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.append_page(self.complete)
        self.set_page_type(self.complete, Gtk.AssistantPageType.PROGRESS)
        self.set_page_title(self.complete, "Page 4: Progress")
        label = Gtk.Label(label="A 'Progress' page is used to prevent changing pages within the Assistant before a long-running process has completed. The 'Continue' button will be marked as insensitive until the process has finished. Once finished, the button will become sensitive.")
        label.set_line_wrap(True)
        self.complete.pack_start(label, True, True, 0)
        checkbutton = Gtk.CheckButton(label="Mark page as complete")
        checkbutton.connect("toggled", self.on_complete_toggled)
        self.complete.pack_start(checkbutton, False, False, 0)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.CONFIRM)
        self.set_page_title(box, "Page 5: Confirm")
        label = Gtk.Label(label="The 'Confirm' page may be set as the final page in the Assistant, however this depends on what the Assistant does. This page provides an 'Apply' button to explicitly set the changes, or a 'Go Back' button to correct any mistakes.")
        label.set_line_wrap(True)
        box.pack_start(label, True, True, 0)
        self.set_page_complete(box, True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.SUMMARY)
        self.set_page_title(box, "Page 6: Summary")
        label = Gtk.Label(label="A 'Summary' should be set as the final page of the Assistant if used however this depends on the purpose of your Assistant. It provides information on the changes that have been made during the configuration or details of what the user should do next. On this page only a Close button is displayed. Once at the Summary page, the user cannot return to any other page.")
        label.set_line_wrap(True)
        box.pack_start(label, True, True, 0)
        self.set_page_complete(box, True)

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

    def start(self, profile_name):
        txaio.start_logging(level='info')

        if not os.path.isdir(self.DOTDIR):
            os.mkdir(self.DOTDIR)
            self.log.info('dotdir created: "{dotdir}"', dotdir=self.DOTDIR)

        config_path = os.path.join(self.DOTDIR, self.DOTFILE)
        if not os.path.isfile(config_path):
            self.log.info('no config exist under "{config_path}"', config_path=config_path)
            self._config = None
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

        d = txaio.create_future()

        if self._config:
            # if we have a config/profile, go on with ..
            win = MainWindow()
        else:
            # if we don't have a config yet,
            win = SelectNewProfile(config_path, 'default', d)

        win.show_all()

        return d


async def main(reactor, profile):
    log = txaio.make_logger()
    app = Application()
    d = app.start(profile)

    def done(selected):
        log.info('Selected action: {selected}', selected=selected)
        Gtk.main_quit()

    def error(err):
        log.error('{err}', err=err)
        sys.exit(1)

    txaio.add_callbacks(d, done, error)
    Gtk.main()


react(main, ('default',))
