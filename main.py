import M5
from M5 import *
from unit import SynthUnit
import time
from time import time_ns
import _thread
from utility import print_error_msg
from hardware import *

######################
#  GLOBAL VARIABLES  #
######################


# SETUP
kb = None
synth = None
mode = 'menu'
looper = Looper()

# SYNTH
instrument = 1
octave = 0
volume = 40
polyphony = True

# LOOPER
start_time = 0
current_time = 0
delta_time = 0
idx = 0

# SCREEN
y = 0 # UI position
background_color = 0xB45B9F # 0xFFB6C1

# MAPS
octave_map = {
    -3: -36,
    -2: -24,
    -1: -12,
    0: 0,
    1: 12,
    2: 24,
    3: 36
}

ui_map = {
  "menu": [
        ("Corizo", "", lambda: print('')),
        ("1. Keyboard mode", "", lambda: print('')),
        ("2. Looper mode", "", lambda: print(''))
        ],
  "piano": [
        ("Inst:", lambda: instruments_map[instrument], lambda: change_instrument(1), lambda: change_instrument(-1)),
        ("Octave:", lambda: octave + 4, lambda: change_octave(1), lambda: change_octave(-1)),
        ("Polyphony:", lambda: polyphony, lambda: switch_polyphony(), lambda: switch_polyphony()),
        ("Volume:", lambda: volume, lambda: change_volume(5), lambda: change_volume(-5))
  ],
  "looper": [
        ('Metronome:', lambda: "On" if looper.metronome_running else "Off", lambda: looper.metronome(), lambda: looper.metronome()),
        ('Playing:', lambda: "On" if looper.is_playing else "Off", lambda: looper.switch_play(), lambda: looper.switch_play()),
        ('Recording:', lambda: "On" if looper.is_recording else "Off", lambda: looper.recording(), lambda: looper.recording()),
        ('Bpm:', lambda: looper.bpm, lambda: looper.change_bpm(1), lambda: looper.change_bpm(-1)),
        ('Time signature:', lambda: looper.time_signature - 1, lambda: looper.change_time_signature(1), lambda: looper.change_time_signature(-1))
  ]
}
        
