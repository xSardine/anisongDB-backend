import sqlite3, re
from pathlib import Path
from functools import lru_cache
import timeit

"""
A collection of useful functions to extract data from the database
"""

local_path = Path("data")
database_path = local_path / Path("Enhanced-AMQ-Database.sqlite")


@lru_cache(maxsize=None)
def extract_song_database():

    """
    Extract the song database and save it to cache

    Returns
    -------
    song_database (dict):
        Dictionary with the song database (map to annSongId)
    """

    command = """
    SELECT * FROM songsFull;
    """

    cursor = connect_to_database(database_path)

    song_database = {}
    for song in run_sql_command(cursor, command):

        song_database[song[7]] = song

    return song_database


@lru_cache(maxsize=None)
def extract_anime_database():

    """
    Extract the anime database and save it to cache

    Returns
    -------
    anime_database (dict):
        Dictionary with the anime database (map to annId)
    """

    command = """
    SELECT * FROM songsFull;
    """

    cursor = connect_to_database(database_path)

    anime_database = {}
    for song in run_sql_command(cursor, command):

        if song[0] not in anime_database:
            anime_database[song[0]] = {
                "animeExpandName": song[1],
                "animeJPName": song[2],
                "animeENName": song[3],
                "animeAltNames": song[4],
                "animeVintage": song[5],
                "animeType": song[6],
                "songs": [],
            }
        anime_database[song[0]]["songs"].append(song)

    return anime_database


@lru_cache(maxsize=None)
def extract_artist_database():

    """
    Extract the artist database and save it to cache

    Returns
    -------
    artist_database (dict):
        Dictionary with the artist database (map to artist id)
    """

    cursor = connect_to_database(database_path)

    extract_basic_info = """
    SELECT id, names, vocalist, performer, composer FROM artistsNames
    """

    basic_info = run_sql_command(cursor, extract_basic_info)

    extract_artist_groups = """
    SELECT id, group_line_up_type, groups_ids, groups_line_ups FROM artistsGroups
    """

    artist_groups = run_sql_command(cursor, extract_artist_groups)

    extract_group_members = """
    SELECT id, member_line_up_type, members, members_line_up FROM artistsMembers
    """

    group_members = run_sql_command(cursor, extract_group_members)

    if len(basic_info) != len(artist_groups) or len(basic_info) != len(group_members):
        print("ERROR EXTRACTING ARTIST DATABASE")
        return {}

    artist_database = {}
    for info, groups in zip(basic_info, artist_groups):

        if info[0] != groups[0]:
            print("ERROR EXTRACTING ARTIST DATABASE")
            return {}

        artist_database[str(info[0])] = {
            "names": info[1].split("\$"),
            "groups": [
                {"type": groups[1], "id": group_id, "line_up_id": int(line_up_id)}
                for group_id, line_up_id in zip(
                    groups[2].split(","), groups[3].split(",")
                )
            ]
            if groups[1]
            else [],
            "line_ups": [],
            "vocalist": True if info[2] else False,
            "performer": True if info[3] else False,
            "composer": True if info[4] else False,
        }

    for info, members in zip(basic_info, group_members):

        if info[0] != members[0]:
            print("ERROR EXTRACTING ARTIST DATABASE")
            return {}

        if not members[2]:
            continue

        for member_id, line_up_id in zip(members[2].split(","), members[3].split(",")):
            member = artist_database[str(member_id)]
            for group in member["groups"]:
                if int(group["id"]) == int(info[0]):
                    while (
                        len(artist_database[str(info[0])]["line_ups"])
                        <= group["line_up_id"]
                    ):
                        artist_database[str(info[0])]["line_ups"].append(
                            {"type": "", "members": []}
                        )
                    artist_database[str(info[0])]["line_ups"][group["line_up_id"]][
                        "type"
                    ] = members[1]
                    if member_id not in [
                        mid["id"]
                        for mid in artist_database[str(info[0])]["line_ups"][
                            group["line_up_id"]
                        ]["members"]
                    ]:
                        artist_database[str(info[0])]["line_ups"][group["line_up_id"]][
                            "members"
                        ].append({"id": member_id, "line_up_id": int(line_up_id)})

    return artist_database


def run_sql_command(cursor, sql_command, data=None):

    """
    Run the SQL command with nice looking print when failed (no)

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor to run the command
    sql_command : str
        The SQL command to run
    data : tuple, optional
        The data to insert in the command, by default None

    Returns
    -------
    list
        The result of the command
    """

    try:
        if data is not None:
            cursor.execute(sql_command, data)
        else:
            cursor.execute(sql_command)

        record = cursor.fetchall()

        return record

    except sqlite3.Error as error:

        if data is not None:
            for param in data:
                if type(param) == str:
                    sql_command = sql_command.replace("?", '"' + str(param) + '"', 1)
                else:
                    sql_command = sql_command.replace("?", str(param), 1)

        print(
            f"\n{error}\nError while running this command: {sql_command}\nData: {data}\n"
        )
        exit()


def regexp(expr, item):
    """
    Function to use the REGEXP operator in sqlite

    Parameters
    ----------
    expr : str
        The expression to match
    item : str
        The item to match

    Returns
    -------
    bool
        True if the item matches the expression, False otherwise
    """
    try:
        reg = re.compile(expr)
        return reg.search(item) is not None
    except Exception as e:
        pass


def connect_to_database(database_path):

    """
    Connect to the database and return the connection's cursor

    Parameters
    ----------
    database_path : str
        The path to the database

    Returns
    -------
    sqlite3.Cursor
        The cursor to run the commands
    """

    try:
        sqliteConnection = sqlite3.connect(database_path)
        sqliteConnection.create_function("REGEXP", 2, regexp)
        cursor = sqliteConnection.cursor()
        return cursor
    except sqlite3.Error as error:
        print("\n", error, "\n")
        exit(0)


