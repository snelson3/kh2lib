import os, subprocess, shutil

class kh2fmtoolkit:
    def __init__(self, workdir='.'):
        self.workdir = workdir
        self.author = 'kh2lib'
        self.version = '1'
    def _check_binary(self):
        if not os.path.isfile(os.path.join(self.workdir, 'KH2FM_Toolkit.exe')):
            raise Exception("KH2FM_Toolkit.exe not found")
    def _run_binary(self, args=[], input='', debug=False):
        self._check_binary()
        origDir = os.getcwd()
        print(args)
        os.chdir(self.workdir)
        try:
            output = subprocess.check_output(["KH2FM_Toolkit.exe"] + args, input=input)
            if debug:
                print(output)
        except subprocess.CalledProcessError as exc:
            # I'm getting this error after patching the game through python
            # Unhandled Exception: System.IO.IOException: The handle is invalid.
            # But the ISO seems to have gotten created properly, so ignoring it for now
            print("KH2FM_Toolkit.exe exited with error, you might be able to ignore this")
        os.chdir(origDir)
    def extract_game(self, outdir):
        self._check_binary()
        print("extracting the game to {}".format(outdir))
        self._run_binary(['-extractor'])
        shutil.move(os.path.join(self.workdir,'export'), outdir)
    def patch_game(self, patches, fn):
        self._check_binary()
        print("patching the game")
        #self._run_binary(patches, debug=False)
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
        self._run_binary(args, input=inp)
        print("patch created")