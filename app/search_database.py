import utils
import sql_calls
from io_classes import *

import re
from typing import Any, List, Set, Tuple, Dict

"""
    This file contains the functions to search the database
"""


def get_member_list_flat(
    artist_database: Dict,
    credit_types: List[CreditType],
    artists: Dict,
    bottom: bool = True,
) -> List[int]:
    """
    get a list of all the members of a group and its subgroups

    Parameters
    ----------
    artist_database : Dict
        The artist database
    credit_type : List[CreditType]
        The credit type of the members that we whould keep
    artists : Dict
        The list of artists and their line up
    bottom : bool, optional
        If True, will skip subgroups and go directly to the lower tier possible, by default True

    Returns
    -------
    List[int]
        The list of all the members of the group and its subgroups
    """

    member_list = set()

    for artist in artists:
        if int(artist["line_up_id"]) == -1:
            member_list.add(artist["id"])

        else:
            if not bottom:
                member_list.add(artist["id"])

            line_up = artist_database[artist["id"]]["line_ups"][
                int(artist["line_up_id"])
            ]
            members = [
                member
                for member in line_up["members"]
                if member["role_type"] in credit_types
            ]

            for member in get_member_list_flat(
                artist_database,
                credit_types,
                members,
                bottom=bottom,
            ):
                member_list.add(member)

    return list(member_list)


def compare_two_artist_list(list1: List[int], list2: List[int]) -> Tuple[int, int]:
    """
    Compare two lists of artists

    Parameters
    ----------
    list1 : List[int]
        The first list of artists
    list2 : List[int]
        The second list of artists

    Returns
    -------
    Tuple[int, int]
        The amount of people present in both lists and the amount of people in list1 that are not in list2
    """

    same_count = 0  # amount of people present in both
    add_count = 0  # additional people in list1 compared to list2

    for artist in list1:
        if artist not in list2:
            add_count += 1
        else:
            same_count += 1

    return same_count, add_count


def check_meets_artists_requirements(
    artist_database: Dict,
    song: List[Any],
    credit_types: List[CreditType],
    artist_ids: List[int],
    group_granularity: int,
    max_other_artists: int,
) -> bool:
    """
    Check if a song meets the artist requirements

    Parameters
    ----------
    artist_database : Dict
        The artist database
    song : List[Any]
        The song to check
    credit_types : List[CreditType]
        The credit type of the members that we should keep
    artist_ids : List[int]
        The list of artist IDs to check
    group_granularity : int
        The group granularity
    max_other_artists : int
        The maximum number of other artists

    Returns
    -------
    bool
        If the song meets the artist requirements
    """

    song_artists = (
        [
            {"id": artist, "line_up_id": int(line_up)}
            for artist, line_up in zip(song[15].split(","), song[16].split(","))
        ]
        if song[15]
        else []
    )
    song_artists_flat = get_member_list_flat(
        artist_database, credit_types, song_artists
    )

    song_performers = (
        [
            {"id": artist, "line_up_id": int(line_up)}
            for artist, line_up in zip(song[17].split(","), song[18].split(","))
        ]
        if song[17]
        else []
    )

    song_composers = (
        [
            {"id": artist, "line_up_id": int(line_up)}
            for artist, line_up in zip(song[19].split(","), song[20].split(","))
        ]
        if song[19]
        else []
    )

    song_arrangers = (
        [
            {"id": artist, "line_up_id": int(line_up)}
            for artist, line_up in zip(song[21].split(","), song[22].split(","))
        ]
        if song[21]
        else []
    )

    support_artists = get_member_list_flat(
        artist_database,
        credit_types,
        song_performers + song_composers + song_arrangers,
        bottom=False,
    )

    for artist_id in artist_ids:
        if artist_id in support_artists:
            return True

        line_ups = [[{"id": str(artist_id), "line_up_id": -1}]]
        if artist_database[str(artist_id)]["line_ups"]:
            line_ups = artist_database[str(artist_id)]["line_ups"]

        for line_up in line_ups:
            if "members" in line_up:
                line_up = line_up["members"]
            checked_list = get_member_list_flat(artist_database, credit_types, line_up)
            present_artist, additional_artist = compare_two_artist_list(
                song_artists_flat, checked_list
            )

            if (
                present_artist >= 1
                and additional_artist <= max_other_artists
                and present_artist >= min(group_granularity, len(line_up))
            ):
                return True

    return False


