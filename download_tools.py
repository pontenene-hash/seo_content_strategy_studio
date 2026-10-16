"""日本時間の保存名とSNS成果物の一括書き出し。"""
from datetime import datetime, timezone, timedelta
from io import BytesIO
from pathlib import PurePosixPath
from zipfile import ZipFile, ZIP_DEFLATED

from social_tools import social_text, creative_prompt_text

JST = timezone(timedelta(hours=9))


def download_timestamp() -> str:
    return datetime.now(JST).strftime("%Y%m%d_%H%M%S")


def dated_filename(filename: str, stamp: str | None = None) -> str:
    path = PurePosixPath(filename)
    return f"{path.stem}_{stamp or download_timestamp()}{path.suffix}"


def social_download_bundle(plan: dict, stamp: str) -> bytes:
    """表示中の生成結果のみを格納する。認証情報やセッション全体は含めない。"""
    posts = social_text(plan)
    prompts = creative_prompt_text(plan)
    combined = "# SNS投稿文・構成と画像・動画制作プロンプト\n\n" + posts + "\n\n---\n\n" + prompts
    files = {
        "SNS投稿文と制作プロンプト_一括.md": combined,
        "SNS投稿文と構成.txt": posts,
        "画像動画制作プロンプト.md": prompts,
    }
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        for name, text in files.items():
            archive.writestr(dated_filename(name, stamp), text.encode("utf-8-sig"))
    return buffer.getvalue()
