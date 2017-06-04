#!/usr/bin/python3

import sys
import subprocess

MAX_DISPLAYS = 3
CMD = 'xrandr'

def get_outputs(inactive=False):
	outputs = []

	connected = ' connected'
	if inactive:
		connected = ' disconnected'

	for line in query().split('\n'):
		if connected in line:
			idx = line.index(connected)
			output = line[:idx]
			outputs.append(output)

	return outputs

def query():
	proc = subprocess.Popen('xrandr', stdout=subprocess.PIPE)
	return proc.stdout.read().decode()

def output_off(output):
	call(['--output', output, '--off'])

def output_on(output, primary, extra = []):
	args = ['--output', output, '--auto']
	if primary:
		args.append('--primary')
	call(args + extra)

def call(args = [], cmd = None):
	if cmd is None:
		cmd = CMD
	try:
		subprocess.check_call([ cmd ] + args)
	except subprocess.CalledProcessError as ex:
		print('Failed to call ' + str([cmd] + args) + ', error: ' + str(ex))

def main():
	global CMD
	if '--dry' in sys.argv:
		CMD = 'echo'

	outputs = get_outputs()
	inactive_outputs = get_outputs(inactive = True)
	laptop = None
	hdmi = None
	vga = None
	
	for out in outputs:
		if 'LVDS' in out:
			laptop = out
		if 'HDMI' in out:
			hdmi = out
		if 'VGA' in out:
			vga = out

	for out in (inactive_outputs + outputs):
		output_off(out)
	
	fhd = [ '--mode', '1920x1080', '--rate', '60' ]
	hd  =  [ '--mode', '1366x768', '--rate', '60' ]
	
	if len(outputs) == 1:
		output_on(outputs[0], True)
	else:
		if hdmi and vga:
			output_on(hdmi, True, fhd)
			output_on(vga, False, ['--left-of', hdmi] + fhd)
		elif laptop and vga:
			output_on(laptop, False, hd)	
			output_on(vga, True, ['--above', laptop] + fhd)
		elif laptop and hdmi:
			output_on(laptop, False, hd)	
			output_on(hdmi, True, ['--above', laptop] + fhd)	
	call(cmd = 'set-wallpaper')

if __name__ == '__main__':
	main()

