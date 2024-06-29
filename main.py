import M5
from M5 import *
from unit import SynthUnit
import time
from time import time_ns
import _thread
from utility import print_error_msg
from hardware import *
from hardware import sdcard
import json


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
            for i in range(16):
                synth.set_all_notes_off(i)
        update_screen(mode, y)

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
        global start_time, idx, drum_idx
        if self.is_playing:
            while True and self.events != []:
                current_time = time_ns() - start_time
                delta_time = current_time % self.measure_length
                try:
                    if delta_time > self.events[idx][0]:
                        if self.events[idx][2] == '':
                            self.play_drum_event(self.events[idx])
                        else:
                            self.play_event(self.events[idx])
                        idx += 1
                        if idx >= len(self.events):
                            idx = 0
                            start_time = time_ns()
                    else:
                        break
                except Exception as e:
                    idx -= 1

    def play_event(self, event):
        global octave
        old_octave = octave
        octave = event[3]
        synth.set_instrument(0, 0, event[2])
        play_note(event[1], event[4])
        octave = event[4]
        synth.set_instrument(0, 0, instrument)
        octave = old_octave

    def play_drum_event(self, event):
        play_drum_note(event[1], event[4])

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
            binary_search_insert(self.events, (t, pitch, 115, octave, 0))

    def metronome(self):
        self.metronome_running = not self.metronome_running
        if not self.metronome_running:
            self.events = [(event[0], event[1], event[2], event[3], 0 if event[2] == 115 else event[4]) for event in self.events]
        else:
            self.events = [(event[0], event[1], event[2], event[3], self.metronome_volume if event[2] == 115 else event[4]) for event in self.events]
        update_screen(mode, y)

    def clear_events(self):
        for i in range(16):
            synth.set_all_notes_off(i)
        self.events = [_ for _ in self.events if _[2] == 115]
        self.history = []
        self.is_playing = False
        Widgets.fillScreen(0x000000)
        Widgets.Label('Events cleared', 10, 10, 2, 0xffffff, 0x000000)
        time.sleep(1)
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

class SD_Card:
    def __init__(self):
        self.sd_card = sdcard.SDCard(slot=3, width=1, sck=40, miso=39, mosi=14, cs=12, freq=1000000)
        self.directory = sdcard.os.getcwd()
        self.listdir = sdcard.os.listdir('/flash')
        self.filename = ''

    def save(self, events):
        events = [_ for _ in events if _[2] != 115]
        if events != []:
            json_events = {
                "events": events,
                "time_signature": looper.time_signature,
                "bpm": looper.bpm
            }
            with open(self.directory + '/' + self.filename + '.json', 'w') as f:
                json_events = json.dump(json_events, f)
            Widgets.fillScreen(0x000000)
            Widgets.Label('Events saved', 10, 10, 2, 0xffffff, 0x000000)
            time.sleep(1)
            self.filename = ''
            set_mode("looper")
        
    def load_file(self, files, idx):
        with open(files[idx], 'r') as f:
            events_dict = json.load(f)
        looper.events = events_dict["events"]
        looper.time_signature = events_dict["time_signature"]
        looper.bpm = events_dict["bpm"]
        looper.is_playing = False
        looper.metronome_running = False
        looper.measure_length = (60 / looper.bpm) * looper.time_signature * 1e9
        interval = (60 / looper.bpm) * 1e9
        for beat in range(looper.time_signature):
            if beat == 0:
                pitch = 100
                t = interval * beat
            elif beat == looper.time_signature:
                pitch = 0
                t = looper.measure_length
            else:
                pitch = 88
                t = interval * beat
            binary_search_insert(looper.events, (t, pitch, 115, octave, 0))
        Widgets.fillScreen(0x000000)
        Widgets.Label('Events loaded', 10, 10, 2, 0xffffff, 0x000000)
        time.sleep(1)
        set_mode("looper")

    def files(self):
        self.sd_card = sdcard.SDCard(slot=3, width=1, sck=40, miso=39, mosi=14, cs=12, freq=1000000)
        self.directory = sdcard.os.getcwd()
        self.listdir = sdcard.os.listdir('/flash')
        files = [f for f in self.listdir if f.endswith('.json')]
        files = sorted(files)
        if not files:
            ui_map["files"].append(
                ("No files on sd card found", lambda: print_info(''), lambda: print_info(''), lambda: print_info(''))
            )
        else:
            files_ui = [
                (f.replace('.json', ''), "", lambda idx=idx: self.load_file(files, idx), lambda: print_info(''))
                for idx, f in enumerate(files)
            ]
            ui_map["files"] = files_ui
        set_mode("files")

    def delete_file(self, y):
        self.sd_card = sdcard.SDCard(slot=3, width=1, sck=40, miso=39, mosi=14, cs=12, freq=1000000)
        self.directory = sdcard.os.getcwd()
        self.listdir = sdcard.os.listdir('/flash')
        files = [f for f in self.listdir if f.endswith('.json')]
        os.remove(files[y])
        Widgets.fillScreen(0x000000)
        Widgets.Label('File deleted', 10, 10, 2, 0xffffff, 0x000000)
        time.sleep(1)
        set_mode("options")



