from __future__ import print_function
import time, sys

def time_string () :
    return time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime ())

def error_message (program_name, message) :
    full_message = "%s %s: ERROR: %s"%(time_string (), program_name, message)
    print (full_message, file=sys.stderr)

def log_message (program_name, message) :
    full_message = "%s %s: INFO: %s"%(time_string (), program_name, message)
    print (full_message)

def warn_message (program_name, message) :
    full_message = "%s %s: WARNING: %s"%(time_string (), program_name, message)
    print (full_message)

def prom_id(prom_name) :
    return prom_name[:1], prom_name[1:]
