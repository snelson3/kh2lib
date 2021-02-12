from .utils import toHex
import os

class pnachmaker:
    def __init__(self, cheatsfn=None):
        if not cheatsfn:
            cheatsfn = "F266B00B.pnach"
        self.outfn = cheatsfn
        self.pnach = []
    def apply_room_cond(self, codes, room, world):
        # Joker a list of codes to only be active in this room
        numcodes = toHex(len(codes))
        return ["E0{}{}{} 0032BAE0".format(numcodes, room, world)] + codes
    def apply_event_cond(self, codes, event):
        # Joker a list of codes to only be active in this room
        return ["E0{}00{} 0032BAE4".format(toHex(len(codes)+2), event),
        "E0{}00{} 0032BAE6".format(toHex(len(codes)+1), event),
        "E0{}00{} 0032BAE8".format(toHex(len(codes)), event)] + codes
    def apply_ram_code(self, codes, comment=False):
        if comment:
            self.pnach.append("// {}".format(comment))
        for line in codes:
            if len(line) == 0:
                continue
            line = line.strip().split()
            self.pnach.append("patch=1,EE,{},extended,{}".format(line[0].upper(),line[1].upper()))
    def write_pnach(self, debug=False):
        with open(self.outfn, "w") as f:
            for l in self.pnach:
                outstr = "{}\n".format(l)
                f.write(outstr)
                if debug:
                    print(outstr)