instruments_map = {
1  : "Grand Piano",
2  : "Bright Piano",
3  : "Electric Grand Piano",
4  : "Honky-tonk Piano",
5  : "Electric Piano 1",
6  : "Electric Piano 2",
7  : "Harpsichord",
8  : "Clavi",
9  : "Celesta",
10  : "Glockenspiel",
11  : "Music Box",
12  : "Vibraphone",
13  : "Marimba",
14  : "Xylophone",
15  : "Tubular Bells",
16  : "Santur",
17  : "Drawbar Organ",
18  : "Percussive Organ",
19  : "Rock Organ",
20  : "Church Organ",
21  : "Reed Organ",
22  : "Accordion (French)",
23  : "Harmonica",
24  : "Tango Accordion",
25  : "Acoustic Guitar (Nylon)",
26  : "Acoustic Guitar (Steel)",
27  : "Electric Guitar (Jazz)",
28  : "Electric Guitar (Clean)",
29  : "Electric Guitar (Muted)",
30  : "Overdriven Guitar",
31  : "Distortion Guitar",
32  : "Guitar Harmonics",
33  : "Acoustic Bass",
34  : "Finger Bass",
35  : "Picked Bass",
36  : "Fretless Bass",
37  : "Slap Bass 1",
38  : "Slap Bass 2",
39  : "Synth Bass 1",
40  : "Violin",
41  : "Viola",
42  : "Cello",
43  : "Contrabass",
44  : "Tremolo Strings",
45  : "Pizzicato Strings",
46  : "Orchestral Harp",
47  : "Timpani",
48  : "String Ensemble 1",
49  : "String Ensemble 2",
50  : "Synth Strings 1",
51  : "Synth Strings 2",
52  : "Choir Aahs",
53  : "Voice Oohs",
54  : "Synth Voice",
55  : "Orchestra Hit",
56  : "Trumpet",
57  : "Trombone",
58  : "Tuba",
59  : "Muted Trumpet",
60  : "French Horn",
61  : "Brass Section",
62  : "Synth Brass 1",
63  : "Synth Brass 2",
64  : "Soprano Sax",
65  : "Alto Sax",
66  : "Tenor Sax",
67  : "Baritone Sax",
68  : "Oboe",
69  : "English Horn",
70  : "Bassoon",
71  : "Clarinet",
72  : "Piccolo",
73  : "Flute",
74  : "Recorder",
75  : "Pan Flute",
76  : "Blown Bottle",
77  : "Shakuhachi",
78  : "Whistle",
79  : "Ocarina",
80  : "Lead 1 (Square)",
81  : "Lead 2 (Sawtooth)",
82  : "Lead 3 (Calliope)",
83  : "Lead 4 (Chiff)",
84  : "Lead 5 (Charang)",
85  : "Lead 6 (Voice)",
86  : "Lead 7 (Fifths)",
87  : "Lead 8 (Bass + Lead)",
88  : "Pad 1 (Fantasia)",
89  : "Pad 2 (Warm)",
90  : "Pad 3 (Polysynth)",
91  : "Pad 4 (Choir)",
92  : "Pad 5 (Bowed)",
93  : "Pad 6 (Metallic)",
94  : "Pad 7 (Halo)",
95  : "Pad 8 (Sweep)",
96  : "FX 1 (Rain)",
97  : "FX 2 (Soundtrack)",
98  : "FX 3 (Crystal)",
99  : "FX 4 (Atmosphere)",
100  : "FX 5 (Brightness)",
101  : "FX 6 (Goblins)",
102  : "FX 7 (Echoes)",
103  : "FX 8 (Sci-fi)",
104  : "Sitar",
105  : "Banjo",
106  : "Shamisen",
107  : "Koto",
108  : "Kalimba",
109  : "Bag Pipe",
110  : "Fiddle",
111  : "Shanai",
112  : "Tinkle Bell",
113  : "Agogo",
114  : "Steel Drums",
115  : "Woodblock",
116  : "Taiko Drum",
117  : "Melodic Tom",
118  : "Synth Drum",
119  : "Reverse Cymbal",
120  : "Guitar Fret Noise",
121  : "Breath Noise",
122  : "Seashore",
123  : "Bird Tweet",
124  : "Telephone Ring",
125  : "Helicopter",
126  : "Applause",
127  : "Gunshot"
}

note_map = {
        'a': 60,
        's': 62,
        'd': 64,
        'f': 65,
        'g': 67,
        'h': 69,
        'j': 71,
        'k': 72
}

key_map = {
    "menu": {
        '1': lambda: set_mode('piano'),
        '2': lambda: set_mode('looper'),
        '3': lambda: print_info('3'),
        '4': lambda: print_info('4'),
        '5': lambda: print_info('5'),
        '6': lambda: print_info('6'),
        '7': lambda: print_info('7'),
        '8': lambda: print_info('8'),
        '9': lambda: print_info('9'),
        '0': lambda: looper.clear_events()
    },
    "piano": {
        ';': lambda: change_y(-1),
        '.': lambda: change_y(1),
        '/': lambda: ui_map[mode][y][2](),
        ',': lambda: ui_map[mode][y][3](),
        '1': lambda: print_info(''),
        '2': lambda: set_mode('looper'),
        '0': lambda: looper.clear_events(),
        'a': lambda: play_note(60, volume),
        'e': lambda: play_note(61, volume),
        's': lambda: play_note(62, volume),
        'r': lambda: play_note(63, volume),
        'd': lambda: play_note(64, volume),
        'f': lambda: play_note(65, volume),
        't': lambda: play_note(66, volume),
        'g': lambda: play_note(67, volume),
        'y': lambda: play_note(68, volume),
        'h': lambda: play_note(69, volume),
        'u': lambda: play_note(70, volume),
        'j': lambda: play_note(71, volume),
        'k': lambda: play_note(72, volume),
        'p': lambda: looper.switch_play(),
        'm': lambda: print_info('Info'),
        '`': lambda: set_mode('menu'),
        '\\': lambda: looper.delete_last()
    },
    "drums":{
        ';': lambda: change_y(-1),
        '.': lambda: change_y(1)

    },
    "looper": {
        ';': lambda: change_y(-1),
        '.': lambda: change_y(1),
        '/': lambda: ui_map[mode][y][2](),
        ',': lambda: ui_map[mode][y][3](),
        '1': lambda: set_mode('piano'),
        '2': lambda: print_info(''),
        '0': lambda: looper.clear_events(),
        'r': lambda: looper.recording(),
        'p': lambda: looper.switch_play(),
        'q': lambda: looper.metronome(),
        'm': lambda: print_info('Info'),
        '`': lambda: set_mode('menu'),
        'y': lambda: change_volume(-5),
        'u': lambda: change_volume(5),
        '\\': lambda: looper.delete_last(),
        'w': lambda: looper.change_bpm(-5),
        'e': lambda: looper.change_bpm(5),
        'i': lambda: looper.change_time_signature(-1),
        'o': lambda: looper.change_time_signature(1)
    }
}