def expand_artist_ids(
    artist_database: Dict,
    credit_types: List[CreditType],
    artist_ids: List[str],
    group_granularity: int,
) -> Set[int]:
    """
    Expand artist ids to include groups and line ups

    Parameters
    ----------
    artist_database : Dict
        Artist database
    credit_types : List[CreditType]
        Authorized credit type, ignore any relation that is not of these type
    artist_ids : List[str]
        List of artist ids to expand
    group_granularity : int
        Group granularity

    Returns
    -------
    Set[int]
        Set of expanded artist ids
    """

    expanded_ids = set()

    for artist_id in artist_ids:
        artist = artist_database.get(str(artist_id), None)

        if artist is None:
            raise ValueError(f"Artist with id {artist_id} not found in database")

        expanded_ids.add(artist_id)

        for group in artist.get("groups", []):
            expanded_ids.add(group["id"])

        if group_granularity > 0:
            for line_up in artist.get("line_ups", []):
                for member in get_member_list_flat(
                    artist_database, credit_types, line_up["members"], bottom=False
                ):
                    expanded_ids.add(member)

    return expanded_ids


def get_artists_ids_songs_list(
    artist_ids: List[str],
    max_other_artists: int,
    group_granularity: int,
    credit_types: List[CreditType],
    ignore_duplicates: bool,
    song_types: List[int],
    song_categories: List[SongCategory],
    song_difficulty_range: IntRange,
    anime_types: List[AnimeType],
    anime_seasons: List[str],
    anime_genres: List[str],
    anime_tags: List[str],
) -> List[SongEntry]:
    """
    Get the list of songs from a list of artist ids

    Parameters
    ----------
    artist_ids : List[str]
        List of artist ids
    max_other_artists : int
        Maximum number of other artists that can sings along the searched artists
    group_granularity : int
        Granularity of the group search
    credit_types : List[CreditType] ['vocalists', 'backing-vocalists', 'composers', 'arrangers', 'performers']
        List of credit types to search
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

    Returns
    -------
    List[SongEntry]
        List of songs fitting the search
    """

    cursor = sql_calls.connect_to_database()

    artist_database = sql_calls.extract_artist_database()

    for artist_id in artist_ids:
        if str(artist_id) not in artist_database:
            artist_ids.pop(artist_ids.index(artist_id))

    if not artist_ids:
        return []

    expanded_ids = expand_artist_ids(
        artist_database, credit_types, artist_ids, group_granularity
    )

    song_ids = sql_calls.get_songs_ids_from_artist_ids(
        cursor, expanded_ids, credit_types
    )

    possible_songs = sql_calls.get_possibles_songs_from_filters(
        cursor,
        song_ids=song_ids,
        ignore_duplicates=ignore_duplicates,
        song_types=song_types,
        song_categories=song_categories,
        song_difficulty_range=song_difficulty_range,
        anime_types=anime_types,
        anime_seasons=anime_seasons,
        anime_genres=anime_genres,
        anime_tags=anime_tags,
    )

    filtered_songs = [
        song
        for song in possible_songs
        if check_meets_artists_requirements(
            artist_database,
            song,
            credit_types,
            artist_ids,
            group_granularity,
            max_other_artists,
        )
    ]

    return utils.format_results(artist_database, filtered_songs)


