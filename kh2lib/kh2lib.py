from .kh2fmtoolkit import kh2fmtoolkit
from .pnachmaker import pnachmaker
from .utils import getarg
from .openKH import openKH
import sys, subprocess, os, shutil

class kh2lib:
    def __init__(self, gitpath=None, patchEngine=kh2fmtoolkit, cheatsfn=None):
        self.__version__ = 0.01
        self.gitpath = getarg("gitpath") or gitpath
        self.cheatengine = pnachmaker(getarg("outpath") or cheatsfn)
        self.patchengine = patchEngine(workdir=getarg("patchenginedir"))
        self.editengine = openKH(workdir=getarg("editorengine"))

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
                    files.append(fn)
                else:
                    print("Warning: Skipping file listed in git status:\n\t{}".format(f))
        return files


    def create_patch(self, files=[], filesdir=None, fromgit=False, outfn='patch.kh2patch'):
        if filesdir:
            if os.path.isdir(filesdir):
                files = files + [os.path.join(filesdir,f) for f in os.listdir(filesdir)]
        if fromgit:
            #TODO This path should be generated based on the git URL, instaed of hardoded to export
            #or not
            origDir = os.getcwd()
            os.chdir(self.patchengine.workdir)
            gitfiles = ["export/" + f for f in self.get_git_modifications()]
            parsedgitfiles = [f[11:] for f in gitfiles]
            # This might not work for all OSes
            for i in range(len(gitfiles)):
                # My brain is broken, I need to just ensure the directory is there, but for now imma cheat and manually make the obj directory
                # everything I'm testing tonight will work like this
                shutil.copy(gitfiles[i], parsedgitfiles[i])
            files = files + parsedgitfiles
            os.chdir(origDir)
        self.patchengine.create_patch(files, outfn)
        if fromgit:
            os.chdir(self.patchengine.workdir)
            # this is weird because it's defined in the other if loop, but it will always exist here
            for f in parsedgitfiles:
                os.remove(f)
            os.chdir(origDir)
        return outfn

    def patch_game(self, patches=[], fromgit=False, fn='KH2-PATCHED.iso'):
        # Send the list of patches (or generate from git) to the patchengine
        # Paths must be relative to the patchengine binary
        if fromgit:
            patches += [self.create_patch(fromgit=True)]
        self.patchengine.patch_game(patches, fn)

