import fileHelper
import hashHelper
import configLoader
from fileTree import Directory, File, build_tree_from_json
import shutil
from pathlib import Path
from logging import getLogger as _getLogger
from re import compile as re_compile
import os

logger = _getLogger('root')


def match_files_against_patterns(flist, plist):
    def match(f, plist):
        for p in plist:
            if p.match(f):
                return True
        return False
    return [f for f in flist if match(f, plist)]


#  Add new files to the 'files' directory
def populate_pack_files(directory):
    """
    :param directory: Directory of pack
    :return: Boolean - whether the pack was indexed and copied to the files directory
    """
    config = configLoader.get_global_config()
    if not fileHelper.dir_exists(directory):
        logger.error("Directory does not exist at r'%s'" % directory)
        return False

    logger.info("Scanning r'%s' for files" % directory)
    files = [os.path.relpath(os.path.join(dp, f), directory).replace("\\", "/") for dp, dn, fn in os.walk(directory) for f in fn]
    logger.info("Checking files against patterns")
    files = match_files_against_patterns(files, [re_compile(p) for p in configLoader.get_list(config.patterns, "mods/+.? config/+.? scripts/+.?".split(" "))])

    file_index = configLoader.get_configuration(config.fileIndex, default=None, fmt=configLoader.PropertiesFormat, update_config_file=False)

    fileHelper.ensureDirectory(config.fileDir)

    logger.info("Indexing files...")
    for f in files:
        try:
            with open(os.path.join(directory, f), 'rb') as fobj:
                hash = hashHelper.md5(fobj)
        except IOError:
            logger.error("Could not calculate hash for r'%s'" % os.path.join(directory, f))
            return False
        if not fileHelper.file_exists(os.path.join(config.fileDir, hash)):
            logger.debug("Copying file r'%s' with hash %s" % (f, hash))
            shutil.copy(os.path.join(directory, f), os.path.join(config.fileDir, hash))
            file_index[hash] = os.path.split(f)[-1]
        else:
            logger.debug("File r'%s' is already saved. Skipping file." % f)

    logger.info("Files indexed successfully")
    configLoader.save_configuration(config.fileIndex, file_index, configLoader.PropertiesFormat)
    return True


def build_version_data(directory):
    """
    :param directory: Directory of pack
    :return: Nested dictionary of directories and files, with file hashes
    """
    config = configLoader.get_global_config()
    if not fileHelper.dir_exists(directory):
        logger.error("Directory does not exist at r'%s'" % directory)
        return False

    logger.info("Scanning r'%s' for files" % directory)
    files = [os.path.relpath(os.path.join(dp, f), directory).replace("\\", "/") for dp, dn, fn in os.walk(directory) for f in fn]
    logger.info("Checking files against patterns")
    files = match_files_against_patterns(files, [re_compile(p) for p in configLoader.get_list(config.patterns, "mods/+.? config/+.? scripts/+.?".split(" "))])

    logger.info("Loading file:hash index")
    file_index = configLoader.get_configuration(config.fileIndex, default=None, fmt=configLoader.PropertiesFormat, update_config_file=False)
    file_index = {file_index[k]: k for k in file_index}

    logger.info("Building file object tree")
    root = Directory(name=os.path.split(directory)[-1])

    for file in files:
        parts = Path(file).parts
        logger.debug("Adding r'%s' to file tree" % file)

        try:
            hash = file_index[parts[-1]]
        except KeyError:
            logger.error("No hash saved for r'%s'" % file)
            continue

        last = root
        for part in parts[:-1]:
            last = last.add(Directory(name=part))

        last.add(File(name=parts[-1], hash=hash))

    logger.info("Compiling object tree to json")
    output = root.build()

    return output


if __name__ == "__main__":
    import logSetup
    logSetup.setup_logger(level="INFO")
    populate_pack_files('E:/ethan/Twitch/Minecraft/Instances/Acro\'s Solid Pack')
    build_version_data('E:/ethan/Twitch/Minecraft/Instances/Acro\'s Solid Pack')