def get_artists_search_songs_list(
    artist_name: str,
    partial_match: bool,
    max_other_artists: int,
    group_granularity: int,
    credit_types: List[CreditType],
    ignore_duplicates: bool,
    song_types: List[int],
    song_categories: List[SongCategory],
    song_difficulty_range: IntRange,
    anime_types: List[AnimeType],
    anime_seasons: List[str],
    anime_genres: List[str],
    anime_tags: List[str],
) -> List[SongEntry]:
    """
    artist_name : str
        Name of the artist to search
    partial_match : bool
        If true, keep partial matches
    max_other_artists : int
        Maximum number of other artists that can sings along the searched artists
    group_granularity : int
        Granularity of the group search
    credit_types : List[CreditType] ['vocalists', 'backing-vocalists', 'composers', 'arrangers', 'performers']
        List of credit types to search
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

    Returns
    -------
    List[SongEntry]
        List of songs fitting the search
    """

    cursor = sql_calls.connect_to_database()

    artist_search = utils.get_regex_search(artist_name, partial_match, swap_words=True)

    artist_ids = sql_calls.get_artist_ids_from_regex(cursor, artist_search)
    artist_ids = [str(artist_id) for artist_id in artist_ids]

    return get_artists_ids_songs_list(
        artist_ids,
        max_other_artists,
        group_granularity,
        credit_types,
        ignore_duplicates,
        song_types,
        song_categories,
        song_difficulty_range,
        anime_types,
        anime_seasons,
        anime_genres,
        anime_tags,
    )


def get_ann_ids_songs_list(
    ann_ids: List[int],
    ignore_duplicates: bool,
    song_types: List[int],
    song_categories: List[SongCategory],
    song_difficulty_range: IntRange,
    max_results_per_search: int,
) -> List[SongEntry]:
    """
    Get the song list from an ann_id

    Parameters
    ----------
    ignore_duplicates : bool
        Ignore duplicate songs
    song_types : list[int]
        List of authorized song types (opening:1, ending:2, insert:3)
    song_categories : List[SongCategory] ['Standard', 'Chanting', 'Character', 'Instrumental']
        List of song categories to search
    song_difficulty_range : IntRange {min: int, max: int}
        Range of difficulty to search
    max_results_per_search : int
        Maximum number of results per search

    Returns
    -------
    List[SongEntry]
        List of songs fitting the search
    """

    cursor = sql_calls.connect_to_database()

    artist_database = sql_calls.extract_artist_database()

    songs = sql_calls.get_possibles_songs_from_filters(
        cursor,
        ann_ids=ann_ids,
        ignore_duplicates=ignore_duplicates,
        song_types=song_types,
        song_categories=song_categories,
        song_difficulty_range=song_difficulty_range,
        max_results_per_search=max_results_per_search,
    )

    return utils.format_results(artist_database, songs)


def get_anime_search_songs_list(
    anime_name,
    partial_match,
    ignore_duplicates: bool,
    song_types: List[int],
    song_categories: List[SongCategory],
    song_difficulty_range: IntRange,
    anime_types: List[AnimeType],
    anime_seasons: List[str],
    anime_genres: List[str],
    anime_tags: List[str],
    max_results_per_search,
) -> List[SongEntry]:
    """
    Get the song list from the anime name search

    Parameters
    ----------
    anime_name : str
        Name of the anime to search
    partial_match : bool
        If true, keep partial matches
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
        Maximum number of results per search

    Returns
    -------
    List[SongEntry]
        List of songs fitting the search
    """

    artist_database = sql_calls.extract_artist_database()
    cursor = sql_calls.connect_to_database()

    get_possible_songs = sql_calls.get_possibles_songs_from_filters(
        cursor,
        ignore_duplicates=ignore_duplicates,
        song_types=song_types,
        song_categories=song_categories,
        song_difficulty_range=song_difficulty_range,
        anime_types=anime_types,
        anime_seasons=anime_seasons,
        anime_genres=anime_genres,
        anime_tags=anime_tags,
    )

    anime_search = utils.get_regex_search(anime_name, partial_match, swap_words=False)

    output_songs = []
    for song in get_possible_songs:
        names = {song[1], song[2], song[3]}.union(
            song[4].split("\$") if song[4] else []
        )

        if any(re.match(anime_search, name.lower()) for name in names if name):
            output_songs.append(song)

    return utils.format_results(artist_database, output_songs)


