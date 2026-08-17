#!/usr/bin/env python3
"""Sync creation dates from git and regenerate index.html article order."""

from __future__ import annotations

import html
import re
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES_DIR = ROOT / "articles"
INDEX_PATH = ROOT / "index.html"

GIT_PREFIXES = ("articles", "programming", "ai-development", "infra")


@dataclass
class Article:
    filename: str
    cluster_id: str
    domain_id: str
    eyebrow: str
    title: str
    description: str
    meta: str
    iso_date: str

    @property
    def href(self) -> str:
        return f"articles/{self.filename}"

    @property
    def label_date(self) -> str:
        year, month, day = self.iso_date.split("-")
        return f"{year}年{int(month)}月{int(day)}日"

    @property
    def sort_key(self) -> str:
        return self.iso_date


CLUSTERS: dict[str, dict[str, str]] = {
    "dev-frontend": {
        "domain": "dev",
        "eyebrow": "開発 &gt; フロントエンド &amp; 配信",
        "heading": "画面、ルーティング、ホスティング、メディア出力",
        "heading_id": "dev-frontend-heading",
    },
    "dev-backend": {
        "domain": "dev",
        "eyebrow": "開発 &gt; バックエンド &amp; API",
        "heading": "サーバー側フレームワークと API 設計",
        "heading_id": "dev-backend-heading",
    },
    "dev-toolchain": {
        "domain": "dev",
        "eyebrow": "開発 &gt; 開発基盤",
        "heading": "言語、ランタイム、パッケージ、リポジトリ、品質ツール",
        "heading_id": "dev-toolchain-heading",
    },
    "game-engine": {
        "domain": "game",
        "eyebrow": "ゲーム &gt; エンジン",
        "heading": "3D エンジンの比較と選定",
        "heading_id": "game-engine-heading",
    },
    "ai-workflow": {
        "domain": "ai",
        "eyebrow": "AI &gt; 開発ワークフロー",
        "heading": "コーディング支援、ツール連携、作業の自動化",
        "heading_id": "ai-workflow-heading",
    },
    "ai-app": {
        "domain": "ai",
        "eyebrow": "AI &gt; アプリケーション設計",
        "heading": "RAG、Agent、データと検索の設計",
        "heading_id": "ai-app-heading",
    },
    "ai-foundation": {
        "domain": "ai",
        "eyebrow": "AI &gt; 基礎",
        "heading": "モデルの仕組みと論文",
        "heading_id": "ai-foundation-heading",
    },
    "ai-articles-papers": {
        "domain": "ai",
        "eyebrow": "AI &gt; 記事・論文",
        "heading": "記事・論文の読み解き",
        "heading_id": "ai-articles-papers-heading",
    },
    "ai-governance": {
        "domain": "ai",
        "eyebrow": "AI &gt; 安全・運用",
        "heading": "企業利用、リスク、ガバナンス",
        "heading_id": "ai-governance-heading",
    },
    "infra-cloud": {
        "domain": "infra",
        "eyebrow": "インフラ &gt; クラウド（AWS）",
        "heading": "VPC、データベース、可用性",
        "heading_id": "infra-cloud-heading",
    },
    "infra-network": {
        "domain": "infra",
        "eyebrow": "インフラ &gt; ネットワーク",
        "heading": "接続とセキュリティ（クラウド外も含む）",
        "heading_id": "infra-network-heading",
    },
}

DOMAINS: dict[str, dict[str, str]] = {
    "dev": {
        "nav": "開発",
        "eyebrow": "開発",
        "title": "ソフトウェアを作る・配布する・支える",
        "map_label": "開発",
        "map_detail": "UI / API / 基盤",
    },
    "game": {
        "nav": "ゲーム",
        "eyebrow": "ゲーム",
        "title": "ゲーム制作の環境選び",
        "map_label": "ゲーム",
        "map_detail": "エンジン選定",
    },
    "ai": {
        "nav": "AI",
        "eyebrow": "AI",
        "title": "AI を使う・作る・理解する・守る",
        "map_label": "AI",
        "map_detail": "ツール / 設計 / 基礎 / 記事・論文 / 運用",
    },
    "infra": {
        "nav": "インフラ",
        "eyebrow": "インフラ",
        "title": "クラウドとネットワーク",
        "map_label": "インフラ",
        "map_detail": "クラウド / ネットワーク",
    },
}

