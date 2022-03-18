from gi.repository import Gtk


@Gtk.Template(resource_path='/org/example/App/window.ui')
class RflUiWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'RflUiWindow'

    label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AboutDialog(Gtk.AboutDialog):

    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)
        self.props.program_name = 'Rufus for Linux'
        self.props.version = "0.0.1"
        self.props.authors = ['OSeL Team']
        self.props.copyright = '(C) 2022 OSeL Team'
        self.props.logo_icon_name = 'org.example.App'
        self.set_transient_for(parent)
