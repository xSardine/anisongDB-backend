import json

"""
A script to detect invalid data in the database
"""

with open("../app/data/song_database.json") as json_file:
    song_database = json.load(json_file)

with open("../app/data/artist_database.json") as json_file:
    artist_database = json.load(json_file)


def check_member_linked_to_group(member, relation_type, to_check_group):
    """
    Check if a member is linked to a group

    Parameters
    ----------
    member_groups : list
        List of groups the member is linked to
    relation_type : str
        Type of relation between the member and the group (vocalist, composer, etc.)
    group : list
        Group to check

    Returns
    -------
    bool
        True if the member is linked to the group, False otherwise
    """

    for group in member["groups"]:
        if (
            group["id"] == to_check_group["id"]
            and group["line_up_id"] == to_check_group["line_up_id"]
            and group["type"] == relation_type
        ):
            return True

    return False


def check_group_linked_to_member(group, relation_type, member):
    """
    Check if a group is linked to a member

    Parameters
    ----------
    group : list
        Group to check
    relation_type : str
        Type of relation between the member and the group (vocalist, composer, etc.)
    member : list
        Member to check

    Returns
    -------
    bool
        True if the group is linked to the member, False otherwise
    """

    if len(group["line_ups"]) <= member["line_up_id"]:
        return False

    if group["line_ups"][member["line_up_id"]]["type"] != relation_type:
        return False

    for l_member in group["line_ups"][member["line_up_id"]]["members"]:
        if l_member["id"] == member["id"]:
            return True

    return False


def get_member_list(artist_id, line_up_id):
    """
    Get the full list of members given an artist id and a line_up id

    Parameters
    ----------
    artist_id : str
        Artist id
    line_up_id : int
        Line_up id

    Returns
    -------
    list
        List of member ids
    """

    member_list = []
    for member in artist_database[artist_id]["line_ups"][line_up_id]["members"]:
        member_list.append(member["id"])
        if member["line_up_id"] != -1:
            member_list += get_member_list(member["id"], member["line_up_id"])
    return member_list


def get_full_artist_list(artists):
    """
    Get the full list of artists given a list of artist ids and line_ups

    Parameters
    ----------
    artists : list
        List of artist ids and line_ups

    Returns
    -------
    list
        List of artist ids
    """

    artist_list = []
    for artist in artists:
        if artist["line_up_id"] == -1:
            artist_list.append(artist["id"])
        else:
            artist_list.append(artist["id"])
            artist_list += get_member_list(artist["id"], artist["line_up_id"])
    return artist_list


def check_sing_in_song(artist_id):
    """
    Check if an artist is linked to a song as a singer

    Parameters
    ----------
    artist_id : str
        Artist id

    Returns
    -------
    bool
        True if the artist is linked to a song as a singer, False otherwise
    """

    for anime_annId in song_database:
        anime = song_database[anime_annId]
        for song in anime["songs"]:
            if artist_id in get_full_artist_list(song["vocalists"]):
                return True
    return False


def check_perform_in_song(artist_id):
    """
    Check if an artist is linked to a song as a performer

    Parameters
    ----------
    artist_id : str
        Artist id

    Returns
    -------
    bool
        True if the artist is linked to a song as a performer, False otherwise
    """

    for anime_annId in song_database:
        anime = song_database[anime_annId]
        for song in anime["songs"]:
            if artist_id in get_full_artist_list(song["performers"]):
                return True
    return False


def check_compose_in_song(artist_id):
    """
    Check if an artist is linked to a song as a composer or arranger

    Parameters
    ----------
    artist_id : str
        Artist id

    Returns
    -------
    bool
        True if the artist is linked to a song as a composer or arranger, False otherwise
    """

    for anime_annId in song_database:
        anime = song_database[anime_annId]
        for song in anime["songs"]:
            if artist_id in get_full_artist_list(song["composers"] + song["arrangers"]):
                return True
    return False


