# GDTDupePurgerPy
The latest version of GDTDupePurger for Python.
A one-file script that takes duplicate asset errors from Black Ops 3 Mod Tools' linker output and attempt to resolve them.

### This version of GDTDupePurger is the currently supported version of GDTDupePurger, and accounts for MidgetBlasters T7 Asset Pack.
### For those using the old version, it's recommended you update to this version as soon as possible.


How to use:

Do "Compile" in BO3 MT. If you have duplicates, they will show in the linker output, such as:

    J:\Steam\steamapps\common\Call of Duty Black Ops III\/gdtdb/gdtdb.exe /update

    gdtDB: updating

    errors found while updating database!

    ERROR: Duplicate 'beam' asset 'flamethrower_beam_dragon_gauntlet' found in j:\steam\steamapps\common\call of duty black ops iii\source_data       \wpn_t7_zmb_dlc3_gauntlet_dragon.gdt:2296
    ERROR: Duplicate 'beam' asset 'flamethrower_beam_dragon_gauntlet' found in j:\steam\steamapps\common\call of duty black ops iii\source_data\wpn_t7_zmb_dlc3_gauntlet_dragon_1.gdt:2296
    gdtDB: processed (2 GDTs) (584 assets) in 0.222 sec


Copy that entire output (all of the text). Open **dupe_error.txt** in a text editor such as notepad, paste the text, then save it and close.

Run ***dupe_fixer.exe***. The console window will show you any issues, or its progress through the GDT purging.

Try compiling in Mod Tools again. Your duplicates should be fixed!

Backups of GDTs will be placed in ***<dupe_fixer_folder>/backup***.



**FLAGS**
You can make shortcuts to the exe or run it from the command line with the following flags:

**no_log** or **quiet** or **shh** - Doesn't print the progress it's making, just tells you when it's done.

**developer_no_backup_use_wisely** - Doesn't backup the GDT that gets edited. I DO NOT RECOMMEND USING THIS, EVER.

###SOURCE USERS###
For people using the source code instead of the built EXE and want to run this script with Python via the Command Prompt / Powershell:
Please make sure to change directory to the dupe_fixer.py folder, otherwise the script will try checking the CMD / PS instance path instead of the dupe_fixer relative path.
Thanks to Gmrh for catching this :D


###NOTE###

v.1.0c only deletes a single duplicate for each asset.
If you have multiple duplicates of one asset, you will need to try compiling in MT after running **dupe_fixer.exe** to get the updated error list, and repeat as many times as necessary.
This will be fixed on full release.




