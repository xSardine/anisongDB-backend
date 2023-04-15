from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import get_search_result
import sql_calls, utils
from random import randrange


class Search_Filter(BaseModel):

    search: str
    partial_match: Optional[bool] = True

    # How much I decompose the group to search for other songs
    # ie. 1: Artists one by one 2: At least two member from the group, etc...
    group_granularity: Optional[int] = Field(2, ge=0)
    # Once I've confirmed group_granularity requirement is met
    # How much other artists that are not from the og group do I accept
    max_other_artist: Optional[int] = Field(2, ge=0)

    # for composer search
    arrangement: Optional[bool] = True

    class Config:
        # This will search for every fripSide song, as well as every Yoshino Nanjo song with not more than 2 other artists
        schema_extra = {
            "example": {
                "search": "fripSide",
                "partial_match": True,
                "group_granularity": 1,
                "max_other_artist": 2,
            }
        }


class Search_Request(BaseModel):

    anime_search_filter: Optional[Search_Filter] = []
    song_name_search_filter: Optional[Search_Filter] = []
    artist_search_filter: Optional[Search_Filter] = []
    composer_search_filter: Optional[Search_Filter] = []
    and_logic: Optional[bool] = True
    ignore_duplicate: Optional[bool] = False
    opening_filter: Optional[bool] = True
    ending_filter: Optional[bool] = True
    insert_filter: Optional[bool] = True

    class Config:
        schema_extra = {
            "example": {
                "anime_search_filter": {
                    "search": "White Album",
                    "ignore_special_character": True,
                    "partial_match": True,
                    "max_artist_per_songs": 99,
                },
                "artist_search_filter": {
                    "search": "Madoka Yonezawa",
                    "ignore_special_character": True,
                    "partial_match": True,
                    "max_artist_per_songs": 99,
                },
            }
        }


class Artist_ID_Search_Request(BaseModel):

    artist_ids: List[int] = []
    group_granularity: Optional[int] = Field(2, ge=0)
    max_other_artist: Optional[int] = Field(2, ge=0)
    ignore_duplicate: Optional[bool] = False
    opening_filter: Optional[bool] = True
    ending_filter: Optional[bool] = True
    insert_filter: Optional[bool] = True


class Composer_ID_Search_Request(BaseModel):

    composer_ids: List[int] = []
    arrangement: Optional[bool] = True
    ignore_duplicate: Optional[bool] = False
    opening_filter: Optional[bool] = True
    ending_filter: Optional[bool] = True
    insert_filter: Optional[bool] = True


class annId_Search_Request(BaseModel):

    annId: int
    ignore_duplicate: Optional[bool] = False
    opening_filter: Optional[bool] = True
    ending_filter: Optional[bool] = True
    insert_filter: Optional[bool] = True


class artist(BaseModel):

    id: int
    names: List[str]
    line_up_id: Optional[int]
    groups: Optional[List[artist]]
    members: Optional[List[artist]]


artist.update_forward_refs()


class Song_Entry(BaseModel):

    annId: int
    annSongId: int
    animeENName: str
    animeJPName: str
    animeAltName: Optional[List[str]]
    animeVintage: Optional[str]
    animeType: Optional[str]
    songType: str
    songName: str
    songArtist: str
    songDifficulty: Optional[float]
    songCategory: Optional[str]
    HQ: Optional[str]
    MQ: Optional[str]
    audio: Optional[str]
    artists: List[artist]
    composers: List[artist]
    arrangers: List[artist]


