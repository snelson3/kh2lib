import os, subprocess

class openKH:
    def __init__(self, workdir):
        self.workdir = workdir
    def _check_binary(self, binary):
        if not os.path.isfile(os.path.join(self.workdir, binary)):
            raise Exception("{} not found".format(binary))
    def _run_binary(self, binary, args=[], input='', debug=False):
        self._check_binary(binary)
        origDir = os.getcwd()
        os.chdir(self.workdir)
        print(binary,args)
        output = subprocess.check_output([binary] + args, input=input)
        if debug:
            print(output)
        os.chdir(origDir)
        return output
    def bar_list(self, bar):
        # given a bar file, list the contents
        print(self._run_binary('OpenKh.Command.Bar.exe', args=['list', bar]).decode('utf-8'))
    def bar_extract(self, bar, outdir):
        # extract bar file to a directory (directory must exist prior to running this)
        self._run_binary('OpenKh.Command.Bar.exe', args=['unpack', '-o', outdir, bar])
    def bar_build(self, projectfn, outputfn):
        self._run_binary('OpenKh.Command.Bar.exe', args=['pack', '-o', outputfn, projectfn])