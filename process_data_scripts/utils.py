import re

"""
A collection of useful functions
"""

ANIME_REGEX_REPLACE_RULES = [
    {"input": "ļ", "replace": "[ļĻ]"},
    {"input": "l", "replace": "[l˥ļĻ]"},
    {"input": "ź", "replace": "[źŹ]"},
    {"input": "z", "replace": "[zźŹ]"},
    {"input": "ou", "replace": "(ou|ō|o)"},
    {"input": "oo", "replace": "(oo|ō|o)"},
    {"input": "oh", "replace": "(oh|ō|o)"},
    {"input": "wo", "replace": "(wo|o)"},
    {"input": "o", "replace": "([oōóòöôøӨΦο]|ou|oo|oh|wo)"},
    {"input": "uu", "replace": "(uu|u|ū)"},
    {"input": "u", "replace": "([uūûúùüǖμ]|uu)"},
    {"input": "aa", "replace": "(aa|a)"},
    {"input": "ae", "replace": "(ae|æ)"},
    {"input": "a", "replace": "([aäãά@âàáạåæā∀Λ]|aa)"},
    {"input": "c", "replace": "[cςč℃]"},
    {"input": "e", "replace": "[eəéêёëèæē]"},
    {"input": "'", "replace": "['’ˈ]"},
    {"input": "n", "replace": "[nñ]"},
    {"input": "0", "replace": "[0Ө]"},
    {"input": "2", "replace": "[2²]"},
    {"input": "3", "replace": "[3³]"},
    {"input": "5", "replace": "[5⁵]"},
    {"input": "*", "replace": "[*✻＊✳︎]"},
    {
        "input": " ",
        "replace": "( ?[²³⁵★☆♥♡\\/\\*✻✳︎＊'ˈ\-∽~〜・·\\.,;:!?@_-⇔→≒=\\+†×±◎Ө♪♣␣∞] ?| )",
    },
    {"input": "i", "replace": "([iíίɪ]|ii)"},
    {"input": "x", "replace": "[x×]"},
    {"input": "b", "replace": "[bßβ]"},
    {"input": "r", "replace": "[rЯ]"},
    {"input": "s", "replace": "[sς]"},
]


def escapeRegExp(str):

    """
    Escape the string to be used in a regex

    Parameters
    ----------
    str : str
        The string to escape

    Returns
    -------
    str
        The escaped string
    """

    str = re.escape(str)
    str = str.replace("\ ", " ")
    str = str.replace("\*", "*")
    return str


def apply_regex_rules(search):
    """
    Apply the regex rules in ANIME_REGEX_REPLACE_RULES to the search string

    Parameters
    ----------
    search : str
        The string to apply the rules to

    Returns
    -------
    str
        The string with the rules applied
    """

    for rule in ANIME_REGEX_REPLACE_RULES:
        search = search.replace(rule["input"], rule["replace"])
    return search


def get_regex_search(og_search, partial_match=True, swap_words=True):
    """
    Get the regex search string from the search string

    Parameters
    ----------
    og_search : str
        The search string
    partial_match : bool, optional
        Whether to allow partial matches, by default True
    swap_words : bool, optional
        Whether to allow swapping the words, by default True

    Returns
    -------
    str
        The regex search string
    """

    og_search = escapeRegExp(og_search.lower())
    search = apply_regex_rules(og_search)
    search = "^" + search + "$" if not partial_match else ".*" + search + ".*"

    if swap_words:
        alt_search = og_search.split(" ")
        if len(alt_search) == 2:
            alt_search = " ".join([alt_search[1], alt_search[0]])
            alt_search = apply_regex_rules(alt_search)
            alt_search = (
                "^" + alt_search + "$"
                if not partial_match
                else ".*" + alt_search + ".*"
            )
            search = f"({search})|({alt_search})"
    return search


def ask_validation(message):
    """
    Ask the user for a validation

    Parameters
    ----------
    message : str
        The message to display

    Returns
    -------
    bool
        True if the user validated, False otherwise
    """

    validation = None
    while validation != "n" and validation != "y":
        validation = input(message)
    if validation == "n":
        return False
    return True


def ask_integer_input(message, allowed_values):
    """
    Ask the user for an integer input

    Parameters
    ----------
    message : str
        The message to display
    allowed_values : list
        The allowed values

    Returns
    -------
    int
        The user input
    """

    user_input = None
    while user_input not in allowed_values:
        user_input = input(message)
        if user_input.isdigit() or user_input[1:].isdigit():
            user_input = int(user_input)
    return user_input


def ask_artist(
    message, song_database, artist_database, not_exist_ok=False, partial_match=False
):
    """
    Ask the user for an artist

    Parameters
    ----------
    message : str
        The message to display
    song_database : SongDatabase
        The song database
    artist_database : ArtistDatabase
        The artist database
    not_exist_ok : bool, optional
        Whether to allow the artist to not exist, and create a new one, by default False
    partial_match : bool, optional
        Whether to allow partial matches, by default False

    Returns
    -------
    str
        The artist name search by the user
    int
        The artist ID
    """

    user_input = input(message)
    artist_id = get_artist_id(
        song_database,
        artist_database,
        user_input,
        not_exist_ok=not_exist_ok,
        partial_match=partial_match,
    )

    return user_input, artist_id


