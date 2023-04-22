from __future__ import annotations
from enum import Enum
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException

"""
    A collection of classes used to validate the input and output of the API using pydantic, with the documentation that will be displayed on the documentation page
"""


class SongType(str, Enum):
    opening = "opening"
    ending = "ending"
    insert = "insert"


class SongCategory(str, Enum):
    Standard = "Standard"
    Chanting = "Chanting"
    Character = "Character"
    Instrumental = "Instrumental"


class CreditType(str, Enum):
    vocalist = "vocalist"
    backing_vocalist = "backing_vocalist"
    composer = "composer"
    arranger = "arranger"
    performer = "performer"


class AnimeType(str, Enum):
    TV = "TV"
    OVA = "OVA"
    movie = "movie"
    special = "special"
    ONA = "ONA"


class CombinationLogic(str, Enum):
    OR = "OR"
    AND = "AND"


class IntRange(BaseModel):
    min: Optional[int] = Field(0, ge=0, le=100)
    max: Optional[int] = Field(100, ge=0, le=100)

    @validator("max")
    def max_must_be_greater_than_min(cls, v, values):
        if v is not None and values["min"] is not None and v <= values["min"]:
            raise HTTPException(
                status_code=400,
                detail="song_difficulty_range.max must be strictly greater than song_difficulty_range.min",
            )
        return v


class SearchBase(BaseModel):
    ignore_duplicates: Optional[bool] = Field(
        default=False,
        description="""If **ignore_duplicates** is set to true, the search will ignore duplicate songs.<br>
        Two songs are considered duplicates if they have the same name and the same artist(s).""",
    )

    song_types: Optional[List[SongType]] = Field(
        default=[SongType.opening, SongType.ending, SongType.insert],
        description="""**song_types** is a list of string containing the song types to search for : opening, ending and insert<br>
        By default, every song type is included.""",
    )

    @validator("song_types")
    def song_types_must_be_valid(cls, v):
        if not v:
            raise HTTPException(
                status_code=400,
                detail="song_types list must contain at least one value of : opening, ending or insert",
            )
        return v

    song_categories: Optional[List[SongCategory]] = Field(
        default=[
            SongCategory.Standard,
            SongCategory.Chanting,
            SongCategory.Character,
            SongCategory.Instrumental,
        ],
        description="""**song_categories** is a list of string containing the song categories to search for : standard, chanting, character and instrumental<br>
        By default, every song category is included.<br>
        <b>*Song categories are not updated regularly.</b> See documentation for more details and latest update date.""",
    )

    @validator("song_categories")
    def song_categories_must_be_valid(cls, v):
        if not v:
            raise HTTPException(
                status_code=400,
                detail="song_categories must contain at least one value of : Standard, Chanting, Character or Instrumental",
            )
        return v

    song_difficulty_range: Optional[IntRange] = Field(
        default=IntRange(min=0, max=100),
        description="""**song_difficulty_range** is a dictionary containing the min and max range for the difficulty of the songs<br>
        Difficulty is a number between 0 and 100, which represent the guess rate on AMQ.<br>
        <b>*Song difficulty is not updated regularly.</b> See documentation for more details and latest update date.""",
    )


