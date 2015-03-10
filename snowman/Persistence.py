#
# 2015 BackendButters
# MIT license
#
from logbook import Logger
import sqlite3
import os.path
from peewee import *
import datetime

log = Logger('Persistence')
db = SqliteDatabase('eldb.db', threadlocals=True)


#---------------------------------------
# db model
#---------------------------------------
class BaseModel(Model):
    class Meta:
        database = db


class FileToUpload(BaseModel):
    id = PrimaryKeyField(unique=True)
    filename = TextField(unique=True)
    description = TextField()
    queued = TextField()


class Vault(BaseModel):
    name = TextField()
    creation = TextField()
    last_inventory = TextField()
    region = TextField()
    size = TextField()
    arn = TextField(unique=True)  # arn (=String) as PK not supported
    id = PrimaryKeyField(unique=True)


class Inventory(BaseModel):
    description = TextField()
    size = TextField()
    archive_id = TextField(unique=True)
    id = PrimaryKeyField(unique=True)
    sha256_tree_hash = TextField()
    creation = TextField()
    vault = ForeignKeyField(Vault, related_name='stored_archives')


class FileToDownload(BaseModel):
    id = PrimaryKeyField(unique=True)
    queued = TextField()
    archive_to_download = ForeignKeyField(Inventory, related_name='archive_to_download')


class FernerSettings(BaseModel):
    aws_secret_key = TextField()
    aws_access_key = TextField()
    aws_settings = TextField()
    default_vault = TextField()
    start_upload_between = TextField()
    start_download_between = TextField()
    upload_folder = TextField()
    download_folder = TextField()
#---------------------------------------


class Persistence(object):

    def __init__(self, database_file):

        if os.path.isfile(database_file):
            log.debug("database found")
            db.connect()
        else:
            log.debug("No database found")
            self.__create_db(database_file)

    #---------------------------------------
    # private methods
    #---------------------------------------
    def __create_db(self, filename):
        log.info("Database does not exist. Creating...")
        db.connect()
        db.create_tables([FileToUpload, FileToUpload, FernerSettings, Vault, Inventory, FileToDownload])
    #---------------------------------------

    #---------------------------------------
    # config
    #---------------------------------------
    def store_config(self):
        pass

    def get_config_value(self, key):
        pass

    def set_config_value(self, key, value):
        pass
    #---------------------------------------

    #---------------------------------------
    # upload
    #---------------------------------------
    def append_to_upload_queue(self, filename):
        pass

    def remove_from_upload_queue(self, filename):
        pass

    def get_file_to_upload(self, filename):
        pass
    #---------------------------------------

    #---------------------------------------
    # download
    #---------------------------------------
    def append_to_download_queue(self, archive_id):
        pass

    def remove_from_download_queue(self, archive_id):
        pass

    def get_file_to_download(self, archive_id):
        pass
    #---------------------------------------
