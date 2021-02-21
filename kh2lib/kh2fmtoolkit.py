import os, subprocess, shutil

class kh2fmtoolkit:
    def __init__(self, workdir='.', binary_name='KH2FM_Toolkit.exe'):
        self.workdir = workdir
        self.author = 'kh2lib'
        self.binary_name = binary_name
        self.version = '1'
    def _check_binary(self):
        if not os.path.isfile(os.path.join(self.workdir, self.binary_name)):
            raise Exception("{} not found".format(self.binary_name))
    def _run_binary(self, args=[], inp='', debug=True):
        self._check_binary()
        proc = subprocess.Popen([self.binary_name] + args, cwd=self.workdir, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        output = proc.communicate(input=inp)
        # if inp == '':
        #     # Using check_output to perform a patch will crash with calledprocesserror at the end
        #     # although the iso does get successfully patched
        #     subprocess.call(["KH2FM_Toolkit.exe"] + args, cwd=self.workdir)
        # else:
        #     output = subprocess.check_output(["KH2FM_Toolkit.exe"] + args, input=inp, cwd=self.workdir)
        if debug:
            print(output)
    def extract_game(self, outdir):
        self._check_binary()
        print("extracting the game to {}".format(outdir))
        self._run_binary(['-extractor'])
        shutil.move(os.path.join(self.workdir,'export'), outdir)
    def patch_game(self, patches, fn, movefile=False, debug=False, game='kh2'):
        self._check_binary()
        print("patching the game")
        args = patches
        inp = ''
        if game == 'kh1':
            args = ['-patch'] + patches
            inp = '\n\n'.encode('utf-8')
            args = [i.replace(".kh2patch",".kh2patch.kh1patch") for i in args]
        self._run_binary(args,inp, debug=debug)
        if movefile:
            print("moving iso")
            # I don't see an way to name the output iso, so use shutil to move it 
            shutil.move(os.path.join(self.workdir, 'KH2FM.NEW.ISO'), fn)
        print("all done")
    def create_patch(self, files, fn, game="kh2"):
        self._check_binary()
        if game == "kh2":
            inp = b'\n'
        elif game == "kh1":
            inp = b'\n\n'
            files = [f.replace("/KINGDOM/","") for f in files]
        else:
            raise Exception("Unknown game")
        for f in files:
            if game == "kh2":
                inp += '{}\n\nY\n\nN\n'.format(f).encode('utf-8')
            elif game == "kh1":
                inp += '{}\n\nY\n\nN\n'.format(f).encode('utf-8')
        inp += b'\n'
        args = ['-patchmaker', '-output', fn, '-author', self.author, '-version', self.version, '-skipchangelog', '-skipcredits']
        self._run_binary(args, inp=inp)
        print("patch created")
        return fn