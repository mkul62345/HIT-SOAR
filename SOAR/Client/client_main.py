import requests 
import datetime
import time
import json 
import os
from evtx import PyEvtxParser
from change_merger import init_from_config

#input: parsed json-dictionary record
#output: none | Consider returning something as ack
def send_to_server(record):
    url = "http://localhost:5000/logger"
    r = requests.post(url, json=record)


def text_to_datetime(convert):
    curr_time = datetime.datetime.strptime(convert, "%Y-%m-%d %H:%M:%S.%f")
    return curr_time


#Pushes all 
def push_logs():
    #Initializing
    date_ref_dict = init_from_config()
    DIRECTORY_PATH = "S:\\SOAR\\Client\\"
    dir = os.listdir( DIRECTORY_PATH + "\\Logs")
    for file in dir:

        #If file is an event log file
        if file.find(".evtx") != -1: 
            parser = PyEvtxParser(DIRECTORY_PATH + "\\" + file)
            time_to_convert = date_ref_dict.get(file)

            #If file is not known from before, init in dictionary
            if time_to_convert is None:
                last_record_time = datetime.datetime(year=1,month=1,day=1)
                date_ref_dict[file] = last_record_time
            else:
                last_record_time = text_to_datetime(time_to_convert)

            #Walk the records and send to server all previously unsent records + update dictionary.
            for record in parser.records_json():                
                record["timestamp"] = record["timestamp"][:-4] #stripping " UTC" from timestamp
                curr_time = text_to_datetime(record["timestamp"])
                if(curr_time > last_record_time):
                    date_ref_dict[file] = curr_time
                    record["timestamp"] = record["timestamp"][:-7] #stripping ".XXXXXX" from timestamp to fit db format
                    send_to_server(record)

                    #Writing progress to changelog.
                    with open( (DIRECTORY_PATH + "\\Configuration\\changelog.txt"), "a") as changelog:
                        changelog.write(json.dumps({ file : curr_time }, default=str) + "\n")






push_logs()
time.sleep(10)









"""
record structure:
    event_record_id
    timestamp
    data


def dump_evtx_json_to_file():
    readfrom = "C:\\Users\\Negi 3000\\Desktop\\Test\\Microsoft-Windows-AppReadiness%4Admin.evtx"
    dumpinto = "C:\\Users\\Negi 3000\\Desktop\\Test\\Output.txt"
    temp = evtx_to_json(readfrom)
    with open(dumpinto, "w") as text_file:
        for result in temp:
            text_file.write("%s\n----------------------------------------------------------------'\n" % result)

dump_evtx_json_to_file()

"""
