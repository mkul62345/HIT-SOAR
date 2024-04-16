import json
import time

def init_from_config():
    DIRECTORY_PATH = "S:\\HIT-SOAR\\SOAR\\Client\\Configuration"
    CONFIG_PATH = DIRECTORY_PATH + "\\cfg.txt"
    CHANGELOG_PATH = DIRECTORY_PATH + "\\changelog.txt"
    date_ref_dict = {}

    #We merge using a dictionary built from both the changes and existing data
    with open(CHANGELOG_PATH, "r") as changelog:
        for line in changelog:
            curr_change = line.split(": ")
            if curr_change is not None:
                date_ref_dict[curr_change[0][2:-1]] = curr_change[1][1:-3]

        with open(CONFIG_PATH, "r") as config:
            for line in config:
                if line != "{}":
                    curr_line = line.split(": ")
                    if date_ref_dict.get(curr_line[0][2:-1]) is None:
                        date_ref_dict[curr_line[0][2:-1]] = curr_line[1][1:-3]


    #After finishing building, we dump the new true data
    with open(CONFIG_PATH, "w") as config:
        for key in date_ref_dict:
            config.write(json.dumps({ key : date_ref_dict[key] }, default=str) + "\n")
   
    with open(CHANGELOG_PATH, "w") as changelog:
        changelog.write("")


    return date_ref_dict