import os, subprocess, shutil

class kh2fmtoolkit:
    def __init__(self, workdir='.'):
        self.workdir = workdir
        self.author = 'kh2lib'
        self.version = '1'
    def _check_binary(self):
        if not os.path.isfile(os.path.join(self.workdir, 'KH2FM_Toolkit.exe')):
            raise Exception("KH2FM_Toolkit.exe not found")
    def _run_binary(self, args=[], inp='', debug=True):
        self._check_binary()
        proc = subprocess.Popen(["KH2FM_Toolkit.exe"] + args, cwd=self.workdir, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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
    def patch_game(self, patches, fn, movefile=False, debug=False):
        self._check_binary()
        print("patching the game")
        self._run_binary(patches, debug=debug)
        if movefile:
            print("moving iso")
            # I don't see an way to name the output iso, so use shutil to move it 
            shutil.move(os.path.join(self.workdir, 'KH2FM.NEW.ISO'), fn)
        print("all done")
    def create_patch(self, files, fn):
        self._check_binary()
        inp = b'\n'
        for f in files:
            inp += '{}\n\nY\n\nN\n'.format(f).encode('utf-8')
        inp += b'\n'
        args = ['-patchmaker', '-output', fn, '-author', self.author, '-version', self.version, '-skipchangelog', '-skipcredits']
        self._run_binary(args, inp=inp)
        print("patch created")
        return fn