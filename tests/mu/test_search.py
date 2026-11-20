"""
Tests for mu's search syntax (Api._build_sql_where) and sort orders
(Api._build_sql_order), both through the SQL they build and through
real queries against the `tracks` fixture.

Syntax recap:
    col:value     contains, case-insensitive
    col=value     exact match
    a & b         both must match
    a , b         either may match
    "..."         quotes protect , and & inside a value
"""

import pytest


def ids(api, term=None, **kwargs) -> list[int]:
    return list(api.get_tracks(term, **kwargs).keys())


# --- _build_sql_where: the SQL itself ---------------------------------------


def test_contains_filter(api):
    sql, values = api._build_sql_where("title:song", "tracks")
    assert "LIKE ?" in sql
    assert values == ("%song%",)


def test_exact_filter(api):
    sql, values = api._build_sql_where("id=3", "tracks")
    assert "id = ?" in sql
    assert values == ("3",)


def test_and_or_grouping(api):
    sql, values = api._build_sql_where("id=1 & title:a, id=2", "tracks")
    assert sql.count(" OR ") == 1
    assert sql.count(" AND ") == 1
    assert values == ("1", "%a%", "2")


def test_values_are_parameters_not_sql(api):
    sql, values = api._build_sql_where("title=x' OR 1=1 --", "tracks")
    assert "OR 1=1" not in sql
    assert values == ("x' OR 1=1 --",)


def test_quotes_protect_delimiters(api):
    _, values = api._build_sql_where('title:"rock, paper & scissors"', "tracks")
    assert values == ("%rock, paper & scissors%",)


def test_value_may_contain_colon_or_equals(api):
    _, values = api._build_sql_where("title:a:b=c", "tracks")
    assert values == ("%a:b=c%",)


def test_whitespace_around_filters_is_ignored(api):
    _, values = api._build_sql_where("  id=1  &  id=2 ", "tracks")
    assert values == ("1", "2")


def test_playlists_table_has_its_own_columns(api):
    api._build_sql_where("description:x", "playlists")
    with pytest.raises(ValueError, match="Invalid column"):
        api._build_sql_where("artist:x", "playlists")


@pytest.mark.parametrize(
    ("term", "message"),
    [
        ("nope:x", "Invalid column"),
        (":x", "No column"),
        ("title", "Missing =/:"),
        ("title:", "Value is empty"),
        ('title:"open', "Unterminated quote"),
        ("id=1,", "No column"),  # trailing comma leaves an empty filter
    ],
)
def test_bad_terms_raise(api, term, message):
    with pytest.raises(ValueError, match=message):
        api._build_sql_where(term, "tracks")


def test_unknown_table_raises(api):
    with pytest.raises(ValueError, match="Cannot search table"):
        api._build_sql_where("id=1", "sqlite_master")


def test_column_name_cannot_inject_sql(api):
    # Everything after the first =/: is the value, so this stays a parameter.
    sql, values = api._build_sql_where("id=1) OR (1=1", "tracks")
    assert values == ("1) OR (1=1",)
    assert "1=1" not in sql
    # And anything before it must be a whitelisted column name.
    with pytest.raises(ValueError):
        api._build_sql_where("1=1 OR id=1", "tracks")


# --- searching real rows -----------------------------------------------------


def test_contains_is_case_insensitive(api, tracks):
    assert ids(api, "title:SONG 3") == [tracks[2]]


def test_exact_match(api, tracks):
    assert ids(api, f"id={tracks[1]}") == [tracks[1]]


def test_exact_match_is_not_a_substring_match(api, tracks):
    assert ids(api, "title=Song") == []


def test_or_returns_both(api, tracks):
    assert sorted(ids(api, f"id={tracks[0]}, id={tracks[4]}")) == [tracks[0], tracks[4]]


def test_and_narrows(api, tracks):
    assert ids(api, f"artist:test & id={tracks[3]}") == [tracks[3]]
    assert ids(api, "artist:test & artist:nobody") == []


def test_no_term_returns_everything(api, tracks):
    assert sorted(ids(api)) == tracks


# --- only_favorited ----------------------------------------------------------


def test_only_favorited_without_term(api, tracks):
    api.favorite_tracks(f"id={tracks[1]}")
    assert ids(api, only_favorited=True) == [tracks[1]]


def test_only_favorited_applies_to_every_or_group(api, tracks):
    api.favorite_tracks(f"id={tracks[1]}")
    # Without parentheses around the OR groups, id=1 would slip through.
    term = f"id={tracks[0]}, id={tracks[1]}"
    assert ids(api, term, only_favorited=True) == [tracks[1]]


# --- ordering ----------------------------------------------------------------


@pytest.fixture
def varied(api):
    """Four tracks whose columns sort differently from their ids."""
    rows = [
        ("b", "Zed", "2:00", 5, "10"),
        ("a", "alpha", "10:00", 0, "9"),
        ("c", "Beta", "0:59", 12, None),
        ("d", None, "1:30", 1, "2"),
    ]
    out = []
    with api.db.write() as conn:
        for name, artist, time, plays, track_no in rows:
            t = api._upsert_track(
                conn,
                {
                    "title": name,
                    "artist": artist,
                    "album": "x",
                    "time": time,
                    "tracknumber": track_no,
                    "albumartist": artist,
                    "discnumber": 1,
                    "genre": None,
                    "date": None,
                    "filepath": f"/f/{name}.mp3",
                    "filename": f"{name}.mp3",
                    "albumart": None,
                },
            )
            conn.execute("UPDATE tracks SET plays = ? WHERE id = ?", (plays, t.id))
            out.append(t.id)
    return dict(zip("abcd", out))


def titles(api, **kw) -> list[str]:
    return [t.title for t in api.get_tracks(**kw).values()]


def test_default_order_is_artist_then_album_then_track(api, varied):
    # NULL artist sorts first in SQLite's default ascending order.
    assert titles(api) == ["d", "a", "c", "b"]


def test_text_sort_ignores_case(api, varied):
    assert titles(api, order_by="artist") == ["a", "c", "b", "d"]


def test_text_sort_descending_keeps_nulls_last(api, varied):
    assert titles(api, order_by="artist", descending=True) == ["b", "c", "a", "d"]


def test_numeric_sort_is_numeric_not_alphabetical(api, varied):
    # As text, "12" < "5"; as numbers it's the other way round.
    assert titles(api, order_by="plays") == ["a", "d", "b", "c"]


def test_time_sort_uses_seconds(api, varied):
    # As text, "10:00" < "2:00".
    assert titles(api, order_by="time") == ["c", "d", "b", "a"]
    assert titles(api, order_by="time", descending=True) == ["a", "b", "d", "c"]


@pytest.mark.parametrize("bad", ["shuffle", "cancel", "reset", "id; DROP TABLE tracks"])
def test_order_by_non_column_raises(api, bad):
    with pytest.raises(ValueError, match="Cannot sort by"):
        api._build_sql_order(bad)  # type: ignore[arg-type]
