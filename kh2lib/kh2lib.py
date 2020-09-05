from .kh2fmtoolkit import kh2fmtoolkit
from .pnachmaker import pnachmaker
from .utils import getarg
import sys, subprocess, os

class kh2lib:
    def __init__(self, gitpath=None, patchEngine=kh2fmtoolkit, cheatsfn=None):
        self.__version__ = 0.01
        self.gitpath = getarg("gitpath") or gitpath
        self.cheatengine = pnachmaker(getarg("outpath") or cheatsfn)
        self.patchengine = patchEngine(workdir=getarg("patchenginedir"))

    def reset_git(self, files_to_remove=[], branch='master'):
        if not self.gitpath:
            raise Exception("No 'gitpath' assigned")
        if not os.path.isdir(os.path.join(self.gitpath, ".git")):
            raise Exception("'gitpath' is not a valid directory")
        output = subprocess.check_output(['git', 'reset', '--hard', branch], cwd=self.gitpath)
        print(output)
        for fn in files_to_remove:
            if os.path.exists(fn):
                os.remove(fn)
        print("Git repository has been reset")

    def get_git_modifications(self):
        output = subprocess.check_output(['git', 'status', '--porcelain'], cwd=self.gitpath)
        print(output)
        # This will ignore any paths with a space in their name, but I don't think there are any in the kh2 iso
        files = []
        for f in output.decode('utf-8').split("\n"):
            if len(f) > 0:
                if f[1] == "M" and len(f.split(' ')) == 3:
                    fn = f.split(' ')[2]
                    # git gives paths that won't work when combined with windows paths
                    # but the patch engine is fine with that, so probably fine
                    # fn = fn.split("/")
                    # fn = os.path.join(*fn)
                    files.append(fn)
                else:
                    print("Warning: Skipping file listed in git status:\n\t{}".format(f))
        return files


    def create_patch(self, files=[], filesdir=None, fromgit=False, outfn='patch.kh2patch'):
        # Gather a list of files
        # create a default filename based on the names of all the files being patched
        # send the files to the patch engine
        # filenames must be paths relative to the patchengine binary
        if filesdir:
            if os.path.isdir(filesdir):
                files = files + [os.path.join(filesdir,f) for f in os.listdir(filesdir)]
        if fromgit:
            files = files + ["export/" + f for f in self.get_git_modifications()]
        self.patchengine.create_patch(files, outfn)

    def patch_game(self, patches=[], fromgit=False, fn='KH2-PATCHED.iso'):
        # Send the list of patches (or generate from git) to the patchengine
        # Paths must be relative to the patchengine binary
        if fromgit:
            patches += self.create_patch(fromgit=True)
        self.patchengine.patch_game(patches, fn)

