import M5
from M5 import *
from unit import SynthUnit
import time

synth = None
metronome = None
kb = None
mode = 'menu'

octave = 0
instrument = 'piano'
polyphony = True
looper = None
metronome_state = None

octave_map = {
  -3: -36,
  -2: -24,
  -1: -12,
  0: 0,
  1: 12,
  2: 24,
  3: 36
}

class MetronomeState:
    def __init__(self, bpm, time_signature):
        self.bpm = bpm
        self.time_signature = time_signature
        self.interval = 60 / bpm
        self.last_time = time.time()
        self.current_beat = 0
        self.running = False

    def reset(self):
        self.last_time = time.time()
        self.current_beat = 0

class Looper:
    def __init__(self, bpm=120, time_signature=(4, 4)):
        self.bpm = bpm
        self.time_signature = time_signature
        self.channels = {}
        self.is_recording = False
        self.current_channel = None
        self.start_time = None

    def set_bpm(self, bpm):
        self.bpm = bpm

    def set_time_signature(self, beats, beat_unit):
        self.time_signature = (beats, beat_unit)

    def select_channel(self, channel):
        if channel not in self.channels:
            self.channels[channel] = []
        self.current_channel = channel

    def start_recording(self):
        if self.current_channel is not None:
            self.is_recording = True
            self.start_time = time.time()
            self.channels[self.current_channel] = []

    def stop_recording(self):
        self.is_recording = False

    def record_event(self, event):
        if self.is_recording and self.current_channel is not None:
            timestamp = time.time() - self.start_time
            self.channels[self.current_channel].append((timestamp, event))

    def play(self):
        if self.current_channel is not None:
            events = self.channels[self.current_channel]
            start_time = time.time()
            for timestamp, event in events:
                while time.time() - start_time < timestamp:
                    pass
                self.play_event(event)

    def play_event(self, event):
        color, note = event
        playColorAndNote(color, note)

def play_beep(frequency, duration=0.1):
    metronome.set_note_on(0, frequency, 70)

def update_metronome():
    global metronome_state
    if metronome_state and metronome_state.running:
        current_time = time.time()
        if current_time - metronome_state.last_time >= metronome_state.interval:
            beats, beat_unit = metronome_state.time_signature
            if metronome_state.current_beat == 0:
                play_beep(100)
            else:
                play_beep(88)
            
            metronome_state.last_time = current_time
            metronome_state.current_beat = (metronome_state.current_beat + 1) % beats

def keyboard(kb):
    global mode, synth, octave, instrument, polyphony, looper, metronome_state
    key = kb.get_string()
    # print(str(key))
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
            play_note(61)
        elif key == 's':
            if not polyphony:
                synth.set_all_notes_off(0)
            play_note(62)
        elif key == 'r':
            if not polyphony:
                synth.set_all_notes_off(0)
            play_note(63)
        elif key == 'd':
            if not polyphony:
                synth.set_all_notes_off(0)
            play_note(64)
        elif key == 'f':
            if not polyphony:
                synth.set_all_notes_off(0)
            play_note(65)
        elif key == 'y':
            if not polyphony:
                synth.set_all_notes_off(0)
            play_note(66)
        elif key == 'g':
            if not polyphony:
                synth.set_all_notes_off(0)
            play_note(67)
        elif key == 'u':
            if not polyphony:
                synth.set_all_notes_off(0)
            play_note(68)
        elif key == 'h':
            if not polyphony:
                synth.set_all_notes_off(0)
            play_note(69)
        elif key == 'alt':
            if not polyphony:
                synth.set_all_notes_off(0)
            play_note(70)
        elif key == 'j':
            if not polyphony:
                synth.set_all_notes_off(0)
            play_note(71)
        elif key == 'k':
            if not polyphony:
                synth.set_all_notes_off(0)
            play_note(72)

        elif key == '1':
            synth.set_instrument(0, 0, 1)
            instrument = 'piano'
            piano()
        elif key == '2':
            synth.set_instrument(0, 0, 20)
            instrument = 'fisa'
            piano()
        elif key == '3':
            synth.set_instrument(0, 0, 78)
            instrument = 'glass'
            piano()
        elif key == '4':
            synth.set_instrument(0, 0, 74)
            instrument = 'violin'
            piano()
        elif key == '5':
            synth.set_instrument(0, 0, 25)
            instrument = 'mandolin'
            piano()
        elif key == '6':
            synth.set_instrument(0, 0, 28)
            instrument = 'piano'
            piano()
        elif key == '7':
            synth.set_instrument(0, 0, 33)
            instrument = 'piano'
            piano()
        elif key == '8':
            synth.set_instrument(0, 0, 41)
            instrument = 'viola'
            piano()
        elif key == '9':
            synth.set_instrument(0, 0, 80)
            instrument = 'synth'
            piano()
        elif key == '0':
            synth.set_instrument(0, 0, 105)
            instrument = 'toy piano'
            piano()
        
        elif key == 'p':
            polyphony = not polyphony
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
        elif key == '3':
            looper.stop_recording()
            print('recording off')
        elif key == '4':
            looper.play()
            print('Play')
        elif key == '5':
            looper.set_bpm(120)
        elif key == '6':
            looper.set_time_signature(4, 4)
        elif key == 'q':
            if metronome_state and metronome_state.running:
                metronome_state.running = False
            else:
                metronome_state = MetronomeState(looper.bpm, looper.time_signature)
                metronome_state.running = True
                metronome_state.reset()
            looper_screen()
        
        elif key == '`':
            mode = 'menu'
            menu()
          
def piano():
    Widgets.fillScreen(0x000000)
    Widgets.Label('Instrument:' + instrument, 10, 10, 2)
    Widgets.Label('Octave:' + str(octave + 4), 10, 30, 2)
    Widgets.Label('Polyphony:' + str(polyphony), 10, 50, 2)

def play_note(note):
    global synth, octave
    if -3 <= octave <= 3:
        note += octave_map[octave]
    synth.set_note_on(0, note, 127)

def looper_screen():
    Widgets.fillScreen(0x000000)
    Widgets.Label('Looper on:' + str(metronome_state.running if metronome_state else False), 10, 10, 2)

def menu():
    synth.set_all_notes_off(0)
    Widgets.fillScreen(0xFFB6C1)
    Widgets.Label("Corizo", 10, 10, 2)
    Widgets.Label("1. Keyboard mode", 10, 40, 2)
    Widgets.Label("2. Looper mode", 10, 60, 2)

def info():
    Widgets.fillScreen(0x000000)
    if mode == 'piano':
        Widgets.Label('Press the numbers to choose instrument', 10, 10, 1)
        Widgets.Label('Press p to switch polyphony on/off.', 10, 20, 1)
        Widgets.Label('Press - or = to change octave.', 10, 30, 1)

def setup():
    global synth, kb, looper, metronome
    M5.begin()
    Widgets.setRotation(1)
    synth = SynthUnit((1, 2), 1)
    metronome = SynthUnit((1, 1), 1)
    # print(dir(SynthUnit))
    metronome.set_reverb(0,0 ,0 ,0)
    kb = MatrixKeyboard()
    kb.set_callback(keyboard)
    synth.set_instrument(0, 0, 1)
    metronome.set_instrument(0, 0, 115)
    looper = Looper()
    if mode == 'menu':
        menu()

def loop():
    M5.update()
    kb.tick()
    update_metronome()

if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
    except (Exception, KeyboardInterrupt) as e:
        print_error_msg(e)
