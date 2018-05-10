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
        hpiplib.log_message(program_name,'%s: START'%(method_name))
        method_to_call(*args)
        hpiplib.log_message(program_name,'%s: DONE'%(method_name))
    except AttributeError :
        hpiplib.error_message(program_name,"Unrecognized method '%s'"%(method_name))
        sys.exit(1)
except IndexError :
    hpiplib.error_message(program_name,'Usage: python hpipline.py <method> [args ...]')
    sys.exit(1)
