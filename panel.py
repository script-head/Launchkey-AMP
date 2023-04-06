import mido
import random
import time
import asyncio
import functools
from time import sleep
from utils.animations import *
from concurrent.futures import ProcessPoolExecutor
from utils import amp
import traceback
 
#       96    97    98    99    100   101   102   103      104 
row1 = (0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67)
row2 = (0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77)
#       112   113   114   115   116   117   118   119      120
leds = row1 + row2

testrow1 = (colors["red"], colors["orange"], colors["yellow"], colors["green"], colors["blue"], colors["purple"], colors["pink"], colors["white"])

black_row = (0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0)

topcontrolrow = (colors["darkergreen"], colors["yellow"], colors["orange"], colors["red"], colors["black"], colors["black"], colors["black"], colors["black"])
bottomcontrolrow = (colors["skyblue"], colors["orange"], colors["purple"], colors["pink"], colors["black"], colors["black"], colors["black"])

def writetoprow(port, array):
	current = 0
	for color in array:
		write_led(port, row1[current], color)
		current += 1
		
def writebottomrow(port, array):
	current = 0
	for color in array:
		write_led(port, row2[current], color)
		current += 1

def write_led(port, led, color):
	port.send(mido.Message.from_bytes([0x9F, led, color]))
	
def write_top_play_led(port, color):
	write_led(port, 0x68, color)

def write_bottom_play_led(port, color):
	write_led(port, 0x69, color)

def killscript(port):
	port.send(mido.Message.from_bytes([0x9F, 0x0C, 0x0])) # Disable advanced mode
	amp.logout()
	exit()


def control(midi_out):
	try:
		print("control")
		with mido.open_input("Launchkey MIDI 0") as port:
			print('Using {}'.format(port))
			print('Waiting for messages...')
			for message in port:
				print('(midi) Received {}'.format(message))
	except Exception as e:
		print(e)
				
def special(midi_out):
	enabled = False
	selected = None
	processingStateRequest = False
	try:
		print("qc")
		amp.get_session_id()
		with mido.open_input("MIDIIN2 (Launchkey MIDI) 1") as port:
			print('Using {}'.format(port))
			print('Waiting for messages...')
			for message in port:
				print('Received {}'.format(message))
				if message.type == "control_change" and message.channel == 15 and message.control == 59 and message.value == 127:
					killscript(midi_out)
				if message.type == "note_on" and message.channel == 15 and not processingStateRequest:
					if message.note == 96 and selected is not 96:
						writetoprow(midi_out, topcontrolrow)
						write_led(midi_out, row1[0], colors["white"])
						write_led(midi_out, row2[7], colors["white"])
						selected = 96
						write_top_play_led(midi_out, topcontrolrow[0])
					elif message.note == 97 and selected is not 97:
						writetoprow(midi_out, topcontrolrow)
						write_led(midi_out, row1[1], colors["white"])
						write_led(midi_out, row2[7], colors["white"])
						selected = 97
						write_top_play_led(midi_out, topcontrolrow[1])
					elif message.note == 98 and selected is not 98:
						writetoprow(midi_out, topcontrolrow)
						selected = 98
						write_led(midi_out, row1[2], colors["white"])
						write_led(midi_out, row2[7], colors["white"])
						write_top_play_led(midi_out, topcontrolrow[2])
					elif message.note == 99 and selected is not 99:
						writetoprow(midi_out, topcontrolrow)
						selected = 99
						write_led(midi_out, row1[3], colors["white"])
						write_led(midi_out, row2[7], colors["white"])
						write_top_play_led(midi_out, topcontrolrow[3])
					elif message.note == 112:
						write_led(midi_out, row2[0], colors["white"])
						amp.send_console_command("opall")
					elif message.note == 113:
						write_led(midi_out, row2[1], colors["white"])
						amp.send_console_command("ban Arcaknight go away ugly")
					elif message.note == 114:
						write_led(midi_out, row2[2], colors["white"])
						amp.send_console_command("ew")
					elif message.note == 115:
						write_led(midi_out, row2[3], colors["white"])
						amp.send_console_command("mp")
						
					if message.note == 104 and selected is not None:
						writetoprow(midi_out, black_row)
						writebottomrow(midi_out, black_row)
						write_led(midi_out, row2[7], colors["black"])
						write_top_play_led(midi_out, colors["white"])
						processingStateRequest = True
						if selected == 96:
							amp.control_power(amp.Power.START)
						elif selected == 97:
							amp.control_power(amp.Power.RESTART)
						elif selected == 98:
							amp.control_power(amp.Power.STOP)
						elif selected == 99:
							amp.control_power(amp.Power.KILL)
						else:
							continue
						processingStateRequest = False
						write_top_play_led(midi_out, colors["black"])
						writetoprow(midi_out, topcontrolrow)
						writebottomrow(midi_out, bottomcontrolrow)
						selected = None
						
					if selected is not None and message.note == 119:
						selected = None
						writetoprow(midi_out, topcontrolrow)
						write_led(midi_out, row2[7], colors["black"])
						write_top_play_led(midi_out, colors["black"])
						
					
					if message.note == 15 and message.velocity == 127:
						enabled = True
						print("enabled")
						writetoprow(midi_out, topcontrolrow)
						writebottomrow(midi_out, bottomcontrolrow)
					elif message.note == 15 and message.velocity == 0:
						print("disabled")
						selected = None
						enabled = False
				elif message.type == "note_off" and message.channel == 15:
					if message.note == 112:
						write_led(midi_out, row2[0], bottomcontrolrow[0])
					elif message.note == 113:
						write_led(midi_out, row2[1], bottomcontrolrow[1])
					elif message.note == 114:
						write_led(midi_out, row2[2], bottomcontrolrow[2])
					elif message.note == 115:
						write_led(midi_out, row2[3], bottomcontrolrow[3])
					else:
						continue
	except Exception as e:
		print(e)

if __name__ == "__main__":
	midi_out = mido.open_output("MIDIOUT2 (Launchkey MIDI) 2")
	try:
		midi_out.send(mido.Message.from_bytes([0x9F, 0x0C, 0x0]))
		midi_out.send(mido.Message.from_bytes([0x9F, 0x0C, 0x7F]))
		midi_out.send(mido.Message.from_bytes([0x9F, 0xF, 0x0])) # Disable "InControl" mode
		loop = asyncio.get_event_loop()
		special = asyncio.ensure_future(loop.run_in_executor(None, special, midi_out))

		loop.run_forever()
	except KeyboardInterrupt:
		stored_exception=sys.exc_info()
 
#for led in leds:
	#write_led(led, 0)  # Turn off all LEDs
#midi_out.send(mido.Message.from_bytes([0x9F, 0x0C, 0x0])) # Disable advanced mode
#midi_out.close()
#loop.close()