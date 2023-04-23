from ..utils import (
    format_song_types_to_integer,
    format_song_types_to_string,
    get_regex_search,
    is_ranked_time,
)
from ..io_classes import SongType

import re
from pytz import timezone
from datetime import datetime


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


class TestRegexSearch:
    def test_regex_1(self):
        regex = get_regex_search("kana hanazawa")
        assert re.match(regex, "Kana Hanazawa".lower())

    def test_regex_2(self):
        regex = get_regex_search("Hanazawa kana")
        assert re.match(regex, "Kana Hanazawa".lower())

    def test_regex_3(self):
        regex = get_regex_search("hanazawa Kana", swap_words=False)
        assert not re.match(regex, "Kana Hanazawa".lower())

    def test_regex_4(self):
        regex = get_regex_search("yoko ono")
        assert re.match(regex, "Ryouko Ono".lower())

    def test_regex_5(self):
        regex = get_regex_search("yoko ono", partial_match=False)
        assert not re.match(regex, "Ono Ryouko".lower())

    def test_regex_6(self):
        regex = get_regex_search("maya sakamoto")
        assert re.match(regex, "Maaya Sakamoto".lower())

    def test_regex_7(self):
        regex = get_regex_search("Naruto Shippuden")
        assert re.match(regex, "Naruto Shippuuden".lower())

    def test_regex_8(self):
        regex = get_regex_search("fine rein")
        assert re.match(regex, "Fine★Rein".lower())

    def test_regex_9(self):
        regex = get_regex_search("et'aek 0n taitn", partial_match=False)
        assert re.match(regex, "ətˈæk 0N tάɪtn".lower())

    def test_regex_10(self):
        regex = get_regex_search("zool")
        assert re.match(regex, "ŹOOĻ".lower())

    def test_regex_11(self):
        regex = get_regex_search("ghibli dansei gasshou dan")
        assert re.match(regex, "Ghibli Dansei Gasshou-dan".lower())

    def test_regex_12(self):
        regex = get_regex_search("girls2")
        assert re.match(regex, "Girls²".lower())

    def test_regex_13(self):
        regex = get_regex_search("bios-o")
        assert re.match(regex, "βίος-δ".lower())

    def test_regex_14(self):
        regex = get_regex_search("*", partial_match=False)
        assert re.match(regex, "✻".lower())

    def test_regex_15(self):
        regex = get_regex_search("kaede cheek fairy")
        assert re.match(regex, "Kaede+Cheek Fairy".lower())

    def test_regex_16(self):
        regex = get_regex_search(r"konnichiwa\(^o^)/kirarinbo harry!!!")
        assert re.match(regex, r"Konnichiwa\(^o^)/Kirarinbo☆Harry!!!".lower())

    def test_regex_17(self):
        regex = get_regex_search("KanaHanazawa")
        assert not re.match(regex, "Kana Hanazawa".lower())


