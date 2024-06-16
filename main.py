import M5
from M5 import *
from unit import SynthUnit
import time

synth = None
kb = None
mode = 'menu'

octave = 0
instrument = 'piano'

octave_map = {
  -3: -36,
  -2: -24,
  -1: -12,
  0: 0,
  1: 12,
  2: 24,
  3: 36
}

def keyboard(kb):
    global mode, synth, octave, instrument
    key = kb.get_string()
    if mode == 'menu':
        if key == '1':
            mode = 'piano'
            piano()
        elif key == '2':
            pass
        else:
            menu()
            
    elif mode == 'piano':

        if key == 'a':
            play_note(60)
        elif key == 'e':
            play_note(61)
        elif key == 's':
            play_note(62)
        elif key == 'r':
            play_note(63)
        elif key == 'd':
            play_note(64)
        elif key == 'f':
            play_note(65)
        elif key == 'y':
            play_note(66)
        elif key == 'g':
            play_note(67)
        elif key == 'u':
            play_note(68)
        elif key == 'h':
            play_note(69)
        elif key == 'i':
            play_note(70)
        elif key == 'j':
            play_note(71)
        elif key == 'k':
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
        
        elif key == '-':
            if octave >= -2:
                octave -= 1
            piano()
        elif key == '=':
            if octave <= 2:
                octave += 1
            piano()

        elif key == '`':
            mode = 'menu'
            menu()

def piano():
    global synth, octave, instrument
    Widgets.fillScreen(0x000000)
    Widgets.Label('Instrument:' + instrument, 10, 10, 2)
    Widgets.Label('Octave:' + str(octave), 10, 30, 2)

def play_note(note):
    global synth, octave
    if -3 <= octave <= 3:
        note += octave_map[octave]
    synth.set_note_on(0, note, 127)

def menu():
    synth.set_all_notes_off(0)
    Widgets.fillScreen(0xFFB6C1)
    Widgets.Label("Corizo", 10, 10, 2)
    Widgets.Label("1. Keyboard mode", 10, 40, 2)
    Widgets.Label("2. Looper mode", 10, 60, 2)

def setup():
    global synth, kb
    M5.begin()
    Widgets.setRotation(1)
    synth = SynthUnit((1, 2), 1)
    kb = MatrixKeyboard()
    kb.set_callback(keyboard)
    synth.set_instrument(0, 0, 1)
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