def ask_relation_type(message):
    """
    Ask the user for a relation type

    Parameters
    ----------
    message : str
        The message to display

    Returns
    -------
    str
        The relation type (vocalists, performers, composers, arrangers)
    """

    relation_map = {
        "0": "vocalists",
        "1": "performers",
        "2": "composers",
        "3": "arrangers",
    }

    message += f"\n{relation_map}\n"

    user_input = None
    while user_input not in ["0", "1", "2", "3"]:
        user_input = input(message)

    return relation_map[user_input]


def ask_song_ids():
    """
    Ask the user to input the song IDs to update

    Returns
    -------
    list
        The song IDs entered by the user
    """

    song_ids = []

    while True:

        song_id = ask_integer_input(
            "\nPlease, input the song ID you want to update: (-2 to stop)\n",
            range(-2, 50000),
        )

        if song_id == -2:
            break

        if song_id == -1:

            songName = input("Please input the song name exactly as it is:\n")
            songArtist = input("Please input the song artist exactly as it is:\n")

            song_ids.append([songName, songArtist])

        else:

            song_ids.append(int(song_id))

    return song_ids


def ask_line_up(
    message, song_database, artist_database, not_exist_ok=False, partial_match=False
):
    """
    Ask the user for a line up of artist

    Parameters
    ----------
    message : str
        The message to display
    song_database : SongDatabase
        The song database
    artist_database : ArtistDatabase
        The artist database
    not_exist_ok : bool, optional
        Whether to allow the artist to not exist, and create a new one, by default False
    partial_match : bool, optional
        Whether to allow partial matches, by default False

    Returns
    -------
    list
        The line up of artist
    """

    group_members = []
    while True:

        user_input = input(message)

        if user_input == "!":
            break

        member_id = get_artist_id(
            song_database,
            artist_database,
            user_input,
            not_exist_ok=not_exist_ok,
            partial_match=partial_match,
            excluded_ids=[member["id"] for member in group_members],
        )

        if member_id in [member["id"] for member in group_members]:
            print("You can't have the same artist twice in the line up !!")
            exit()

        if not artist_database[member_id]["line_ups"]:
            group_members.append({"id": member_id, "line_up_id": -1})
            print(f"Adding {[member_id, -1]}")

        elif len(artist_database[member_id]["line_ups"]) == 1:
            group_members.append({"id": member_id, "line_up_id": 0})
            print(f"Adding {[member_id, 0]}")

        else:
            print(artist_database[member_id])

            line_ups = "\n"
            for i, line_up in enumerate(artist_database[member_id]["line_ups"]):
                line_up = [
                    artist_database[member["id"]]["name"]
                    for member in line_up["members"]
                ]
                line_ups += f"{i}: {', '.join(line_up)}\n"
            line_up_id = ask_integer_input(
                f"Please select the line up you want to add as a member:{line_ups}",
                range(len(artist_database[member_id]["line_ups"])),
            )
            group_members.append([member_id, line_up_id])
            print(f"Adding {[member_id, line_up_id]}")
        print()

    return group_members


def update_line_up(group, line_up_id, song_database, artist_database):
    """
    Update a line up

    Parameters
    ----------
    group : dict
        The group to update
    line_up_id : int
        The line up ID to update
    song_database : SongDatabase
        The song database
    artist_database : ArtistDatabase
        The artist database

    Returns
    -------
    list
        The updated line up
    """

    group_members = []

    for member in group["line_ups"][line_up_id]["members"]:
        user_input = ""
        while user_input not in ["=", "-"]:
            user_input = input(f"{artist_database[member['id']]['name']} ? (=/-)\n")
            if user_input == "=":
                group_members.append(member)
            else:
                print(f"removing {artist_database[member['id']]['name']}")

    line_up = ask_line_up(
        "Select people to add to the line up\n",
        song_database,
        artist_database,
        not_exist_ok=True,
    )
    group_members += line_up
    return group_members


def add_new_artist_to_DB(
    artist_database, artist, vocalist=True, performer=False, composing=False
):

    """
    Add a new artist to the artist database

    Parameters
    ----------
    artist_database : ArtistDatabase
        The artist database
    artist : str
        The artist name
    vocalist : bool, optional
        Whether the artist is a vocalist, by default True
    performer : bool, optional
        Whether the artist is a performer, by default False
    composing : bool, optional
        Whether the artist is a composer, by default False

    Returns
    -------
    str
        The new artist ID
    """

    new_id = str(int(list(artist_database.keys())[-1]) + 1)
    if new_id not in artist_database:
        artist_database[new_id] = {
            "name": artist,
            "amqNames": [artist],
            "altNames": [],
            "groups": [],
            "line_ups": [],
            "vocalist": vocalist,
            "performer": performer,
            "composer": composing,
        }
    return new_id


