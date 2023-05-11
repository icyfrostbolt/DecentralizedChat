import json

def open_file():
    file = open('data.json')
    data = json.load(file)
    return data

def update_file(data):
    file = open("data.json", "w")
    json.dump(data, file, indent=4)
    file.close()