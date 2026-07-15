from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from data_prep import load_catalog, DataLoadError
import analytics as an

st.set_page_config(
    page_title="Netflix Catalog, Decoded",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap');

:root {
    --void: #0B0B0F;
    --surface: #16161D;
    --surface-raised: #1E1E28;
    --border: #2A2A36;
    --red: #E50914;
    --red-dim: rgba(229,9,20,0.12);
    --gold: #F5C518;
    --muted: #8C8C9A;
    --text: #D8D8E0;
    --text-bright: #FFFFFF;
}

html, body, .stApp {
    background-color: var(--void) !important;
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

.block-container { padding: 2rem 3rem !important; max-width: 1400px !important; }

.nf-header {
    border-bottom: 1px solid var(--border);
    padding-bottom: 1.8rem;
    margin-bottom: 2rem;
}
.nf-kicker {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--red);
    margin-bottom: 0.4rem;
}
.nf-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.4rem;
    font-weight: 400;
    color: var(--text-bright);
    margin: 0;
    line-height: 1;
    letter-spacing: 0.02em;
}
.nf-title span { color: var(--red); }
.nf-sub {
    color: var(--muted);
    font-size: 0.95rem;
    margin-top: 0.7rem;
    max-width: 680px;
    line-height: 1.6;
}

.nf-section {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.5rem;
    letter-spacing: 0.04em;
    color: var(--text-bright);
    margin: 2.4rem 0 0.2rem 0;
    display: flex;
    align-items: center;
    gap: 0.7rem;
}
.nf-section .num {
    color: var(--red);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
}
.nf-section::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}
.nf-section-sub {
    color: var(--muted);
    font-size: 0.85rem;
    margin-bottom: 1rem;
}

.nf-stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.2rem 0;
}
.nf-stat {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.1rem 1.3rem;
}
.nf-stat-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.4rem;
    color: var(--text-bright);
    display: block;
    line-height: 1;
}
.nf-stat-value.red { color: var(--red); }
.nf-stat-value.gold { color: var(--gold); }
.nf-stat-label {
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.35rem;
    display: block;
}

.nf-insight {
    background: var(--red-dim);
    border-left: 3px solid var(--red);
    border-radius: 4px;
    padding: 0.8rem 1.1rem;
    font-size: 0.88rem;
    color: var(--text);
    margin: 0.8rem 0;
    line-height: 1.55;
}
.nf-insight strong { color: var(--text-bright); }
</style>
"""

st.markdown(_CSS, unsafe_allow_html=True)

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#16161D",
    font=dict(family="Inter, sans-serif", color="#8C8C9A", size=11),
    margin=dict(l=40, r=20, t=30, b=40),
)

RED = "#E50914"
GOLD = "#F5C518"
MUTED = "#4A4A58"
GRID = "#2A2A36"


def styled_axes(fig, x_title=None, y_title=None):
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, title_text=x_title or "", title_font=dict(color="#8C8C9A"))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, title_text=y_title or "", title_font=dict(color="#8C8C9A"))
    return fig


st.markdown(
    """
    <div class="nf-header">
        <div class="nf-kicker">CATALOG ANALYSIS — 2008 TO 2021</div>
        <p class="nf-title">NETFLIX, <span>DECODED</span></p>
        <p class="nf-sub">
            8,807 titles of catalog data, read as strategy. When did Netflix go
            international? Does it actually favor TV over movies? Why does everything
            get cancelled after one season? The data answers all three.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.spinner("Loading catalog..."):
    try:
        catalog = load_catalog("netflix_titles.csv")
    except DataLoadError as e:
        st.error(str(e))
        st.stop()

df = catalog.df