# Launch API
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def format_artist_ids(artist_database, artist_id, artist_line_up=-1):

    artist = artist_database[str(artist_id)]

    formatted_artist = {
        "id": artist_id,
        "names": artist["names"],
    }

    if artist_line_up != -1:
        formatted_artist["line_up_id"] = artist_line_up

    if artist["groups"]:
        formatted_group_list = []
        for group_id, group_line_up_id in artist["groups"]:
            current_group = {
                "id": group_id,
                "names": artist_database[str(group_id)]["names"],
            }
            if group_line_up_id != -1:
                current_group["line_up_id"] = group_line_up_id
            formatted_group_list.append(current_group)
        formatted_artist["groups"] = formatted_group_list

    if artist_line_up != -1 and artist["members"]:
        formatted_member_list = []
        for member_id, member_line_up_id in artist["members"][artist_line_up]:
            current_member = {
                "id": member_id,
                "names": artist_database[str(member_id)]["names"],
            }
            if member_line_up_id:
                current_member["line_up_id"] = member_line_up_id
            formatted_member_list.append(current_member)
        formatted_artist["members"] = formatted_member_list

    return formatted_artist


def format_composer_ids(artist_database, composer_id):
    composer = {"id": composer_id}

    composer["names"] = artist_database[str(composer_id)]["names"]

    return composer


def format_arranger_ids(artist_database, arranger_id):
    arranger = {"id": arranger_id}
    arranger["names"] = artist_database[str(arranger_id)]["names"]

    return arranger


@app.post("/api/search_request", response_model=List[Song_Entry])
async def search_request(query: Search_Request):

    authorized_type = []
    if query.opening_filter:
        authorized_type.append(1)
    if query.ending_filter:
        authorized_type.append(2)
    if query.insert_filter:
        authorized_type.append(3)

    if not authorized_type:
        return []

    song_list = get_search_result.get_search_results(
        query.anime_search_filter,
        query.song_name_search_filter,
        query.artist_search_filter,
        query.composer_search_filter,
        query.and_logic,
        query.ignore_duplicate,
        300,
        authorized_type,
    )

    return song_list


@app.post("/api/get_50_random_songs", response_model=List[Song_Entry])
async def get_50_random_songs():

    cursor = sql_calls.connect_to_database(sql_calls.database_path)

    songIds = [randrange(28000) for i in range(50)]

    artist_database = sql_calls.extract_artist_database()

    # Extract every song from song IDs
    get_songs_from_songs_ids = (
        f"SELECT * from songsFull WHERE songId IN ({','.join('?'*len(songIds))})"
    )
    songs = sql_calls.run_sql_command(cursor, get_songs_from_songs_ids, songIds)

    song_list = [utils.format_song(artist_database, song) for song in songs]

    return song_list


@app.post("/api/artist_ids_request", response_model=List[Song_Entry])
async def search_request(query: Artist_ID_Search_Request):

    authorized_type = []
    if query.opening_filter:
        authorized_type.append(1)
    if query.ending_filter:
        authorized_type.append(2)
    if query.insert_filter:
        authorized_type.append(3)

    if not authorized_type:
        return []

    song_list = get_search_result.get_artists_ids_song_list(
        query.artist_ids,
        query.max_other_artist,
        query.group_granularity,
        query.ignore_duplicate,
        authorized_type,
    )

    return song_list


@app.post("/api/composer_ids_request", response_model=List[Song_Entry])
async def search_request(query: Composer_ID_Search_Request):

    authorized_type = []
    if query.opening_filter:
        authorized_type.append(1)
    if query.ending_filter:
        authorized_type.append(2)
    if query.insert_filter:
        authorized_type.append(3)

    if not authorized_type:
        return []

    song_list = get_search_result.get_composer_ids_song_list(
        query.composer_ids,
        query.arrangement,
        query.ignore_duplicate,
        authorized_type,
    )

    return song_list


@app.post("/api/annId_request", response_model=List[Song_Entry])
async def search_request(query: annId_Search_Request):

    authorized_type = []
    if query.opening_filter:
        authorized_type.append(1)
    if query.ending_filter:
        authorized_type.append(2)
    if query.insert_filter:
        authorized_type.append(3)

    if not authorized_type:
        return []

    song_list = get_search_result.get_annId_song_list(
        query.annId,
        query.ignore_duplicate,
        authorized_type,
    )

    return song_list
