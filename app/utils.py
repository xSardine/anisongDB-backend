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


def format_song(artist_database, song):

    if song[9] == 1:
        type = "Opening " + str(song[10])
    elif song[9] == 2:
        type = "Ending " + str(song[10])
    else:
        type = "Insert Song"

    artists = []

    if song[15]:
        for artist_id, line_up in zip(song[15].split(","), song[16].split(",")):

            line_up = int(line_up)

            current_artist = {
                "id": artist_id,
                "names": artist_database[str(artist_id)]["names"],
                "line_up_id": line_up,
            }

            if (
                artist_database[str(artist_id)]["line_ups"]
                and len(artist_database[str(artist_id)]["line_ups"]) >= line_up
            ):
                current_artist["line_ups"] = []
                for member in artist_database[str(artist_id)]["line_ups"][line_up][
                    "members"
                ]:
                    current_artist["line_ups"].append(
                        {
                            "id": member["id"],
                            "names": artist_database[str(member["id"])]["names"],
                        }
                    )

            if artist_database[str(artist_id)]["groups"]:
                current_artist["groups"] = []
                added_group = set()
                for group in artist_database[str(artist_id)]["groups"]:
                    if group["id"] in added_group:
                        continue
                    added_group.add(group["id"])
                    current_artist["groups"].append(
                        {
                            "id": group["id"],
                            "names": artist_database[str(group["id"])]["names"],
                        }
                    )

            artists.append(current_artist)

    performers = []
    if song[17]:
        for performer_id in song[17].split(","):
            performers.append(
                {
                    "id": performer_id,
                    "names": artist_database[str(performer_id)]["names"],
                }
            )

    composers = []
    if song[19]:
        for composer_id in song[19].split(","):
            composers.append(
                {"id": composer_id, "names": artist_database[str(composer_id)]["names"]}
            )

    arrangers = []
    if song[21]:
        for arranger_id in song[21].split(","):
            arrangers.append(
                {"id": arranger_id, "names": artist_database[str(arranger_id)]["names"]}
            )

    songinfo = {
        "annId": song[0],
        "annSongId": song[8],
        "animeJPName": song[2] if song[2] else song[1],
        "animeENName": song[3] if song[3] else song[1],
        "animeAltName": song[4].split("\$") if song[4] else song[4],
        "animeVintage": song[5],
        "animeType": song[6],
        "songType": type,
        "songName": song[11],
        "songArtist": song[12],
        "songDifficulty": song[17],
        "songCategory": song[18],
        "HQ": song[22],
        "MQ": song[23],
        "audio": song[24],
        "artists": artists,
        "performers": performers,
        "composers": composers,
        "arrangers": arrangers,
    }

    return songinfo