######################
#  GLOBAL VARIABLES  #
######################


# SETUP
kb = None
synth = None
mode = 'menu'
looper = Looper()
sd_card = None
master = 125

# SYNTH
instrument = 1
octave = 0
volume = 40
polyphony = True
drum_kit = 1
channel = 0

# LOOPER
start_time = 0
current_time = 0
delta_time = 0
idx = 0
drum_idx = 0

# SCREEN
y = 0 # UI position
rel_y = 0
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
        ("2. Looper mode", "", lambda: print('')),
        ("3. Drum mode", "", lambda: print('')),
        ("4. Options", "", lambda: print(''))
        ],
  "piano": [
        ("Inst:", lambda: instruments_map[instrument], lambda: change_instrument(1), lambda: change_instrument(-1)),
        ("Octave:", lambda: str(octave + 4) + ' ' * 5, lambda: change_octave(1), lambda: change_octave(-1)),
        ("Polyphony:", lambda: polyphony, lambda: switch_polyphony(), lambda: switch_polyphony()),
        ("Volume:", lambda: volume, lambda: change_volume(5), lambda: change_volume(-5))
  ],
  "drums": [
        ("Drum kit:", lambda: drum_kit, lambda: print_info(''), lambda: print_info('')),
        ("Volume:", lambda: volume, lambda: change_volume(5), lambda: change_volume(-5))
  ],
  "looper": [
        ('Metronome:', lambda: "On" if looper.metronome_running else "Off", lambda: looper.metronome(), lambda: looper.metronome()),
        ('Playing:', lambda: "On" if looper.is_playing else "Off", lambda: looper.switch_play(), lambda: looper.switch_play()),
        ('Recording:', lambda: "On" if looper.is_recording else "Off", lambda: looper.recording(), lambda: looper.recording()),
        ('Bpm:', lambda: looper.bpm, lambda: looper.change_bpm(5), lambda: looper.change_bpm(-5)),
        ('Time signature:', lambda: looper.time_signature - 1, lambda: looper.change_time_signature(1), lambda: looper.change_time_signature(-1))
  ],
  "options": [
        ('', lambda: "Save ->" if sd_card else "No SD card found", lambda: set_mode("menu"), lambda: set_mode("filename")),
        ('', lambda: "Load ->" if sd_card else "", lambda: set_mode("menu"), lambda: sd_card.files()),
        ('Master vol:', lambda: master, lambda: change_master(-1), lambda: change_master(1))
  ],
  "files": [

  ],
  "filename": [
       ('Name:', lambda: sd_card.filename if sd_card else "No SD card found", lambda: print(''), lambda: sd_card.save(looper.events))
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
        'e': 61,
        's': 62,
        'r': 63,
        'd': 64,
        'f': 65,
        't': 66,
        'g': 67,
        'y': 68,
        'h': 69,
        'u': 70,
        'j': 71,
        'k': 72
}

drum_map = {
        1: ['Kick drum', 'Snare Drum', 'Acoustic Low Tom', 'Acoustic Middle Tom', 'Crash Cymbal 2', 'Crash Cymbal', 'Ride Cymbal', 'Open Hi Hat [EXC1]', 'Closed Hi Hat [EXC1]']
}

drum_note_map = {
      'a': 0,
      's': 1,
      'd': 2,
      'f': 3,
      'g': 4,
      'h': 5,
      'j': 6,
      'k': 7,
      'l': 8
}

