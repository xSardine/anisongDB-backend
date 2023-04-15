import json
import utils

song_database_path = "../app/data/song_database.json"
artist_database_path = "../app/data/artist_database.json"

with open(song_database_path, encoding="utf-8") as json_file:
    song_database = json.load(json_file)
with open(artist_database_path, encoding="utf-8") as json_file:
    artist_database = json.load(json_file)


def get_fused_artist(ids):

    """
    Get the result of the artist fusion given in parameters

    Parameters
    ----------
    ids : list of str
        List of artist ids to fuse

    Returns
    -------
    dict
        The fused artist
    """

    main_name = ""
    all_amq_names = set()
    all_alt_names = set()
    all_groups = []
    all_line_up = []
    vocalist = False
    performer = False
    composer = False
    for id in ids:
        if not main_name:
            main_name = artist_database[id]["name"]
        for name in artist_database[id]["amqNames"]:
            all_amq_names.add(name)
        for name in artist_database[id]["altNames"]:
            if name not in all_amq_names:
                all_alt_names.add(name)
        for group in artist_database[id]["groups"]:
            all_groups.append(group)
        for line_up in artist_database[id]["line_ups"]:
            all_line_up.append(line_up)
        if artist_database[id]["vocalist"]:
            vocalist = True
        if artist_database[id]["performer"]:
            performer = True
        if artist_database[id]["composer"]:
            composer = True

    return {
        "name": main_name,
        "amqNames": list(all_amq_names),
        "altNames": list(all_alt_names),
        "groups": all_groups,
        "line_ups": all_line_up,
        "vocalist": vocalist,
        "performer": performer,
        "composer": composer,
    }


def process():

    artists = utils.ask_line_up(
        "Type in the artist line up you want to fuse (first one will be the center)\n",
        song_database,
        artist_database,
    )

    artists = [artist["id"] for artist in artists]

    if len(artists) < 2:
        print("You need two people or more to start this process, cancelled")
        return

    recap_artist = ""
    for artist in artists:
        recap_artist += f"{artist}> {artist_database[artist]['name']} {artist_database[artist]['amqNames']} {artist_database[artist]['altNames']} - {artist_database[artist]['groups']} - {artist_database[artist]['line_ups']}\n"

    center_id = artists[0]
    removed_ids = artists
    removed_ids.pop(artists.index(center_id))

    print()

    # Updating the center_id with the new fused artist
    artist_database[center_id] = get_fused_artist([center_id] + artists)

    # Updating link in song_database for artist, composers and arrangers of deleted artists
    line_up_id = 0 if artist_database[center_id]["line_ups"] else -1

    for anime_annId in song_database:
        anime = song_database[anime_annId]
        for song in anime["songs"]:

            for key in ["vocalists", "performers", "composers", "arrangers"]:
                for artist in song[key] + song[key] + song[key] + song[key]:
                    if artist["id"] in removed_ids:
                        print(
                            f"{key} {song['songName']} {artist} → {[center_id, line_up_id]}"
                        )
                        artist["id"] = center_id
                        artist["line_up_id"] = line_up_id

    # Updating every artist that has a deleted artist as a member or a group to now link to center_id
    for id in removed_ids:
        for artist_id in artist_database:
            if artist_id == center_id:
                continue
            artist = artist_database[artist_id]
            for line_up in artist["line_ups"]:
                for member in line_up["members"]:
                    if member["id"] in removed_ids:
                        print(
                            f"{artist['name']} Member: {member['id']} {member['line_up_id']} → {[center_id, line_up_id]}"
                        )
                        member["id"] = center_id
                        member["line_up_id"] = line_up_id
            for group in artist["groups"]:
                if group["id"] in removed_ids:
                    print(
                        f"{artist['name']} Group: {group['id']} {group['line_up_id']} → {[center_id, group['line_up_id']]}"
                    )
                    group["id"] = center_id
        artist_database.pop(id)

    print()
    validation_message = f"You will be removing these artists: {removed_ids}\nID {center_id} is chosen to be the one to stay\nNew artist:\nNames : {artist_database[center_id]['name']} {artist_database[center_id]['amqNames']} {artist_database[center_id]['altNames']}\nGroups : {artist_database[center_id]['groups']}\nLine ups : {artist_database[center_id]['line_ups']}\nCredits : {artist_database[center_id]['vocalist']}, {artist_database[center_id]['performer']}, {artist_database[center_id]['composer']}\nDo you want to proceed ?\n"
    validation = utils.ask_validation(validation_message)
    if not validation:
        print("User cancelled")
        return

    with open(song_database_path, "w", encoding="utf-8") as outfile:
        json.dump(song_database, outfile)
    with open(artist_database_path, "w", encoding="utf-8") as outfile:
        json.dump(artist_database, outfile)


process()

# TODO fusing groups not working
