from .kh2fmtoolkit import kh2fmtoolkit
from .pnachmaker import pnachmaker
from .memoryparser import memoryparser
from .utils import getarg
from .openKH import openKH
import sys, subprocess, os, shutil, json

class kh2lib:
    def __init__(self, gitpath=None, patchEngine=kh2fmtoolkit, cheatsfn=None):
        self.__version__ = 0.01
        self.gitpath = getarg("gitpath") or gitpath
        self.cheatengine = pnachmaker(getarg("outpath") or cheatsfn)
        self.patchengine = patchEngine(workdir=getarg("patchenginedir"))
        self.parsingengine = memoryparser()
        self.editengine = openKH(workdir=getarg("editorengine"))
        self.worlds = json.load(open(os.path.join(os.path.dirname(__file__), "data", "worlds.json")))
        self.objects = json.load(open(os.path.join(os.path.dirname(__file__), "data", "objlist.json")))

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

    def create_patch(self, files=[], filesdir=None, fromgit=False, outfn='patch.kh2patch', gitprefix='export/'):
        if filesdir:
            if os.path.isdir(filesdir):
                files = files + [os.path.join(filesdir,f) for f in os.listdir(filesdir)]
        if fromgit:
            gitfiles = [gitprefix + f for f in self.get_git_modifications()]
            parsedgitfiles = [f[11:] for f in gitfiles]
            # This might not work for all OSes
            for i in range(len(gitfiles)):
                # I need to throw everything in a dist folder, so I can make sure it's clean in the case of an error during patching
                directory = os.path.dirname(os.path.join(self.patchengine.workdir,parsedgitfiles[i]))
                if not os.path.exists(directory):
                    os.makedirs(directory)
                shutil.copy(os.path.join(self.patchengine.workdir,gitfiles[i]), os.path.join(self.patchengine.workdir, parsedgitfiles[i]))
            files = files + parsedgitfiles
        self.patchengine.create_patch(files, outfn)
        if fromgit:
            for f in parsedgitfiles:
                os.remove(os.path.join(self.patchengine.workdir, f))
        return outfn

    def patch_game(self, patches=[], fromgit=False, fn='KH2-PATCHED.iso'):
        # Send the list of patches (or generate from git) to the patchengine
        # Paths must be relative to the patchengine binary
        if fromgit:
            patches += [self.create_patch(fromgit=True)]
        self.patchengine.patch_game(patches, fn)

    def get_object(self, ucm=None, mdlx=None, name=None):
        # Return the object matching or a list if there are multiple
        if len(list(filter(lambda k: k != None, list(set([ucm, mdlx, name]))))) != 1:
            raise Exception("Must pass in exactly 1 of ucm, mdlx, or name!")
        matches = []
        if ucm:
            match = str(ucm)
            for obj in self.objects:
                if match.zfill(4) == str(obj["ucm"]).zfill(4):
                    matches.append(obj)
        if mdlx:
            match = str(mdlx)
            for obj in self.objects:
                if match.lower() == obj["mdlx"].lower():
                    matches.append(obj)
        if name:
            match = name.lower().replace(' ', '')
            for obj in self.objects:
                if match in obj["name"].lower().replace(' ', ''):
                    matches.append(obj)
        if len(matches) == 0:
            raise Exception("Object not found")
        elif len(matches) == 1:
            return matches[0]
        return matches
                
        

    
    def get_world(self, wid=None, abv=None, name=None):
        if len(list(filter(lambda k: k != None, list(set([wid, abv, name]))))) != 1:
            raise Exception("Must pass in exactly 1 of wid, abv, or name!")
        if wid:
            for world in self.worlds:
                match = str(wid)
                if match == str(world["wid"]):
                    return world
            raise Exception("world {} not found".format(wid))
        if abv:
            for world in self.worlds:
                match = abv.lower()
                if match == world["abv"].lower():
                    return world
            raise Exception("world {} not found".format(abv))
        if name:
            match = name.lower().replace(' ', '')
            for world in self.worlds:
                if match == world["name"].lower().replace(' ', ''):
                    return world
            raise Exception("world {} not found".format(name))