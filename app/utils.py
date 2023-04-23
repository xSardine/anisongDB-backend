from .io_classes import SongType

import re
from pytz import timezone
from datetime import datetime, timedelta
from typing import Any, List, Dict

"""
A collection of useful functions
"""

ANIME_REGEX_REPLACE_RULES = {
    "ļ": "[ļĻ]",
    "l": "[l˥ļĻ]",
    "ź": "[źŹ]",
    "z": "[zźŹ]",
    "ou": "(ou|ō|o)",
    "oo": "(oo|ō|o)",
    "oh": "(oh|ō|o)",
    "wo": "(wo|o)",
    "o": "([oōóòöôøӨΦοδ]|ou|oo|oh|wo)",
    "uu": "(uu|u|ū)",
    "u": "([uūûúùüǖμ]|uu)",
    "aa": "(aa|a)",
    "ae": "(ae|æ)",
    "a": "([aäãά@âàáạåæā∀Λ]|aa)",
    "c": "[cςč℃]",
    "e": "[eəéêёëèæē]",
    "'": "['’ˈ]",
    "n": "[nñ]",
    "0": "[0Ө]",
    "2": "[2²]",
    "3": "[3³]",
    "5": "[5⁵]",
    "*": "[*✻＊✳︎]",
    " ": "([^a-zA-Z0-9])",
    "i": "([iíίɪ]|ii)",
    "x": "[x×]",
    "b": "[bßβ]",
    "r": "[rЯ]",
    "s": "[sς]",
}


def escape_regex(search_string: str) -> str:
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

    return re.escape(search_string).replace(r"\ ", " ").replace(r"\*", "*")


def apply_regex_rules(search_string: str) -> str:
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

    for rule, replacement in ANIME_REGEX_REPLACE_RULES.items():
        search_string = search_string.replace(rule, replacement)
    return search_string


