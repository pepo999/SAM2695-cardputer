import M5
from M5 import *
from unit import SynthUnit
import time
import _thread
from utility import print_error_msg
from hardware import *

synth = None
kb = None
mode = 'menu'

octave = 0
instrument = 1
polyphony = True
looper = None
metronome = None
measure_time = None

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

octave_map = {
  -3: -36,
  -2: -24,
  -1: -12,
  0: 0,
  1: 12,
  2: 24,
  3: 36
}

class Looper:
    def __init__(self, bpm=120, time_signature=(4, 4)):
        self.bpm = bpm
        self.time_signature = time_signature
        self.measure_length = (60 / bpm) * time_signature[0]
        self.events = []  # List to store recorded events
        self.is_recording = False
        self.start_time = None
        self.playback_running = False
        self.playback_thread_id = None
        self.metronome_running = False
        self.metronome_thread_id = None

    def start_recording(self):
        self.is_recording = True
        self.start_time = time.time()
        self.events = []

    def stop_recording(self):
        self.is_recording = False

    def record_event(self, event):
        if self.is_recording:
            timestamp = time.time() - self.start_time
            self.events.append((timestamp, event))

    def play(self):
        if self.playback_running:
            print("Playback already running.")
            return
        self.playback_running = True
        self.playback_thread_id = _thread.start_new_thread(self._play_thread, ())

    def stop_playback(self):
        self.playback_running = False

    def _play_thread(self):
        global measure_time
        if not self.events:
            pass
            # print("No events recorded.")
        
        if measure_time is None:
            measure_time = time.time()
        while self.playback_running:
            if self.events != []:
                self.events = sorted(self.events, key = lambda x: x[0])
                time_diffs =[self.events[0][0]] + [self.events[i+1][0]-self.events[i][0] for i in range(len(self.events)-1)]
                for event, t in zip(self.events, time_diffs):
                    if time.time() - measure_time >= self.measure_length:
                        measure_time = time.time()
                    time.sleep(t)
                    self.play_event(event)
                

    def play_event(self, event):
        octave = event[3]
        synth.set_instrument(0, 0, event[2])
        play_note(event[1])
        synth.set_instrument(0, 0, instrument)

    def start_metronome(self):
        beats, beat_unit = self.time_signature
        interval = 60 / self.bpm
        for beat in range(beats):
            if beat == 0:
                pitch = 100
            else:
                pitch = 88
            self.events.append((interval * (beat + 1), pitch, 115, 0))
        self.metronome_running = True

    def stop_metronome(self):
        self.events = [event for event in self.events if event[2] != 115]
        self.metronome_running = False
        looper_screen()