#############
#  CLASSES  #
#############


class Looper:
    def __init__(self):
        self.bpm = 120
        self.time_signature = 5
        self.measure_length = (60 / self.bpm) * self.time_signature * 1e9
        self.measure_time = None
        self.events = []
        self.is_recording = False
        self.metronome_running = False
        self.metronome_volume = 30
        self.is_playing = False
        self.history = []

    def recording(self):
        self.is_recording = not self.is_recording
        update_screen(mode, y)

    def switch_play(self):
        global start_time, delta_time, idx, current_time
        start_time = time_ns()
        self.is_playing = not self.is_playing
        if not self.is_playing:
            idx = 0
            delta_time = 0
            current_time = 0

    def change_time_signature(self, change):
        if 0 < self.time_signature + change:
            self.time_signature += change

            self.events = [_ for _ in self.events if _[2] != 115]
            self.measure_length = (60 / self.bpm) * self.time_signature * 1e9
            interval = (60 / self.bpm) * 1e9
            for beat in range(self.time_signature):
                if beat == 0:
                    pitch = 100
                    t = interval * beat
                elif beat == self.time_signature:
                    pitch = 0
                    t = self.measure_length
                else:
                    pitch = 88
                    t = interval * beat
                binary_search_insert(self.events, (t, pitch, 115, octave, 0))
            if self.metronome_running:
                self.events = [(event[0], event[1], event[2], event[3], self.metronome_volume if event[2] == 115 else event[4]) for event in self.events]
            update_screen(mode, y)

    def change_bpm(self, change):
        if 0 < self.bpm + change:
            # to add: events time should be recalculated relative to bpm
            self.bpm += change
            self.events = [_ for _ in self.events if _[2] != 115]
            self.measure_length = (60 / self.bpm) * self.time_signature * 1e9
            interval = (60 / self.bpm) * 1e9
            for beat in range(self.time_signature):
                if beat == 0:
                    pitch = 100
                    t = interval * beat
                elif beat == self.time_signature:
                    pitch = 0
                    t = self.measure_length
                else:
                    pitch = 88
                    t = interval * beat
                binary_search_insert(self.events, (t, pitch, 115, octave, 0))
            if self.metronome_running:
                self.events = [(event[0], event[1], event[2], event[3], self.metronome_volume if event[2] == 115 else event[4]) for event in self.events]
            update_screen(mode, y)

    def loop(self):
        global start_time, idx
        if self.is_playing:
            while True and self.events != []:
                current_time = time_ns() - start_time
                delta_time = current_time % self.measure_length
                try:
                    if delta_time > self.events[idx][0]:
                        self.play_event(self.events[idx])
                        idx += 1
                        if idx >= len(self.events):
                            idx = 0
                            start_time = time_ns()
                    else:
                        break
                except Exception as e:
                    # print('Error', str(e))
                    idx -= 1

    def play_event(self, event):
        global octave
        old_octave = octave
        octave = event[3]
        synth.set_instrument(0, 0, event[2])
        play_note(event[1], event[4])
        octave = old_octave
        synth.set_instrument(0, 0, instrument)

    def init_metronome(self):
        interval = (60 / self.bpm * 1e9)
        for beat in range(self.time_signature):
            if beat == 0:
                pitch = 100
                t = interval * beat
            elif beat == self.time_signature:
                pitch = 0
                t = self.measure_length
            else:
                pitch = 88
                t = interval * beat
            self.events.append((t, pitch, 115, octave, 0))

    def metronome(self):
        self.metronome_running = not self.metronome_running
        if not self.metronome_running:
            self.events = [(event[0], event[1], event[2], event[3], 0 if event[2] == 115 else event[4]) for event in self.events]
        else:
            self.events = [(event[0], event[1], event[2], event[3], self.metronome_volume if event[2] == 115 else event[4]) for event in self.events]
        update_screen(mode, y)

    def clear_events(self):
        synth.set_all_notes_off(0)
        self.events = [_ for _ in self.events if _[2] == 115]
        self.is_playing = False
        update_screen(mode, y)

    def delete_last(self):
        if not self.history:
            return
        last_event = self.history[-1]
        if last_event in self.events:
            del self.events[self.events.index(last_event)]
            self.history.pop()
        else:
            self.history.pop()
            self.delete_last()