class SearchNonAnnIdBase(SearchBase):
    anime_types: Optional[List[AnimeType]] = Field(
        default=[
            AnimeType.TV,
            AnimeType.OVA,
            AnimeType.movie,
            AnimeType.special,
            AnimeType.ONA,
        ],
        description="""**anime_types** is a list of string containing the the anime types to search for : TV, OVA, movie, special and ONA<br>
        By default, every anime type is included.<br>
        <b>*Anime types are not updated regularly.</b> See documentation for more details and latest update date.""",
    )

    @validator("anime_types")
    def anime_types_must_be_valid(cls, v):
        if not v:
            raise HTTPException(
                status_code=400,
                detail="anime_types must contain at least one value of : TV, OVA, movie, special or ONA",
            )
        return v

    anime_seasons: Optional[List[str]] = Field(
        default=[],
        description="""**anime_seasons** is the list of seasons where the anime has been released.<br>
        If no seasons are specified, the search will return songs from any anime.<br>
        Seasons are defined as such : 'Season YYYY' (ex: 'Winter 2019').<br>
        <b>*Seasons are not updated regularly.</b> See documentation for more details and latest update date.""",
    )

    @validator("anime_seasons")
    def anime_seasons_must_be_valid(cls, v):
        for anime_season in v:
            release_season = anime_season.split(" ")
            if len(release_season) != 2:
                raise HTTPException(
                    status_code=400,
                    detail="anime_seasons must be in the format 'Season YYYY' (ex: 'Winter 2019').",
                )
            season, year = release_season
            if season not in ["Winter", "Spring", "Summer", "Fall"]:
                raise HTTPException(
                    status_code=400,
                    detail="anime_seasons must be in the format 'Season YYYY'. Season must be one of the following : Winter, Spring, Summer, Fall (ex: 'Winter 2019').",
                )
            if not year.isdigit() or int(year) < 1900 or int(year) > 2030:
                raise HTTPException(
                    status_code=400,
                    detail="anime_seasons must be in the format 'Season YYYY'. YYYY must be a number between 1900 and 2030 (ex: 'Winter 2019').",
                )
        return v

    anime_genres: Optional[List[str]] = Field(
        default=[],
        description="""**anime_genres** is the list of genres that need to be linked to the anime.<br>
        <b>*This parameter will have no effect as it is not yet implemented.</b><br>
        If no genres are specified, the search will return songs from any anime.<br>
        Genres on AMQ are taken from the Anilist genres.<br>
        <b>*Anime genres are not updated regularly.</b> See documentation for more details and latest update date.""",
    )
    anime_tags: Optional[List[str]] = Field(
        default=[],
        description="""**anime_tags** is the list of tags that need to be linked to the anime.<br>
        <b>*This parameter will have no effect as it is not yet implemented.</b><br>
        If no tags are specified, the search will return songs from any anime.<br>
        Tags on AMQ are taken from the Anilist tags.<br>
        <b>*Anime tags are not updated regularly.</b> See documentation for more details and latest update date.""",
    )


class SongSearchParams(SearchNonAnnIdBase):
    song_name: str = Field(
        description="""**song_name** is the string to search for in the song name.<br>
        It will be modified according to regex rules for special characters.""",
    )

    @validator("song_name")
    def song_name_must_be_valid(cls, v):
        if not v:
            raise HTTPException(
                status_code=400,
                detail="song_name must not be empty",
            )
        return v

    partial_match: Optional[bool] = Field(
        default=True,
        description="""If **partial_match** is set to true, the search will return songs with a name that contains the **song_name** string.<br>
        If false, the search will return songs with a name that is exactly the **song_name** string.""",
    )


class AnimeSearchParams(SearchNonAnnIdBase):
    anime_name: str = Field(
        description="""**anime_name** is the string to search for in the anime name.<br>
        It will be modified according to regex rules for special characters.""",
    )

    @validator("anime_name")
    def song_name_must_be_valid(cls, v):
        if not v:
            raise HTTPException(
                status_code=400,
                detail="anime_name must not be empty",
            )
        return v

    partial_match: Optional[bool] = Field(
        default=True,
        description="""If **partial_match** is set to true, the search will return songs with a name that contains the **anime_name** string.<br>
        If false, the search will return songs with a name that is exactly the **anime_name** string.""",
    )


class AnimeAnnIdSearchParams(SearchBase):
    ann_id: int = Field(
        ge=1,
        description="""**ann_id** is the ANN ID of the anime to search for.<br>
        This is the ID used on AnimeNewsNetwork.""",
    )


class ArtistSearchBase(SearchNonAnnIdBase):
    credit_types: Optional[List[CreditType]] = Field(
        default=[
            CreditType.vocalist,
            CreditType.backing_vocalist,
            CreditType.composer,
            CreditType.arranger,
            CreditType.performer,
        ],
        description="""**credit_types** is a list of credit types to search for : vocalist, backing_vocalist, composer, arranger and performer.<br>
        By default, every credit type is included.""",
    )

    @validator("credit_types")
    def credit_types_must_be_valid(cls, v):
        if not v:
            raise HTTPException(
                status_code=400,
                detail="credit_types list must contain at least one value of : vocalist, composer, arranger or performer",
            )
        return v

    group_granularity: Optional[int] = Field(
        default=0,
        ge=0,
        description="""**group_granularity is only useful for groups which have their members linked and are credited to vocals**<br>
        This is the granularity at which the group will be decomposed between its members.<br>
        By default, it is set to 0, which means the group will not be decomposed and only the group itself will be searched.<br>
        If set to **1**, it will search for the group and **each of its members**.<br>
        If set to **2**, it will search for the group, and every songs where at least **2 members** of the group are present.<br>
        etc...""",
    )
    max_other_artists: Optional[int] = Field(
        default=99,
        ge=0,
        description="""**max_other_artists is only useful for artists credited to vocals**<br>
        This is the maximum number of other artists different than the one searched, that can sing in the song.<br>
        By default, it is set to 99, which basically means it will not be taken into account.<br>
        If set to **0**, it will search for songs where the artist is the only one singing.<br>
        If set to **1**, it will search for songs where the artist is the only one singing, or where there is one single other artist singing alongside.<br>
        etc...""",
    )


