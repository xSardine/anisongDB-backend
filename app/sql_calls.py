import datetime
from io_classes import *

import re
import sqlite3
from pathlib import Path
from functools import lru_cache
from typing import Any, List

from decouple import config

"""
A collection of useful functions to extract data from the database
"""

DATABASE_PATH = config("DATABASE_PATH")
LOGS_PATH = config("LOGS_PATH")
MAX_RESULTS_PER_SEARCH = config("MAX_RESULTS_PER_SEARCH")


@lru_cache(maxsize=None)
def extract_song_database():
    """
    Extract the song database and save it to cache

    Returns
    -------
    song_database (dict):
        Dictionary with the song database (map to ann_song_id)
    """

    command = """
    SELECT * FROM songsFull;
    """

    cursor = connect_to_database()

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
        Dictionary with the anime database (map to ann_id)
    """

    command = """
    SELECT * FROM songsFull;
    """

    cursor = connect_to_database()

    anime_database = {}
    for song in run_sql_command(cursor, command):
        if song[0] not in anime_database:
            anime_database[song[0]] = {
                "ann_id": song[0],
                "anime_expand_name": song[1],
                "anime_jp_name": song[2],
                "anime_en_name": song[3],
                "anime_alt_names": set(song[4].split("\$")) if song[4] else set(),
                "anime_season": song[5],
                "anime_type": song[6],
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

    artist_database = {}

    cursor = connect_to_database()

    # Basic info

    extract_basic_info = """
    SELECT id, names, is_vocalist, is_performer, is_composer, is_arranger FROM artistsNames
    """

    for (
        artist_id,
        artist_names,
        is_vocalist,
        is_performer,
        is_composer,
        is_arranger,
    ) in run_sql_command(cursor, extract_basic_info):
        artist_database[str(artist_id)] = {
            "names": artist_names.split("\$"),
            "groups": [],
            "line_ups": [],
            "vocalist": True if is_vocalist else False,
            "performer": True if is_performer else False,
            "composer": True if is_composer else False,
            "arranger": True if is_arranger else False,
        }

    # Groups

    extract_artist_groups = """
    SELECT id, groups_role_types, groups_ids, groups_line_ups FROM artistsGroups
    """

    for artist_id, group_role_types, group_ids, groups_line_up_ids in run_sql_command(
        cursor, extract_artist_groups
    ):
        artist_id = str(artist_id)
        if artist_id not in artist_database:
            raise ValueError("Artist id not found in artist database")

        if not group_role_types:
            continue

        for role_type, group_id, line_up_id in zip(
            group_role_types.split(","),
            group_ids.split(","),
            groups_line_up_ids.split(","),
        ):
            artist_database[artist_id]["groups"].append(
                {
                    "role_type": role_type,
                    "id": group_id,
                    "line_up_id": line_up_id,
                }
            )

    # Members

    extract_group_members = """
    SELECT id, group_line_up_id, member_role_type, members, members_line_up FROM artistsMembers
    """

    for (
        group_id,
        group_line_up_id,
        members_role_types,
        members_ids,
        members_line_up_ids,
    ) in run_sql_command(cursor, extract_group_members):
        group_id = str(group_id)
        if group_id not in artist_database:
            raise ValueError("Group id not found in artist database")

        if not members_role_types:
            continue

        if group_line_up_id != len(artist_database[group_id]["line_ups"]):
            raise ValueError("A group line up id has been skipped")

        members = []
        for role_type, member_id, line_up_id in zip(
            members_role_types.split(","),
            members_ids.split(","),
            members_line_up_ids.split(","),
        ):
            members.append(
                {"role_type": role_type, "id": member_id, "line_up_id": line_up_id}
            )

        artist_database[group_id]["line_ups"].append(
            {"line_up_id": group_line_up_id, "members": members}
        )

    return artist_database


def run_sql_command(cursor: sqlite3.Cursor, sql_command: str, data: List[Any] = None):
    """
    Run the SQL command with nice looking print when failed (no)

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor of the database to run the command
    sql_command : str
        The SQL command to run
    data : List[Any], optional
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


