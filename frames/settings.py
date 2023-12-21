import customtkinter as ctk

from tools.abs import AppABC, FrameABC
from tools.tabs import instruments


class SettingsFrame(FrameABC):
    def __init__(self, master: AppABC, **kwargs):
        super().__init__(master, **kwargs)
        self._master: AppABC = master

        self.grid_columnconfigure(0, weight=1)

        self.frame = ctk.CTkFrame(self)
        self.frame.grid(padx=20, pady=20, sticky=ctk.NSEW)

        self.frame.grid_columnconfigure(3, weight=1)
        self.frame.grid_rowconfigure(13, weight=1)

        # BPM
        self.bpm_title = ctk.CTkLabel(self.frame, text="Bpm detection:", font=ctk.CTkFont(size=18))
        self.bpm_title.grid(row=0, column=0, padx=20, pady=(10, 0), sticky=ctk.W)

        self.bpm_auto = ctk.CTkRadioButton(self.frame, variable=self.master.config.bpm_detection, value="auto",
                                           text="Automatic detection", font=ctk.CTkFont(size=18),
                                           command=self.choose_bpm)
        self.bpm_auto.grid(row=1, column=0, padx=20, pady=(10, 0), sticky=ctk.W)

        self.bpm_specified = ctk.CTkRadioButton(self.frame, variable=self.master.config.bpm_detection,
                                                value="specified", text="Specified", font=ctk.CTkFont(size=18),
                                                command=self.choose_bpm)
        self.bpm_specified.grid(row=2, column=0, padx=20, pady=(10, 0), sticky=ctk.W)

        if self.master.config.bpm_detection.get() == "auto":
            slider_state, display_text = "disable", ""
        else:
            slider_state, display_text = "normal", self.master.config.bpm.get()

        self.bpm_slider = ctk.CTkSlider(self.frame, 420, 22, from_=30, to=240, state=slider_state, number_of_steps=210,
                                        variable=self.master.config.bpm, command=self.bpm_slider_event)
        self.bpm_slider.grid(row=2, column=1, pady=(10, 0), sticky=ctk.W)

        self.bpm_display = ctk.CTkLabel(self.frame, text=display_text, font=ctk.CTkFont(size=18))
        self.bpm_display.grid(row=2, column=2, pady=(10, 0), padx=60, sticky=ctk.W)

        # Instruments
        self.instrument_title = ctk.CTkLabel(self.frame, text="Instrument:", font=ctk.CTkFont(size=18))
        self.instrument_title.grid(row=3, column=0, padx=20, pady=(30, 0), sticky=ctk.W)

        self.instrument_menu = ctk.CTkOptionMenu(self.frame, values=list(instruments.keys()),
                                                 variable=self.master.config.instrument)
        self.instrument_menu.grid(row=3, column=1, pady=(30, 0), sticky=ctk.W)

        # Pitches
        self.pitches_title = ctk.CTkLabel(self.frame, text="Pitches:", font=ctk.CTkFont(size=18))
        self.pitches_title.grid(row=4, column=0, padx=20, pady=(30, 0), sticky=ctk.W)

        self.pitches_one = ctk.CTkRadioButton(self.frame, variable=self.master.config.pitches, value="one note",
                                              text="One note", font=ctk.CTkFont(size=18))
        self.pitches_one.grid(row=5, column=0, padx=20, pady=(10, 0), sticky=ctk.W)

        self.pitches_randomly = ctk.CTkRadioButton(self.frame, variable=self.master.config.pitches,
                                                   value="randomly", text="Randomly", font=ctk.CTkFont(size=18))
        self.pitches_randomly.grid(row=6, column=0, padx=20, pady=(10, 0), sticky=ctk.W)

        self.pitches_by_note_duration = ctk.CTkRadioButton(self.frame, variable=self.master.config.pitches,
                                                           value="by note duration", font=ctk.CTkFont(size=18),
                                                           text="Depending on the note duration")
        self.pitches_by_note_duration.grid(row=7, column=0, padx=20, pady=(10, 0), sticky=ctk.W)

        # Appearance mode
        self.appearance_mode_title = ctk.CTkLabel(self.frame, text="Appearance mode:", font=ctk.CTkFont(size=18))
        self.appearance_mode_title.grid(row=8, column=0, padx=20, pady=(30, 0), sticky=ctk.W)

        self.appearance_mode_menu = ctk.CTkOptionMenu(self.frame, values=["System", "Light", "Dark"],
                                                      variable=self.master.config.appearance_mode,
                                                      command=lambda mode: ctk.set_appearance_mode(mode))
        self.appearance_mode_menu.grid(row=8, column=1, pady=(30, 10), sticky=ctk.W)

        # Scaling
        self.scaling_title = ctk.CTkLabel(self.frame, text="Scaling:", font=ctk.CTkFont(size=18))
        self.scaling_title.grid(row=11, column=0, padx=20, pady=(30, 10), sticky=ctk.W)

        self.scaling_menu = ctk.CTkOptionMenu(
            self.frame, values=["80%", "90%", "100%", "110%", "120%"], variable=self.master.config.scaling,
            command=lambda scale: ctk.set_widget_scaling(int(scale.replace("%", "")) / 100))
        self.scaling_menu.grid(row=11, column=1, pady=(30, 10), sticky=ctk.W)

    def choose_bpm(self):
        if self.master.config.bpm_detection.get() == "auto":
            self.bpm_slider.configure(state="disable")
            self.bpm_display.configure(text=f"")
            self.master.config.bpm_detection
        else:
            self.bpm_slider.configure(state="normal")
            self.bpm_slider_event(self.bpm_slider.get())

    def bpm_slider_event(self, value):
        self.bpm_display.configure(text=f"{int(value)}")

    @property
    def master(self):
        return self._master

    @master.setter
    def master(self, value):
        self._master = value
