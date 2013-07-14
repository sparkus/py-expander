py-expander
===========

A python script designed to post-process Transmission torrents.
Particularily if you had a seedbox like server sitting out in serverland.

The script extracts files recursively (if extract is necessary..) 
and the moves the files to pre-configured folders based on their type!
if no rars are present in the download - the script will copy the files.

The script relies on scene torrent naming standards (such as SxxExx TV shows numbering)

In any case - original torrent files are conserved for upload.

This script was originally forked from py-expander, and was modified to work on linux.
https://github.com/omerbenamram/py-expander
NOT Tested on Windows!

It doesn't work on my box...you stink!!!
======
1. If you're not running with full open permissions....check:
   a. That you have execution permissions from the user that transmission installs itself as (usually debian-transmission)
   b. That the script can write to the directory its executed in (for logging, file is logPyExpander.log)
   c. That you haven't run the script under another user and logPyExpander.log can be writeent to by debian-transmission

Modes of operation:
1. Transmission calls script directly, and sets the TR_TORRENT_DIR and TR_TORRENT_NAME as environment variables
2. Script can be called as python torrent_handler.py <dir> <name>
3. Test mode: python torrent_handler.py -t
4. Test mode with example files: python torrent_handler.py -t <dir> <name>