def regexp(expr: str, item: str):
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


def connect_to_database(database_path=DATABASE_PATH):
    """
    Connect to the database and return the connection's cursor

    Parameters
    ----------
    database_path : str, optional
        The path to the database, by default DATABASE_PATH

    Returns
    -------
    sqlite3.Cursor
        The cursor of the database to run the commands
    """

    try:
        sqliteConnection = sqlite3.connect(database_path)
        sqliteConnection.create_function("REGEXP", 2, regexp)
        cursor = sqliteConnection.cursor()
        return cursor
    except sqlite3.Error as error:
        print("\n", error, "\n")
        exit(0)


def get_possibles_songs_from_filters(
    cursor: sqlite3.Cursor,
    ann_ids: List[int] = [],
    song_ids: List[int] = [],
    anime_name_regex: str = "",
    song_name_regex: str = "",
    artist_name_regex: str = "",
    ignore_duplicates: bool = False,
    song_types: List[int] = [1, 2, 3],
    song_categories: List[SongCategory] = [
        SongCategory.Standard,
        SongCategory.Chanting,
        SongCategory.Character,
        SongCategory.Instrumental,
    ],
    song_difficulty_range: IntRange = IntRange(min=0, max=100),
    anime_types: List[AnimeType] = [
        AnimeType.TV,
        AnimeType.movie,
        AnimeType.OVA,
        AnimeType.special,
        AnimeType.ONA,
    ],
    anime_seasons: List[str] = [],
    anime_genres: List[str] = [],
    anime_tags: List[str] = [],
    max_results_per_search: int = -1,
):
    """
    Filter the song database

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor of the database to run the command
    ann_ids : List[int], optional
        List of ANN ids to search, by default ignored
    song_ids : List[int], optional
        List of song ids to search, by default ignored
    anime_name_regex : str, optional
        Regex to search in anime names, not implemented yet
    song_name_regex : str, optional
        Regex to search in song names
    artist_name_regex : str, optional
        Regex to search in artist names
    ignore_duplicates : bool
        Ignore duplicate songs
    song_types : list[int]
        List of authorized song types (opening:1, ending:2, insert:3)
    song_categories : List[SongCategory] ['Standard', 'Chanting', 'Character', 'Instrumental']
        List of song categories to search
    song_difficulty_range : IntRange {min: int, max: int}
        Range of difficulty to search
    anime_types : List[AnimeType] ['TV', 'movie', 'OVA', 'special', 'ONA']
        List of anime types to search
    anime_seasons : List[str]
        List of anime seasons to search (ex: ['Winter 2001', 'Spring 2022'])
    anime_genres : List[str]
        List of anime genres to search
    anime_tags : List[str]
        List of anime tags to search
    max_results_per_search : int
        Maximum number of results per search, -1 for no limit

    Returns
    -------
    list
        List of songs that match the filters
    """

    where_filters = []

    ann_ids = ", ".join([str(ann_id) for ann_id in ann_ids])
    if ann_ids:
        where_filters.append(f"ann_id IN ({ann_ids})")

    song_ids = ", ".join([str(song_id) for song_id in song_ids])

    if song_ids:
        where_filters.append(f"song_id IN ({song_ids})")

    anime_types = ", ".join([f"'{anime_type}'" for anime_type in anime_types])
    where_filters.append(f"anime_type IN ({anime_types})")

    anime_seasons = ", ".join([f"'{anime_season}'" for anime_season in anime_seasons])
    if anime_seasons:
        where_filters.append(f"anime_season IN ({anime_seasons})")

    song_types = ", ".join([str(song_type) for song_type in song_types])
    where_filters.append(f"song_type IN ({song_types})")

    song_categories = ", ".join(
        [f"'{song_category}'" for song_category in song_categories]
    )
    where_filters.append(f"song_category IN ({song_categories})")

    where_filters.append(f"song_difficulty >= {song_difficulty_range.min}")
    where_filters.append(f"song_difficulty <= {song_difficulty_range.max}")

    if song_name_regex:
        where_filters.append(f"lower(song_name) REGEXP '{song_name_regex}'")

    if artist_name_regex:
        where_filters.append(f"lower(song_artist) REGEXP '{artist_name_regex}'")

    get_songs_from_filters_query = (
        f"SELECT * from songsFull WHERE "
        + " AND ".join(where_filters)
        + (f" GROUP BY song_name, song_artist" if ignore_duplicates else "")
        + (f" LIMIT {max_results_per_search}" if max_results_per_search != -1 else "")
    )

    return run_sql_command(cursor, get_songs_from_filters_query)