def get_songs_list_from_annIds(cursor, annIds, authorized_types):
    """
    Get the songs from the annId

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor to run the command
    annIds : list
        The annId of the anime
    authorized_types : list
        The authorized types of the songs

    Returns
    -------
    list
        The list of the songs from the annId
    """
    get_songs_from_annId = f"SELECT * from songsFull WHERE songType IN ({','.join('?'*len(authorized_types))}) AND annId IN ({','.join('?'*len(annIds))}) LIMIT 300"
    return run_sql_command(cursor, get_songs_from_annId, authorized_types + annIds)


def get_song_list_from_songArtist(cursor, regex, authorized_types=[1, 2, 3]):
    """
    Get the songs from the song artist

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor to run the command
    regex : str
        The regex to match
    authorized_types : list, optional
        The authorized types of the songs, by default [1,2,3]

    Returns
    -------
    list
        The list of the songs corresponding to the song artist search
    """

    # TODO Indexes on lower ?
    get_song_list_from_songArtist = f"SELECT * from songsFull WHERE songType IN ({','.join('?'*len(authorized_types))}) AND lower(songArtist) REGEXP ? LIMIT 300"
    return run_sql_command(
        cursor, get_song_list_from_songArtist, authorized_types + [regex]
    )


def get_songs_ids_from_artist_ids(cursor, artist_ids):
    """
    Get the songs from the artist id (any type: vocalists, composers, arrangers, ...)

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor to run the command
    artist_ids : list
        The artist id

    Returns
    -------
    list
        The list of the songs corresponding to the artist id
    """

    get_songs_ids_from_artist_ids = f"SELECT song_id from link_song_artist WHERE artist_id IN ({','.join('?'*len(artist_ids))})"
    return [
        id[0]
        for id in run_sql_command(
            cursor, get_songs_ids_from_artist_ids, [str(id) for id in artist_ids]
        )
    ]


def get_songs_ids_from_vocalist_ids(cursor, artist_ids):
    """
    Get the songs from the vocalist id

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor to run the command
    artist_ids : list
        The artist id

    Returns
    -------
    list
        The list of the songs corresponding to the vocalist id
    """

    get_songs_ids_from_vocalist_ids = f"SELECT song_id from link_song_artist WHERE artist_line_up_type == 'vocalists' AND artist_id IN ({','.join('?'*len(artist_ids))})"
    return [
        id[0]
        for id in run_sql_command(
            cursor, get_songs_ids_from_vocalist_ids, [str(id) for id in artist_ids]
        )
    ]


def get_songs_ids_from_performer_ids(cursor, artist_ids):
    """
    Get the songs from the performer id

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor to run the command
    artist_ids : list
        The artist id

    Returns
    -------
    list
        The list of the songs corresponding to the performer id
    """

    get_songs_ids_from_performer_ids = f"SELECT song_id from link_song_artist WHERE artist_line_up_type == 'performers' AND artist_id IN ({','.join('?'*len(artist_ids))})"
    return [
        id[0]
        for id in run_sql_command(
            cursor, get_songs_ids_from_performer_ids, [str(id) for id in artist_ids]
        )
    ]


def get_songs_ids_from_composing_team_ids(cursor, composer_ids, arrangement):
    """
    Get the songs from the composing team id

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor to run the command
    composer_ids : list
        The composing team id
    arrangement : bool
        If the song is an arrangement

    Returns
    -------
    list
        The list of the songs corresponding to the composing team id
    """

    # TODO FIND A BETTER WAY WITH VIEW
    get_songs_ids_from_composer_ids = f"SELECT song_id from link_song_artist WHERE (artist_line_up_type == 'composers' AND composer_id IN ({','.join('?'*len(composer_ids))}) LIMIT 300"
    songIds = set()
    for song_id in run_sql_command(
        cursor, get_songs_ids_from_composer_ids, composer_ids
    ):
        songIds.add(song_id[0])

    if arrangement:
        get_songs_ids_from_arranger_ids = f"SELECT song_id from link_song_artist WHERE artist_line_up_type == 'arrangers' AND arranger_id IN ({','.join('?'*len(composer_ids))}) LIMIT 300"
        for song_id in run_sql_command(
            cursor, get_songs_ids_from_arranger_ids, composer_ids
        ):
            songIds.add(song_id[0])

    songIds = list(songIds)

    return songIds


def get_artist_ids_from_regex(cursor, regex):
    """
    Get the artist id from the artist name regex

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor to run the command
    regex : str
        The regex to match

    Returns
    -------
    list
        The list of the artist id corresponding to the artist name regex
    """

    # TODO Index on lower ?
    get_artist_ids_from_regex = "SELECT artist_id from artist_names WHERE lower(name) REGEXP ? GROUP BY artist_id LIMIT 50"
    artist_ids = [
        id[0] for id in run_sql_command(cursor, get_artist_ids_from_regex, [regex])
    ]
    return artist_ids


def get_song_list_from_links(cursor, link):
    """
    Get the songs from the link

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor to run the command
    link : str
        The link to match

    Returns
    -------
    list
        The list of the songs corresponding to the link
    """

    if "catbox.moe" not in link or (".webm" not in link and ".mp3" not in link):
        return []

    link = f".*{link}.*"

    # TODO Indexes ?
    get_songs_from_link = (
        f"SELECT * from songsFull WHERE HQ REGEXP ? OR MQ REGEXP ? OR audio REGEXP ?"
    )
    songs = run_sql_command(cursor, get_songs_from_link, [link, link, link])
    return songs
