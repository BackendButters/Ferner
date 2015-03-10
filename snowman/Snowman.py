#!/usr/bin/python3
#
# 2015 BackendButters
# MIT license
#

import time
from logbook import Logger
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import sys
import optparse
from Glacierhandling import *
import yaml

log = Logger('Snowman observer')

class Fileeventhandler(PatternMatchingEventHandler):
    ignore_patterns = ["*/.*"]
    
    def on_created(self, event):
        log.debug("New file: " + event.src_path)
        glacierhnd.append_to_queue(event.src_path)

    def on_moved(self, event):
        log.debug("moved: " + event.src_path + " - dest: " + event.dest_path)
        glacierhnd.append_to_queue(event.dest_path)


if __name__ == "__main__":

    parser = optparse.OptionParser()
    parser.add_option("-c", "--configfile", dest="configfile",
                      type="string",
                      help="specify the configuration file to use")
   
    (options, argv) = parser.parse_args()
    if not options.configfile:
        parser.error('configfile not given')
    
    configstream = open(options.configfile, 'r')
    config = yaml.load(configstream)
    
    try:
        access_key = config['AWS_Access_Key']
        secret_key = config['AWS_Secret_Key']
        defaultVault = config['Vault']
        glacierRegion = config['AWS_Region']
    except KeyError:
        sys.exit("Error parsing config file")

    try:
        uploadTimeRange = config['StartUploadBetween']
    except KeyError:
        uploadTimeRange = None

    try:
        downloadTimeRange = config['StartDownloadBetween']
    except KeyError:
        downloadTimeRange = None

    try:
        uploadFolder = config['UploadFolder']
    except KeyError:
        uploadFolder = "uploads"

    try:
        downloadFolder = config['DownloadFolder']
    except KeyError:
        downloadFolder = "downloads"

    log.info("Using AWS access key: " + access_key)
    log.info("Using AWS secret key: <Top_Secret>")
    log.info("Using vault " + defaultVault + " @ region " + glacierRegion)
    log.info("Uploading files between: " + str(uploadTimeRange))
    log.info("Watching folder " + uploadFolder + "/")

    glacierhnd = Glacierhandling(access_key, secret_key, defaultVault, glacierRegion, uploadTimeRange)
    
    glacierhnd.daemon = True
    glacierhnd.start()
  
    hndlr = Fileeventhandler()
    observer = Observer()
    observer.schedule(hndlr, './' + uploadFolder, recursive=False)
    observer.start()
    
    log.info("Watching the snowman melting...")
    
    try:
        while True:
            time.sleep(1)
    except(KeyboardInterrupt, SystemExit):
        log.debug("Shutting down")
        observer.stop()
    observer.join()
    log.info("Only water is left.")
    sys.exit(0)