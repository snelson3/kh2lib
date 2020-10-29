## KH2Lib

This is the repository for a python library to assist with creating mods/codes to Kingdom Hearts 2 Final Mix +

The library can do the following (and more)
* Extract/Patch/Repack KH2 iso's, (using KH2FM_Toolkit.exe)
* Extract/Repack BAR files using openKH
* Given a memdump of the running game, locate the offset where a given file is located
* Given a source and modified file, generate codes to perform the changes in memory, without patching (useful for fast prototypes)
* Provides lookup methods for objects (look up object id/name/mdlx based on just one of those)

To install run the following

`pip install kh2lib`

The library is most useful when used in conjunction with some other pieces of software, and detects their presence using the following environment variables

USE_KH2_EDITORENGINE - Is the path to the openkh executables

example - `C:\Users\12sam\Desktop\openkh`

USE_KH2_GITPATH - Is the path to an extracted KH2 ISO

example - `C:\Users\12sam\Desktop\Kingdom Hearts 2 Modding\ISO\export`

USE_KH2_OUTPATH - Where the library should places created pnach files (usually the cheats folder of pcsx2)

example - `C:\Users\12sam\Desktop\pcsx\PCSX2 1.6.0\cheats\F266B00B.pnach`

USE_KH2_PATCHENGINEDIR - Is the path to a directory containing KH2FM_Toolkit.exe

example - `C:\Users\12sam\Desktop\Kingdom Hearts 2 Modding\ISO`


## Usage

See the examples folder for examples on how to perform various tasks