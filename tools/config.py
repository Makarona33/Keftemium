import configparser

import customtkinter as ctk


class Config:
    def __init__(self, root, file):
        self._root = root
        self._file = file

        self._parser = configparser.ConfigParser()
        self._parser.read(file)

        self.recording_method = ctk.StringVar(root, self._parser.get("DEFAULT", "recording_method",
                                                                     fallback="Using clicks"))

        self.bpm = ctk.IntVar(root, self._parser.getint("DEFAULT", "bpm", fallback="5"))
        self.bpm_detection = ctk.StringVar(root, self._parser.get("DEFAULT", "bpm_detection", fallback="auto"))
        self.instrument = ctk.StringVar(root, self._parser.get("DEFAULT", "instrument",
                                                               fallback="Acoustic grand piano"))
        self.pitches = ctk.StringVar(root, self._parser.get("DEFAULT", "pitches", fallback="one note"))

        self.appearance_mode = ctk.StringVar(root, self._parser.get("DEFAULT", "appearance_mode", fallback="System"))
        self.scaling = ctk.StringVar(root, self._parser.get("DEFAULT", "scaling", fallback="100%"))

    def save(self):
        self._parser["DEFAULT"] = {k: str(v.get()).replace('%', "%%") for k, v in self.__dict__.items()
                                   if not k.startswith('_')}

        with open(self._file, 'w') as file:
            self._parser.write(file)

        self._root.destroy()
