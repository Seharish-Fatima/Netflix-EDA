from __future__ import annotations

import pandas as pd
import numpy as np


def catalog_growth(df: pd.DataFrame) -> pd.DataFrame:
    valid = df.dropna(subset=["year_added"])
    growth = (
        valid.groupby(["year_added", "type"])
        .size()
        .reset_index(name="titles_added")
    )
    growth["year_added"] = growth["year_added"].astype(int)
    return growth


def cumulative_catalog(df: pd.DataFrame) -> pd.DataFrame:
    growth = catalog_growth(df)
    pivot = growth.pivot(index="year_added", columns="type", values="titles_added").fillna(0)
    return pivot.cumsum().reset_index()


def type_share_by_year(df: pd.DataFrame, min_titles: int = 50) -> pd.DataFrame:
    growth = catalog_growth(df)
    pivot = growth.pivot(index="year_added", columns="type", values="titles_added").fillna(0)
    totals = pivot.sum(axis=1)
    pivot = pivot[totals >= min_titles]
    share = pivot.div(pivot.sum(axis=1), axis=0) * 100
    return share.reset_index()


def top_countries(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    counts: dict[str, int] = {}
    for c in df["country"].dropna():
        for country in str(c).split(","):
            country = country.strip()
            if country:
                counts[country] = counts.get(country, 0) + 1
    result = (
        pd.DataFrame(counts.items(), columns=["country", "titles"])
        .sort_values("titles", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )
    return result


def international_share_over_time(df: pd.DataFrame, min_titles: int = 50) -> pd.DataFrame:
    valid = df.dropna(subset=["year_added", "primary_country"])
    valid = valid.copy()
    valid["is_us"] = valid["primary_country"] == "United States"
    yearly = valid.groupby("year_added").agg(
        total=("show_id", "count"),
        us=("is_us", "sum"),
    )
    yearly = yearly[yearly["total"] >= min_titles]
    yearly["international_pct"] = (1 - yearly["us"] / yearly["total"]) * 100
    yearly = yearly.reset_index()
    yearly["year_added"] = yearly["year_added"].astype(int)
    return yearly


def country_growth(df: pd.DataFrame, countries: list[str]) -> pd.DataFrame:
    valid = df.dropna(subset=["year_added", "primary_country"])
    subset = valid[valid["primary_country"].isin(countries)]
    growth = (
        subset.groupby(["year_added", "primary_country"])
        .size()
        .reset_index(name="titles_added")
    )
    growth["year_added"] = growth["year_added"].astype(int)
    return growth


def genre_counts(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    counts: dict[str, int] = {}
    for genres in df["genres"]:
        if isinstance(genres, list):
            for g in genres:
                g = g.strip()
                if g and g != "nan":
                    counts[g] = counts.get(g, 0) + 1
    return (
        pd.DataFrame(counts.items(), columns=["genre", "titles"])
        .sort_values("titles", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def rating_distribution(df: pd.DataFrame) -> pd.DataFrame:
    counts = (
        df.groupby(["rating", "type"])
        .size()
        .reset_index(name="titles")
    )
    order = df["rating"].value_counts().index.tolist()
    counts["rating"] = pd.Categorical(counts["rating"], categories=order, ordered=True)
    return counts.sort_values("rating")


def content_freshness(df: pd.DataFrame) -> pd.DataFrame:
    valid = df.dropna(subset=["content_age_at_add"])
    valid = valid[valid["content_age_at_add"] >= 0]
    return valid[["type", "content_age_at_add", "title", "release_year", "year_added"]]


def freshness_by_year(df: pd.DataFrame) -> pd.DataFrame:
    valid = df.dropna(subset=["content_age_at_add", "year_added"])
    valid = valid[valid["content_age_at_add"] >= 0]
    yearly = (
        valid.groupby("year_added")["content_age_at_add"]
        .median()
        .reset_index(name="median_content_age")
    )
    yearly["year_added"] = yearly["year_added"].astype(int)
    return yearly


def oldest_titles(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    valid = df.dropna(subset=["content_age_at_add"])
    valid = valid[valid["content_age_at_add"] >= 0]
    oldest = valid.nlargest(n, "content_age_at_add")[
        ["title", "type", "release_year", "year_added", "content_age_at_add", "primary_country"]
    ].reset_index(drop=True)
    oldest["release_year"] = oldest["release_year"].astype(int)
    oldest["year_added"] = oldest["year_added"].astype(int)
    oldest["content_age_at_add"] = oldest["content_age_at_add"].astype(int)
    return oldest


def movie_duration_distribution(df: pd.DataFrame) -> pd.Series:
    return df[df["type"] == "Movie"]["duration_minutes"].dropna()


def tv_seasons_distribution(df: pd.DataFrame) -> pd.DataFrame:
    seasons = df[df["type"] == "TV Show"]["duration_seasons"].dropna().astype(int)
    counts = seasons.value_counts().sort_index().reset_index()
    counts.columns = ["seasons", "shows"]
    return counts