class ArtistSearchParams(ArtistSearchBase):
    artist_name: str = Field(
        description="""**artist_name** is the string to search for in the artist name.<br>
        It will be modified according to regex rules for special characters.""",
    )

    @validator("artist_name")
    def song_name_must_be_valid(cls, v):
        if not v:
            raise HTTPException(
                status_code=400,
                detail="artist_name must not be empty",
            )
        return v

    partial_match: Optional[bool] = Field(
        default=True,
        description="""If **partial_match** is set to true, the search will return songs with a name that contains the **artist_name** string.<br>
        If false, the search will return songs with a name that is exactly the **artist_name** string.""",
    )


class ArtistIdSearchParams(ArtistSearchBase):
    artist_id: int = Field(
        ge=1,
        description="""**artist_id** contains the ID of the artist to search for.<br>
        This is the ID used on my database.""",
    )


class GlobalSearch(BaseModel):
    anime_searches: Optional[List[AnimeSearchParams]] = Field(
        default=[],
        description="""**anime_searches** is a list of searches similar to the anime_search endpoint.<br>
        If no anime names are specified, the search will return songs from any anime.""",
    )
    song_name_searches: Optional[List[SongSearchParams]] = Field(
        default=[],
        description="""**song_name_searches** is a list of searches similar to the song_name_search endpoint.<br>
        If no song names are specified, the search will return songs with any song name.""",
    )
    artist_searches: Optional[List[ArtistSearchParams]] = Field(
        default=[],
        description="""**artist_searches** is a list of searches similar to the artist_search endpoint.<br>
        If no artists are specified, the search will return songs from any artist.""",
    )

    combination_logic: Optional[CombinationLogic] = Field(
        default=CombinationLogic.OR,
        description="""**combination_logic** is the logic to use to combine the results of the different searches.<br>
        By default, it is set to OR, which means that the results will be the union of all the searches.<br>
        If set to AND, it will return the intersection of all the searches.""",
    )

    class Config:
        schema_extra = {
            "example": {
                "anime_searches": [
                    {
                        "ignore_duplicates": True,
                        "anime_name": "Gundam Unicorn",
                        "partial_match": True,
                    }
                ],
                "artist_searches": [
                    {
                        "ignore_duplicates": True,
                        "credit_types": ["vocalist", "backing_vocalist"],
                        "group_granularity": 0,
                        "max_other_artists": 99,
                        "artist_name": "Aimer",
                        "partial_match": True,
                    },
                    {
                        "ignore_duplicates": True,
                        "credit_types": ["composer", "arranger"],
                        "artist_name": "Hiroyuki Sawano",
                        "partial_match": True,
                    },
                ],
                "combination_logic": "AND",
            }
        }


class Artist(BaseModel):
    artist_id: int = Field(
        description="**artist_id** is the ID of the artist on my database."
    )
    names: List[str] = Field(
        description="**names** is a list of all the names of the artist."
    )
    groups: Optional[List[Artist]] = Field(
        description="**groups** is a list of all the groups the artist is or has been part of if they have been in any."
    )
    line_ups: Optional[List[LineUp]] = Field(
        description="**line_ups** is a list of all the line ups that are linked to this group."
    )


class LineUp(BaseModel):
    line_up_id: int = Field(
        description="**line_up_id** is the ID of the line up on my database."
    )
    members: List[Artist] = Field(
        description="**members** is a list of all the members that are part of the line up."
    )


class ArtistSong(BaseModel):
    artist_id: int = Field(
        description="**artist_id** is the ID of the artist on my database."
    )
    line_up_id: Optional[int] = Field(
        default=-1,
        description="**line_up_id** is the ID of the line up on my database.",
    )


Artist.update_forward_refs()
LineUp.update_forward_refs()