CLUSTER_ORDER: dict[str, list[str]] = {
    "dev": ["dev-frontend", "dev-backend", "dev-toolchain"],
    "game": ["game-engine"],
    "ai": ["ai-workflow", "ai-app", "ai-foundation", "ai-articles-papers", "ai-governance"],
    "infra": ["infra-cloud", "infra-network"],
}

ARTICLE_CLUSTER: dict[str, str] = {
    "golang-net-http.html": "dev-backend",
    "go-backend-api-frameworks.html": "dev-backend",
    "google-sso.html": "dev-backend",
    "aws-google-sso-architecture.html": "infra-cloud",
    "react-router-vs-tanstack-router.html": "dev-frontend",
    "spa-ssg-ssr.html": "dev-frontend",
    "use-action-state.html": "dev-frontend",
    "react-19-changes.html": "dev-frontend",
    "remotion-rendering.html": "dev-frontend",
    "nestjs.html": "dev-backend",
    "hono.html": "dev-backend",
    "go-project-layout.html": "dev-toolchain",
    "go-task.html": "dev-toolchain",
    "package-managers.html": "dev-toolchain",
    "nodejs-versions.html": "dev-toolchain",
    "nodejs-bun-production-comparison.html": "dev-toolchain",
    "temporal-api.html": "dev-toolchain",
    "typescript-5-6-7.html": "dev-toolchain",
    "typescript-lint-format-tooling.html": "dev-toolchain",
    "turborepo-monorepo.html": "dev-toolchain",
    "3d-game-engines.html": "game-engine",
    "rtk-ai-token-proxy.html": "ai-workflow",
    "mcp-server.html": "ai-workflow",
    "claude-code-dynamic-workflows.html": "ai-workflow",
    "cursor-vs-github-ai-coding.html": "ai-workflow",
    "forward-deployed-engineer.html": "ai-workflow",
    "harness-engineering.html": "ai-workflow",
    "rag.html": "ai-app",
    "ai-agent.html": "ai-app",
    "ai-friendly-relational-database.html": "ai-app",
    "transformer-paper.html": "ai-foundation",
    "torvalds-ai-programming-productivity.html": "ai-articles-papers",
    "chatgpt-enterprise-risk.html": "ai-governance",
    "gemma-on-premise-web-app.html": "ai-governance",
    "hitl-hotl-hootl-loop-design.html": "ai-governance",
    "aws-web-db-network.html": "infra-cloud",
    "aws-database-operations.html": "infra-cloud",
    "wifi-security.html": "infra-network",
}

