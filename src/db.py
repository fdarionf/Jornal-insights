import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg.connect(DATABASE_URL)


def init_db() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id            BIGSERIAL PRIMARY KEY,
                    title         TEXT NOT NULL,
                    link          TEXT NOT NULL UNIQUE,
                    fonte         TEXT NOT NULL,
                    categoria     TEXT NOT NULL,
                    published_at  TIMESTAMPTZ,
                    collected_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_articles_published_at
                    ON articles (published_at);
            """)
        conn.commit()


def save_articles(articles: list[dict]) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            inserted = 0
            for article in articles:
                cur.execute(
                    """
                    INSERT INTO articles (title, link, fonte, categoria, published_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (link) DO NOTHING
                """,
                    (
                        article["title"],
                        article["link"],
                        article["fonte"],
                        article["categoria"],
                        article["published_at"],
                    ),
                )
                inserted += cur.rowcount
            conn.commit()
            return inserted