def get_songs_list_from_song_artist(
    cursor: sqlite3.Cursor, regex: str, authorized_types: List[int] = [1, 2, 3]
):
    """
    Get the songs from the song artist

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor of the database to run the command
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
    get_songs_list_from_song_artist = f"SELECT * from songsFull WHERE song_type IN ({','.join('?'*len(authorized_types))}) AND lower(song_artist) REGEXP ? LIMIT {MAX_RESULTS_PER_SEARCH}"
    return run_sql_command(
        cursor, get_songs_list_from_song_artist, authorized_types + [regex]
    )


def get_songs_ids_from_artist_ids(
    cursor: sqlite3.Cursor, artist_ids: List[str], credit_types: List[CreditType]
):
    """
    Get the songs from the artist id (any type: vocalist, composers, arrangers, ...)

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor of the database to run the command
    artist_ids : List[str]
        The list of artist ids
    credit_types : List[CreditType] : [vocalist, backing_vocalist, composer, arranger, performer]
        List of credit types to search

    Returns
    -------
    list
        The list of the songs corresponding to the artist id
    """

    credit_types = [f"'{credit_type}'" for credit_type in credit_types]
    get_songs_ids_from_artist_ids = f"SELECT DISTINCT song_id from link_song_artist WHERE role_type IN ({','.join(credit_types)}) AND artist_id IN ({','.join('?'*len(artist_ids))})"

    return [
        id[0]
        for id in run_sql_command(
            cursor, get_songs_ids_from_artist_ids, [str(id) for id in artist_ids]
        )
    ]


def get_artist_ids_from_regex(
    cursor: sqlite3.Cursor, regex: str, max_nb_results: int = 50
):
    """
    Get the artist id from the artist name regex.

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor of the database to run the command
    regex : str
        The regex to match
    max_nb_results : int, optional
        The maximum number of artist_id to return, by default 50

    Returns
    -------
    list
        The list of the artist id corresponding to the artist name regex
    """

    # TODO Index on lower ?
    get_artist_ids_from_regex = f"SELECT DISTINCT artist_id from link_artist_name WHERE lower(name) REGEXP ? LIMIT {max_nb_results}"
    artist_ids = [
        id[0] for id in run_sql_command(cursor, get_artist_ids_from_regex, [regex])
    ]
    return artist_ids


def get_songs_list_from_songIds(cursor: sqlite3.Cursor, songIds: List[str]):
    """
    Get the songs from the songIds

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor of the database to run the command
    songIds : List[str]
        The songIds to match

    Returns
    -------
    list
        The list of the songs corresponding to the songIds
    """

    get_songs_from_sonbIds = f"SELECT * from songsFull WHERE songId IN ({','.join('?'*len(songIds))}) LIMIT {MAX_RESULTS_PER_SEARCH}"
    songs = run_sql_command(cursor, get_songs_from_sonbIds, songIds)
    return songs


def get_songs_list_from_links(cursor: sqlite3.Cursor, link: str):
    """
    Get the songs from the link

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The cursor of the database to run the command
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
    get_songs_from_link = f"SELECT * from songsFull WHERE HQ REGEXP ? OR MQ REGEXP ? OR audio REGEXP ? LIMIT {MAX_RESULTS_PER_SEARCH}"
    songs = run_sql_command(cursor, get_songs_from_link, [link, link, link])
    return songs