ARTICLE_CARD_OVERRIDES: dict[str, dict[str, str]] = {
    "aws-google-sso-architecture.html": {
        "eyebrow": "AWS / 認証アーキテクチャ",
        "title": "AWS上のGoogle SSO構成案を比較する",
        "description": "AWS上のtoBサービスで、企業・個人Googleアカウントの双方を認証する5構成を比較します。",
        "meta": "5構成比較 · 両アカウント対応",
    },
    "google-sso.html": {
        "eyebrow": "認証 / OpenID Connect",
        "title": "Google認証によるSSOの仕組みと導入手順",
        "description": "OIDCの認証フロー、必要なインフラ、既存アカウントとの紐付け、実装時の注意点を整理します。",
        "meta": "導入手順 · セキュリティ",
    },
    "gemma-on-premise-web-app.html": {
        "eyebrow": "AI運用 / オンプレミス",
        "title": "GemmaはオンプレWebアプリで有用か",
        "description": "ライセンス、費用、企業事例、Webアプリ構成、導入時の注意点を公式情報から整理します。",
        "meta": "規約確認済み · 企業事例あり",
    },
    "torvalds-ai-programming-productivity.html": {
        "eyebrow": "AI記事 / 開発生産性",
        "title": "Linus TorvaldsのAIプログラミング観を読む",
        "description": "AIは強力な道具だが理解と保守責任は人間に残る、という発言を要約し、賛否の反応を整理します。",
        "meta": "記事読解 · ネット反応整理",
    },
    "forward-deployed-engineer.html": {
        "eyebrow": "AI導入 / FDE",
        "title": "Forward Deployed Engineerの由来と意味",
        "description": "Palantirで知られるFDEについて、言葉の由来、登場経緯、AI時代に再注目される理由を整理します。",
        "meta": "由来整理 · 役割比較",
    },
    "wifi-security.html": {
        "eyebrow": "ネットワーク / Wi-Fi",
        "title": "Wi-Fiセキュリティ設定と公衆Wi-Fiのリスク",
        "description": "WPA3などの家庭用設定と、カフェなどの公衆Wi-Fiを今どの程度信頼できるかを整理します。",
        "meta": "公式情報確認済み · 比較表あり",
    },
    "harness-engineering.html": {
        "eyebrow": "AI Agent / 検証設計",
        "title": "ハーネスエンジニアリングは何に使うのか",
        "description": "AI Harness Engineering論文をもとに、モデル単体ではなく実行基盤としてエージェントを評価する考え方を整理します。",
        "meta": "論文要約 · H0-H3図解",
    },
    "nodejs-bun-production-comparison.html": {
        "eyebrow": "JavaScript / ランタイム選定",
        "title": "Node.jsとBunを本番プロダクト視点で比較する",
        "description": "設計思想、互換性、ユースケース、監視やCI/CDまで含めて、実運用で採用判断する観点を整理します。",
        "meta": "本番運用比較 · 公式情報確認済み",
    },
    "cursor-vs-github-ai-coding.html": {
        "eyebrow": "AI開発環境 / Cursor",
        "title": "CursorはGitHubに対して何が強いのか",
        "description": "CursorのAIエージェント中心設計と、GitHub / Copilotの開発基盤としての強みを比較します。",
        "meta": "一次情報確認済み · 展望整理",
    },
    "go-project-layout.html": {
        "eyebrow": "Go / プロジェクト構成",
        "title": "Goプロジェクトレイアウトの考え方",
        "description": "golang-standards/project-layoutの位置づけ、cmd・internal・pkgの使い分け、実用面のメリットを整理します。",
        "meta": "図解あり · 公式情報確認済み",
    },
    "go-task.html": {
        "eyebrow": "開発基盤 / タスクランナー",
        "title": "go-taskの用途と使い方",
        "description": "Taskfile.ymlで開発、テスト、ビルド、生成などの定型コマンドをまとめる方法を整理します。",
        "meta": "最小例あり · 公式情報確認済み",
    },
    "golang-net-http.html": {
        "eyebrow": "Go / net/http",
        "title": "Goのnet/httpは何ができるのか",
        "description": "Go標準ライブラリnet/httpのサーバー、クライアント、Transport、ServeMux、静的配信、テスト機能を整理します。",
        "meta": "機能地図 · 公式情報確認済み",
    },
    "hitl-hotl-hootl-loop-design.html": {
        "eyebrow": "AI Agent / ガバナンス",
        "title": "業務システムにおけるループ設計の効果的な設計",
        "description": "提供PDFの章立てに沿って、HITL、HOTL、HOOTLの定義、設計原則、現場適用をHTML化します。",
        "meta": "PDF本文HTML化 · 図解あり",
    },
}


