import os, subprocess, shutil
from .utils import getarg

BOARD_DELIMITER = bytearray(b'\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

class DDD:
    def __init__(self, mom):
        self.mom = mom

    def extract_lboard(self, fn, outdir):
        print("EXTRACTING")
        data = bytearray(open(fn,"rb").read())
        # Header len 240
        if not [i for i in data[:4]] == [0x44,0x33,0x22,0x11]:
            raise Exception("File does not have header for lboard.bin")

        header_len = 240

        header = data[:header_len]
        boards = data[header_len:]


        open(os.path.join(outdir, "header.bin"), "wb").write(header)
        
        board = None
        bn = 0

        for i in range(0, len(boards),16):  
            line = boards[i:i+16]

            if line == BOARD_DELIMITER:
                if board:
                    with open(os.path.join(outdir, "sboard{}.bin".format(str(bn).zfill(2))), "wb") as f:
                        f.write(board)
                board = bytearray()
                bn += 1
            else:
                board += line
        with open(os.path.join(outdir, "sboard{}-r.bin".format(bn)), "wb") as f:
            f.write(board)

    def compile_lboard(self, indir, outfn):
        print("COMPILING")
        # Important it's alphabetical order how it should be in the file
        data = bytearray()
        for fn in os.listdir(indir):
            infn = os.path.join(indir, fn)
            fdata = bytearray(open(infn,"rb").read())
            data += fdata
            data += BOARD_DELIMITER
        data = data[:-len(BOARD_DELIMITER)]
        open(outfn, "wb").write(data)

    def patch_game(self, mods):
        #reser git needs to restore the modified rbins
        modded_rbins = []
        offsets = {}
        for mod in mods:
            fn = os.path.join(self.mom.gamedir, mod)
            rbin = mod.split("/")[0]
            rbinfn = os.path.join(self.mom.gamedir, rbin+".rbin")
            tempfn = fn+".temp"
            shutil.copy(fn, tempfn)
            subprocess.check_call(["git", "restore", mod], cwd=self.mom.gamedir)
            try:
                self.mom.parsingengine.load_memdump(rbinfn)
                offsets[fn] = self.mom.parsingengine.locate_file(fn)
            except:
                print("Skipping {}".format(mod))
        for mod in mods:
            print(mod)
            fn = os.path.join(self.mom.gamedir, mod)
            rbin = mod.split("/")[0]
            rbinfn = os.path.join(self.mom.gamedir, rbin+".rbin")
            tempfn = fn+".temp"
            try:
                location = offsets[fn]
                if type(location) == list:
                    location = location[0]
                offset = int(location, 16)
            except:
                print("couldn't replace file")
                continue

            ba = bytearray(open(rbinfn, "rb").read())
            fileb = bytearray(open(tempfn, "rb").read())

            ba_m = ba[0:offset]+fileb+ba[offset+len(fileb):]

            open(rbinfn, "wb").write(ba_m)

            modded_rbins.append(rbinfn)
            shutil.copy(tempfn, fn)
            os.remove(tempfn)
        for rbin in set(modded_rbins):
            print(rbin, os.path.join(getarg("ddd_mod_path"), rbin))
            shutil.copy(rbin, os.path.join(getarg("ddd_mod_path"), os.path.basename(rbin)))
        
