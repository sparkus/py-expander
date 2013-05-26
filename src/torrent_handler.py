#!/usr/bin/python

"""
@author: sparkus

File originated from py-expander https://github.com/omerbenamram/py-expander
"""

import os
import errno
import shutil
import subprocess
import logging
import logging.handlers
import re
import itertools
import sys
import config



VIDEO_EXTENSIONS = ['.mkv', '.avi', '.mov', '.mp4']
MUSIC_EXTENSIONS = ['.flac', '.mp3', '.ogg', '.wav']
SOFTWARE_EXTENSIONS = ['.iso', '.exe']
ARCHIVE_EXTENSIONS = ['.rar', '.zip', '.7z']

TV_RE = re.compile("S\d{2}E\d{2}", re.IGNORECASE)

class torrentHandler:
    def __init__(self, torrentDirectory, torrentName, testMode=False):
        self.testMode = testMode
        self.torrentDirectory = torrentDirectory
        self.torrentName = torrentName
        self.logger = logging.getLogger("torHandler")
    def _find_target_archives(self,directory):
        """
        Look for archives in sourcedir + subdirectories.
        Returns archive to extract
        :param directory:
        :type directory: str
        :rtype: list
        """
        archives_list = []
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                candidate_extension = os.path.splitext(f)[1]
                if candidate_extension in ARCHIVE_EXTENSIONS:
                    self.logger.debug('Found archive %s in %s' % (os.path.join(dirpath, f), directory))
                    archives_list.append(os.path.join(dirpath, f))

        #Deals with redundant part01.rar part02.rar etc..
        def _redundant_parts_filter(self,file_name):
            match = re.search("part(?P<part_num>\d+).rar", file_name, re.IGNORECASE)

            # if parts pattern is not present, leave object unfiltered
            if not match:
                return True

            # if match, return true only if int value is 1
            if int(match.group('part_num')) == 1:
                return True

            self.logger.debug('%s is redundant - not extracting' % file_name)
            return False

        after_parts_filtration = itertools.ifilter(_redundant_parts_filter, archives_list)

        return list(after_parts_filtration)


    def _extract(self,archive_path, destination):
        """
        Extract archive content to destination
        :param  archive_path:
        :type archive_path: str
        :param  destination:
        :type destination: str
        """
        if self.testMode == False:
            extract_job = subprocess.Popen([config.EXECUTABLE,  # 7Zip Executable
                                        'e',  # extract to current working dir
                                      #  '-y',  # assume yes to all (overwrite)
                                        archive_path],
                                       cwd=destination)              # Change current working directory
        # Since 7Zip only works with e flag..

            extract_job.wait()
        else:
            self.logger.debug("Would have run subprocess " + str(config.EXECUTABLE) + " against " + archive_path + " to " + destination)


    def _create_extraction_path(self,directory_path):
        """
        Verifies that current path exists - if not, creates the path.

        :param directory_path:
        :type directory_path: str, unicode
        """
        if not os.path.exists(directory_path):
            try:
                if self.testMode == False:
                    os.makedirs(directory_path)
                    self.logger.info("Creating directory %s" % directory_path)
                else:
                    self.logger.debug("Would have created " + directory_path)

            except OSError as e:
                if e.errno != errno.EEXIST:
                    self.logger.exception("Failed to create directory %s" % directory_path, e)
                    raise
                pass


    def extract_all(self):
        """
        recursively extracts all archives in folder.
        recursive extraction is iterative and is saved under

        /foler/config.EXTRACTION_TEMP_DIR_NAME/unpacked_%iteration number

        :param folder:
        """
        current_dir = self.torrentDirectory
        archives_to_extract = self._find_target_archives(current_dir)

        if len(archives_to_extract) > 0:
            iteration = 1
            extracted_root = os.path.join(self.torrentDirectory, config.EXTRACTION_TEMP_DIR_NAME)
            if self.testMode == False:
                os.mkdir(extracted_root)
            else:
                self.logger.debug("Would have created " + extracted_root)
                

            while len(archives_to_extract) > 0:
                current_dir = os.path.join(extracted_root, 'unpacked_%d' % iteration)
                if self.testMode == False:
                    os.mkdir(current_dir)
                else:
                    self.logger.debug("Would have created " + current_dir)

                for target_archive in archives_to_extract:
                    self.logger.info("Extracting %s to %s" % (target_archive, current_dir))
                    _extract(target_archive, current_dir)

                iteration += 1
                archives_to_extract = _find_target_archives(current_dir)

        else:
            self.logger.info("Found no archives in %s !" % current_dir)


    def _handle_directory(self, directory, handler, torrent_name):
        """
        This is the main directory processing function.
        It's called by the _choose_handler function with the proper handling command for the
        files to process (copy/move).
        It searches for files in the directories matching the known extensions and moves the to
        the relevant path in the destination (/path/category/torrent_name)

        :param directory:
        :param handler:
        :param torrent_name:
        """
        if os.path.isfile(directory):
            category_path, file_category = get_categorized_path(filename)
            if category_path is not None:
                original_path = os.path.join(directory_path, filename)
                self.logger.info("Found %s file %s" % (file_category, original_path))
                destination_dir = os.path.join(category_path, torrent_name)
                _create_extraction_path(destination_dir)
                try:
                    # Move\Copy all relevant files to their location (keep original files for uploading)
                    if self.testMode == False:
                        handler(original_path, destination_path)
                    else:
                        self.logger.debug("Would have run " + str(handler) + " on " + str(original_path) + " to " + str(destination_path))
                    
                    self.logger.info('%s %s to %s' % (handler.__name__, original_path, destination_path))

                except OSError as e:
                    self.logger.exception("Failed to %s %s : %s" % (handler.__name__, original_path, e))
        for directory_path, subdirectories, filenames in os.walk(directory):
            self.logger.info("Processing Directory %s" % directory_path)
            for filename in filenames:
                category_path, file_category = self.get_categorized_path(filename)

                if category_path is not None:

                    original_path = os.path.join(directory_path, filename)
                    self.logger.info("Found %s file %s" % (file_category, original_path))

                    destination_dir = os.path.join(category_path, torrent_name)
                    self._create_extraction_path(destination_dir)  # Creates target directory (of category path)
                    destination_path = os.path.join(destination_dir, filename)

                    try:
                        # Move\Copy all relevant files to their location (keep original files for uploading)
                        if self.testMode == False:
                            handler(original_path, destination_path)
                            self.logger.info('%s %s to %s' % (handler.__name__, original_path, destination_path))
                        else:
                            self.logger.debug("Would have run " + str(handler.__name__) + " on " + str(original_path) + " to " + str(destination_path))
                        
                        

                    except OSError as e:
                        self.logger.exception("Failed to %s %s : %s" % (handler.__name__, original_path, e))


    def _choose_handler(self):
        """
        This function chooses between copying and moving rars (to conserve the original torrent files)
        :param folder:
        :type folder: str
        """

        # If folder has extracted rars...
        if os.path.isdir(self.torrentDirectory):
            listdir = os.listdir(self.torrentDirectory)
            if config.EXTRACTION_TEMP_DIR_NAME in listdir:
                self.logger.debug("Found Extraction Temp in _choose_handler, moving extracted file(s)")
                self._handle_directory(os.path.join(self.torrentDirectory, config.EXTRACTION_TEMP_DIR_NAME), shutil.move, self.torrentName)

            # If folder has content only
            else:
                self.logger.debug("Content only in _choose_handler, selected copy")
                self._handle_directory(self.torrentDirectory, shutil.copy, self.torrentName)
        else:
            self.logger.debug("File only in _choose_handler, selected copy")
            self._handle_directory(self.torrentDirectory, shutil.copy, self.torrentName)


    def _cleanup_temp(self):
        """
        This function searches for the subdirectory created for extraction and deletes it.

        :param folder:
        """
        self.logger.info('Cleaning up...')

        listdir = os.listdir(self.torrentDirectory)

        if config.EXTRACTION_TEMP_DIR_NAME in listdir:
            try:
                self.logger.info('Going to delete %s' % (os.path.join(self.torrentDirectory, config.EXTRACTION_TEMP_DIR_NAME)))
                if self.testMode == False:
                    shutil.rmtree(os.path.join(self.torrentDirectory, config.EXTRACTION_TEMP_DIR_NAME))
                else:
                    self.logger.debug("Would have deleted the directory " + str(os.path.join(self.torrentDirectory, config.EXTRACTION_TEMP_DIR_NAME)))
                
            except OSError:
                self.logger.exception("Failed to delete directory %s ! " %
                                  (os.path.join(self.torrentDirectory, config.EXTRACTION_TEMP_DIR_NAME)))


    def _is_tv_show(self,filename):
        """
        Takes filename "file.ext"
        Returns True if file is TV Show based on S01E01 regex
        """
        if TV_RE.search(filename):
            return True
        return False


    def _get_content_type(self, filename):
        """
        returns 'tv', 'movie', 'music', 'app' for respective filetypes
        :rtype : str
        :param filename:
        "filename.ext"
        """
        base_filename = os.path.basename(filename)
        base_filename.lower()
        extension = os.path.splitext(base_filename)[1]
        self.logger.debug("_get_content_type is searching for content match for " + str(filename))
        if extension in VIDEO_EXTENSIONS:
            if base_filename.find('sample') != -1:
                self.logger.debug("Found content sample")
                return "vid-sample"
            if self._is_tv_show(base_filename):
                self.logger.debug("Found TV")
                return 'tv'
            else:
                self.logger.debug("Found Movie")
                return 'movie'
        if extension in MUSIC_EXTENSIONS:
            self.logger.debug("Found music")
            return 'music'
        if extension in SOFTWARE_EXTENSIONS:
            self.logger.debug("Found software")
            return 'app'
        else:
            self.logger.debug("No match in _get_content_type")
            return None


    def get_categorized_path(self, filename):
        """
        returns destination path for extractions according to the category to which the file belongs
        :param filename:
        "filename.ext"
        :rtype : tuple or None
        """
        try:
            return config.CATEGORY_PATH[self._get_content_type(filename)], self._get_content_type(filename)

        # If file is not recognized by any of the categories/checks - there would be no entry at the
        # config file
        except KeyError:
            self.logger.debug("%s is not in any relevant category, ignoring" % self.torrentDirectory)
            return None


