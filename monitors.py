#!/usr/bin/python3

import sys
import subprocess
import re

MAX_DISPLAYS = 3
CMD = 'xrandr'

class Output:
    def __init__(self, id='INVALID', connected=False):
        self.connected = connected
        self.id = id
        self.best_mode = '0x0'
        self.best_rate = '0'

def get_outputs():
    outputs = []
    lines = query().split('\n')
    rex = re.compile(r'\s*([1234567890x]*)\s*([1234567890\.]*)')
    for i in range(0, len(lines)):
        line = lines[i]
        splitted = line.split()
        if(len(splitted) == 0):
            continue
        id = line.split()[0]
        output = Output(id)

        if 'disconnected' in line:
            output.connected = False
            outputs.append(output)
        elif 'connected' in line:
            output.connected = True
            next_line = lines[i + 1]
            mode, rate = rex.search(next_line).groups()
            output.best_mode = mode
            output.best_rate = rate
            outputs.append(output)
    return outputs

def query_mock():
    return """Screen 0: minimum 8 x 8, current 1366 x 768, maximum 32767 x 32767
LVDS1 connected primary 1366x768+0+0 (normal left inverted right x axis y axis) 344mm x 194mm
   1366x768      60.00*+
   1360x768      59.80    59.96  
   1280x720      60.00  
   1024x768      60.00  
   1024x576      60.00  
   960x540       60.00  
   800x600       60.32    56.25  
   864x486       60.00  
   640x480       59.94  
   720x405       60.00  
   680x384       60.00  
   640x360       60.00  
DP1 disconnected (normal left inverted right x axis y axis)
HDMI1 disconnected (normal left inverted right x axis y axis)
VGA1 disconnected (normal left inverted right x axis y axis)
VIRTUAL1 disconnected (normal left inverted right x axis y axis)"""

def test():
    global query
    query = query_mock
    outputs = get_outputs()

    assert(len(outputs) == 5)
    out = outputs[0]
    assert(out.id == 'LVDS1')
    assert(out.connected == True)
    assert(out.best_mode == '1366x768')
    assert(out.best_rate == '60.00')
    out = outputs[1]
    assert(out.id == 'DP1')
    assert(out.connected == False)
    assert(out.best_mode == '0x0')
    assert(out.best_rate == '0')
    out = outputs[2]
    assert(out.id == 'HDMI1')
    assert(out.connected == False)
    assert(out.best_mode == '0x0')
    assert(out.best_rate == '0')
    out = outputs[3]
    assert(out.id == 'VGA1')
    assert(out.connected == False)
    assert(out.best_mode == '0x0')
    assert(out.best_rate == '0')
    out = outputs[4]
    assert(out.id == 'VIRTUAL1')
    assert(out.connected == False)
    assert(out.best_mode == '0x0')
    assert(out.best_rate == '0')

def query():
    proc = subprocess.Popen('xrandr', stdout=subprocess.PIPE)
    return proc.stdout.read().decode()

def output_off(output):
    call(['--output', output.id, '--off'])

def output_on(output, primary, extra = []):
    args = ['--output', output.id, '--auto']
    if output.best_mode != '0x0':
        args.extend(['--mode', output.best_mode])
    if output.best_rate != '0':
        args.extend(['--rate', output.best_rate])
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

    if '--test' in sys.argv:
        test()
        sys.exit(0)
    if '--dry' in sys.argv:
        CMD = 'echo'

    outputs = get_outputs()
    connected = list(filter(lambda x: x.connected, outputs))
    laptop = None
    hdmi = None
    vga = None
    
    for out in connected:
        if 'LVDS' in out.id:
            laptop = out
        if 'HDMI' in out.id:
            hdmi = out
        if 'VGA' in out.id:
            vga = out

    for out in outputs:
        if not out.connected:
            output_off(out)
    
    if len(connected) == 1:
        output_on(outputs[0], True)
    else:
        if hdmi and vga:
            output_off(laptop)
            output_on(hdmi, True)
            output_on(vga, False, ['--left-of', hdmi.id])
        elif laptop and vga:
            output_on(laptop, True)    
            output_on(vga, False, ['--left-of', laptop.id])
        elif laptop and hdmi:
            output_on(laptop, False)    
            output_on(hdmi, True, ['--above', laptop.id])

    call(cmd = 'set-wallpaper')

if __name__ == '__main__':
    main()

