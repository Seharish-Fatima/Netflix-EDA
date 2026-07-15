from __future__ import annotations

import pandas as pd
import numpy as np
from dataclasses import dataclass


EXPECTED_COLUMNS = {
    "show_id",
    "type",
    "title",
    "director",
    "cast",
    "country",
    "date_added",
    "release_year",
    "rating",
    "duration",
    "listed_in",
    "description",
}


class DataLoadError(Exception):
    pass


@dataclass
class NetflixCatalog:
    df: pd.DataFrame
    n_titles: int
    n_movies: int
    n_shows: int
    year_added_range: tuple[int, int]
    n_countries: int
    n_genres: int


def _clean_rating(df: pd.DataFrame) -> pd.DataFrame:
    duration_like = df["rating"].astype(str).str.contains(r"\d+\s*min", na=False)
    df.loc[duration_like & df["duration"].isna(), "duration"] = df.loc[
        duration_like & df["duration"].isna(), "rating"
    ]
    df.loc[duration_like, "rating"] = np.nan
    return df


def _parse_duration(df: pd.DataFrame) -> pd.DataFrame:
    minutes = df["duration"].astype(str).str.extract(r"(\d+)\s*min", expand=False)
    seasons = df["duration"].astype(str).str.extract(r"(\d+)\s*Season", expand=False)
    df["duration_minutes"] = pd.to_numeric(minutes, errors="coerce")
    df["duration_seasons"] = pd.to_numeric(seasons, errors="coerce")
    return df


def load_catalog(source) -> NetflixCatalog:
    try:
        df = pd.read_csv(source)
    except Exception as e:
        raise DataLoadError(f"Could not read CSV: {e}")

    missing = EXPECTED_COLUMNS - set(df.columns)
    if missing:
        raise DataLoadError(
            f"Missing required columns: {sorted(missing)}. "
            "Make sure you're using the Kaggle netflix_titles.csv dataset."
        )

    df = df.copy()

    df["date_added"] = pd.to_datetime(
        df["date_added"].astype(str).str.strip(), format="%B %d, %Y", errors="coerce"
    )
    df["year_added"] = df["date_added"].dt.year
    df["month_added"] = df["date_added"].dt.month

    df = _clean_rating(df)
    df = _parse_duration(df)

    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")
    df["content_age_at_add"] = df["year_added"] - df["release_year"]

    df["primary_country"] = (
        df["country"].astype(str).str.split(",").str[0].str.strip().replace("nan", np.nan)
    )

    df["genres"] = df["listed_in"].astype(str).str.split(", ")

    valid_years = df["year_added"].dropna()
    year_range = (
        (int(valid_years.min()), int(valid_years.max()))
        if len(valid_years)
        else (0, 0)
    )

    all_countries = set()
    for c in df["country"].dropna():
        all_countries.update(x.strip() for x in str(c).split(","))
    all_countries.discard("")

    all_genres = set()
    for g in df["listed_in"].dropna():
        all_genres.update(x.strip() for x in str(g).split(","))
    all_genres.discard("")

    return NetflixCatalog(
        df=df,
        n_titles=len(df),
        n_movies=int((df["type"] == "Movie").sum()),
        n_shows=int((df["type"] == "TV Show").sum()),
        year_added_range=year_range,
        n_countries=len(all_countries),
        n_genres=len(all_genres),
    )