from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..config import settings
from .models import Base

engine = create_async_engine(
    settings.db_uri,
    echo=settings.echo_sql
)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def create_db_utils():
    async with async_session() as conn:
        await conn.execute(text("""
        CREATE OR REPLACE FUNCTION get_C() RETURNS FLOAT AS $$
        DECLARE
            result FLOAT;
        BEGIN
            SELECT AVG(vote_average) INTO result FROM movies;
            RETURN result;
        END;
        $$ LANGUAGE plpgsql;
        """))

        await conn.execute(text("""
        CREATE OR REPLACE FUNCTION get_m() RETURNS INTEGER AS $$
        DECLARE
            result INTEGER;
        BEGIN
            SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY vote_count) INTO result FROM movies;
            RETURN result;
        END;
        $$ LANGUAGE plpgsql;
        """))

        await conn.execute(text("""
        CREATE OR REPLACE FUNCTION get_top_movies() RETURNS SETOF movies AS $$
        DECLARE
            threshold INTEGER := get_m();
        BEGIN
            RETURN QUERY
            SELECT * FROM movies
            WHERE vote_count >= threshold AND vote_average IS NOT NULL AND vote_count IS NOT NULL;
        END;
        $$ LANGUAGE plpgsql;
        """))

        await conn.execute(text("""
        CREATE OR REPLACE FUNCTION weighted_rating(vote_count BIGINT, vote_average DOUBLE PRECISION) RETURNS FLOAT AS $$
        DECLARE
            v INTEGER := vote_count;
            R FLOAT := vote_average;
            m INTEGER := get_m();
            C FLOAT := get_C();
            result FLOAT;
        BEGIN
            IF v IS NULL OR R IS NULL THEN
                RETURN NULL;
            END IF;
            result := (v / (v + m) * R) + (m / (m + v) * C);
            RETURN result;
        END;
        $$ LANGUAGE plpgsql;
        """))
    
        await conn.execute(text("""
        CREATE OR REPLACE FUNCTION get_best_movies() RETURNS SETOF movies AS $$
        DECLARE
            threshold INTEGER := get_m();
        BEGIN
            RETURN QUERY
            SELECT m.*
            FROM movies m
            WHERE vote_count >= threshold AND vote_average IS NOT NULL AND vote_count IS NOT NULL
            ORDER BY weighted_rating(vote_count, vote_average) DESC
            LIMIT 20;
        END;
        $$ LANGUAGE plpgsql;
        """))

async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()
