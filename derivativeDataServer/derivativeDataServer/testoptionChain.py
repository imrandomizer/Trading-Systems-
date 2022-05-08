from optionChain import *

import sys
import pprint

import code, traceback, signal

def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging."""
    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    #i = code.InteractiveConsole(d)
    message  = "Signal received : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    print(message)

def listen():
    signal.signal(signal.SIGUSR1, debug)  # Register handler




#d = completeOptionChainStructure("ZEEL")
#d.downloadNewSource()
print(sys.argv[1])
d = optionChainAnalysis(sys.argv[1])

ref = False

try:
    if("True" in sys.argv[2]):
        ref = True
except:
    pass

d.analyzeOptionChain(refresh=ref)
pprint.pprint(d.analysis)
