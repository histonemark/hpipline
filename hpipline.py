from __future__ import print_function
import sys, os
import hpiplib

program_name = 'hpipline'

try :
    method_name = sys.argv[1]
    args = sys.argv[2:]
    try :
        method_to_call = getattr(hpiplib,method_name)
        for f in args :
            if not os.path.exists(f) :
                hpiplib.error_message(program_name,
                                      "Input file '%s' does not exist"%(f))
                sys.exit(1)
        # if we are here, everything is fine and we can call the method
        method_to_call(*args)
    except AttributeError :
        print("Unrecognized method '%s'"%(method_name),file=sys.stderr)
        sys.exit(1)
except IndexError :
    print('Usage: python hpipline.py <method> [args ...]',file=sys.stderr)
    sys.exit(1)
