from dataclasses import dataclass

from neoscore.western.duration import Duration


def relative_duration(duration: Duration):
    relative_base_duration = 4 / duration.display.base_duration  # duration relative to the quarter note
    relative_dots_duration = 0

    for dot in range(1, duration.display.dot_count + 1):
        relative_dots_duration += 4 / (duration.display.base_duration * 2 ** dot)

    return relative_base_duration + relative_dots_duration


def duration_in_sec(duration: Duration, bpm: int):
    return relative_duration(duration) * 60 / bpm


def midi_number_to_pitch(number):
    notes = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
    octaves = [',,,,,', ',,,,', ',,,', ',,', ',', '', '\'', '\'\'', '\'\'\'', '\'\'\'\'', '\'\'\'\'\'', '\'\'\'\'\'\'']
    notes_in_octaves = len(notes)

    return "{}{}".format(notes[number % notes_in_octaves], octaves[number // notes_in_octaves])


# List if all using durations. I don't see the point in using durations with two points or more.
durations = [
    Duration.from_description(1, 0),  # whole note
    Duration.from_description(2, 1),  # dotted half note
    Duration.from_description(2, 0),  # half note
    Duration.from_description(4, 1),  # dotted quarter note
    Duration.from_description(4, 0),  # quarter note
    Duration.from_description(8, 1),  # dotted eighth note
    Duration.from_description(8, 0),  # eighth note
    Duration.from_description(16, 1),  # dotted sixteenth note
    Duration.from_description(16, 0),  # sixteenth note
    Duration.from_description(32, 1),  # dotted thirty-second note
    Duration.from_description(32, 0),  # thirty-second note
    Duration.from_description(64, 1),  # dotted sixty-fourth note
    Duration.from_description(64, 0)  # sixty-fourth note
]


@dataclass
class Note:
    duration: Duration
    pitch: int  # midi number


# key - instrument name, value - midi number
# I have chosen several musical instruments in my opinion
instruments = {
    "Acoustic grand piano": 0,
    "Steel string acoustic guitar": 25,
    "Clean electric guitar": 27,
    "Acoustic bass": 32,
    "Slap bass 1": 36,
    "Choir aahs": 52
}


# Key - instrument type, value - clef and pitches (midi numbers)
# Pitches are chosen in such a way that only notes without sharps and flats are among them.
# For bass and guitars, the first pitch indicates the pitch of the 4th or 6th string in the standard formation.
# The number of pitches is equal to the number of available durations
instruments_musical_ranges = {
    "bass": ["bass_8vb", [28, 29, 31, 33, 35, 36, 38, 40, 41, 43, 45, 47, 48]],
    "guitar": ["bass", [40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60]],
    "other": ["treble", [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81]]
}


