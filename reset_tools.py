"""次の記事に進む際の入力と成果物のクリア。API設定は対象にしない。"""
def reset_article_state(state):
    keep = {"social_brand_name", "integrated_brand_name", "url_use_ipv4"}
    prefixes = ("research_", "keyword_article_", "url_", "rewrite_", "social_", "seo_")
    for key in list(state):
        if key not in keep and (key.startswith(prefixes) or key == "competitor_result"):
            del state[key]