def get_song_name_search_songs_list(
    song_name: str,
    partial_match: bool,
    ignore_duplicates: bool,
    song_types: List[int],
    song_categories: List[SongCategory],
    song_difficulty_range: IntRange,
    anime_types: List[AnimeType],
    anime_seasons: List[str],
    anime_genres: List[str],
    anime_tags: List[str],
    max_results_per_search: int,
) -> List[SongEntry]:
    """
    Get the song list from the song name search

    Parameters
    ----------
    song_name : str
        Name of the song to search
    partial_match : bool
        If true, keep partial matches
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
        Maximum number of results per search

    Returns
    -------
    List[SongEntry]
        List of songs fitting the search
    """

    artist_database = sql_calls.extract_artist_database()
    song_name_regex = utils.get_regex_search(song_name, partial_match)

    cursor = sql_calls.connect_to_database()

    songs = sql_calls.get_possibles_songs_from_filters(
        cursor,
        song_name_regex=song_name_regex,
        ignore_duplicates=ignore_duplicates,
        song_types=song_types,
        song_categories=song_categories,
        song_difficulty_range=song_difficulty_range,
        anime_types=anime_types,
        anime_seasons=anime_seasons,
        anime_genres=anime_genres,
        anime_tags=anime_tags,
        max_results_per_search=max_results_per_search,
    )

    return utils.format_results(artist_database, songs)


def hashable_dict(to_make_hashable_dict: Dict) -> Tuple:
    """
    Convert a dictionary to a hashable tuple of its key-value pairs,
    with any nested dictionaries or lists converted to hashable tuples recursively.

    Parameters
    ----------
    to_make_hashable_dict : Dict
        The dictionary to convert

    Returns
    -------
    Tuple
        The hashable tuples of key-value pairs
    """
    if not isinstance(to_make_hashable_dict, dict):
        return to_make_hashable_dict
    items = []
    for key, value in to_make_hashable_dict.items():
        if isinstance(value, dict):
            items.append((key, hashable_dict(value)))
        elif isinstance(value, list):
            items.append((key, tuple(hashable_dict(x) for x in value)))
        else:
            items.append((key, value))
    return tuple(sorted(items))


def combine_results(
    results: List[List[SongEntry]], combination_logic: CombinationLogic
) -> List[SongEntry]:
    """
    Combine the results of the different searches

    Parameters
    ----------
    results : List[List[SongEntry]]
        List of results from the different searches
    combination_logic : CombinationLogic | ENUM : AND or OR
        Logic to combine the searches

    Returns
    -------
    List[SongEntry]
        List of songs fitting the search
    """

    if combination_logic == "AND":
        # Convert each dictionary to a hashable tuple of its key-value pairs
        sets = [set(hashable_dict(d) for d in r) for r in results]
        # Take the intersection of the sets
        intersection = set.intersection(*sets)
        # Convert each tuple back to a dictionary
        return [dict(t) for t in intersection]
    elif combination_logic == "OR":
        # Convert each dictionary to a hashable tuple of its key-value pairs
        sets = [set(hashable_dict(d) for d in r) for r in results]
        # Take the union of the sets
        union = set.union(*sets)
        # Convert each tuple back to a dictionary
        return [dict(t) for t in union]


def get_global_search_songs_list(
    anime_searches: List[AnimeSearchParams],
    song_name_searches: List[SongSearchParams],
    artist_searches: List[ArtistSearchParams],
    combination_logic: CombinationLogic,
) -> List[SongEntry]:
    """
    Get the song list from the global search

    Parameters
    ----------
    anime_searches : List[AnimeSearchParams]
        List of anime searches
    song_name_searches : List[SongSearchParams]
        List of song name searches
    artist_searches : List[ArtistSearchParams]
        List of artist searches
    combination_logic : CombinationLogic | ENUM : AND or OR
        Logic to combine the searches

    Returns
    -------
    List[SongEntry]
        List of songs fitting the search
    """

    results = []

    for anime_search in anime_searches:
        anime_search.song_types = utils.format_song_types_to_integer(
            anime_search.song_types
        )
        results.append(get_anime_search_songs_list(**dict(anime_search)))

    for song_name_search in song_name_searches:
        song_name_search.song_types = utils.format_song_types_to_integer(
            song_name_search.song_types
        )
        results.append(get_song_name_search_songs_list(**dict(song_name_search)))

    for artist_search in artist_searches:
        artist_search.song_types = utils.format_song_types_to_integer(
            artist_search.song_types
        )
        results.append(get_artists_search_songs_list(**dict(artist_search)))

    return combine_results(results, combination_logic)
