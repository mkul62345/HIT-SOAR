def init_from_config():
    CONFIG_PATH = "S:\\SOAR\\cfg.txt" #Change to local
    date_ref_dict = {}

    #We merge using a dictionary built from both the changes and existing data-
    with open(CONFIG_PATH, "r") as config:
        for line in config:
            parts = line.split(": ")
            if parts is not None:
                date_ref_dict[parts[0][2:-1]] = parts[1][1:-3]

    return date_ref_dict