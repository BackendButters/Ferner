#
# 2015 BackendButters
# MIT license
#

from boto.glacier.layer1 import *
from boto.glacier.layer2 import *
from logbook import Logger
import traceback
import queue
import threading
import datetime
import time

log = Logger('Glacier handler')


class Glacierhandling(threading.Thread):

    def __check_time(self):
        if self.on_time is None:
            return True
        timenow = datetime.datetime.now().time()
        if self.on_time > self.off_time:
            if timenow > self.on_time or timenow < self.off_time:
                return True
        elif self.on_time < self.off_time:
            if self.on_time < timenow < self.off_time:
                return True
        return False
    
    def __init__(self, access_key, secret_key, vaultname, region, uploadtimerange):
        threading.Thread.__init__(self)
        self.glacier_layer2 = Layer2(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
        self.glacier_layer1 = Layer1(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
        self.vault = self.glacier_layer2.get_vault(vaultname)
        self.vaultname = vaultname
        self.isUploading = False
        self.q = queue.Queue()

        if uploadtimerange is None:
            self.on_time = None
        else:
            timerange = uploadtimerange.split('-')
            self.on_time = datetime.time(int(timerange[0].split(':')[0]), int(timerange[0].split(':')[1]))
            self.off_time = datetime.time(int(timerange[1].split(':')[0]), int(timerange[1].split(':')[1]))
    
    def __uploadfile(self, file):
        try:
            log.info("Snowman is shoveling your file " + file + " to the clouds")
            archive_id = self.vault.create_archive_from_file(file)
            log.info("Done uploading!")
            os.remove(file)
            log.info("Upload successful, file locally removed. Archive id: " + archive_id)
        except:
            log.error("The snowman encountered problems while uploading " + file + " :(")
            traceback.print_exc()
            self.q.put(file)  # add again for upload
        finally:
            self.isUploading = False
    
    def download_file(self, archive_id, filename):
        job_id = self.vault.retrieve_archive(archive_id).id
        log.info("Retrieving of " + filename + " initiated. Waiting...")

        while True:
            job = self.vault.get_job(job_id)
            if not job.completed:
                log.info("Retrieval of " + filename + " not yet completed. waiting 10 minutes")
                time.sleep(600)
            else:
                break

        log.info("Downloading " + filename)
        job.download_to_file(filename)
        log.info("The snowman got your file " + filename + " back!")

    def remove_archive(self, archiveid):
        pass

    def retrieve_inventory(self, vaulttouse):
        for i in self.glacier_layer2.list_vaults():
            log.debug("Found " + str(i))
            if vaulttouse in str(i):
                try:
                    v = i
                    jobid = v.retrieve_inventory()
                    log.info("Retrieving inventory job for " + str(i) + " committed")
                    break
                except UnexpectedHTTPResponseError as e:
                    if "Amazon Glacier has not yet generated an initial inventory for this vault" in str(e):
                        log.error("Amazon Glacier has not yet generated" +
                                  "an initial inventory for this vault. Try again later")
                    elif "AccessDeniedException" in str(e):
                        log.error("Access denied to " + str(i) + ". Check the permissions of the snowman.")
                    else:
                        log.error(str(e))
        while True:
            job = v.get_job(jobid)
            if not job.completed:
                log.info("Retrieve inventory job not yet completed. waiting 10 minutes")
                time.sleep(600)
            else:
                log.info("Retrieve inventory job completed: " + str(job.get_output()))
                break

    def append_to_queue(self, file):
        self.q.put(file)
        if self.isUploading:
            log.info("A file is already being uploaded. Waiting until upload finished before proceeding.")
        if not self.__check_time():
            log.info("It's not yet time for starting an upload. Waiting until " + str(self.on_time))

    def run(self):
        log.debug("I am running")
        while True:
            if not self.isUploading and not self.q.empty() and self.__check_time():
                self.isUploading = True
                threading.Thread(target=self.__uploadfile,
                                 args=(self.q.get(),)).start()
            time.sleep(1)