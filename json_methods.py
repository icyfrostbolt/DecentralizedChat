import json

def open_file(guild):
    file = open('data.json')
    data = json.load(file)
    if not str(guild) in data:
        full_data = {
            "chat": {
                "group": {},
                "individual": {},
                "channel": {}
            },
            "individuals": {},
            "profiles": {},
            "settings": {
                "journal": False
            },
        }
        return full_data, data
    return data[str(guild)], data

def update_file(data, guild, full_data):
    file = open("data.json", "w")
    full_data[str(guild)] = data
    json.dump(full_data, file, indent=4)
    file.close()