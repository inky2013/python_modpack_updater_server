import pack_manipulation
import fileHelper
import fileTree
import logSetup
from io import BytesIO
import zipfile
from os import path as opath
from json import dumps
from json import loads
import configLoader

logger = logSetup.setup_logger()


def update_pack(in_path, pack_id, pack_version, pack_version_readable, pack_author):
    logger.info("Attempting update of pack: %s" % pack_id)
    config = configLoader.get_global_config()
    if not pack_manipulation.populate_pack_files(in_path):
        logger.error("Pack files could not be copied. Pack will not be added.")
        return False

    pack_path = opath.join(config.packDir, pack_id)

    if fileHelper.dir_exists(opath.join(pack_path, str(pack_version))):
        logger.error("The version '%s' is already defined on the server" % str(pack_version))
        return False

    if not fileHelper.dir_exists(pack_path):
        logger.error("Pack cannot be updated becuase it doesn't exist. Use the 'add_pack' function instead.")
        return False

    version_data = pack_manipulation.build_version_data(in_path)

    configLoader.save_configuration(opath.join(pack_path, str(pack_version), "files.json"), version_data)
    configLoader.save_configuration(opath.join(pack_path, str(pack_version), "version.json"),
                                    {"version": pack_version, "version_name": pack_version_readable,
                                     "authors": pack_author.split(";")})

    pack_data = configLoader.get_configuration(opath.join(pack_path, "pack.json"), update_config_file=False)
    pack_data["latest_version"] = pack_version
    pack_data["authors"] = [i for i in set(pack_data.get("authors", []))]
    configLoader.save_configuration(opath.join(pack_path, "pack.json"), pack_data)

    logger.info("Pack updated successfully")
    return True


def add_pack(in_path, pack_id, pack_name, pack_version, pack_version_readable, pack_author):
    logger.info("Attempting to add pack: %s" % pack_id)
    config = configLoader.get_global_config()
    pack_path = opath.join(config.packDir, pack_id)
    if fileHelper.dir_exists(pack_path):
        logger.error("Pack could not be added as it already exists. Use the 'update_pack' function instead.")
        return False
    configLoader.save_configuration(opath.join(pack_path, "pack.json"), {"id": pack_id, "name": pack_name, "latest_version": pack_version, "authors": pack_author.split(";")})
    logger.info("Generated pack data files. Running update to generate file list for initial version")
    return update_pack(in_path, pack_id, pack_version, pack_version_readable, pack_author)


def get_update(pack_id, current_version, target_version):
    logger.info("Processing update from '%s' to '%s' for pack: %s" % (current_version, target_version, pack_id))
    config = configLoader.get_global_config()
    pack_path = opath.join(config.packDir, pack_id)
    if not fileHelper.dir_exists(pack_path):
        logger.error("Pack '%s' is not saved on the server. Cannot update pack" % pack_id)
        return None

    try:
        ctree = fileHelper.readFile(opath.join(config.packDir, pack_id, str(current_version), "files.json"))
    except IOError:
        logger.error("No update matching version %s was found" % str(current_version))
        return None

    try:
        ttree = fileHelper.readFile(opath.join(config.packDir, pack_id, str(target_version), "files.json"))
    except IOError:
        logger.error("No update matching version %s was found" % str(target_version))
        return None


    toadd, toremove = fileTree.compare_trees(
        fileTree.build_tree_from_json(loads(ctree)),
        fileTree.build_tree_from_json(loads(ttree))
    )

    logger.info("Client has %i files to download, %i to remove" % (len(toadd), len(toremove)))

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file in toadd:
            try:
                zip_file.writestr(file.hash, open(opath.join("files", file.hash), "rb").read())
            except IOError:
                logger.error("Error adding file to ZIP (r'%s')" % file.path)
                return None

        zip_file.writestr("update.json", dumps({
            "additions": [{"hash": i.hash, "path": i.path} for i in toadd],
            "deletions": [i.path for i in toremove],
            "version": configLoader.get_configuration(opath.join(config.packDir, pack_id, str(target_version), "version.json")),
            "pack": configLoader.get_configuration(opath.join(config.packDir, pack_id, "pack.json"))
        }, indent=4))

    zip_buffer.seek(0)
    output = zip_buffer.read()
    zip_buffer.close()
    logger.debug("ZIP file of %s created" % fileHelper.sizeof_fmt(len(output)))
    return output




if __name__ == "__main__":
    pass
    #add_pack('E:/ethan/Twitch/Minecraft/Instances/Acro\'s Solid Pack', 'acros_solid_pack', 'Acro\'s solid pack', 1.0, "1.0", "acrominer;inky2013")
    #update_pack('E:/ethan/Twitch/Minecraft/Instances/Acro\'s Solid Pack - Copy', 'acros_solid_pack', 1.1, "1.1", "inky2013")
    #with open("test.zip", "wb+") as f:
    #   f.write(get_update('acros_solid_pack', 1.0, 1.1))


