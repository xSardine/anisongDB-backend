import sqlite3, re
from pathlib import Path
from functools import lru_cache
import timeit

local_path = Path("data")
database_path = local_path / Path("Enhanced-AMQ-Database.db")


@lru_cache(maxsize=None)
def extract_song_database():

    """
    Extract the song database
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
    Extract the song database
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
    Extract the artist database
    """

    cursor = connect_to_database(database_path)

    extract_basic_info = """
    SELECT id, names, vocalist, composer FROM artistsNames
    """

    basic_info = run_sql_command(cursor, extract_basic_info)

    extract_artist_groups = """
    SELECT id, groups, groups_line_up FROM artistsGroups
    """

    artist_groups = run_sql_command(cursor, extract_artist_groups)

    extract_group_members = """
    SELECT id, members, members_line_up FROM artistsMembers
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
                [group, int(line_up)]
                for group, line_up in zip(groups[1].split(","), groups[2].split(","))
            ]
            if groups[1]
            else [],
            "members": [],
            "vocalist": True if info[2] else False,
            "composer": True if info[3] else False,
        }

    for info, members in zip(basic_info, group_members):

        if info[0] != members[0]:
            print("ERROR EXTRACTING ARTIST DATABASE")
            return {}

        if not members[1]:
            continue

        for member_id, line_up in zip(members[1].split(","), members[2].split(",")):
            member = artist_database[str(member_id)]
            for group_id, group_line_up in member["groups"]:
                if int(group_id) == int(info[0]):
                    while (
                        len(artist_database[str(info[0])]["members"]) <= group_line_up
                    ):
                        artist_database[str(info[0])]["members"].append([])
                    if member_id not in [
                        mid[0]
                        for mid in artist_database[str(info[0])]["members"][
                            group_line_up
                        ]
                    ]:
                        artist_database[str(info[0])]["members"][group_line_up].append(
                            [member_id, int(line_up)]
                        )

    return artist_database


def run_sql_command(cursor, sql_command, data=None):

    """
    Run the SQL command with nice looking print when failed (no)
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
            "\nError while running this command: \n",
            sql_command,
            "\n",
            error,
            "\nData: ",
            data,
            "\n",
        )
        return None


def regexp(expr, item):
    try:
        reg = re.compile(expr)
        return reg.search(item) is not None
    except Exception as e:
        pass


def connect_to_database(database_path):

    """
    Connect to the database and return the connection's cursor
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
    get_songs_from_annId = f"SELECT * from songsFull WHERE songType IN ({','.join('?'*len(authorized_types))}) AND annId IN ({','.join('?'*len(annIds))}) LIMIT 300"
    return run_sql_command(cursor, get_songs_from_annId, authorized_types + annIds)


def get_annId_from_anime(cursor, regex, authorized_types=[1, 2, 3]):

    # TODO Indexes on lower ?
    get_animeID_from_animeName = f"SELECT annId from animes WHERE (lower(animeENName) REGEXP ? OR lower(animeJPName) REGEXP ?) LIMIT 300"
    return [
        id[0]
        for id in run_sql_command(cursor, get_animeID_from_animeName, [regex, regex])
    ]


def get_song_list_from_song_name(cursor, regex, authorized_types=[1, 2, 3]):

    start = timeit.default_timer()
    # TODO Indexes on lower ?
    get_animeID_from_songName = f"SELECT * from songsFull WHERE songType IN ({','.join('?'*len(authorized_types))}) AND lower(songName) REGEXP ? LIMIT 300"
    results = run_sql_command(
        cursor, get_animeID_from_songName, authorized_types + [regex]
    )
    print()
    print(len(results))
    print(f"Song List from Song Name SQL: {round(timeit.default_timer() - start, 4)}")
    print()
    return results


def get_song_list_from_songArtist(cursor, regex, authorized_types=[1, 2, 3]):

    # TODO Indexes on lower ?
    get_song_list_from_songArtist = f"SELECT * from songsFull WHERE songType IN ({','.join('?'*len(authorized_types))}) AND lower(songArtist) REGEXP ? LIMIT 300"
    return run_sql_command(
        cursor, get_song_list_from_songArtist, authorized_types + [regex]
    )


def get_songs_ids_from_artist_ids(cursor, artist_ids):

    get_songs_ids_from_artist_ids = f"SELECT song_id from link_song_artist WHERE artist_id IN ({','.join('?'*len(artist_ids))})"
    return [
        id[0]
        for id in run_sql_command(
            cursor, get_songs_ids_from_artist_ids, [str(id) for id in artist_ids]
        )
    ]


def get_songs_ids_from_composing_team_ids(cursor, composer_ids, arrangement):

    # TODO FIND A BETTER WAY WITH VIEW
    get_songs_ids_from_composer_ids = f"SELECT song_id from link_song_composer WHERE composer_id IN ({','.join('?'*len(composer_ids))}) LIMIT 300"
    songIds = set()
    for song_id in run_sql_command(
        cursor, get_songs_ids_from_composer_ids, composer_ids
    ):
        songIds.add(song_id[0])

    if arrangement:
        get_songs_ids_from_arranger_ids = f"SELECT song_id from link_song_arranger WHERE arranger_id IN ({','.join('?'*len(composer_ids))}) LIMIT 300"
        for song_id in run_sql_command(
            cursor, get_songs_ids_from_arranger_ids, composer_ids
        ):
            songIds.add(song_id[0])

    songIds = list(songIds)

    return songIds


def get_artist_ids_from_regex(cursor, regex):

    # TODO Index on lower ?
    get_artist_ids_from_regex = "SELECT artist_id from artist_names WHERE lower(name) REGEXP ? GROUP BY artist_id LIMIT 50"
    artist_ids = [
        id[0] for id in run_sql_command(cursor, get_artist_ids_from_regex, [regex])
    ]
    return artist_ids


def get_song_list_from_links(cursor, link):

    if "catbox.moe" not in link or (".webm" not in link and ".mp3" not in link):
        return []

    link = f".*{link}.*"

    # TODO Indexes ?
    get_songs_from_link = (
        f"SELECT * from songsFull WHERE HQ REGEXP ? OR MQ REGEXP ? OR audio REGEXP ?"
    )
    songs = run_sql_command(cursor, get_songs_from_link, [link, link, link])
    return songs


def get_artist_names_from_artist_id(cursor, artist_id):

    """
    Return the list of names linked to the artist id as a dict
    """

    command = "SELECT names FROM artistsNames WHERE id == ?;"

    result = run_sql_command(cursor, command, [int(artist_id)])[0][0].split("\\$")

    return result


def get_artist_line_ups(cursor, artist_id):

    command = f"SELECT * FROM artistsLineUps WHERE id = {artist_id}"
    return run_sql_command(cursor, command)


def get_artist_groups(cursor, artist_id):

    command = f"SELECT * FROM artistsGroups WHERE id = {artist_id}"
    groups = run_sql_command(cursor, command)[0]
    if not groups[1]:
        return []
    else:
        return [
            [group, line_up]
            for group, line_up in zip(groups[1].split(","), groups[2].split(","))
        ]
