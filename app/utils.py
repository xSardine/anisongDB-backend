from .io_classes import SongType

import re
from datetime import datetime
from typing import Any, List, Dict

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
        "replace": "( ?[²³⁵★☆♥♡\\/\\*✻✳︎＊'ˈ\\-∽~〜・·\\.,;:!?@_-⇔→≒=\\+†×±◎Ө♪♣␣∞] ?| )",
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
    str = str.replace(r"\ ", " ")
    str = str.replace(r"\*", "*")
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


def is_ranked_time() -> bool:
    """
    Returns true if it is ranked time

    Returns
    -------
    bool
        If it is ranked time
    """

    return False

    date = datetime.utcnow()
    # If ranked time UTC
    if (
        # CST
        (
            (date.hour == 1 and date.minute >= 30)
            or (date.hour == 2 and date.minute < 28)
        )
        # JST
        or (
            (date.hour == 11 and date.minute >= 30)
            or (date.hour == 12 and date.minute < 28)
        )
        # CET
        or (
            (date.hour == 18 and date.minute >= 30)
            or (date.hour == 19 and date.minute < 28)
        )
    ):
        return True
    return False


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
