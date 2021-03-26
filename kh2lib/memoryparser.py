from .utils import toHex
import os, time

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
    def locate_file(self, fn, starting_substr_len=None, timeout=5, single_result=False):
        self._check_for_dump()
        finddata = open(fn, "rb").read()
        if not starting_substr_len:
            starting_substr_len = len(finddata) // 2
        searchstr = bytearray(finddata[:starting_substr_len])
        oldmatches = None
        # I need to only except the valueerror here for missing the substr
        start_time = time.time()
        for b in finddata[starting_substr_len:]:
            searchstr.append(b)
            try:
                if time.time() - start_time > timeout:
                    raise Exception("Timed out looking for match")
                matches = self.search_substr(searchstr)
                if matches == []:
                    raise Exception("Could not find match")
                if len(matches) == 1:
                    return matches[0]
                oldmatches = matches
            except:
                if oldmatches:
                    print("Multiple potential matches")
                    if single_result:
                        return oldmatches[0]
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
    def set_file_bytes(self, fn, proportions=[1], byte_to_set=0x0):
        f = bytearray(open(fn, "rb").read())

        replace = True
        assert sum(proportions) == 1
        prop_lengths = [int(len(f) * i) for i in proportions]
        prop_len = sum(prop_lengths)
        f_len = len(f)
        if not prop_len == f_len:
            if prop_len > f_len:
                prop_lengths[-1] -= prop_len-f_len
            else:
                prop_lengths[-1] += f_len-prop_len
        bi = 0
        for prop in prop_lengths:
            for i in range(prop):
                if replace:
                    f[bi] = byte_to_set
                else:
                    pass
                bi += 1
            replace = not replace
        open(fn, "wb").write(f)
    def readable_data(self, fn, record_spec, header_length=0x0, footer_length=0x0,hide_indices=[],swapendian=False, showinhex=True, aspandas=False, displayHeader=False,displayFooter=False, recordstoshow=None, showUniqueIndex=False, filter_to_nonzero_indices=[], returnOutput=False):
        def _readable(ba):
            return " ".join([hex(i)[2:].zfill(2).upper() for i in ba])
        if aspandas:
            import pandas as pd

        f = bytearray(open(fn, "rb").read())

        header = f[:header_length]

        records = f[header_length:len(f)-footer_length]
        rec_len = sum(record_spec)
        num_records = len(records) // sum(record_spec)

        footer = f[len(f)-footer_length:]

        if displayHeader:
            print("HEADER")
            print(_readable(header))
            print("\n")
        if displayFooter:
            print("FOOTER")
            print(_readable(footer))
            print("\n")
        print("\n\n\n")

        df = ''
        recs = []
        for x in range(num_records):
            if recordstoshow and x > recordstoshow:
                continue
            r = []
            prev = 0
            for i in record_spec:
                r.append([records[rec_len*x+im+prev] for im in range(i)])
                prev += i
            if swapendian:
                for v in range(len(r)):
                    var = r[v]
                    if len(var) > 1:
                        r[v] = var[::-1]
            # Convert to more readable form
            for v in range(len(r)):
                var = r[v]
                var = _readable(var).replace(" ", "")
                if not showinhex:
                    var = int(var, 16)
                if v in hide_indices:
                    var = "__"
                r[v] = var
            recs.append(r)

        if filter_to_nonzero_indices:
            for i in filter_to_nonzero_indices:
                if not showinhex:
                    recs = list(filter(lambda r: r[i] != 0, recs))
                else:
                    recs = list(filter(lambda r: r[i] != '0'.zfill(len(r[i])), recs))

        if showUniqueIndex:
            s = []
            for r in recs:
                s.append(r[showUniqueIndex])
            s = list(set(s))
        elif not aspandas:
            for rec in recs:
                if not showinhex:
                    print(rec)
                else:
                    x = " ".join(rec)
                    if returnOutput:
                        df += x + '\n'
                    else:
                        print(x)
        else:
            df = pd.DataFrame(recs)
        return df


    def shuffle_data(self, fn, record_spec=None, header_length=0x0, footer_length=0x0, indices_to_shuffle=None):
        f = bytearray(open(fn, "rb").read())
        import random
        header = f[:header_length]

        records = f[header_length:len(f)-footer_length]
        rec_len = sum(record_spec)
        num_records = len(records) // sum(record_spec)

        footer = f[len(f)-footer_length:]
        recs = []
        for x in range(num_records):
            r = []
            prev = 0
            for i in record_spec:
                r.append([records[rec_len*x+im+prev] for im in range(i)])
                prev += i
            recs.append(r)
            
        # Default shuffle everything
        if not indices_to_shuffle:
            indices_to_shuffle = list(range(len(recs[0])))


        lists_of_indices = [[n[i] for n in recs] for i in range(len(recs[0]))]

        for i in range(len(lists_of_indices)):
            if i in indices_to_shuffle:
                random.shuffle(lists_of_indices[i])

        recs = [[] for r in recs]
        for indi in lists_of_indices:
            for r in range(len(indi)):
                for bt in indi[r]:
                    recs[r].append(bt)
        recs_new = []
        for rec in recs:
            for i in rec:
                recs_new.append(i)

        new_file = header + bytearray(recs_new) + footer

        open(fn, "wb").write(new_file)        