def get_example_song_for_artist(song_database, artist_id):
    """
    Get example songs for an artist

    Parameters
    ----------
    song_database : SongDatabase
        The song database
    artist_id : str
        The artist ID

    Returns
    -------
    list
        The list of example songs
    """

    example_animes = set()
    for anime_annId in song_database:
        anime = song_database[anime_annId]
        for song in anime["songs"]:
            if artist_id in [aid["id"] for aid in song["vocalists"]] + [
                pid["id"] for pid in song["performers"]
            ] + [cid["id"] for cid in song["composers"]] + [
                arid["id"] for arid in song["arrangers"]
            ]:
                example_animes.add(anime["animeExpandName"])
                break
    return list(example_animes)


def get_recap_artists(song_database, artist_database, ids):
    """
    Get a recap string for the artists given in parameters

    Parameters
    ----------
    song_database : SongDatabase
        The song database
    artist_database : ArtistDatabase
        The artist database
    ids : list
        The list of artist IDs

    Returns
    -------
    str
        The recap string
    """

    recap_str = ""
    for id in ids:
        ex_animes = get_example_song_for_artist(song_database, id)
        recap_str += f"{id} {artist_database[id]['name']}> {' | '.join(ex_animes[:min(3, len(ex_animes))])}\n"
    return recap_str


def get_artist_id(
    song_database,
    artist_database,
    artist,
    not_exist_ok=False,
    vocalist=True,
    composing=False,
    partial_match=False,
    exact_match=False,
    excluded_ids=[],
):
    """
    Get the artist ID from the artist name

    Parameters
    ----------
    song_database : SongDatabase
        The song database
    artist_database : ArtistDatabase
        The artist database
    artist : str
        The artist name
    not_exist_ok : bool, optional
        Whether the artist can be not in the database, and to create a new one, by default False
    vocalist : bool, optional
        Whether the artist is a vocalist, by default True
    composing : bool, optional
        Whether the artist is a composer, by default False
    partial_match : bool, optional
        Whether to allow partial match, by default False
    exact_match : bool, optional
        Whether to allow exact match, by default False
    excluded_ids : list, optional
        The list of excluded IDs, by default []
    """

    ids = []
    if not exact_match:

        if partial_match:

            artist_regex = get_regex_search(artist)

            for id in artist_database.keys():
                flag = False
                for name in (
                    artist_database[id]["amqNames"] + artist_database[id]["altNames"]
                ):
                    if re.match(artist_regex, name, re.IGNORECASE):
                        flag = True
                if flag:
                    ids.append(id)

        if not partial_match or (ids and len(ids) > 10):
            if partial_match:
                print("Too much results, removing partial match")
            artist_regex = get_regex_search(artist, partial_match=False)
            ids = []
            for id in artist_database.keys():
                flag = False
                for name in (
                    artist_database[id]["amqNames"] + artist_database[id]["altNames"]
                ):
                    if re.match(artist_regex, name, re.IGNORECASE):
                        flag = True
                if flag:
                    ids.append(id)

    else:

        for id in artist_database.keys():
            if (
                artist
                in artist_database[id]["amqNames"] + artist_database[id]["altNames"]
                and id not in ids
            ):
                ids.append(id)

    # if no IDs found
    if not ids:
        if not not_exist_ok:
            print(f"{artist} NOT FOUND, CANCELLED")
            # return -1
        new_id = add_new_artist_to_DB(artist_database, artist, vocalist, composing)
        print(f"COULDN'T FIND {artist}, adding {new_id}")
        return new_id

    if len(ids) > 1:
        for i, id in enumerate(ids):
            if id in excluded_ids:
                ids.pop(i)

    # if more than one ID, ask user to desambiguate
    if len(ids) > 1:

        recap_str = get_recap_artists(song_database, artist_database, ids)

        if not_exist_ok:
            input_message = f"\nMultiple artist found for {artist}, please input the correct ID (-1 if NONE):\n{recap_str}"
            disambiguated_id = ask_integer_input(
                input_message, [int(id) for id in ids] + [-1]
            )
        else:
            input_message = f"\nMultiple artist found for {artist}, please input the correct ID:\n{recap_str}"
            disambiguated_id = ask_integer_input(input_message, [int(id) for id in ids])

        if disambiguated_id == -1:
            new_id = add_new_artist_to_DB(artist_database, artist, vocalist, composing)
            print(f"ASKED TO CREATE NEW {artist}, adding {new_id}")
            return new_id

        return str(disambiguated_id)

    # else return found ID
    print(f"Found existing artist for {artist}")
    return ids[0]


def check_same_song(source_song, song):
    """
    Check if the song is the same as the source song

    Parameters
    ----------
    source_song : dict
        The source song
    song : str or list
        The song to check

    Returns
    -------
    bool
        Whether the song is the same as the source song
    """

    if song == source_song["annSongId"] or (
        type(song) == list
        and song[0] == source_song["songName"]
        and song[1] == source_song["songArtist"]
    ):
        return True
    return False
