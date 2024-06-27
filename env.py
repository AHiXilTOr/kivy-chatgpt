import sys

def set_variables(local):
    P = A = 'http://localhost' if local else None
    A = '' if not local else A
    return P, A

local = "local" in sys.argv
PROXY, API = set_variables(local)