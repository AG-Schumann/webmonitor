from pymongo import MongoClient
import os


def user(meta):
    pass

def base_context(**kwargs):
    with MongoClient(os.environ['MONGO_URI_DAQ']) as client:
        modes = client

def base_command(command):
    doc = {
            "command" : command,
            "acknowledged" : [],
            "host" : "charon",
        }
    return doc

def insert_command(command, **kwargs):
    pass
