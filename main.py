import os, sys, io
import M5
from M5 import *
from unit import SynthUnit
import time
from hardware import *
from utility import print_error_msg

synth = None
kb = None

def playColorAndNote(color, note):
  global synth, isPlaying
  Widgets.fillScreen(color)
  synth.set_note_on(0, note, 127)

def kb_pressed_event(kb):
  global synth
  Widgets.fillScreen(0x000000)
  synth.set_all_notes_off(0)
  key = kb.get_string()
  if key == 'a':
    playColorAndNote(0x003f5c,60)
  elif key == 's':
    playColorAndNote(0x2c4875,62)
  elif key == 'd':
    playColorAndNote(0x8a508f,64)
  elif key == 'f':
    playColorAndNote(0xbc5090,65)
  elif key == 'g':
    playColorAndNote(0xff6361,67)
  elif key == 'h':
    playColorAndNote(0xff8531,69)
  elif key == 'j':
    playColorAndNote(0xffa600,71)
  elif key == '1':
    synth.set_instrument(0, 0, 1)
  elif key == '2':
    synth.set_instrument(0, 0, 20)
  elif key == '3':
    synth.set_instrument(0, 0, 78)
  elif key == '4':
    synth.set_instrument(0, 0, 74)
  elif key == '5':
    synth.set_instrument(0, 0, 25)
  elif key == '6':
    synth.set_instrument(0, 0, 28)
  elif key == '7':
    synth.set_instrument(0, 0, 33)
  elif key == '8':
    synth.set_instrument(0, 0, 41)
  elif key == '9':
    synth.set_instrument(0, 0, 80)
  elif key == '0':
    synth.set_instrument(0, 0, 105)

def setup():
  M5.begin()
  global synth, kb, label0
  Widgets.setRotation(1)
  Widgets.fillScreen(0x41fd99)
  synth = SynthUnit((1,2),1)
  kb = MatrixKeyboard()
  kb.set_callback(kb_pressed_event)
  synth.set_instrument(0, 0, 1)

def loop():
  global synth, kb, label0, isPlaying
  M5.update()
  kb.tick()
    
if __name__ == '__main__':
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    try:
      print_error_msg(e)
    except ImportError:
      print("please update to latest firmware")