st.markdown('<div class="nf-section"><span class="num">01</span>THE CATALOG AT A GLANCE</div>', unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="nf-stat-grid">
        <div class="nf-stat">
            <span class="nf-stat-value">{catalog.n_titles:,}</span>
            <span class="nf-stat-label">Total Titles</span>
        </div>
        <div class="nf-stat">
            <span class="nf-stat-value red">{catalog.n_movies:,}</span>
            <span class="nf-stat-label">Movies</span>
        </div>
        <div class="nf-stat">
            <span class="nf-stat-value red">{catalog.n_shows:,}</span>
            <span class="nf-stat-label">TV Shows</span>
        </div>
        <div class="nf-stat">
            <span class="nf-stat-value gold">{catalog.n_countries}</span>
            <span class="nf-stat-label">Countries Represented</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    growth = an.catalog_growth(df)
    fig = go.Figure()
    for content_type, color in [("Movie", RED), ("TV Show", GOLD)]:
        sub = growth[growth["type"] == content_type]
        fig.add_trace(go.Bar(x=sub["year_added"], y=sub["titles_added"], name=content_type, marker_color=color))
    fig.update_layout(**CHART_LAYOUT, barmode="stack", height=320,
                      title=dict(text="Titles Added Per Year", font=dict(color="#D8D8E0", size=13)),
                      legend=dict(font=dict(color="#8C8C9A")))
    styled_axes(fig, "Year Added", "Titles")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    share = an.type_share_by_year(df)
    fig = go.Figure()
    if "TV Show" in share.columns:
        fig.add_trace(go.Scatter(x=share["year_added"], y=share["TV Show"], name="TV Show %",
                                 line=dict(color=GOLD, width=3), mode="lines+markers"))
    if "Movie" in share.columns:
        fig.add_trace(go.Scatter(x=share["year_added"], y=share["Movie"], name="Movie %",
                                 line=dict(color=RED, width=3), mode="lines+markers"))
    fig.update_layout(**CHART_LAYOUT, height=320,
                      title=dict(text="Movies vs TV — Share of New Additions", font=dict(color="#D8D8E0", size=13)),
                      legend=dict(font=dict(color="#8C8C9A")))
    styled_axes(fig, "Year Added", "% of Additions")
    st.plotly_chart(fig, use_container_width=True)

st.markdown(
    '<div class="nf-insight">Despite the "Netflix pivoted to TV" narrative, <strong>movies dominated '
    'additions every single year</strong> — 59–75% of new titles. The real strategic shift in this data '
    'is somewhere else entirely. Keep scrolling.</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="nf-section"><span class="num">02</span>THE INTERNATIONAL BET</div>', unsafe_allow_html=True)
st.markdown('<p class="nf-section-sub">The actual pivot — from Hollywood catalog to global content engine.</p>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    intl = an.international_share_over_time(df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=intl["year_added"], y=intl["international_pct"],
        fill="tozeroy", line=dict(color=RED, width=3),
        fillcolor="rgba(229,9,20,0.15)", mode="lines+markers", name="International %",
    ))
    fig.add_hline(y=50, line=dict(color="#8C8C9A", dash="dot", width=1))
    fig.update_layout(**CHART_LAYOUT, height=330,
                      title=dict(text="Non-US Share of New Additions", font=dict(color="#D8D8E0", size=13)))
    styled_axes(fig, "Year Added", "% Non-US Content")
    st.plotly_chart(fig, use_container_width=True)

with col4:
    tc = an.top_countries(df, 12)
    fig = go.Figure(go.Bar(
        x=tc["titles"], y=tc["country"], orientation="h",
        marker_color=[RED if c == "United States" else (GOLD if c in ("South Korea", "India", "Japan") else MUTED) for c in tc["country"]],
    ))
    fig.update_layout(**CHART_LAYOUT, height=330,
                      title=dict(text="Titles by Country (multi-country counted)", font=dict(color="#D8D8E0", size=13)))
    fig.update_yaxes(autorange="reversed", gridcolor=GRID)
    fig.update_xaxes(gridcolor=GRID, title_text="Titles", title_font=dict(color="#8C8C9A"))
    st.plotly_chart(fig, use_container_width=True)

intl_2015 = intl[intl["year_added"] == 2015]["international_pct"].values
intl_peak_row = intl.loc[intl["international_pct"].idxmax()]
v15 = f"{intl_2015[0]:.0f}%" if len(intl_2015) else "—"
peak_pct = f"{intl_peak_row['international_pct']:.0f}%"
peak_year = int(intl_peak_row["year_added"])

st.markdown(
    f'<div class="nf-insight">Non-US content went from <strong>{v15} of additions in 2015 to crossing '
    f'the 50% line in 2016, peaking at {peak_pct} in {peak_year}</strong>. India alone contributed 1,000+ titles. '
    f'South Korea, with 231 titles, punches far above its size in cultural impact — and this catalog snapshot '
    f'predates the full Squid Game effect.</div>',
    unsafe_allow_html=True,
)

selected_countries = st.multiselect(
    "Compare country growth",
    options=an.top_countries(df, 15)["country"].tolist(),
    default=["India", "South Korea", "Japan", "Spain"],
)

if selected_countries:
    cg = an.country_growth(df, selected_countries)
    fig = go.Figure()
    palette = [RED, GOLD, "#00C8FF", "#9D5CFF", "#FF7A00", "#3DDC84"]
    for i, country in enumerate(selected_countries):
        sub = cg[cg["primary_country"] == country]
        fig.add_trace(go.Scatter(x=sub["year_added"], y=sub["titles_added"],
                                 name=country, mode="lines+markers",
                                 line=dict(color=palette[i % len(palette)], width=2.5)))
    fig.update_layout(**CHART_LAYOUT, height=340,
                      title=dict(text="New Titles Per Year — Selected Countries", font=dict(color="#D8D8E0", size=13)),
                      legend=dict(font=dict(color="#8C8C9A")))
    styled_axes(fig, "Year Added", "Titles Added")
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="nf-section"><span class="num">03</span>GENRE LANDSCAPE</div>', unsafe_allow_html=True)

