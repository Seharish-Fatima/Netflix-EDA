# Netflix, Decoded 🎬

### Live: [netflix-decoded.streamlit.app](https://netflix-decoded.streamlit.app/)

Everyone has an opinion about Netflix. "They pivoted to TV." "They cancel everything after one season." "It's all international content now." Cool opinions — but 8,807 titles of catalog data are sitting right there, so I decided to check which ones are actually true.

Spoiler: one of them is flat-out wrong, one is dramatically true, and one is a meme with real statistical weight behind it.

## What it actually does (no cap)

A five-section data story built on the classic Kaggle netflix_titles dataset (every title on Netflix, 2008–2021):

- **The Catalog at a Glance** — 8,807 titles, 6,131 movies, 2,676 shows, 122 countries. Plus the first myth-check: despite the "Netflix pivoted to TV" narrative, **movies dominated additions every single year** (59–75% of new titles). The pivot everyone talks about isn't in this data.
- **The International Bet** — the pivot that IS in the data. Non-US content went from 32% of additions in 2015 to **crossing 50% in 2016 and peaking at 67% in 2018**. India alone contributed 1,000+ titles. South Korea's 231 titles punch absurdly above their weight — and this snapshot ends _before_ Squid Game fully detonated. There's a country-comparison multiselect so you can watch any country's rise yourself.
- **Genre Landscape** — "International Movies" is literally the single biggest genre tag (2,752 titles). Bigger than Dramas. Bigger than Comedies. Even Netflix's own taxonomy is telling you where the strategy went.
- **Content Freshness** — is Netflix a fresh-content pipeline or a nostalgia dumpster? The gap between release year and date-added answers it: **the median title is 1 year old when added**, every year since 2017. The exceptions are deliberate curation — a 1925 women-filmmakers collection, 1940s war documentaries — not clearance-sale catalog dumps.
- **The One-Season Graveyard** — 1,793 of 2,676 TV shows (**67%**) have exactly one season. Some of that is limited series and international one-offs. But yes: the "Netflix cancels everything" meme has receipts.

Every section ends with an insight callout that states the finding in one sentence — because a dashboard without conclusions is just chart soup.

## Project structure

```
netflix-decoded/
├── app.py               # the actual app (Streamlit UI)
├── analytics.py         # every aggregation — growth, shares, genres, freshness
├── data_prep.py         # loading, cleaning, feature engineering
├── netflix_titles.csv   # the dataset, bundled — app works instantly, no upload
└── requirements.txt
```

`analytics.py` does the math. `data_prep.py` cleans the data. `app.py` only renders. The analytics layer doesn't know Streamlit exists — same separation as my other apps, because it keeps working when the UI changes.

## A real note on the source data (there's always something)

- Some rows had the **duration accidentally stored in the rating column** — a movie "rated" 74 min. Detected and moved to the right column instead of treating "74 min" as a maturity rating.
- `date_added` has random leading whitespace throughout. Stripped before parsing — zero parse failures on real dates after that.
- `duration` means minutes for movies and seasons for TV, in the same column. Split into two proper columns.
- Some titles list **multiple countries** — counted properly in the country rankings instead of just taking the first one and pretending.
- The early years (2008–2014) have so few additions (sometimes literally 1) that percentage charts on them are pure noise — one year swung to "100% movies" on a sample of two titles. Share charts require ≥50 additions per year to include it, because a percentage of nothing is a lie with confidence.
- 14 titles were added before their listed release year. Netflix time travel, or metadata quirks. Handled gracefully instead of crashing.

## Running this yourself

```bash
pip install -r requirements.txt
streamlit run app.py
```

Dataset is bundled — it just works. Or use the live deployment above, zero setup.

## Dataset

Kaggle's [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows) by Shivam Bansal — the classic catalog snapshot, 8,807 titles through late 2021. Yes, it ends at 2021; this is an analysis of a fixed historical snapshot, framed honestly as such.
