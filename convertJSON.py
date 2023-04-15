import json
from pathlib import Path

song_database_path = Path("app/data/old/song_database.json")
artist_database_path = Path("app/data/old/artist_database.json")

with open(song_database_path, encoding="utf-8") as json_file:
    song_database = json.load(json_file)
with open(artist_database_path, encoding="utf-8") as json_file:
    artist_database = json.load(json_file)

new_song_database = {}
for anime in song_database:
    for song in anime["songs"]:

        composer_line_up = []
        for composer, _ in song["composer_ids"]:
            composer_line_up.append([composer, -1])

        arranger_line_up = []
        for arranger, _ in song["composer_ids"]:
            arranger_line_up.append([arranger, -1])

        song["vocals"] = song["artist_ids"]
        song["performers"] = []
        song["composers"] = composer_line_up
        song["arrangers"] = arranger_line_up
        del song["artist_ids"]
        del song["composer_ids"]
        del song["arranger_ids"]

    new_song_database[anime["annId"]] = anime

new_group_database = {}
new_artist_database = {}
for artist_id in artist_database:
    artist = artist_database[artist_id]

    if artist["members"]:

        new_group_database[artist_id] = {}
        new_group_database[artist_id]["amqNames"] = artist["names"]
        new_group_database[artist_id]["altNames"] = []
        new_group_database[artist_id]["groups"] = artist["groups"]
        new_group_database[artist_id]["vocals_line_up"] = artist["members"]
        new_group_database[artist_id]["performers_line_up"] = []
        new_group_database[artist_id]["composers_line_up"] = []
        new_group_database[artist_id]["arrangers_line_up"] = []

    else:

        new_artist_database[artist_id] = {}
        new_artist_database[artist_id]["amqNames"] = artist["names"]
        new_artist_database[artist_id]["altNames"] = []
        new_artist_database[artist_id]["groups"] = artist["groups"]
        new_artist_database[artist_id]["vocalist"] = artist["vocalist"]
        new_artist_database[artist_id]["performer"] = False
        new_artist_database[artist_id]["composer"] = artist["composer"]

with open("app/data/song_database.json", "w", encoding="utf-8") as outfile:
    json.dump(new_song_database, outfile)
with open("app/data/group_database.json", "w", encoding="utf-8") as outfile:
    json.dump(new_group_database, outfile)
with open("app/data/artist_database.json", "w", encoding="utf-8") as outfile:
    json.dump(new_artist_database, outfile)
