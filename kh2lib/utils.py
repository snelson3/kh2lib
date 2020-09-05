import sys, os

def toHex(v, n=2):
    return hex(v)[2:].zfill(n).upper()

def getarg(v):
    for a in sys.argv:
        if a.lower().startswith(v.lower()+"="):
            return a[len(v)+1:]
    for a in os.environ:
        if a.lower().startswith("USE_KH2_{}".format(v).lower()):
            return os.environ[a]
    return None