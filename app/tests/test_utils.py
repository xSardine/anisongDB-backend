from ..utils import format_song_types_to_integer, format_song_types_to_string
from ..io_classes import SongType


# Test formatting from the database to the output format
class TestFormatResults:
    def test_format_song_types_to_integer_1(self):
        song_types = [SongType.opening, SongType.ending, SongType.insert]
        song_types = format_song_types_to_integer(song_types)
        assert song_types == [1, 2, 3]

    def test_format_song_types_to_integer_2(self):
        song_types = [SongType.ending]
        song_types = format_song_types_to_integer(song_types)
        assert song_types == [2]

    def test_format_song_types_to_string_1(self):
        song_type = format_song_types_to_string(1, 1)
        assert song_type == "Opening 1"

    def test_format_song_types_to_string_2(self):
        song_type = format_song_types_to_string(2, 3)
        assert song_type == "Ending 3"

    def test_format_song_types_to_string_3(self):
        song_type = format_song_types_to_string(3, 0)
        assert song_type == "Insert Song"

    def test_format_song_types_to_string_4(self):
        song_type = format_song_types_to_string(3, 1)
        assert song_type == "Insert Song"
