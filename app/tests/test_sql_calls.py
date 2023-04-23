from ..sql_calls import extract_artist_database


class TestExtractDatabaseData:
    def test_extract_artist_database(self):
        artist_database = extract_artist_database(
            "app/data/enhanced_amq_database.sqlite"
        )

        assert artist_database is not None
        assert "Kana Hanazawa" in artist_database["4437"]["names"]
