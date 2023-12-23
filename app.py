import customtkinter as ctk
from PIL import ImageTk

from frames.home import HomeFrame
from frames.navigation import NavigationFrame
from frames.settings import SettingsFrame
from tools.abs import AppABC
from tools.config import Config


class App(AppABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.title("Keftemium")

        self.iconbitmap()
        # noinspection PyTypeChecker
        self.iconphoto(True, ImageTk.PhotoImage(file="logo.png", master=self))

        self.geometry("1200x700")
        self.minsize(1200, 700)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._config = Config(self, "config.ini")

        # set saved values for app
        ctk.set_widget_scaling(int(self._config.scaling.get().replace("%", "")) / 100)
        ctk.set_appearance_mode(self._config.appearance_mode.get())

        self.navigation_frame = NavigationFrame(self, [(HomeFrame, "home"), (SettingsFrame, "settings")])

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value


app = App()
app.protocol("WM_DELETE_WINDOW", lambda: app.config.save())

if __name__ == "__main__":
    app.mainloop()