def git_created_date(filename: str) -> str:
    for prefix in GIT_PREFIXES:
        path = f"{prefix}/{filename}"
        result = subprocess.run(
            ["git", "log", "--follow", "--reverse", "--format=%as", "--", path],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        lines = [line for line in result.stdout.strip().splitlines() if line]
        if lines:
            return lines[0]
    return date.today().isoformat()


def parse_index_cards() -> dict[str, dict[str, str]]:
    content = INDEX_PATH.read_text(encoding="utf-8")
    cards: dict[str, dict[str, str]] = {}

    card_pattern = re.compile(
        r'<a class="article-card" href="articles/([^"]+)">\s*'
        r'<p class="card-meta-row">\s*'
        r'<time class="article-date" datetime="[^"]+">[^<]*</time>\s*'
        r'<span class="eyebrow">([^<]*)</span>\s*'
        r"</p>\s*"
        r"<h4>([^<]*)</h4>\s*"
        r"<p>([^<]*)</p>\s*"
        r'<span class="meta">([^<]*)</span>',
        re.MULTILINE,
    )
    row_pattern = re.compile(
        r'<a class="article-row" href="articles/([^"]+)">.*?'
        r'<span class="article-row-eyebrow">([^<]*)</span>.*?'
        r'<span class="article-row-title">([^<]*)</span>\s*'
        r'<p class="article-row-desc">([^<]*)</p>.*?'
        r'<span class="article-row-meta">([^<]*)</span>',
        re.MULTILINE | re.DOTALL,
    )
    row_legacy_pattern = re.compile(
        r'<a class="article-row" href="articles/([^"]+)">\s*'
        r'<time class="article-date" datetime="[^"]+">[^<]*</time>\s*'
        r'<span class="article-row-eyebrow">([^<]*)</span>\s*'
        r'<span class="article-row-title">([^<]*)</span>\s*'
        r'<span class="article-row-desc">([^<]*)</span>\s*'
        r'<span class="article-row-meta">([^<]*)</span>',
        re.MULTILINE,
    )

    for pattern in (card_pattern, row_pattern, row_legacy_pattern):
        for match in pattern.finditer(content):
            filename, eyebrow, title, description, meta = match.groups()
            cards[filename] = {
                "eyebrow": html.unescape(eyebrow),
                "title": html.unescape(title),
                "description": html.unescape(description),
                "meta": html.unescape(meta),
            }
    return cards


def load_articles() -> list[Article]:
    cards = parse_index_cards()
    articles: list[Article] = []
    for filename, cluster_id in ARTICLE_CLUSTER.items():
        card = ARTICLE_CARD_OVERRIDES.get(filename, cards.get(filename))
        if card is None:
            raise KeyError(f"No index card or override found for {filename}")
        cluster = CLUSTERS[cluster_id]
        articles.append(
            Article(
                filename=filename,
                cluster_id=cluster_id,
                domain_id=cluster["domain"],
                eyebrow=card["eyebrow"],
                title=card["title"],
                description=card["description"],
                meta=card["meta"],
                iso_date=git_created_date(filename),
            )
        )
    return articles


RECENT_LIMIT = 6


def render_card(article: Article) -> str:
    return f"""            <a class="article-card" href="{article.href}">
              <p class="card-meta-row">
                <time class="article-date" datetime="{article.iso_date}">{article.label_date}</time>
                <span class="eyebrow">{html.escape(article.eyebrow)}</span>
              </p>
              <h4>{html.escape(article.title)}</h4>
              <p>{html.escape(article.description)}</p>
              <span class="meta">{html.escape(article.meta)}</span>
            </a>"""


def render_row(article: Article) -> str:
    return f"""            <a class="article-row" href="{article.href}">
              <div class="article-row-aside">
                <time class="article-date" datetime="{article.iso_date}">{article.label_date}</time>
                <span class="article-row-eyebrow">{html.escape(article.eyebrow)}</span>
              </div>
              <div class="article-row-main">
                <span class="article-row-title">{html.escape(article.title)}</span>
                <p class="article-row-desc">{html.escape(article.description)}</p>
              </div>
              <span class="article-row-meta">{html.escape(article.meta)}</span>
            </a>"""


def render_cluster(cluster_id: str, articles: list[Article]) -> str:
    cluster = CLUSTERS[cluster_id]
    rows = "\n\n".join(render_row(article) for article in articles)
    return f"""        <section class="article-cluster" aria-labelledby="{cluster['heading_id']}">
          <div class="cluster-heading">
            <p class="eyebrow">{cluster['eyebrow']}</p>
            <h3 id="{cluster['heading_id']}">{cluster['heading']}</h3>
          </div>
          <div class="article-row-list">
{rows}
          </div>
        </section>"""


def render_recent_section(articles: list[Article]) -> str:
    cards = "\n\n".join(render_card(article) for article in articles)
    return f"""    <section class="recent-section" id="recent" aria-labelledby="recent-heading">
      <div class="domain-heading">
        <p class="eyebrow">新着</p>
        <h2 id="recent-heading">最近追加した記事</h2>
        <p class="section-note">直近 {RECENT_LIMIT} 件。作成日は git の初回コミット日です。</p>
      </div>
      <div class="article-list recent-list">
{cards}
      </div>
    </section>"""


def render_domain(domain_id: str, clusters_html: str) -> str:
    domain = DOMAINS[domain_id]
    return f"""    <section class="domain-section" id="{domain_id}" aria-labelledby="{domain_id}-heading">
      <div class="domain-heading">
        <p class="eyebrow">{domain['eyebrow']}</p>
        <h2 id="{domain_id}-heading">{domain['title']}</h2>
      </div>

      <div class="cluster-stack">
{clusters_html}
      </div>
    </section>"""


def render_index(articles: list[Article]) -> str:
    by_cluster: dict[str, list[Article]] = {}
    for article in articles:
        by_cluster.setdefault(article.cluster_id, []).append(article)

    for cluster_articles in by_cluster.values():
        cluster_articles.sort(key=lambda item: item.sort_key, reverse=True)

    recent = sorted(articles, key=lambda item: item.sort_key, reverse=True)[:RECENT_LIMIT]

    domain_sections: list[str] = []
    for domain_id in ("dev", "game", "ai", "infra"):
        cluster_ids = CLUSTER_ORDER[domain_id]
        cluster_ids.sort(
            key=lambda cluster_id: max(
                (article.sort_key for article in by_cluster.get(cluster_id, [])),
                default="1970-01-01",
            ),
            reverse=True,
        )
        clusters_html = "\n\n".join(
            render_cluster(cluster_id, by_cluster[cluster_id])
            for cluster_id in cluster_ids
            if cluster_id in by_cluster
        )
        domain_sections.append(render_domain(domain_id, clusters_html))

    nav = "\n".join(
        f'        <a href="#{domain_id}">{DOMAINS[domain_id]["nav"]}</a>'
        for domain_id in ("dev", "game", "ai", "infra")
    )
    map_links = "\n".join(
        f"""      <a href="#{domain_id}">
        <span class="section-map-label">{DOMAINS[domain_id]['map_label']}</span>
        <strong>{DOMAINS[domain_id]['map_detail']}</strong>
      </a>"""
        for domain_id in ("dev", "game", "ai", "infra")
    )

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>技術質問ノート</title>
  <link rel="stylesheet" href="styles/site.css">
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="index.html">技術質問ノート</a>
      <nav class="nav" aria-label="カテゴリ">
        <a href="#recent">新着</a>
{nav}
      </nav>
    </div>
  </header>

  <main class="page">
    <section class="hero home-hero">
      <p class="eyebrow">知識整理</p>
      <h1>技術的な疑問を、読み返せる形で残す</h1>
      <p class="lead">質問への回答を <code>articles/</code> に蓄積し、このページでは内容別に探せるようにしています。各カードの日付は記事の追加日（git 初回コミット）で、新しい順に並べています。</p>
    </section>

    <section class="section-map" aria-label="分類マップ">
      <a href="#recent">
        <span class="section-map-label">新着</span>
        <strong>作成日が新しい順</strong>
      </a>
{map_links}
    </section>

{render_recent_section(recent)}

{chr(10).join(domain_sections)}
  </main>

  <footer class="site-footer">
    <p>新しい質問は <code>articles/</code> に HTML を追加し、<code>scripts/sync-article-dates.py</code> で index と作成日を同期します。</p>
  </footer>
</body>
</html>
"""


CREATED_BLOCK = re.compile(
    r'\n\s*<p class="article-created"><time datetime="[^"]+">作成日:[^<]+</time></p>',
)
CREATED_PATTERN = '<p class="article-created"><time datetime="{iso}">作成日: {label}</time></p>\n        '


def patch_article_page(path: Path, article: Article) -> None:
    content = path.read_text(encoding="utf-8")
    content = CREATED_BLOCK.sub("", content)
    block = CREATED_PATTERN.format(iso=article.iso_date, label=article.label_date)
    if '<p class="article-created">' in content:
        content = re.sub(
            r'<p class="article-created"><time datetime="[^"]+">作成日:[^<]+</time></p>\s*',
            block,
            content,
            count=1,
        )
    else:
        content = content.replace("</h1>\n        <p class=\"lead\">", f"</h1>\n        {block}<p class=\"lead\">", 1)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    articles = load_articles()
    INDEX_PATH.write_text(render_index(articles), encoding="utf-8")
    article_by_name = {article.filename: article for article in articles}
    for path in sorted(ARTICLES_DIR.glob("*.html")):
        patch_article_page(path, article_by_name[path.name])
    print(f"Updated {len(articles)} articles and index.html")


if __name__ == "__main__":
    main()