class TestCheckRankedTime:
    utc_tz = timezone("UTC")

    # Test during ranked time in CET with DST
    def test_ranked_time_1(self):
        # initialize CET timezone
        cet_tz = timezone("CET")

        # create cet datetime April at 20:30
        cet_datetime_1 = cet_tz.localize(datetime(2023, 4, 1, 20, 30, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime = cet_datetime_1.astimezone(self.utc_tz)

        # create cet datetime April at 21:28
        cet_datetime_2 = cet_tz.localize(datetime(2023, 4, 1, 21, 28, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime_2 = cet_datetime_2.astimezone(self.utc_tz)

        # assert that the UTC datetime is during ranked time
        assert is_ranked_time(utc_datetime, ranked_length=58)
        assert is_ranked_time(utc_datetime_2, ranked_length=58)

    # Test during ranked time in CET without DST
    def test_ranked_time_2(self):
        # initialize CET timezone
        cet_tz = timezone("CET")

        # create cet datetime January at 20:30
        cet_datetime_1 = cet_tz.localize(datetime(2023, 1, 1, 20, 30, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime = cet_datetime_1.astimezone(self.utc_tz)

        # create cet datetime January at 21:28
        cet_datetime_2 = cet_tz.localize(datetime(2023, 1, 1, 21, 28, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime_2 = cet_datetime_2.astimezone(self.utc_tz)

        # assert that the UTC datetime is during ranked time
        assert is_ranked_time(utc_datetime, ranked_length=58)
        assert is_ranked_time(utc_datetime_2, ranked_length=58)

    # Test outside ranked time close to CET
    def test_ranked_time_3(self):
        # initialize CET timezone
        cet_tz = timezone("CET")

        # create cet datetime January at 20:29
        cet_datetime_1 = cet_tz.localize(datetime(2023, 4, 1, 20, 29, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime = cet_datetime_1.astimezone(self.utc_tz)

        # create cet datetime January at 21:29
        cet_datetime_2 = cet_tz.localize(datetime(2023, 1, 1, 21, 29, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime_2 = cet_datetime_2.astimezone(self.utc_tz)

        # assert that the UTC datetime is during ranked time
        assert not is_ranked_time(utc_datetime, ranked_length=58)
        assert not is_ranked_time(utc_datetime_2, ranked_length=58)

    # Test during ranked time in CST with DST
    def test_ranked_time_4(self):
        # initialize CET timezone
        cst_tz = timezone("America/Chicago")

        # create cet datetime April at 20:30
        cst_datetime_1 = cst_tz.localize(datetime(2023, 4, 1, 20, 30, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime = cst_datetime_1.astimezone(self.utc_tz)

        # create cet datetime April at 21:28
        cst_datetime_2 = cst_tz.localize(datetime(2023, 4, 1, 21, 28, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime_2 = cst_datetime_2.astimezone(self.utc_tz)

        # assert that the UTC datetime is during ranked time
        assert is_ranked_time(utc_datetime, ranked_length=58)
        assert is_ranked_time(utc_datetime_2, ranked_length=58)

    # Test during ranked time in CST without DST
    def test_ranked_time_5(self):
        # initialize CET timezone
        cst_tz = timezone("America/Chicago")

        # create cet datetime April at 20:30
        cst_datetime_1 = cst_tz.localize(datetime(2023, 1, 1, 20, 30, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime = cst_datetime_1.astimezone(self.utc_tz)

        # create cet datetime April at 21:28
        cst_datetime_2 = cst_tz.localize(datetime(2023, 1, 1, 21, 28, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime_2 = cst_datetime_2.astimezone(self.utc_tz)

        # assert that the UTC datetime is during ranked time
        assert is_ranked_time(utc_datetime, ranked_length=58)
        assert is_ranked_time(utc_datetime_2, ranked_length=58)

    # Test outside ranked time close to CST
    def test_ranked_time_6(self):
        # initialize CET timezone
        cst_tz = timezone("America/Chicago")

        # create cet datetime April at 20:30
        cst_datetime_1 = cst_tz.localize(datetime(2023, 1, 1, 20, 29, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime = cst_datetime_1.astimezone(self.utc_tz)

        # create cet datetime April at 21:28
        cst_datetime_2 = cst_tz.localize(datetime(2023, 4, 1, 21, 29, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime_2 = cst_datetime_2.astimezone(self.utc_tz)

        # assert that the UTC datetime is during ranked time
        assert not is_ranked_time(utc_datetime, ranked_length=58)
        assert not is_ranked_time(utc_datetime_2, ranked_length=58)

    # Test during ranked time in JST
    def test_ranked_time_7(self):
        # initialize CET timezone
        jst_tz = timezone("Japan")

        # create cet datetime April at 20:30
        jst_datetime_1 = jst_tz.localize(datetime(2023, 1, 1, 20, 30, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime = jst_datetime_1.astimezone(self.utc_tz)

        # create cet datetime April at 21:28
        jst_datetime_2 = jst_tz.localize(datetime(2023, 4, 1, 21, 28, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime_2 = jst_datetime_2.astimezone(self.utc_tz)

        # assert that the UTC datetime is during ranked time
        assert is_ranked_time(utc_datetime, ranked_length=58)
        assert is_ranked_time(utc_datetime_2, ranked_length=58)

    # Test outside ranked time close to JST
    def test_ranked_time_8(self):
        # initialize CET timezone
        jst_tz = timezone("Japan")

        # create cet datetime April at 20:30
        jst_datetime_1 = jst_tz.localize(datetime(2023, 1, 1, 20, 29, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime = jst_datetime_1.astimezone(self.utc_tz)

        # create cet datetime April at 21:28
        jst_datetime_2 = jst_tz.localize(datetime(2023, 1, 1, 21, 29, 0), is_dst=None)
        # convert the CET datetime to UTC
        utc_datetime_2 = jst_datetime_2.astimezone(self.utc_tz)

        # assert that the UTC datetime is during ranked time
        assert not is_ranked_time(utc_datetime, ranked_length=58)
        assert not is_ranked_time(utc_datetime_2, ranked_length=58)
