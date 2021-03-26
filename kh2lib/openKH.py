import os, subprocess

class openKH:
    def __init__(self, workdir):
        self.workdir = workdir
    def _check_binary(self, binary):
        if not os.path.isfile(os.path.join(self.workdir, binary)):
            raise Exception("{} not found".format(binary))
    def _run_binary(self, binary, args=[], inp='', debug=True):
        self._check_binary(binary)
        if debug:
            print(args)
            import sys; sys.stdout.flush()
        proc = subprocess.Popen([binary] + args, cwd=self.workdir, shell=True)
        output = proc.communicate(inp)
        if debug:
            print(output)
        return output[0]
    def bar_list(self, bar):
        # given a bar file, list the contents
        print(self._run_binary('OpenKh.Command.Bar.exe', args=['list', bar]).decode('utf-8'))
    def bar_extract(self, bar, outdir):
        # extract bar file to a directory (directory must exist prior to running this)
        self._run_binary('OpenKh.Command.Bar.exe', args=['unpack', '-o', outdir, bar])
    def bar_build(self, projectfn, outputfn):
        self._run_binary('OpenKh.Command.Bar.exe', args=['pack', '-o', outputfn, projectfn])
    def spawnscript_extract(self, pth, outfn):
        self._run_binary('OpenKh.Command.SpawnScript.exe', args=['decompile', '-o', outfn, pth], debug=True)
    def spawnscript_compile(self, pth, outfn):
        self._run_binary('OpenKh.Command.SpawnScript.exe', args=['compile', '-o', outfn, pth])
    def spawnpoint_extract(self, pth, outfn):
        self._run_binary('OpenKh.Command.SpawnScript.exe', args=['unpoint', '-o', outfn, pth])
    def spawnpoint_build(self, pth, outfn):
        self._run_binary('OpenKh.Command.SpawnScript.exe', args=['repoint', '-o', outfn, pth])
                