donetmp = set()
for anime_annId in song_database:
    anime = song_database[anime_annId]
    for song in anime["songs"]:
        for relation_type in ["vocalists", "performers", "composers", "arrangers"]:

            for artist in song[relation_type]:

                if artist["id"] not in artist_database:
                    if artist["id"] in donetmp:
                        continue
                    donetmp.add(artist["id"])
                    print("not in database: ", artist["id"])
                    print(song["songArtist"])

                elif artist["line_up_id"] != -1 and (
                    not artist_database[artist["id"]]["line_ups"]
                    or artist["line_up_id"]
                    >= len(artist_database[artist["id"]]["line_ups"])
                ):
                    print("line_up_id out of range: ", artist["id"])
                    print(song["songArtist"])

                else:
                    if (
                        artist["line_up_id"] != -1
                        and artist_database[artist["id"]]["line_ups"][
                            artist["line_up_id"]
                        ]["type"]
                        != relation_type
                    ):
                        print(
                            f"Inconsistent line_up_type: {relation_type} vs {artist_database[artist['id']]['line_ups'][artist['line_up_id']]['type']}"
                        )

                nb_line_up = 0
                for line_up in artist_database[artist["id"]]["line_ups"]:
                    if line_up["type"] == relation_type:
                        nb_line_up += 1
                if artist["line_up_id"] == -1 and nb_line_up > 0:
                    print(
                        f"Group {artist['id']} {artist_database[artist['id']]['name']} have line ups for {relation_type}, but is linked to -1"
                    )


print("CHECKING ARTIST DATABASE DONE")
print()

annSongId = []
for anime_annId in song_database:
    anime = song_database[anime_annId]
    for song in anime["songs"]:

        if song["annSongId"] != -1:
            if song["annSongId"] not in annSongId:
                annSongId.append(song["annSongId"])
            else:
                print(f"Duplicate Song ID: {song['annSongId']}")

        for artist_id in get_full_artist_list(song["vocalists"]):
            if not artist_database[artist_id]["vocalist"]:
                print(
                    f"auto-fix {artist_database[artist_id]['name']} is singing in a song but is not a vocalist"
                )
                artist_database[artist_id]["vocalist"] = True

        for artist_id in get_full_artist_list(song["performers"]):
            if not artist_database[artist_id]["performer"]:
                print(
                    f"auto-fix {artist_database[artist_id]['name']} is performing in a song but is not a performer"
                )
                artist_database[artist_id]["performer"] = True

        for artist_id in get_full_artist_list(song["composers"] + song["arrangers"]):
            if not artist_database[artist_id]["composer"]:
                print(
                    f"auto-fix {artist_database[artist_id]['name']} is composing/arranging in a song but is not a composer"
                )
                artist_database[artist_id]["composer"] = True

to_delete = set()
for artist_id in artist_database:

    artist = artist_database[artist_id]

    # TODO check names

    for i, line_up in enumerate(artist["line_ups"]):
        for member in line_up["members"]:
            if not check_member_linked_to_group(
                artist_database[member["id"]],
                line_up["type"],
                {"id": artist_id, "line_up_id": i},
            ):
                print(
                    f"{artist['name']} IS SAID TO HAVE {member['id']} IN ITS MEMBER BUT THE LATTER DOESNT HAVE IT AS GROUP"
                )

    for group in artist["groups"]:
        if not check_group_linked_to_member(
            artist_database[group["id"]],
            group["type"],
            {"id": artist_id, "line_up_id": group["line_up_id"]},
        ):
            print(
                f"{artist['name']} IS SAID TO HAVE {group['id']} IN ITS GROUPS BUT THE LATTER DOESNT HAVE IT AS MEMBER"
            )

    if artist["vocalist"] and not check_sing_in_song(artist_id):
        print(
            f"auto-fix {artist['name']} is said to be a vocalist but is not singing in any song"
        )
        artist["vocalist"] = False

    if artist["performer"] and not check_perform_in_song(artist_id):
        print(
            f"auto-fix {artist['name']} is said to be a performer but is not performing in any song"
        )
        artist["performer"] = False

    if artist["composer"] and not check_compose_in_song(artist_id):
        print(
            f"auto-fix {artist['name']} is said to be a composer but is not composing in any song"
        )
        artist["composer"] = False

    if not artist["vocalist"] and not artist["composer"] and not artist["performer"]:
        print(f"{artist['name']} is neither vocalist, composer nor performer")
        to_delete.add(artist_id)


delete_exceptions = [
    "EXILE TRIBE",
    "BEST FRIENDS",
    "AIKATSU☆STARS",
    "Mistera Feo",
    "Hina",
]
for delete in to_delete:
    if artist_database[delete]["name"] not in delete_exceptions:
        print("delete", delete, artist_database[delete])
        artist_database.pop(delete)
        continue


with open("song_database.json", "w", encoding="utf-8") as outfile:
    json.dump(song_database, outfile)
with open("artist_database.json", "w", encoding="utf-8") as outfile:
    json.dump(artist_database, outfile)


"""
TODO: Doesn't autofix vocalists that are not vocalist=true
"""
