from .utils import toHex
import os

class memoryparser:
    def __init__(self):
        self.memdump = None
    def _check_for_dump(self):
        if not self.memdump:
            raise Exception("Must load memdump into parser")
    def load_memdump(self, fn):
        self.memdump = bytearray(open(fn, "rb").read())
        return self.memdump
    def search_substr(self, bytestr):
        self._check_for_dump()
        addresses = []
        subdata = bytearray(self.memdump)
        index = 0
        if not bytestr in subdata:
            return []
        while bytestr in subdata:
            a = subdata.index(bytestr)
            addresses.append(a+index)
            index = index + a + len(bytestr)
            subdata = subdata[a+len(bytestr):]
        return ["0x"+str(hex(ad))[2:].zfill(8) for ad in addresses]
    def locate_file(self, fn, starting_substr_len=None):
        self._check_for_dump()
        finddata = open(fn, "rb").read()
        if not starting_substr_len:
            starting_substr_len = len(finddata) // 2
        searchstr = bytearray(finddata[:starting_substr_len])
        oldmatches = None
        # I need to only except the valueerror here for missing the substr
        for b in finddata[starting_substr_len:]:
            searchstr.append(b)
            try:
                matches = self.search_substr(searchstr)
                if len(matches) == 1:
                    return matches[0]
                oldmatches = matches
            except:
                if oldmatches:
                    print("Multiple potential matches")
                    return oldmatches
                raise Exception("Could not find match")
        raise Exception("You should never see this")
    def generate_codes(self, starting_offset, base_file, mod_file):
        self._check_for_dump()
        base = bytearray(open(base_file, "rb").read())
        mod = bytearray(open(mod_file, "rb").read())
        if len(base) != len(mod):
            raise Exception("base and mod files are different lengths, cannot generate diff codes")
        codes = []
        for i in range(0, len(base), 4):
            def _getv(arr, i):
                if i >= len(arr):
                    return 0 # technically might not be 0 if editing the very end of a file, but fine for now
                return arr[i]
            base_word = [_getv(base,i), _getv(base,i+1), _getv(base,i+2), _getv(base,i+3)]
            mod_word = [_getv(mod,i), _getv(mod,i+1), _getv(mod,i+2), _getv(mod,i+3)]
            if base_word != mod_word:
                codes.append("{} {}".format(hex(int(i)+int(starting_offset))[2:].zfill(8), ''.join([hex(n)[2:].zfill(2) for n in mod_word][::-1])))
        return codes