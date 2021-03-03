import os

BOARD_DELIMITER = bytearray(b'\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

class DDD:
    def __init__(self):
        pass

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