key_map = {
    "menu": {
        '1': lambda: set_mode('piano'),
        '2': lambda: set_mode('looper'),
        '3': lambda: set_mode('drums'),
        '4': lambda: set_mode('options'),
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
        '2': lambda: set_mode('looper'),
        '3': lambda: set_mode('drums'),
        '4': lambda: set_mode('options'),
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
        '.': lambda: change_y(1),
        '/': lambda: ui_map[mode][y][2](),
        ',': lambda: ui_map[mode][y][3](),
        '0': lambda: looper.clear_events(),
        '1': lambda: set_mode('piano'),
        '2': lambda: set_mode('looper'),
        '4': lambda: set_mode('options'),
        '`': lambda: set_mode('menu'),
        'a': lambda: play_drum_note(drum_map[drum_kit][0], volume),
        's': lambda: play_drum_note(drum_map[drum_kit][1], volume),
        'd': lambda: play_drum_note(drum_map[drum_kit][2], volume),
        'f': lambda: play_drum_note(drum_map[drum_kit][3], volume),
        'g': lambda: play_drum_note(drum_map[drum_kit][4], volume),
        'h': lambda: play_drum_note(drum_map[drum_kit][5], volume),
        'j': lambda: play_drum_note(drum_map[drum_kit][6], volume),
        'k': lambda: play_drum_note(drum_map[drum_kit][7], volume),
        'l': lambda: play_drum_note(drum_map[drum_kit][8], volume),
        '\\': lambda: looper.delete_last()
    },
    "looper": {
        ';': lambda: change_y(-1),
        '.': lambda: change_y(1),
        '/': lambda: ui_map[mode][y][2](),
        ',': lambda: ui_map[mode][y][3](),
        '1': lambda: set_mode('piano'),
        '3': lambda: set_mode('drums'),
        '4': lambda: set_mode('options'),
        '0': lambda: looper.clear_events(),
        'r': lambda: looper.recording(),
        'p': lambda: looper.switch_play(),
        'q': lambda: looper.metronome(),
        'm': lambda: print_info('Info'),
        '`': lambda: set_mode('menu'),
        '\\': lambda: looper.delete_last()
    },
    "options": {
        ';': lambda: change_y(-1),
        '.': lambda: change_y(1),
        '/': lambda: ui_map[mode][y][3](),
        ',': lambda: ui_map[mode][y][2](),
        '1': lambda: set_mode('piano'),
        '2': lambda: set_mode('looper'),
        '3': lambda: set_mode('drums'),
        '0': lambda: looper.clear_events(),
        'm': lambda: print_info('Info'),
        '`': lambda: set_mode('menu'),
        '\\': lambda: looper.delete_last()
    },
    "files": {
        ';': lambda: change_y(-1),
        '.': lambda: change_y(1),
        '/': lambda: ui_map[mode][y][2](),
        ',': lambda: ui_map[mode][y][3](),
        '`': lambda: set_mode('options'),
        'd': lambda: sd_card.delete_file(y),
        '1': lambda: set_mode('piano'),
        '2': lambda: set_mode('looper'),
        '3': lambda: set_mode('drums')
    },
    "filename":{
      '`': lambda: set_mode('options'),
      ',': lambda: set_mode('options'),
      '/': lambda: ui_map[mode][y][3]()
    }
}  
    

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

    if mode == "filename" and key != '\\' and key != '/':
        sd_card.filename += key
        set_mode("filename")
    if mode == "filename" and key == '\\':
        sd_card.filename = sd_card.filename[:-1] if len(sd_card.filename) > 0 else sd_card.filename
        set_mode("filename")

    note = note_map.get(key, None)
    if looper.is_recording and looper.is_playing and note and mode == 'piano':
        current_time = time_ns() - start_time
        delta_time = current_time % (looper.measure_length)
        binary_search_insert(looper.events, (delta_time, note, instrument, octave, volume))
        looper.history.append((delta_time, note, instrument, octave, volume))
    drum_sound = drum_note_map.get(key, None)
    if looper.is_recording and looper.is_playing and drum_sound is not None and mode == 'drums':
        current_time = time_ns() - start_time
        delta_time = current_time % (looper.measure_length)
        binary_search_insert(looper.events, (delta_time, drum_map[drum_kit][drum_sound], '', 0, volume))
        looper.history.append((delta_time, drum_map[drum_kit][drum_sound], '', 0, volume))
    

def play_note(note, volume):
    global synth, octave, channel
    if not polyphony:
        synth.set_all_notes_off(0)
    if -3 <= octave <= 3:
        note += octave_map[octave]
    volume_out = volume - (125 - master)
    if volume_out >= 125:
        volume_out = 125
    if volume_out <= 0:
        volume_out = 0
    synth.set_note_on(0, note, volume_out)
    if channel + 1 <= 15:
        channel += 1
    else:
        channel = 0

def play_drum_note(drum_sound, volume):
    if not polyphony:
        synth.set_all_notes_off(0)
    volume_out = volume - (125 - master)
    if volume_out >= 125:
        volume_out = 125
    if volume_out <= 0:
        volume_out = 0
    synth.set_drums_instrument(drum_sound, volume_out)

def change_master(change):
    global master
    if 0 <= master + change <= 125:
        master += change
    update_screen(mode, y)

def change_y(change):
    global y
    if 0 <= y + change < len(ui_map[mode]):
        y += change
    update_screen(mode, y)

def change_instrument(change):
    global instrument
    instrument = (instrument + change - 1) % 127 + 1
    if instrument == 115 and change == 1:
        instrument = 116
    if instrument == 115 and change == -1:
        instrument = 114
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
    global mode, y, rel_h
    y = 0
    rel_y = 0
    mode = new_mode
    update_screen(mode, y)

def switch_polyphony():
    global polyphony
    polyphony = not polyphony
    update_screen(mode, y)

def print_info(info):
    pass

def update_screen(mode, y):
    label_y = 10
    if y >= 4:
        label_y -= (20 * (y - 4))
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
        # time.sleep(0.00001)

def setup():
    global kb, synth, looper, sd_card
    M5.begin()
    Widgets.setRotation(1)
    synth = SynthUnit((1, 2), 1)
    synth.set_instrument(0, 0, instrument)
    kb = MatrixKeyboard()
    kb.set_callback(keyboard)
    sd_card = None
    try:
        sd_card = SD_Card()
        print("SD card loaded succesfully")
    except Exception as e:
        print("No SD card loaded:", str(e))
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