def main():
    """
    This main function is designed to be called by transmission.

    """
    
    logger = logging.getLogger("torHandler")
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler("logPyExpander.log", mode='a', maxBytes=20000, backupCount=3)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('Initializing')
    testArg=False #a holder for the testmode argument
    if len(sys.argv) == 2: #do we have any incoming arguments?
        logger.debug("got 2 arguments in the sys.argv")
        if sys.argv[1] == '-t': #testMode
            logger.debug("Test mode detected")
            testArg=True
            testDir1 = os.path.join(os.getcwd(), 'testDir') #make a subdirectory with the folder testDir that all of the test stuff will be in.
            if (not os.path.isdir(testDir1)): #check for existince, make if missing.
                os.makedirs(testDir1)
            #First Test
            test1DirectoryName = 'torTest1'
            test1TorrentName = 'test1.mp4'
            testTorDirectory1 = os.path.join(testDir1, test1DirectoryName)
            if (not os.path.isdir(testTorDirectory1)): #check for existince, make if missing.
                os.makedirs(testTorDirectory1)
            testTorFile1 = os.path.join(testTorDirectory1, test1TorrentName)
            fileWriter = open(testTorFile1, 'w')
            fileWriter.write('I like to test')
            fileWriter.close()
            TORRENT_DIR = testTorDirectory1
            TORRENT_NAME = test1TorrentName
            logger.info('**TEST** Torrent_Dir: '+ str(TORRENT_DIR))
            logger.info('**TEST** Torrent Name: ' + str(TORRENT_NAME))
    else:
        #Get environmental values from transmission
        #Path should be $TR_TORRENT_DIR/$TR_TORRENT_NAME
        TORRENT_DIR = os.environ.get('TR_TORRENT_DIR', None)
        TORRENT_NAME = os.environ.get('TR_TORRENT_NAME', None)
        logger.info('Torrent_Dir: '+ str(TORRENT_DIR))
        logger.info('Torrent Name: ' + str(TORRENT_NAME))
    torHandler = torrentHandler(TORRENT_DIR, TORRENT_NAME, testMode=testArg)
    TORRENT_DIR = os.path.realpath(os.path.join(TORRENT_DIR, TORRENT_NAME))
    #TORRENT_DIR, TORRENT_NAME = config.get_environmental_variables_from_transmission()


    torHandler.extract_all()
    torHandler._choose_handler()
    torHandler._cleanup_temp()

    if testArg:
        shutil.rmtree(testDir1)
    logger.info('Done!')
    


if __name__ == "__main__":
    main()


