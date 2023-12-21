import os
import random
import threading
import time
from io import BytesIO
from statistics import mean
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showerror

import customtkinter as ctk
import numpy
import pyaudio
from PIL import Image
from midiutil import MIDIFile
from neoscore.core import neoscore
from neoscore.core.units import Mm, ZERO
from neoscore.western.chordrest import Chordrest
from neoscore.western.clef import Clef
from neoscore.western.metronome_mark import MetronomeMark
from neoscore.western.staff import Staff
from scipy.signal import find_peaks

from tools.abs import AppABC
from tools.abs import FrameABC
from tools.tabs import duration_in_sec
from tools.tabs import durations, Note, instruments_musical_ranges, instruments, midi_number_to_pitch

# Disable welcome message when importing pygame
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
pygame = __import__("pygame")
pygame.mixer.init()


class HomeFrame(FrameABC):
    def __init__(self, master: AppABC, **kwargs):
        super().__init__(master, **kwargs)
        self._master: AppABC = master
        self.midi_file = None
        self.notes = []
        self.instrument_type = "other"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.record_frame = RecordFrame(self)
        self.record_frame.grid(row=0, padx=10, pady=10, sticky="nsew")

        self.result_frame = ResultFrame(self, fg_color="transparent")
        self.result_frame.grid(row=2, sticky="nsew")

    @property
    def master(self):
        return self._master

    @master.setter
    def master(self, value):
        self._master = value


class RecordFrame(ctk.CTkFrame):
    def __init__(self, master: HomeFrame, **kwargs):
        super().__init__(master, **kwargs)
        self.master: HomeFrame = master
        self.app = self.master.master

        self.__clicks_times = []
        self.__audio_array = numpy.array(0)
        self.__recording_thread: threading.Thread | None = None

        self.grid_columnconfigure(0, weight=1)

        self.widget = None
        self.main_button = ctk.CTkButton(self, text="Start", font=ctk.CTkFont(size=18), command=self.main_button_event)
        self.main_button.grid(row=1, column=0, pady=20)

        self.recording_method = ctk.CTkOptionMenu(self, variable=self.app.config.recording_method,
                                                  values=["Using clicks", "Using a microphone"],
                                                  command=lambda rm: self.change_widget(rm))
        self.recording_method.grid(row=0, column=0, padx=10, pady=10, sticky=ctk.NE)

        self.change_widget(self.recording_method.get())

    def change_widget(self, recording_method):
        if self.widget:
            self.widget.destroy()

        if recording_method == "Using clicks":
            self.widget = ctk.CTkButton(self, 200, 200, text="", corner_radius=100, state=ctk.DISABLED,
                                        command=self.click_event)
            self.widget.grid(row=0, column=0, padx=10, pady=(10, 5))
        else:
            self.widget = ctk.CTkLabel(self, text="—", font=ctk.CTkFont(size=100))
            self.widget.grid(row=0, column=0, pady=(20, 0))

    def click_event(self):
        self.__clicks_times.append(time.time())

    def main_button_event(self):
        change_state = {ctk.DISABLED: ctk.NORMAL, ctk.NORMAL: ctk.DISABLED}

        self.widget.configure(state=change_state[self.widget.cget("state")])
        self.recording_method.configure(state=change_state[self.recording_method.cget("state")])

        self.master.result_frame.play_button.configure(state=ctk.DISABLED)
        self.master.result_frame.save_button.configure(state=ctk.DISABLED)

        if self.main_button.cget("text") == "Start":
            self.__clicks_times = []
            self.master.notes = []
            pygame.mixer.music.stop()
            self.main_button.configure(text="Stop")

            if self.recording_method.get() == "Using a microphone":
                def tick():
                    if self.main_button.cget("text") == "Start":
                        self.widget.configure(text="—")
                        return

                    if self.widget.cget("text") == "—":
                        self.widget.configure(text="0")
                    else:
                        self.widget.configure(text=str(int(self.widget.cget("text")) + 1))
                    self.after(1000, tick)

                tick()

                self.__recording_thread = threading.Thread(target=self.record_micro)
                self.__recording_thread.start()
            return

        # After clicking/recording
        self.main_button.configure(text="Start")

        # Wait end of recording
        if self.__recording_thread:
            while self.__recording_thread.is_alive():
                continue

        if self.recording_method.get() == "Using a microphone":
            peaks = find_peaks(self.__audio_array, prominence=numpy.max(self.__audio_array) / 10, distance=40)[0]

            if len(peaks) < 2:
                return []

            peaks = (peaks / 441)
            notes_duration = numpy.diff(numpy.append(peaks, peaks[-1] * 2)).tolist()
        else:
            self.__clicks_times.append(time.time())

            notes_duration = []
            for i in range(len(self.__clicks_times) - 1):
                v = self.__clicks_times[i + 1] - self.__clicks_times[i]
                notes_duration.append(v)

        if not notes_duration:
            return

        if self.app.config.bpm_detection.get() == "auto":  # automatic detection bpm
            reference_note_value = notes_duration[0]  # Let it be 1/4

            quarters = []

            for i in notes_duration:
                if 0.9 <= abs(reference_note_value / i) <= 1.1:  # notes that are close in duration
                    quarters.append(i)

            self.app.config.bpm.set(max(min(240, int(round(60 / mean(quarters), 0))), 30))  # from 30 to 240

        def create_note(value) -> Note:
            difference = 100
            duration = None

            for dur in durations:
                diff = abs(duration_in_sec(dur, self.app.config.bpm.get()) - value)
                if diff < difference:
                    difference = diff
                    duration = dur

            for instrument in instruments_musical_ranges.keys():
                if instrument in self.app.config.instrument.get():
                    self.master.instrument_type = instrument
                    break
            else:
                self.master.instrument_type = "other"

            match self.app.config.pitches.get():
                case "one note":
                    pitch = instruments_musical_ranges[self.master.instrument_type][1][0]
                case "randomly":
                    pitch = random.choice(instruments_musical_ranges[self.master.instrument_type][1])
                case _:
                    pitch = instruments_musical_ranges[self.master.instrument_type][1][durations.index(duration)]

            return Note(duration, pitch)

        for i in notes_duration:
            self.master.notes.append(create_note(i))

        # convert to midi
        mem = BytesIO()
        self.master.midi_file = MIDIFile()
        self.master.midi_file.addTempo(0, 0, self.app.config.bpm.get())
        self.master.midi_file.addProgramChange(0, 0, 0, instruments[self.app.config.instrument.get()])

        t = 0
        for note in self.master.notes:
            i = float(note.duration.fraction) * 4
            self.master.midi_file.addNote(0, 0, note.pitch, t, i, 100)
            t += i

        self.master.result_frame.midi_duration = int(t * 60 / self.app.config.bpm.get() * 1000)
        self.master.midi_file.writeFile(mem)
        mem.seek(0)
        pygame.mixer.music.load(mem)

        self.master.result_frame.play_button.configure(state="normal")
        self.master.result_frame.save_button.configure(state="normal")
        self.master.result_frame.draw_tabs()

    def record_micro(self):
        p = pyaudio.PyAudio()

        try:
            stream = p.open(format=pyaudio.paFloat32, channels=1, rate=22050, input=True, frames_per_buffer=1024)
        except OSError:
            self.main_button.configure(text="Start")
            self.__audio_array = numpy.array(0)
            showerror("Error", "The microphone was not found. Connect the microphone and restart the app")
            return

        frames = []
        while self.main_button.cget("text") == "Stop":
            frames.append(numpy.frombuffer(stream.read(1024), dtype=numpy.float32))

        stream.stop_stream()
        stream.close()
        p.terminate()

        self.__audio_array = numpy.abs(numpy.hstack(frames)[::50])


