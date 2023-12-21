import customtkinter as ctk
from PIL import Image

from tools.abs import AppABC, FrameABC


class NavigationFrame(FrameABC):
    def __init__(self, master: AppABC, pages: list[tuple[type, str]], **kwargs):
        super().__init__(master, **kwargs)
        self._master = master
        self.pages = pages

        # self.logo_image = ctk.CTkImage(Image.open(""), size=(26, 26))

        self.frame = ctk.CTkFrame(master, corner_radius=0)
        self.frame.grid(row=0, column=0, sticky=ctk.NSEW)
        self.frame.grid_rowconfigure(len(pages) + 1, weight=1)

        self.label = ctk.CTkLabel(self.frame, text="Keftemium", compound=ctk.LEFT,
                                  font=ctk.CTkFont(size=20, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=20)

        rows = 1
        for frame, name in pages:
            setattr(self, f"{name}_frame", frame(master, corner_radius=0, fg_color="transparent"))

            setattr(self, f"{name}_button", self.make_button(name, lambda x=name: self.select_frame_by_name(x)))
            getattr(self, f"{name}_button").grid(row=rows, column=0, sticky=ctk.EW)

            rows += 1

        self.select_frame_by_name(pages[0][1])

    def make_button(self, text, command):
        return ctk.CTkButton(self.frame, corner_radius=0, height=40, border_spacing=10, text=text.capitalize(),
                             fg_color="transparent", font=("Areal", 20), text_color=("gray10", "gray90"),
                             hover_color=("gray70", "gray30"), anchor=ctk.W, command=command)

    def select_frame_by_name(self, name):
        frame_name = getattr(self, f"{name}_frame")
        button_name = getattr(self, f"{name}_button")

        for page in self.pages:
            frame = getattr(self, f"{page[1]}_frame")
            button = getattr(self, f"{page[1]}_button")

            frame.grid(row=0, column=1, sticky=ctk.NSEW) if frame == frame_name else frame.grid_forget()
            button.configure(fg_color=("gray75", "gray25") if button == button_name else "transparent")

    @property
    def master(self):
        return self._master

    @master.setter
    def master(self, value):
        self._master = value