###############
#  FUNCTIONS  #       
###############


def binary_search_insert(events, new_event):
    low = 0
    high = len(events)
    while low < high:
        mid = (low + high) // 2
        if events[mid][0] < new_event[0]:
            low = mid + 1
        else:
            high = mid
    events.insert(low, new_event)

def keyboard(kb):
    global mode
    key = kb.get_string()
    if key in key_map[mode]:
        key_map[mode][key]()
    note = note_map.get(key, None)
    if looper.is_recording and looper.is_playing and note and mode == 'piano':
        current_time = time_ns() - start_time
        delta_time = current_time % (looper.measure_length)
        binary_search_insert(looper.events, (delta_time, note, instrument, octave, volume))
        looper.history.append((delta_time, note, instrument, octave, volume))
    update_screen(mode, y)

def play_note(note, volume):
    global synth, octave
    if not polyphony:
        synth.set_all_notes_off(0)
    if -3 <= octave <= 3:
        note += octave_map[octave]
    synth.set_note_on(0, note, volume)

def change_y(change):
    global y
    if 0 <= y + change < len(ui_map[mode]):
        y += change
    update_screen(mode, y)

def change_instrument(change):
    global instrument
    instrument = (instrument + change - 1) % 127 + 1
    synth.set_instrument(0, 0, instrument)
    update_screen(mode, y)

def change_volume(change):
    global volume
    if 0 <= volume + change <= 125:
        volume += change
    update_screen(mode, y)

def change_octave(change):
    global octave
    if -3 <= octave + change <= 3:
        octave += change
    update_screen(mode, y)

def set_mode(new_mode):
    global mode, y
    y = 0
    mode = new_mode
    update_screen(mode, y)

def switch_polyphony():
    global polyphony
    polyphony = not polyphony
    update_screen(mode, y)

def print_info(info):
    pass
    # print(info)

def update_screen(mode, y):
    label_y = 10
    if mode == 'menu':
        Widgets.fillScreen(background_color)
        for idx, label_info in enumerate(ui_map[mode]):
            label_text = label_info[0]
            Widgets.Label(label_text, 10, label_y, 2, 0xffffff, 0x000000)
            label_y += 20
    else:
        Widgets.fillScreen(0x000000)
        for idx, label_info in enumerate(ui_map[mode]):
            label_text = label_info[0]
            get_label_val = label_info[1]
            label_val = get_label_val() if callable(get_label_val) else get_label_val
            if y == idx:
                Widgets.Label(label_text + str(label_val), 10, label_y, 2, 0xffffff, background_color)
            else:
                Widgets.Label(label_text + str(label_val), 10, label_y, 2, 0xffffff, 0x000000)
            label_y += 20

def main():
    while True:
        kb.tick()
        looper.loop()
        M5.update()
        time.sleep(0.00001)

def setup():
    global kb, synth, looper
    M5.begin()
    Widgets.setRotation(1)
    synth = SynthUnit((1, 2), 1)
    synth.set_instrument(0, 0, instrument)
    synth.set_instrument(1, 1, 115)
    synth.set_reverb(1, 0, 0, 0)
    kb = MatrixKeyboard()
    kb.set_callback(keyboard)
    looper.init_metronome()
    Widgets.fillScreen(background_color)
    update_screen(mode, y)


###########################
#  MAIN FUNCTION CALLING  #
###########################


if __name__ == '__main__':
    try:
        setup()
        main()
    except (Exception, KeyboardInterrupt) as e:
        print_error_msg(e)