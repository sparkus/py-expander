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
