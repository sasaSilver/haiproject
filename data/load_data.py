import sys
import os
import pandas as pd
from ast import literal_eval

from sqlalchemy import create_engine, text, insert
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))
from src.config import settings
from src.database.models import (
    GenreSchema, movie_genre,
    KeywordSchema, movie_keyword
)


if __name__ == "__main__":
    engine = create_engine(settings.db_uri.replace("+asyncpg", ""))
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS movies CASCADE;"))
        
    md = pd.read_csv("data/movies_metadata.csv", usecols=[
        "genres", "id", "title", "release_date",
        "poster_path", "overview", "tagline",
        "popularity", "vote_count", "vote_average"
    ])
    links = pd.read_csv("data/links_small.csv", dtype=str)
    links = links[links["tmdbId"].notnull()]
    keywords = pd.read_csv("data/keywords.csv", dtype=str)
    
    md = md.drop([19730, 29503, 35587]).drop_duplicates()
    md = md[md["id"].isin(links["tmdbId"])] 
    md = md.merge(links[["tmdbId", "imdbId"]], left_on="id", right_on="tmdbId", how="left")
    md = md.merge(keywords[["id", "keywords"]], on="id", how="left")
    md["id"] = md["imdbId"]
    md["vote_count"] = md["vote_count"].fillna(0).astype(int)
    md["vote_average"] = md["vote_average"].fillna(0).astype(float)
    md["popularity"] = md["popularity"].fillna(0).astype(float)
    md["genres"] = md["genres"].fillna("[]").apply(literal_eval)
    md["keywords"] = md["keywords"].fillna("[]").apply(literal_eval)
    md["tagline"] = md["tagline"].fillna("")
    md["description"] = md["overview"] + md["tagline"]
    md["description"] = md["description"].fillna("")
    md["year"] = pd.to_datetime(md["release_date"], errors="coerce").apply(
        lambda x: int(str(x).split("-")[0]) if not pd.isna(x) else None
    )
    genre_records: set[tuple[int, str]]= set()
    movie_genre_records: set[tuple[str, int]]= set()
    
    for movie_id, genre_list in zip(md["id"], md["genres"]):
        for genre_dict in genre_list:
            genre_id = genre_dict["id"]
            genre_name = genre_dict["name"]
            genre_records.add((genre_id, genre_name))
            movie_genre_records.add((movie_id, genre_id))
    
    keyword_records: set[tuple[int, str]]= set()
    movie_keyword_records: set[tuple[str, int]]= set()
    
    for movie_id, keyword_list in zip(md["id"], md["keywords"]):
        for keyword_dict in keyword_list:
            keyword_id = keyword_dict["id"]
            keyword_name = keyword_dict["name"]
            keyword_records.add((keyword_id, keyword_name))
            movie_keyword_records.add((movie_id, keyword_id))

    
    md.drop(columns=[
        "genres", "keywords", "overview", "tagline",
        "release_date", "poster_path", "imdbId"
    ]).to_sql(
        name="movies",
        con=engine,
        if_exists="replace",
        index=False
    )
    with engine.begin() as conn:
        conn.execute(
            insert(GenreSchema).values([
                {"id": id, "name": name} for id, name in genre_records
            ])
        )
        conn.execute(
            insert(movie_genre).values([
                {"movie_id": mid, "genre_id": gid} for mid, gid in movie_genre_records
            ])
        )
        conn.execute(
            insert(KeywordSchema).values([
                {"id": id, "name": name} for id, name in keyword_records
            ])
        )
        conn.execute(
            insert(movie_keyword).values([
                {"movie_id": mid, "keyword_id": kid} for mid, kid in movie_keyword_records
            ])
        )