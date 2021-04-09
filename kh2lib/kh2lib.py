from .kh2fmtoolkit import kh2fmtoolkit
from .pnachmaker import pnachmaker
from .memoryparser import memoryparser
from .utils import getarg
from .ddd import DDD
from .openKH import openKH
import sys, subprocess, os, shutil, json, random

CRITITEMS = [  "Reaction Boost","Air Combo Boost","Auto Healing","Magic Lock-On","Jackpot","Jackpot","No Experience"]
class kh2lib:
    def __init__(self, gitpath=None, gamedir=None, patchEngine=kh2fmtoolkit, cheatsfn=None, game="kh2"):
        if gitpath:
            gamedir = gitpath
        self.game = game
        self.__version__ = 0.01
        self.gamedir = gamedir or self._getGitpath(game) 
        self.cheatengine = pnachmaker(os.path.join(os.path.dirname(getarg("outpath")),cheatsfn) if cheatsfn else getarg("outpath"))
        if game == "kh2":
            self.patchengine = patchEngine(workdir=getarg("patchenginedir"))
        elif game == "kh1":
            self.patchengine = patchEngine(getarg("patchenginedir-kh1"), "KH1FM_Toolkit.exe")
        elif game == "ddd":
            self.ddd = DDD(mom=self)
        self.parsingengine = memoryparser()
        self.editengine = openKH(workdir=getarg("editorengine"))
        self.openkh = self.editengine
        self.worlds = json.load(open(os.path.join(os.path.dirname(__file__), "data", "worlds.json")))
        self.objects = json.load(open(os.path.join(os.path.dirname(__file__), "data", "objlist.json")))
        self.characters = self.getCharacters()
        self.inventory = self.getInventory()

    def getCharacters(self):
        characters = {}
        for line in open(os.path.join(os.path.join(os.path.dirname(__file__), "data", "characters"))):
            parts = [i.strip() for i in line.split("|")]
            characters[int(parts[1])] = parts[2]
        return characters

    def getInventory(self):
        inventory = {}
        for line in open(os.path.join(os.path.join(os.path.dirname(__file__), "data", "inventory"))):
            parts = [i.strip() for i in line.split("|")]
            inventory[int(parts[1])] = parts[2]
        return inventory

    def _getGitpath(self, game):
        if game=="kh2":
            return getarg("gitpath")
        if game=="bbs":
            return getarg("bbs_gitpath")
        if game=="ddd":
            return getarg("ddd_gitpath")
        if game=="kh1":
            return getarg("kh1_gitpath")
        raise Exception("Unknown game")

    def reset_git(self, files_to_remove=[], branch='master', gitpath=None, gamedir=None):
        if gitpath:
            gamedir = gitpath
        if not self.gamedir and not gamedir:
            raise Exception("No 'gamedir' assigned")
        if not gamedir:
            gamedir = self.gamedir
        if not os.path.isdir(os.path.join(gamedir, ".git")):
            raise Exception("'gamedir' is not a valid git repository")
        output = subprocess.check_output(['git', 'reset', '--hard', branch], cwd=gamedir)
        for fn in files_to_remove:
            if os.path.exists(fn):
                os.remove(fn)
        print("Git repository has been reset")

    def get_git_modifications(self):
        output = subprocess.check_output(['git', 'status', '--porcelain'], cwd=self.gamedir)
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
            if self.game == 'kh2':
                gitprefix = "export/"
            elif self.game == 'kh1':
                gitprefix = "export//KINGDOM/"
            gitfiles = [gitprefix + f for f in self.get_git_modifications()]
            if self.game == "kh2":
                parsedgitfiles = [f[11:] for f in gitfiles]
            elif self.game == "kh1":
                parsedgitfiles = [f[16:] for f in gitfiles]
            else:
                raise Exception("Game not found")
            # This might not work for all OSes
            for i in range(len(gitfiles)):
                # I need to throw everything in a dist folder, so I can make sure it's clean in the case of an error during patching
                directory = os.path.dirname(os.path.join(self.patchengine.workdir,parsedgitfiles[i]))
                if not os.path.exists(directory):
                    os.makedirs(directory)
                shutil.copy(os.path.join(self.patchengine.workdir,gitfiles[i]), os.path.join(self.patchengine.workdir, parsedgitfiles[i]))
            files = files + parsedgitfiles
        self.patchengine.create_patch(files, outfn, game=self.game)
        if fromgit:
            for f in parsedgitfiles:
                os.remove(os.path.join(self.patchengine.workdir, f))
        return outfn

    def patch_game(self, patches=[], fromgit=True, fn='KH2-PATCHED.iso', useModManager=True):
        # Send the list of patches (or generate from git) to the patchengine
        # Paths must be relative to the patchengine binary
        if useModManager:
            if self.game in ["kh2"]:
                print("'patched', make sure to launch with mod manager")
                return
        if self.game == "ddd":
            self.ddd.patch_game(self.get_git_modifications())
            return
        gitprefix=None
        if self.game == "kh1":
            fn = 'KH1-PATCHED.iso'
            gitprefix=''
        if fromgit:
            patches += [self.create_patch(fromgit=True, gitprefix=gitprefix)]
            
        self.patchengine.patch_game(patches, fn, game=self.game)

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

    def randomize_files(self, paths_to_randomize, subfile_type=None):
        log = ''
        paths = list(paths_to_randomize)
        print("Randomizing {} files (if num is odd 1 file will be definitely unrandomized)".format(len(paths)))
        random.shuffle(paths)
        for i in range(0, len(paths), 2):
            if i+1 == len(paths):
                file1 = paths[i]
                file2 = paths[0]
            else:
                file1 = paths[i]
                file2 = paths[i+1]
            log += "\n{}<->{}".format(file1, file2)
            if subfile_type:
                tmpdir = os.path.join(os.getcwd(), "tmp")
                if os.path.exists(tmpdir):
                    shutil.rmtree(tmpdir)
                os.mkdir(tmpdir)
                tmp_file1 = os.path.join(tmpdir, "file1")
                self.editengine.bar_extract(file1, tmp_file1)
                tmp_file2 = os.path.join(tmpdir, "file2")
                self.editengine.bar_extract(file2, tmp_file2)
                subfile1_list = [i for i in os.listdir(tmp_file1) if i.endswith(subfile_type)]
                subfile1_json = [i for i in os.listdir(tmp_file1) if i.endswith(".json")][0]
                if not subfile1_list:
                    continue
                subfile2_list = [i for i in os.listdir(tmp_file2) if i.endswith(subfile_type)]
                subfile2_json = [i for i in os.listdir(tmp_file2) if i.endswith(".json")][0]
                if not subfile2_list:
                    continue
                subfile1 = os.path.join(tmp_file1, subfile1_list[0])
                subfile2 = os.path.join(tmp_file2, subfile2_list[0])
                self.swap_files(subfile1, subfile2)
                self.editengine.bar_build(os.path.join(tmp_file1, subfile1_json), file1)
                self.editengine.bar_build(os.path.join(tmp_file2, subfile2_json), file2)
            else:
                self.swap_files(file1, file2)
        print("Randomization complete")
        open(os.path.join(os.getcwd(),"log"),"w").write(log)

    def swap_files(self, file1, file2):
        tempfn = os.path.join(os.path.dirname(file1), "tempfilerename")
        import sys; sys.stdout.flush()
        os.rename(file1, tempfn)
        os.rename(file2, file1)
        os.rename(tempfn, file2)

    def spawn_in(self, world, room, localset, fadetype="16386", jumptype="2", entrance="0", setflags=[]):
        tempdir = os.path.join(os.getcwd(), "tempard")
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)
        os.mkdir(tempdir)
        ardfn = os.path.join(self.gamedir, "KH2", "ard", "tt01.ard")
        self.editengine.bar_extract(ardfn, tempdir)
        sc = open(os.path.join(os.path.dirname(__file__), "data", "tt01.spawnscript")).read()
        flags = "\n\t"
        for flag in setflags:
            flags += "SetProgressFlag {}\n\t".format(flag)
        sc_m = sc.format(world.upper(), room, localset, entrance, fadetype, jumptype, flags)
        scfn = os.path.join(tempdir, "spawnscript")
        open(scfn, "w").write(sc_m)
        self.editengine.spawnscript_compile(scfn, os.path.join(tempdir, "evt.script"))
        self.editengine.bar_build(os.path.join(tempdir, "tt01.ard.json"), ardfn)

    def give_to_sora(self, hp=20, mp=100, ap=50, accessoryslt=0, armorslt=0, itemslt=0, items=[]):
        options = {
            "hp": hp,
            "mp": mp,
            "ap": ap,
            "accessoryslots": accessoryslt,
            "armorslots": armorslt,
            "itemslots": itemslt,
            "items": items
        }
        self.give_to({0: options, -1: options})

    def give_to(self, characters):
        def _lookupCharId(name):
            if type(name) == type(15):
                return name
            for k in self.characters:
                if self.characters[k] == name:
                    return k
        def _lookupInvNum(item):
            if type(item) == list:
                return item[::-1]
            itembytes = [0,0]
            if item.startswith("EQ"):
                itembytes[0] = 8
                item = item[2:]
            idt = None
            for k in self.inventory:
                if self.inventory[k] == item:
                    idt = k
            if not idt:
                raise Exception("Item not found: {}".format(item))
            # Due to either bug in understanding of plrp or in kh2 itself, giving starting inventory with values > 255 is bugged
            idt = idt - (idt // 255)
            itembytes[0] = itembytes[0] + idt // 255 # sig byte
            itembytes[1] = idt % 255 # insig byte
            return itembytes[::-1]
            
        # can't give multiple people things right now
        plrpheader = [1,0,0,0,64,0,0,0]
        sc =  sc = open(os.path.join(os.path.dirname(__file__), "data", "character_records.yaml"))
        import yaml
        recs = yaml.load(sc)
        for character_index in characters:
            for option in characters[character_index]:
                recs[character_index][option] = characters[character_index][option]
        cr = bytearray(plrpheader)
        for c in recs:
            unkid = hex(c["unkid"])[2:].zfill(4)
            cr.append(int(unkid[:2], 16))
            cr.append(int(unkid[2:], 16))
            character = hex(_lookupCharId(c["character"]))[2:].zfill(2)
            cr.append(int(character, 16))
            cr.append( c["hp"])
            cr.append( c["mp"])
            cr.append( c["ap"])
            cr.append( c["armorslots"])
            cr.append( c["armorslots"])
            cr.append( c["accessoryslots"])
            cr.append( c["accessoryslots"])
            cr.append( c["itemslots"])
            cr.append( c["itemslots"])
            if len(c["items"]) > 58:
                raise Exception("Too many items")
            items = c["items"] + [[0,0] for _ in range(58-len(c["items"]))]
            for item in items:
                for subbyte in _lookupInvNum(item):
                    cr.append( subbyte )
        tempdir = os.path.join(os.getcwd(), "tempbattle")
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)
        os.mkdir(tempdir)        
        battlefn = os.path.join(self.gamedir, "KH2", "00battle.bin")
        self.editengine.bar_extract(battlefn, tempdir)
        plrppthnew = os.path.join(tempdir, "plrp.list")
        open(plrppthnew, "wb").write(cr)
        self.openkh.bar_build(os.path.join(tempdir, "00battle.bin.json"), battlefn)