class ResultFrame(ctk.CTkFrame):
    def __init__(self, master: HomeFrame, **kwargs):
        super().__init__(master, **kwargs)
        self.master: HomeFrame = master
        self.app = self.master.master
        self.midi_duration = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # tabs frame
        self.tabs_frame = ctk.CTkScrollableFrame(self)
        self.tabs_frame.grid(row=1, padx=10, pady=(10, 0), sticky=ctk.NSEW)

        self.tabs_frame.grid_columnconfigure(0, weight=1)

        self.image_label = ctk.CTkLabel(self.tabs_frame, text='')
        self.image_label.grid()

        # lower frame
        self.lower_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lower_frame.grid(padx=10, pady=(20, 10), sticky=ctk.EW)
        self.lower_frame.grid_columnconfigure(1, weight=1)

        self.play_button = ctk.CTkButton(self.lower_frame, text="Play", state=ctk.DISABLED, font=ctk.CTkFont(size=18),
                                         command=self.play_or_stop_midi)
        self.play_button.grid(column=0, row=1)

        self.save_button = ctk.CTkButton(self.lower_frame, text="Save", state=ctk.DISABLED, font=ctk.CTkFont(size=18),
                                         command=self.save_midi)
        self.save_button.grid(column=3, row=1)

    def draw_tabs(self):
        neoscore.setup()

        # I don't use flowable because notes are drawn crookedly with it
        def create_staff(pos_y: int = 0):
            s = Staff((ZERO, Mm(pos_y)), None, Mm(170))
            Clef(ZERO, s, instruments_musical_ranges[self.master.instrument_type][0])
            return s

        staff = create_staff()
        MetronomeMark((ZERO, staff.unit(-5)), staff, "metNoteQuarterUp", f"= {self.app.config.bpm.get()}")

        offset = 5
        staff_offset = 0

        for note in self.master.notes:
            if offset >= 170:
                offset = 5
                staff_offset += 1
                staff = create_staff(staff_offset * 20)

            Chordrest(Mm(offset), staff, [midi_number_to_pitch(note.pitch)], note.duration)
            offset += 10

        mem = bytearray()
        neoscore.render_image(None, mem, preserve_alpha=False)
        neoscore.shutdown()

        image = Image.open(BytesIO(mem)).convert("RGBA")
        new_width = int(self.tabs_frame.winfo_width() * 100 / int(self.app.config.scaling.get().replace("%", "")))
        new_height = int(new_width * image.height / image.width)
        image = image.resize((new_width, new_height))

        image = ctk.CTkImage(light_image=image, dark_image=image, size=(image.width, image.height))
        self.image_label.configure(image=image)

    def play_or_stop_midi(self):
        if self.play_button.cget("text") == "Play":
            self.play_button.configure(text="Stop")
            pygame.mixer.music.play()

            self.play_button.after(self.midi_duration, lambda: self.play_button.configure(text="Play"))
        else:
            self.play_button.configure(text="Play")
            pygame.mixer.music.stop()

    def save_midi(self):
        path = asksaveasfilename(defaultextension="mid", initialfile="kefteme.mid",
                                 filetypes=(("Midi Files", "*.mid"),), title="Save midi", parent=self)

        if path != "":
            print(path)
            with open(path, "wb") as file:
                self.master.midi_file.writeFile(file)