def add_logs(
    nb_results: int = 0,
    execution_time: int = 0,
    ann_id: int = "NULL",
    anime_name: str = "NULL",
    song_name: str = "NULL",
    artist_id: int = "NULL",
    artist_name: str = "NULL",
    max_other_artists: int = 99,
    group_granularity: int = 0,
    credit_types: List[CreditType] = [
        CreditType.vocalist,
        CreditType.backing_vocalist,
        CreditType.performer,
        CreditType.composer,
        CreditType.arranger,
    ],
    song_types: List[int] = [1, 2, 3],
    song_categories: List[SongCategory] = [
        SongCategory.Standard,
        SongCategory.Chanting,
        SongCategory.Character,
        SongCategory.Instrumental,
    ],
    song_difficulty_range: IntRange = IntRange(min=0, max=100),
    anime_types: List[AnimeType] = [
        AnimeType.TV,
        AnimeType.movie,
        AnimeType.OVA,
        AnimeType.special,
        AnimeType.ONA,
    ],
    anime_seasons: List[str] = "NULL",
    anime_genres: List[str] = "NULL",
    anime_tags: List[str] = "NULL",
    partial_match: bool = True,
    ignore_duplicates: bool = False,
    max_results_per_search: int = "NULL",
) -> None:
    sqliteConnection = sqlite3.connect(LOGS_PATH)
    cursor = sqliteConnection.cursor()
    run_sql_command(
        cursor,
        """CREATE TABLE IF NOT EXISTS logs(
            date TEXT,
            nb_results INTEGER,
            execution_time FLOAT,

            ann_id INTEGER, 
            anime_name TEXT,
            anime_types TEXT, 
            anime_seasons TEXT, 
            anime_genres TEXT, 
            anime_tags TEXT, 

            song_name TEXT, 
            song_types TEXT, 
            song_categories TEXT, 
            song_difficulty_min TEXT,
            song_difficulty_max TEXT,

            artist_id INTEGER, 
            artist_name TEXT, 
            max_other_artists INTEGER,
            group_granularity INTEGER,
            credit_types TEXT,
            
            partial_match BIT,
            ignore_duplicates BIT, 
            max_results_per_search INTEGER
        )""",
    )

    credit_types = f"'{','.join(credit_types)}'"

    anime_types = f"'{','.join(anime_types)}'"

    song_types = f"'{','.join([str(song_type) for song_type in song_types])}'"
    song_categories = f"'{','.join(song_categories)}'"

    anime_seasons = f"'{','.join(anime_seasons)}'" if anime_seasons else "NULL"
    anime_genres = f"'{','.join(anime_genres)}'" if anime_genres else "NULL"
    anime_tags = f"'{','.join(anime_tags)}'" if anime_tags else "NULL"

    log = f"""INSERT INTO logs (
        date, nb_results, execution_time,
        ann_id, anime_name, anime_types, anime_seasons, anime_genres, anime_tags, 
        song_name, song_types, song_categories, song_difficulty_min, song_difficulty_max, 
        artist_id, artist_name, max_other_artists, group_granularity, credit_types, 
        partial_match, ignore_duplicates, max_results_per_search) VALUES (
        '{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', {nb_results}, {round(execution_time, 2)},
        {ann_id}, '{anime_name}', {anime_types}, {anime_seasons}, {anime_genres}, {anime_tags}, 
        '{song_name}', {song_types}, {song_categories}, {song_difficulty_range.min}, {song_difficulty_range.max},
        {artist_id}, '{artist_name}', {max_other_artists}, {group_granularity},{credit_types},
        {partial_match}, {ignore_duplicates}, {max_results_per_search}
        )"""
    print(log)
    run_sql_command(cursor, log)

    sqliteConnection.commit()
    cursor.close()