def get_regex_search(
    search_string: str, partial_match: bool = True, swap_words: bool = True
) -> str:
    """
    Get the regex search string from the search string

    Parameters
    ----------
    search_string : str
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

    search_string = escape_regex(search_string.lower())
    search_regex = apply_regex_rules(search_string)
    search_regex = f"^{search_regex}$" if not partial_match else f".*{search_regex}.*"

    if swap_words and len(search_string.split()) == 2:
        alt_regex = apply_regex_rules(" ".join(reversed(search_string.split())))
        alt_regex = f"^{alt_regex}$" if not partial_match else f".*{alt_regex}.*"
        search_regex = f"({search_regex})|({alt_regex})"

    return search_regex


def is_ranked_time(
    utc_datetime_now: datetime.utcnow().time(), ranked_length: int = 58
) -> bool:
    """
    Returns true if it is ranked time :
    Ranked time occurs at these timestamps :
    19:30 - 20:28 CET
    19:30 - 20:28 JST
    19:30 - 20:28 CST

    Parameters
    ----------
    utc_now : datetime, optional
        The current UTC time, by default datetime.utcnow()
    ranked_length : int, optional
        The length of ranked time in minutes, by default 58

    Returns
    -------
    bool
        If it is ranked time
    """

    cet_tz = timezone("CET")
    cst_tz = timezone("America/Chicago")
    jst_tz = timezone("Japan")

    cet_time = utc_datetime_now.astimezone(cet_tz).time()
    cst_time = utc_datetime_now.astimezone(cst_tz).time()
    jst_time = utc_datetime_now.astimezone(jst_tz).time()

    start_time = datetime(
        utc_datetime_now.year, utc_datetime_now.month, utc_datetime_now.day, 20, 30
    )
    end_time = start_time + timedelta(minutes=ranked_length)

    return (
        start_time.time() <= cet_time <= end_time.time()
        or start_time.time() <= cst_time <= end_time.time()
        or start_time.time() <= jst_time <= end_time.time()
    )


def format_song_types_to_integer(song_types: List[SongType]):
    """
    Format the song_types from the query to their integer mapping

    Parameters
    ----------
    song_types : List[SongType] : [opening, ending, insert]}
        The list of song types to format

    Returns
    -------
    list
        The list of formatted song types
    """

    song_type_mapping = {
        "opening": 1,
        "ending": 2,
        "insert": 3,
    }

    return [song_type_mapping[type] for type in song_types]


def format_song_types_to_string(song_type: int, song_number: int) -> str:
    """
    Format the song_types from the query to their string mapping

    Parameters
    ----------
    song_type : int
        The song type to format
    song_number : int
        The song number

    Returns
    -------
    str
        The formatted song type (Examples: Opening 1, Ending 3, Insert Song)
    """

    if song_type == 1:
        song_type = f"Opening {song_number}"
    elif song_type == 2:
        song_type = f"Ending {song_number}"
    elif song_type == 3:
        song_type = "Insert Song"

    return song_type


def format_artist_id(artist_database: Dict, artist_id: int) -> Dict:
    """
    Format the artist to the output format

    Parameters
    ----------
    artist_database : Dict
        The artist database
    artist_id : int
        The artist id

    Returns
    -------
    Dict
        The formatted artist
    """

    artist = artist_database.get(str(artist_id))

    if artist is None:
        return {}

    formatted_groups = []
    for group in artist.get("groups", []):
        group_names = artist_database.get(group["id"], {}).get("names", [])
        formatted_groups.append({"artist_id": int(group["id"]), "names": group_names})

    formatted_members = []
    line_ups = []
    for i, line_up in enumerate(artist["line_ups"]):
        for member in line_up.get("members", []):
            member_names = artist_database.get(member["id"], {}).get("names", [])
            formatted_members.append(
                {
                    "artist_id": int(member["id"]),
                    "names": member_names,
                    "line_up_id": int(member["line_up_id"]),
                }
            )
        line_ups.append({"line_up_id": i, "members": formatted_members})

    return {
        "artist_id": int(artist_id),
        "names": artist.get("names", []),
        "line_ups": line_ups if line_ups else None,
        "groups": formatted_groups if formatted_groups else None,
    }


def format_results(artist_database: Dict, songs: List[List[Any]]) -> Dict:
    """
    Format the song to the output format

    Parameters
    ----------
    artist_database : Dict
        The artist database
    song : List[Any]
        The song to format

    Returns
    -------
    Dict
        The formatted results
    """

    output_anime = []
    output_songs = []
    output_artists = []

    artist_ids = set()
    ann_ids = set()

    for song in songs:
        song_type = format_song_types_to_string(song[9], song[10])

        role_type_columns = {
            "vocalists": 15,
            "backing_vocalists": 17,
            "performers": 19,
            "composers": 21,
            "arrangers": 23,
        }

        role_type_artists = {}
        for role_type in role_type_columns:
            column = role_type_columns[role_type]
            role_type_artists[role_type] = []
            if not song[column]:
                continue

            for artist_id, artist_line_up_id in zip(
                song[column].split(","), song[column + 1].split(",")
            ):
                if artist_id not in artist_ids:
                    output_artists.append(format_artist_id(artist_database, artist_id))
                    artist_ids.add(artist_id)
                role_type_artists[role_type].append(
                    {"artist_id": int(artist_id), "line_up_id": int(artist_line_up_id)}
                )

        if song[0] not in ann_ids:
            output_anime.append(
                {
                    "ann_id": song[0],
                    "anime_jp_name": song[2] or song[1],
                    "anime_en_name": song[3] or song[1],
                    "anime_alt_names": song[4].split(r"\$") if song[4] else song[4],
                    "anime_season": song[5],
                    "anime_type": song[6],
                    "anime_genres": [],
                    "anime_tags": [],
                }
            )
            ann_ids.add(song[0])

        output_songs.append(
            {
                "ann_id": song[0],
                "ann_song_id": song[8],
                "song_type": song_type,
                "song_name": song[11],
                "song_artist": song[12],
                "song_difficulty": song[13],
                "song_category": song[14],
                "HQ": song[25],
                "MQ": song[26],
                "audio": song[27],
                "vocalists": role_type_artists["vocalists"],
                "backing_vocalists": role_type_artists["backing_vocalists"],
                "performers": role_type_artists["performers"],
                "composers": role_type_artists["composers"],
                "arrangers": role_type_artists["arrangers"],
            }
        )

    return {
        "anime": output_anime,
        "songs": output_songs,
        "artists": output_artists,
    }