class AnimeEntry(BaseModel):
    ann_id: int = Field(
        description="**ann_id** is the ID of the song on the Anime News Network database."
    )
    anime_en_name: str = Field(
        description="""**anime_en_name** is the Japanese name of the anime the song is from.<br>
        <b>*anime_en_name is not updated regularly, it default to the name in Expand Library when not available.</b> See documentation for more details and latest update date."""
    )
    anime_jp_name: str = Field(
        description="""**anime_jp_name** is the Japanese name of the anime the song is from.<br>
        <b>*anime_jp_name is not updated regularly.</b> See documentation for more details and latest update date."""
    )
    anime_alt_names: Optional[List[str]] = Field(
        default=[],
        description="""**anime_alt_names** is a list of any other names on AMQ for the anime the song is from.<br>
        <b>*anime_alt_names are not updated regularly.</b> See documentation for more details and latest update date.""",
    )
    anime_season: Optional[str] = Field(
        description="""**anime_season** is the season of the anime the song is from.<br>
        <b>*anime_season is not updated regularly.</b> See documentation for more details and latest update date."""
    )
    anime_type: Optional[str] = Field(
        description="""**anime_type** is the type of the anime (TV, OVA, movie, special, ONA).<br>
        <b>*anime_type is not updated regularly.</b> See documentation for more details and latest update date."""
    )
    anime_genres: Optional[List[str]] = Field(
        default=[],
        description="""**anime_genres** is a list of genres for the anime the song is from.<br>
        <b>*This parameter will have no effect as it is not yet implemented.</b><br>
        <b>*anime_genres are not updated regularly.</b> See documentation for more details and latest update date.""",
    )
    anime_tags: Optional[List[str]] = Field(
        default=[],
        description="""**anime_tags** is a list of tags for the anime the song is from.<br>
        <b>*This parameter will have no effect as it is not yet implemented.</b><br>
        <b>*anime_tags are not updated regularly.</b> See documentation for more details and latest update date.""",
    )


class SongEntry(BaseModel):
    ann_id: int = Field(
        description="**ann_id** is the ID of the song on the Anime News Network database."
    )
    ann_song_id: int = Field(
        description="""**ann_song_id** is the ID of the song on AMQ. Don't ask me why Egerod called it that way.<br>
        <b>*ann_song_id is not available for songs fully uploaded and not in Expand Library. Default to -1 for those.</b>"""
    )
    song_type: str = Field(
        description="**song_type** is the type of the song (Opening 2, Ending 5, Insert Song, etc)."
    )
    song_name: str = Field(description="**song_name** is the name of the song.")
    song_artist: str = Field(
        description="**song_artist** is the name of the artist singing the song."
    )
    song_difficulty: Optional[float] = Field(
        description="""**song_difficulty** is the difficulty of the song.<br>
        <b>*song_difficulty is not updated regularly.</b> See documentation for more details and latest update date."""
    )
    song_category: Optional[SongCategory] = Field(
        description="""**song_category** is the difficulty of the song.<br>
        <b>*song_category is not updated regularly.</b> See documentation for more details and latest update date."""
    )
    HQ: Optional[str] = Field(
        description="**HQ** is the 720p webm of the song if available."
    )
    MQ: Optional[str] = Field(
        description="**MQ** is the 480p webm of the song if available."
    )
    audio: Optional[str] = Field(
        description="**audio** is the mp3 of the song if available."
    )
    vocalists: Optional[List[ArtistSong]] = Field(
        description="**vocalists** is the list of Tuple [artist_id, line_up_id] singing in the song."
    )
    backing_vocalists: Optional[List[ArtistSong]] = Field(
        description="**backing_vocalists** is the list of Tuple [artists, line_up_id] backing the lead singers in the song. They usually sing along during chorus or do adlibs. WIP."
    )
    performers: Optional[List[ArtistSong]] = Field(
        description="**performers** is the list of notorious Tuple [artists, line_up_id] performing an instrument in the song. WIP."
    )
    composers: Optional[List[ArtistSong]] = Field(
        description="**composers** is the list of Tuple [artists, line_up_id] who composed the song. WIP."
    )
    arrangers: Optional[List[ArtistSong]] = Field(
        description="**arrangers** is the list of Tuple [artists, line_up_id] who arranged the song. WIP."
    )


class Results(BaseModel):
    songs: List[SongEntry] = Field(
        description="**songs** is a list of all the songs that match the search."
    )
    anime: List[AnimeEntry] = Field(
        description="**anime** is a list of all the anime from which the songs results are."
    )
    artists: List[Artist] = Field(
        description="**artists** is a list of all the artists credited in the songs results."
    )