gc = an.genre_counts(df, 15)
fig = go.Figure(go.Bar(
    x=gc["genre"], y=gc["titles"],
    marker_color=[RED if "International" in g else MUTED for g in gc["genre"]],
))
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#16161D",
    font=dict(family="Inter, sans-serif", color="#8C8C9A", size=11),
    margin=dict(l=40, r=20, t=30, b=120),
    height=420,
    title=dict(text="Top 15 Genres by Title Count", font=dict(color="#D8D8E0", size=13)),
)
styled_axes(fig, None, "Titles")
fig.update_xaxes(tickangle=35)
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    '<div class="nf-insight"><strong>"International Movies" is the single largest genre tag</strong> (2,752 titles) — '
    'larger than Dramas or Comedies. Even the genre taxonomy reflects the international strategy.</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="nf-section"><span class="num">04</span>CONTENT FRESHNESS</div>', unsafe_allow_html=True)
st.markdown('<p class="nf-section-sub">Is Netflix adding new content or buying up old catalogs? The gap between release year and date added answers it.</p>', unsafe_allow_html=True)

col5, col6 = st.columns([3, 2])

with col5:
    fresh = an.content_freshness(df)
    fig = go.Figure()
    for content_type, color in [("Movie", RED), ("TV Show", GOLD)]:
        sub = fresh[fresh["type"] == content_type]["content_age_at_add"]
        fig.add_trace(go.Histogram(x=sub, name=content_type, marker_color=color, opacity=0.75, nbinsx=50))
    fig.update_layout(**CHART_LAYOUT, barmode="overlay", height=330,
                      title=dict(text="Age of Content When Added (years)", font=dict(color="#D8D8E0", size=13)),
                      legend=dict(font=dict(color="#8C8C9A")))
    styled_axes(fig, "Years Between Release and Addition", "Titles")
    fig.update_xaxes(range=[0, 40])
    st.plotly_chart(fig, use_container_width=True)

with col6:
    old = an.oldest_titles(df, 8)
    st.markdown('<p style="color:#D8D8E0; font-size:0.85rem; font-weight:600; margin-bottom:0.4rem;">Oldest content in the catalog</p>', unsafe_allow_html=True)
    display_old = old[["title", "release_year", "content_age_at_add"]].rename(
        columns={"title": "Title", "release_year": "Released", "content_age_at_add": "Age When Added"}
    )
    display_old["Released"] = display_old["Released"].astype(str)
    st.dataframe(
        display_old,
        use_container_width=True,
        hide_index=True,
        height=300,
    )

st.markdown(
    '<div class="nf-insight">The median title is added <strong>just 1 year after release</strong>, every year since 2017 — '
    'Netflix is a fresh-content pipeline, not a nostalgia library. The exceptions are deliberate: '
    'a 1925 women-filmmakers collection, 1940s war documentaries. Curation, not clearance sales.</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="nf-section"><span class="num">05</span>THE ONE-SEASON GRAVEYARD</div>', unsafe_allow_html=True)

col7, col8 = st.columns(2)

with col7:
    tv = an.tv_seasons_distribution(df)
    fig = go.Figure(go.Bar(
        x=tv["seasons"], y=tv["shows"],
        marker_color=[RED if s == 1 else MUTED for s in tv["seasons"]],
    ))
    fig.update_layout(**CHART_LAYOUT, height=330,
                      title=dict(text="TV Shows by Number of Seasons", font=dict(color="#D8D8E0", size=13)))
    styled_axes(fig, "Seasons", "Shows")
    st.plotly_chart(fig, use_container_width=True)

with col8:
    md = an.movie_duration_distribution(df)
    fig = go.Figure(go.Histogram(x=md, marker_color=RED, nbinsx=60))
    fig.add_vline(x=float(md.median()), line=dict(color=GOLD, dash="dash", width=2),
                  annotation_text=f"median {md.median():.0f} min", annotation_font_color=GOLD)
    fig.update_layout(**CHART_LAYOUT, height=330,
                      title=dict(text="Movie Runtime Distribution", font=dict(color="#D8D8E0", size=13)))
    styled_axes(fig, "Runtime (minutes)", "Movies")
    st.plotly_chart(fig, use_container_width=True)

one_season = int(tv[tv["seasons"] == 1]["shows"].values[0])
total_shows = int(tv["shows"].sum())
pct = one_season / total_shows * 100

st.markdown(
    f'<div class="nf-insight"><strong>{one_season:,} of {total_shows:,} TV shows ({pct:.0f}%) have exactly one season.</strong> '
    f'Part of this is limited series and international one-offs — but the meme about Netflix cancelling '
    f'everything after season 1 has real statistical weight behind it.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="margin-top:3rem; border-top:1px solid #2A2A36; padding-top:1rem;">
        <p style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#4A4A58; letter-spacing:0.1em;">
        NETFLIX, DECODED — NOCTAVENT · CATALOG SNAPSHOT 2008–2021 · KAGGLE NETFLIX_TITLES DATASET
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)