def keyboard(kb):
    global mode, synth, octave, instrument, polyphony, looper
    key = kb.get_string()
    if mode == 'menu':
        if key == '1':
            mode = 'piano'
            piano()
        elif key == '2':
            mode = 'looper'
            looper_screen()
        else:
            menu()
            
    elif mode == 'piano':
        if key == 'a':
            if not polyphony:
                synth.set_all_notes_off(0)
            play_note(60)
        elif key == 'e':
            if not polyphony:
                synth.set_all_notes_off(0)
            if looper.is_recording:
                  looper.events.append((time.time() - measure_time, 61, instrument, octave))
                  
            play_note(61)
        elif key == 's':
            if not polyphony:
                synth.set_all_notes_off(0)
            if looper.is_recording:
                  looper.events.append((time.time() - measure_time, 62, instrument, octave))
            play_note(62)
        elif key == 'r':
            if not polyphony:
                synth.set_all_notes_off(0)
            if looper.is_recording:
                  looper.events.append((time.time() - measure_time, 63, instrument, octave))
            play_note(63)
        elif key == 'd':
            if not polyphony:
                synth.set_all_notes_off(0)
            if looper.is_recording:
                  looper.events.append((time.time() - measure_time, 64, instrument, octave))
            play_note(64)
        elif key == 'f':
            if not polyphony:
                synth.set_all_notes_off(0)
            if looper.is_recording:
                  looper.events.append((time.time() - measure_time, 65, instrument, octave))
            play_note(65)
        elif key == 'y':
            if not polyphony:
                synth.set_all_notes_off(0)
            if looper.is_recording:
                  looper.events.append((time.time() - measure_time, 66, instrument, octave))
            play_note(66)
        elif key == 'g':
            if not polyphony:
                synth.set_all_notes_off(0)
            if looper.is_recording:
                  looper.events.append((time.time() - measure_time, 67, instrument, octave))
            play_note(67)
        elif key == 'u':
            if not polyphony:
                synth.set_all_notes_off(0)
            if looper.is_recording:
                  looper.events.append((time.time() - measure_time, 68, instrument, octave))
            play_note(68)
        elif key == 'h':
            if not polyphony:
                synth.set_all_notes_off(0)
            if looper.is_recording:
                  looper.events.append((time.time() - measure_time, 69, instrument, octave))
            play_note(69)
        elif key == 'alt':
            if not polyphony:
                synth.set_all_notes_off(0)
            if looper.is_recording:
                  looper.events.append((time.time() - measure_time, 70, instrument, octave))
            play_note(70)
        elif key == 'j':
            if not polyphony:
                synth.set_all_notes_off(0)
            if looper.is_recording:
                  looper.events.append((time.time() - measure_time, 71, instrument, octave))
            play_note(71)
        elif key == 'k':
            if not polyphony:
                synth.set_all_notes_off(0)
            if looper.is_recording:
                  looper.events.append((time.time() - measure_time, 72, instrument, octave))
            play_note(72)

        elif key == '[':
            instrument -= 1
            if instrument == 0:
                instrument = 127
            synth.set_instrument(0, 0, instrument)
            piano()
        elif key == ']':
            instrument += 1
            if instrument == 128:
                instrument = 1
            synth.set_instrument(0, 0, instrument)
            piano()
        
        elif key == 'p':
            polyphony = not polyphony
            if polyphony == False:
                synth.set_all_notes_off(0)
            piano()

        elif key == '-':
            if octave >= -2:
                octave -= 1
            piano()
        elif key == '=':
            if octave <= 2:
                octave += 1
            piano()
        elif key == 'm':
            info()
        elif key == '`':
            mode = 'menu'
            menu()

    elif mode == 'looper':
        if key == '1':
            print('Select channel')
            looper.select_channel(0)
        elif key == '2':
            looper.start_recording()
            print('start recording')
        elif key == '4':
            looper.play()
            print('Play')
        elif key == '5':
            looper.set_bpm(120)
        elif key == '6':
            looper.set_time_signature(4, 4)
        elif key == 'q':
            if looper.metronome_running:
                looper.stop_metronome()
            else:
                looper.start_metronome()
            looper_screen()
        elif key == '3':
            looper.stop_recording()
            synth.set_all_notes_off(0)
            looper.playback_running = False

        
        elif key == '`':
            mode = 'menu'
            menu()

def piano():
    Widgets.fillScreen(0x000000)
    active_inst = instruments_map[instrument]
    Widgets.Label('Inst:' + active_inst, 10, 10, 2)
    Widgets.Label('Octave:' + str(octave + 4), 10, 30, 2)
    Widgets.Label('Poly:' + str(polyphony), 10, 50, 2)

def play_note(note):
    global synth, octave
    if -3 <= octave <= 3:
        note += octave_map[octave]
    synth.set_note_on(0, note, 127)

def looper_screen():
    Widgets.fillScreen(0x000000)
    Widgets.Label('Metronome:' + str(looper.metronome_running), 10, 10, 2)

def menu():
    # synth.set_all_notes_off(0)
    Widgets.fillScreen(0xFFB6C1)
    Widgets.Label("Corizo", 10, 10, 2)
    Widgets.Label("1. Keyboard mode", 10, 40, 2)
    Widgets.Label("2. Looper mode", 10, 60, 2)

def info():
    Widgets.fillScreen(0x000000)
    if mode == 'piano':
        Widgets.Label('Press the [ or ] to change instrument', 10, 10, 1)
        Widgets.Label('Press p to switch polyphony on/off.', 10, 20, 1)
        Widgets.Label('Press - or = to change octave.', 10, 30, 1)

def setup():
    global synth, kb, looper, metronome
    M5.begin()
    Widgets.setRotation(1)
    synth = SynthUnit((1, 2), 1)
    metronome = SynthUnit((1, 1), 1)
    metronome.set_reverb(0,0,0,0)
    kb = MatrixKeyboard()
    kb.set_callback(keyboard)
    synth.set_instrument(0, 0, 1)
    # looper = Looper()
    looper = Looper(bpm=120, time_signature=(4, 4))
    if mode == 'menu':
        menu()

def loop():
    M5.update()
    kb.tick()

if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
    except (Exception, KeyboardInterrupt) as e:
        print_error_msg(e)
