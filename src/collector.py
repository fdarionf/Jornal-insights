import json
from pathlib import Path
import httpx
import feedparser
import calendar
from datetime import datetime, timezone

source_path = Path(__file__).parent.parent / "data" / "sources.json"
articles_path = Path(__file__).parent.parent / "data" / "articles.json"

HEADERS = {
    "User-Agent": "jornal-insights/0.1 (RSS collector; contato: seu-email)",
}


def load_sources() -> list[dict]:
    with source_path.open(encoding="utf-8") as file:
        return json.load(file)


def fetch_feed(client: httpx.Client, source: dict) -> httpx.Response:
    return client.get(source["url"], headers=HEADERS)


def parse_feed(response: httpx.Response, source: dict) -> list[dict]:
    feed = feedparser.parse(response.content)

    articles = []
    for entry in feed.entries:
        parsed = entry.get("published_parsed")
        if parsed:
            published_at = datetime.fromtimestamp(
                calendar.timegm(parsed), timezone.utc
            ).isoformat()
        else:
            published_at = None
        articles.append(
            {
                "title": entry.title,
                "link": entry.link,
                "fonte": source["nome"],
                "categoria": source["categoria"],
                "published_at": published_at,
            }
        )
    return articles


def save_articles(articles: list[dict]) -> None:
    with articles_path.open("w", encoding="utf-8") as file:
        json.dump(articles, file, ensure_ascii=False, indent=4)


def main() -> None:
    sources = load_sources()
    print(f"Fontes carregadas: {len(sources)}\n")
    with httpx.Client(timeout=30.0) as client:
        all_articles = []
        for source in sources:
            response = fetch_feed(client, source)
            size_kb = len(response.content) / 1024

            if response.status_code == 200:
                print(
                    f"[{response.status_code}] {source['nome']} "
                    f"({source['categoria']}) — {size_kb:.1f} KB"
                )
                articles = parse_feed(response, source)
                all_articles.extend(articles)
                if articles:
                    print(
                        f"Tamanho do feed: {len(articles)}\n"
                        f"Primeiro artigo: {articles[0]['title']}\n"
                        f"Link: {articles[0]['link']}\n"
                        f"Fonte: {articles[0]['fonte']}\n"
                        f"Categoria: {articles[0]['categoria']}\n"
                    )
            else:
                print(
                    f"[{response.status_code}] {source['nome']} "
                    f"  Erro ao buscar: {source['url']}"
                    "\n"
                )

        print(f"Total de artigos coletados: {len(all_articles)}")

        save_articles(all_articles)
        print(f"Artigos salvos com sucesso em {articles_path}!")


if __name__ == "__main__":
    main()
