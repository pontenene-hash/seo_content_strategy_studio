import json
import re

PRODUCTION_STANDARDS = """
【画像・動画共通：追加品質基準20項目】
1. 全体品質：InstagramやWeb広告で使えるプロの販促デザインを目指す。明るく清潔で親しみやすく、一目で内容が伝わる構成。絵・文字・背景・装飾と余白を調整し、情報過多にしない。
2. イラスト：記事と各場面に合う絵を必ず制作する。立ち絵だけにせず、自然な表情・動作・姿勢・背景・小物・身体の状態・施術や生活シーンで内容を伝える。日本人向けに自然な人物・生活環境・店舗像とし、顔・手・指・身体の形を確認する。
3. 情報量：タイトルだけで終わらせず、記事にある悩み・原因・対策・メリット・注意点・施術内容・おすすめポイントを短文と図解で伝える。記事にない原因・効果やサービスを作らない。
4. 配置：テキストとイラストの表示エリアを明確に分ける。図解内のラベルや吹き出しにも専用の空白・カードを設け、人物の顔・身体・重要な絵には重ねない。高コントラストを確保し、タイトルは大きく、サブテキストは約80％を目安にする。読めない小文字で情報を詰め込まない。
5. 改行：文節と意味のまとまりで改行し、単語・固有名詞・数字と単位を分断しない。『パーソナルトレーニング』は一体で扱い、枠を広げるか配置を調整する。助詞だけが行頭・行末に残る改行を避け、生成後に文字切れ・誤字・不自然な改行を確認する。
6. 統一感：カルーセル全9枚を1つの作品として設計する。色調・フォント・タッチ・人物デザイン・余白・タイトル位置・テキスト配置・装飾・ブランド像を統一する。図解や人物の構図は各ページの主題に合わせて変える。
7. 表紙：強いが誇張しないキャッチコピー、明確なテーマ、魅力的な絵、読みやすい文字で『誰のための、どんな内容か』を一目で伝える。
8. 最終ページ：記事のまとめから、指定された店舗・サービスへの優しいCTAにつなぐ。『こんなお悩みがある方はご相談ください』『無理なく始めてみませんか？』などを内容に合わせる。提供された正式名称・予約方法のみ使用し、未提供の電話番号・URL・営業時間は創作しない。
9. マーケティング：続きを見たいか、自分の悩みだと感じるか、サービスに興味が持てるか、保存したくなるかを検討する。根拠のない効果保証や強引な広告表現を避ける。
10. 動画構成：表紙→悩み・問題提起→記事にある原因や背景→解決策・ポイント→提供情報にあるサービス紹介→CTAを基本にする。単なる静止画連結ではなく、文字演出と自然な微動・転換で読みやすいテンポにする。
11. 冒頭：最初の1〜3秒で自分に関係するテーマだと分かる完成表紙を表示する。表紙自体は5〜6秒程度保持し、キャッチコピーを読む時間を確保する。黒画面や待ち時間を入れない。
12. テロップ：ナレーション無し。サブテキストは独立した文字レイヤーで1文字ずつタイプライター風に表示する。見出しは最初から読める状態にする。入力中に改行位置を動かさず、読了前に次の場面へ切り替えない。
13. BGM：明るく穏やか、少しポップで前向きな、健康・美容・リラクゼーション・店舗紹介に合う利用権のあるインストゥルメンタル。主張しすぎない音量で、途中で途切れさせない。
14. 縦型：Reels・TikTokはスマートフォン用。上下左右に操作UI用の安全余白を設け、顔や重要文字を端に置かない。既存の9枚構成を維持し、読める速さと間延びしないテンポを両立する。
15. 横型：YouTubeは16:9専用。縦型の単純変換をせず、人物・図解・タイトル・説明テロップを横画面へ独立設計する。左右配置など横幅を生かして余白と重心を整える。
16. 正式名称：指定された店舗名・サービス名を一字一句正確に使う。勝手に略称・英語・別名称に変えない。提供された店舗情報を優先する。情報がない場合は架空の名称を補わない。
17. 品質確認：生成後に誤字脱字・漢字・文字化け・文字切れ・単語途中の改行・不自然な日本語・顔・手指・身体・文字と絵の重なり・見切れ・余白・情報量・色・スマートフォン可読性・ブランド名を確認し、問題は修正する。
18. 三つの専門視点：グラフィックデザイナー、イラストレーター、SNSマーケティング担当者の視点で、一目で伝わるか、魅力、絵と内容の一致、読みやすさ、情報量、広告の強さ、保存・シェア・予約へのつながりを最終確認する。
19. 工程：元データを理解→伝える内容を整理→デザイン構成→生成→誤字・配置・人物確認→マーケティング確認→修正→再確認→最終版。一度の生成だけで完成扱いにしない。実施していない検品を実施済みと報告しない。
20. 最重要：記事の文章をただ画像化せず、内容を視覚的に再構成する。本文を読まなくても悩み・原因・解決方法・サービスのメリットが記事の根拠の範囲で分かることを目指す。明るさ、絵の魅力、適切な情報量、文字の読みやすさ、全体バランスを重視する。
適用範囲：静止画像には画像関連の項目、動画には全共通項目と該当する横型・縦型の項目を適用する。表紙・最終ページの指定は該当するページに適用する。
"""


MEDIA_FILENAMES = {
    "x_image": "X_投稿画像.png",
    "facebook_eyecatch": "Facebook_アイキャッチ.png",
    "gbp_image": "GBP_投稿画像.png",
    "threads_image": "Threads_投稿画像.png",
    "reel_cover": "Instagram_リール表紙.png",
    "reel_video": "Instagram_リール動画.mp4",
    "youtube_thumbnail": "YouTube_サムネイル.png",
    "youtube_video": "YouTube_動画.mp4",
    "tiktok_cover": "TikTok_表紙.png",
    "tiktok_video": "TikTok_動画.mp4",
}

IMAGE_QUALITY = (
    "あなたは読者心理と購買行動を熟知したプロのマーケティングコンサルタントであり、"
    "広告・出版分野で経験豊富なプロのイラストレーターです。マーケティング視点で情報の優先順位と視線誘導を設計し、"
    "細部まで丁寧で、ひと目で内容に興味を持てる高品質な商用イラストを制作する。"
    "画面全体は明るいハイキー照明を基本に、白・アイボリー・明るいパステルカラーを土台とし、"
    "内容に合う鮮やかなアクセントカラーを加える。自然光が差し込むような透明感、清潔感、前向きさ、"
    "温かさ、親しみやすさを表現し、スマートフォンの小さな画面でも主役と要点がすぐ分かる色彩設計にする。"
    "読者の感情が伝わる自然な表情と仕草、正確な人体、丁寧な手指、内容に合う背景と小物、柔らかな自然光、"
    "奥行きと質感、清潔感・信頼感・親しみやすさを備えた現代的な日本の雑誌広告風。"
    "記事の内容に応じて、人物の年代・服装・姿勢・動作・表情、場所、季節、道具、小物を具体的に描き分ける。"
    "複数画像では同じ構図や同じポーズを使い回さず、各画像の要点がイラストだけでも伝わる場面にする。"
    "安価な素材集風、幼すぎる絵、棒人間、平面的で単調な構図、不自然な手指、過剰な医療表現、"
    "暗い画面、くすんだ灰色一色、濁った配色、重苦しい雰囲気、恐怖をあおる表情、情報と無関係な飾り、"
    "実在ロゴ、著名キャラクター、特定作家の画風、透かし、意味不明な文字を使用しない。"
)

TEXT_LAYOUT_RULES = (
    "最優先：文字数だけで機械的に改行・切り捨てをしない。『マーケティング』『検索意図』『10分』など意味の単位は必ず一体で扱う。"
    "見出し・本文・吹き出し・図解ラベルすべてに適用する。長い語は枠を広げるかブロックごと移動し、語の途中で分割しない。"
    "文字を描画する前に、全文を日本語として読み、文節・語句・固有名詞・熟語の境界を確認して改行位置を確定する。"
    "確定した各行を分割禁止の1つのテキストオブジェクトとして配置し、制作ツールによる自動折り返しを無効にする。"
    "単語、固有名詞、商品名、施設名、熟語、数字と単位の途中では絶対に改行しない。"
    "助詞、句読点、長音、閉じ括弧を行頭に置かず、1文字だけの行や極端に短い行を作らない。"
    "行の長さを揃えることより意味のまとまりを優先する。見出しは中央揃え、説明・チェックリストは読みやすい左揃えも使う。"
    "上段だけ長い、下段だけ短い、片側へ寄る構成を避け、テキストブロック全体の重心を中央に整える。"
)

INFOGRAPHIC_RULES = (
    "画像だけで『何が大切か・なぜか・どう行動するか』が理解できる編集型イラストにする。"
    "人物を飾りとして置くだけでなく、記事の具体的な要点を、吹き出し・短いラベル・矢印・比較・手順・チェックリストで視覚化する。"
    "図解のラベルは専用の空白や説明カードに配置し、テキストと絵の表示エリアを明確に分ける。人物や重要な絵に重ねず、対象との対応関係を明確にする。"
    "1画像1主題、強い見出し1つ、具体的な要点2〜3つを基本とし、情報源が少ない場合は水増ししない。"
    "本文を丸ごと貼らず、見出し→図解→具体策の順で視線を誘導する。画像内の同じ文章の重複や装飾だけのラベルは禁止。"
    "読者自身の悩みと得られる理解を結び付け、明るい表情や具体的な行動場面で共感を生む。誇張、恐怖訴求、根拠のない効果保証は禁止。"
    "指定された記事由来の情報だけを使い、数値・口コミ・比較結果・因果関係を創作しない。条件や注意点を削って意味を変えない。"
    "情報量は小さい文字で増やさず、図解と階層化で増やす。スマートフォン表示で読める余白と高コントラストを確保する。"
    "日本語を正確に描けない生成ツールでは、文字なしの図解素材を作り、指定文言を編集可能なテキストレイヤーで後から配置する。"
)

PROFESSIONAL_REVIEW = (
    "納品前に、プロのグラフィックデザイナー・イラストレーター・SNSマーケティング担当者の3つの視点で100％表示とスマートフォン縮小表示の両方を最終検品する。"
    "検品項目は、誤字、文字化け、単語途中の改行、行頭禁則、各行の長さ、文字の中央揃え、行間、余白、視覚的重心、"
    "文字同士の衝突、顔や重要な動作の遮蔽、記事との一致、図解の対応関係、人物の顔・手指・身体、小物、背景、色、コントラスト、媒体サイズである。"
    "1項目でも不合格なら内部でレイアウトまたはイラストを修正して再検品し、すべて合格した完成版だけを出力する。"
    "ラフ、途中経過、未検品版、複数候補は出力しない。"
)


def _strip_code_fence(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _load_json_response(raw: str) -> dict:
    cleaned = _strip_code_fence(raw)
    candidates = [cleaned]
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start >= 0 and end > start:
        candidates.append(cleaned[start : end + 1])
    for candidate in candidates:
        try:
            data = json.loads(re.sub(r",\s*([}\]])", r"\1", candidate))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue
    raise json.JSONDecodeError("SNS構成のJSONを解析できません。", cleaned, 0)


def _plain_text(value: str, limit: int | None = 100) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", str(value or ""))
    value = re.sub(r"[*_`>#]", "", value)
    text = re.sub(r"\s+", " ", value).strip()
    return text if limit is None else text[:limit]


def _display_text(value) -> str:
    """表示文言は文字数で切らない。長文は生成側で意味を保って編集する。"""
    return _plain_text(value, None)


def _labels(value) -> list[str]:
    return [_display_text(item) for item in value if isinstance(item, str) and item.strip()][:3] if isinstance(value, list) else []


def _safe_filename_part(value: str, limit: int = 24) -> str:
    value = re.sub(r'[\\/:*?"<>|]', "", _plain_text(value, limit))
    return re.sub(r"\s+", "_", value).strip("._") or "記事セクション"


def _article_sections(article: str) -> list[dict]:
    sections, current, body = [], None, []
    for raw in article.splitlines():
        match = re.match(r"^(#{2,3})\s+(.+)$", raw.strip())
        if match:
            if current:
                current["summary"] = _display_text(" ".join(body))
                sections.append(current)
            current = {
                "level": "H2" if len(match.group(1)) == 2 else "H3",
                "heading": _display_text(match.group(2)),
            }
            body = []
        elif current and raw.strip():
            body.append(raw.strip())
    if current:
        current["summary"] = _display_text(" ".join(body))
        sections.append(current)
    return sections[:30]


def _article_image_sections(article: str, maximum: int = 6) -> list[dict]:
    """記事画像は重要なH2だけに絞り、長い記事でも作り過ぎない。"""
    sections = _article_sections(article)
    h2_sections = [section for section in sections if section.get("level") == "H2"]
    candidates = h2_sections or sections
    if len(candidates) <= maximum:
        return candidates

    # 冒頭・中盤・終盤から均等に選び、記事全体を過不足なくカバーする。
    positions = [round(index * (len(candidates) - 1) / (maximum - 1)) for index in range(maximum)]
    return [candidates[position] for position in positions]


def _normalize_plan(data: dict, article: str) -> dict:
    if not isinstance(data, dict):
        raise ValueError("SNS構成が正しい形式ではありません。")
    carousel = data.setdefault("carousel", {})
    if not isinstance(carousel, dict):
        carousel = {}
        data["carousel"] = carousel
    slides = carousel.get("slides", [])
    if not isinstance(slides, list):
        slides = []
    sections = _article_sections(article)
    while len(slides) < 9:
        source = sections[min(len(slides), len(sections) - 1)] if sections else {}
        slides.append({
            "title": source.get("heading", "まとめ" if len(slides) == 8 else f"ポイント{len(slides) + 1}"),
            "body": source.get("summary", "記事の要点を分かりやすく確認しましょう。"),
            "visual": (
                f"『{source.get('heading', '記事のポイント')}』の要点を、"
                f"{source.get('summary', '読者が内容を理解して前向きに行動する様子')}に合う"
                "人物・表情・動作・背景・小物で具体的に表現する"
            ),
        })
    carousel["slides"] = slides[:9]
    # 記事をまとめたカルーセル9枚を、そのまま動画の絵コンテとして再利用する。
    video_scenes = []
    for index, slide in enumerate(carousel["slides"], 1):
        slide = slide if isinstance(slide, dict) else {}
        video_scenes.append({
            "caption": _display_text(slide.get("title", f"ポイント{index}")),
            "narration": _display_text(slide.get("body", "")),
            "labels": _labels(slide.get("labels", [])),
            "visual": _plain_text(
                slide.get("visual")
                or f"カルーセル{index}枚目の要点を表す明るいイラスト",
                160,
            ),
            "source_image": f"Instagram_カルーセル_{index:02d}.png",
        })
    for video_key in ("reel", "tiktok"):
        video = data.setdefault(video_key, {})
        if not isinstance(video, dict):
            video = {}
            data[video_key] = video
        video["scenes"] = [dict(scene) for scene in video_scenes]
    youtube = data.setdefault("youtube", {})
    if not isinstance(youtube, dict):
        youtube = data["youtube"] = {}
    scenes = youtube.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        # 旧データでも内容だけを引き継ぎ、縦画像への参照は持たせない。
        scenes = video_scenes
    youtube["scenes"] = [
        {key: value for key, value in scene.items() if key != "source_image"}
        for scene in scenes if isinstance(scene, dict)
    ]
    return data


def _image_prompt_item(
    title: str,
    body: str,
    size: str,
    layout: str,
    font_spec: str,
    filename: str,
    scene: str = "",
    labels=None,
) -> dict:
    title = _display_text(title) or "記事のポイント"
    body = _display_text(body)
    visual_direction = _display_text(scene or f"{title}。{body}")
    labels = _labels(labels)
    prompt = (
        f"{PRODUCTION_STANDARDS}\n{INFOGRAPHIC_RULES}"
        f"{IMAGE_QUALITY} 出力サイズは{size}。テーマは『{visual_direction}』。"
        f"レイアウトは{layout}。見出し『{title}』"
        + (f"、補足『{body}』" if body else "")
        + "を意味を変えずに入れる。人物の顔、手、重要な動作や小物を文字で隠さない。"
        + (f"図解内に配置する具体的な文言：{json.dumps(labels, ensure_ascii=False)}。対応する対象にラベルや吹き出しとして配置する。" if labels else "補足から重要語句を抽出して図解内に配置してよい。新しい事実は加えない。")
        + f"フォントは{font_spec}。{TEXT_LAYOUT_RULES}"
        "フォント指定を目安に、見出し・本文・ラベルの3段階で強弱をつける。"
        "文字が収まらない場合はまず枠と配置を調整し、それでも長い場合は条件や意味を保った完結した短文へ編集する。末尾を機械的に切らない。高コントラストと十分な安全余白を確保する。"
        f"{PROFESSIONAL_REVIEW}"
    )
    return {
        "size": size,
        "catch_copy": title,
        "sub_copy": body,
        "labels": labels,
        "layout": layout,
        "font_spec": font_spec,
        "output_filename": filename,
        "prompt": prompt,
    }


def _video_prompt_item(
    plan_item: dict,
    size: str,
    duration: str,
    filename: str,
    vertical: bool,
    brand_name: str,
    article_summary: str = "",
) -> dict:
    scene_lines = []
    for index, raw_scene in enumerate(plan_item.get("scenes", []), 1):
        scene = raw_scene if isinstance(raw_scene, dict) else {}
        heading = _display_text(scene.get("caption", ""))
        telop_text = _display_text(scene.get("narration", ""))
        visual = _display_text(scene.get("visual") or scene.get("direction", ""))
        source_image = _plain_text(
            scene.get("source_image") or f"Instagram_カルーセル_{index:02d}.png",
            60,
        )
        if not vertical:
            scene_lines.append(
                f"シーン{index}：見出し『{heading}』。サブテキスト『{telop_text}』。"
                f"横長専用の場面・図解：{visual or telop_text}。"
                f"静止ラベル：{json.dumps(_labels(scene.get('labels', [])), ensure_ascii=False)}。"
                "横長の新規構図で制作し、見出し・図解は静止表示、サブテキストだけをタイプ入力風にする。"
            )
            continue
        scene_lines.append(
            f"シーン{index}（{source_image}を約6秒、文字量に応じて延長）：見出し『{heading}』。"
            f"図解内のラベル・吹き出しも維持する：{json.dumps(_labels(scene.get('labels', [])), ensure_ascii=False)}。"
            f"説明カードの文章『{telop_text}』は音声にせず、元画像と同じ位置でタイピング風に表示する。"
            "同じ見出しや説明文を別の場所へ重複表示しない。"
            f"元画像のイラストは『{visual or telop_text}』を表す具体的な人物・表情・動作・背景・小物。"
            "元画像のデザインと文字を保ち、ゆっくりしたズーム、パン、光、人物や小物のごく自然な微動だけを加える。"
        )
    scene_script = " ".join(scene_lines)
    if vertical:
        layout = "縦型の見出しと図解カードを統合し、右端と最下部に操作UI用の安全余白を確保する"
        font_spec = "太めの日本語ゴシック体。表紙メイン96〜120px、表紙サブはメインの約80％、場面見出し72〜88px、下部補足は見出しの約80％、最大2行、行間1.25〜1.4倍"
        cta = "最後の3〜4秒は、記事内で確認できる次の行動を自然に案内し、必要に応じてプロフィールのリンクへ誘導する"
    else:
        layout = "16:9専用構図。上部約15％に見出し、中央約60％に横に広がるイラスト・図解、下部約20％にサブテキスト、残りは余白。中央は人物と説明を約6:4で配置する案を基本に、比較なら左右2列、手順なら横方向など主題に応じて調整する。画面四辺に5％程度の安全余白を取り、人物の大きさ・余白・文字量の釣り合いを優先する"
        font_spec = "太めの日本語ゴシック体。表紙メイン88〜112px、表紙サブはメインの約80％、場面見出し64〜80px、下部補足は見出しの約80％、最大2行、行間1.25〜1.4倍"
        cta = "最後の3〜4秒は、記事内で確認できる次の行動を自然に案内し、必要に応じて概要欄のリンクへ誘導する"
    brand = str(brand_name or "").strip()
    brand_rule = f"ブランド名『{brand}』は必要な場合のみ控えめに表示する。" if brand else ""
    format_rules = (
        "入力素材はInstagram_カルーセル_01.pngからInstagram_カルーセル_09.pngまでの9枚。"
        "01→09の順序、記事の内容、人物、配色、構図、図解ラベルを維持する。"
        "既存の縦型動画のデザインを維持し、サブテキストの演出だけを変更する。"
        if vertical else
        "YouTube用に1920×1080・16:9の横長動画を独立設計する。"
        "記事の重要点と結論を忠実に要約し、横画面に適した場面数・順序・構図を採用する。"
        "リールやTikTokの画像、9枚構成、画面配置へ合わせる必要はない。"
        "縦型画像を中央に小さく置く、左右をぼかしで埋める、引き伸ばす、無理に切り抜く構成は禁止する。"
        "横方向の視線誘導とイラスト・文字・余白の釣り合いを設計し、横長用の新規イラストを制作する。"
    )
    typing_rules = (
        "サブテキストは背景と分離した編集可能な文字レイヤーで制作し、全文を最初から表示しない。"
        "左から右へ1文字ずつ、1文字0.04〜0.07秒でタイプ入力風に表示する。見出し・図解ラベルは最初から静止表示する。"
        "全文の改行位置と配置を先に確定し、文字が増えても中央位置・行位置・文字サイズを動かさない。"
        "単語の途中で改行しない。打ち終わりは2秒以上、文章量に応じて読める時間を保持し、表示途中で場面転換しない。"
        "元画像にサブテキストが焼き込まれている場合は、その文章部分だけ背景を復元した素材を用意し、同じ位置に文字レイヤーを重ねる。"
        "焼き込み文字の上への二重表示、静止全文を残したままのタイプ表示は禁止。背景素材と文字レイヤーを動画編集で合成する。"
        "文章が長い場合は文・文節単位のカードに分け、前の文を読める時間を確保してから次をタイプ表示する。"
    )
    prompt = (
        f"{PRODUCTION_STANDARDS}\n{INFOGRAPHIC_RULES}"
        "あなたは読者心理と視聴維持を熟知したプロのマーケティングコンサルタントであり、"
        "プロのイラストレーター兼映像ディレクターである。情報の優先順位と視線誘導を設計した、求心力のある高品質なイラスト動画を制作する。"
        f"動画全体で伝える記事の要約は『{_display_text(article_summary)}』。"
        "動画はこの要約の重要点を順番に理解できるミニストーリーとして構成し、記事と無関係な一般映像で埋めない。"
        f"{format_rules}{typing_rules}"
        f"出力は{size}、長さは{duration}を目安とし、情報量が多い場合は読む時間を優先して延長する。{layout}。文字は固定レイヤーで保護し、ズームで欠けたり変形しない。"
        "再生開始0.0秒の最初のフレームから、完成した表紙イラストと短いキャッチコピーを明るく鮮明に表示する。"
        "冒頭の黒画面、空白画面、無地背景、読み込み待ち、暗転、黒からのフェードインを一切入れない。"
        "1枚目の表紙は5〜6秒間表示する。最初の0.5秒以内に完成した表紙を表示し、視聴者がキャッチコピーとイラストを落ち着いて読める時間を確保する。"
        f"{font_spec}。上部は場面見出し、下部は具体的な補足説明とし、同じ文章を上下へ重複表示しない。"
        "下部の補足（サブテキスト）のフォントサイズは、上部の見出し（メインテキスト）の約80％に統一する。"
        f"すべての画面テキストは日本語にする。{TEXT_LAYOUT_RULES}"
        f"場面構成：{scene_script} "
        "各シーンは指定された媒体別の構図で、記事の別の要点を視覚化する。"
        "すべての場面を明るいハイキー照明、透明感のあるパステルカラー、内容に合う鮮やかなアクセントカラーで統一する。"
        "暗い、くすんだ、重苦しい、無関係な汎用映像、同じ場面の使い回しは禁止する。"
        "人の声、音声ナレーション、読み上げ音声、会話音声は一切入れない。元のnarration欄の文章はすべて画面テロップとして使用する。"
        "テロップ本文は、パソコンやスマートフォンで文字を入力しているように、左から右へ1文字ずつ現れるタイピング演出にする。"
        "1文字の表示間隔は0.04〜0.07秒を目安とし、1行を打ち終えた後は1.5〜2秒読める状態で保持する。点滅カーソルは控えめにし、読みにくい高速表示は禁止する。"
        "テロップは指定レイアウトの説明カード内、ラベルは対応する図解の近くに配置し、顔・手・重要な動作を隠さない。図解ラベルは静止表示し読む時間を確保する。"
        "前のテロップが消えてから次のテロップが始まるまでの空白は最大0.2秒とし、場面転換は0.2〜0.4秒で行う。"
        "明るくポップで前向きな、著作権上利用可能なインストゥルメンタルBGMを0.0秒から入れる。"
        "メジャーキーの軽快なピアノ、ウクレレ、柔らかなギター、控えめな手拍子と軽いパーカッションを使い、親しみ・安心感・期待感が伝わる曲調にする。"
        "子ども向けすぎる音、騒がしい音、コミカルすぎる音、暗い・不安・悲しい・重い曲調は禁止する。"
        "BGMは場面転換中も途切れさせず、テロップのタイピング演出と映像の切り替えをリズムに合わせ、終了時だけ自然にフェードアウトする。"
        "意味のない静止、BGMの音切れ、冒頭の黒フレームは禁止し、問題があれば再生成する。"
        f"{cta}。{brand_rule} Instagram、YouTube、TikTok、X、FacebookなどのSNS名、SNSロゴ、アプリアイコン、"
        "ユーザー名、保存ファイル名、拡張子、透かしを画面に表示しない。不自然な身体変形、激しい点滅、過剰な動き、記事と無関係な人物や文字の追加を避ける。"
        "画面転換は明るいクロスディゾルブまたはスライドで統一し、場面の連続性が分かるテンポにする。"
        "検品では、媒体別に指定された場面構成、記事の主要内容の網羅、横縦それぞれの画面バランスを確認する。"
        "さらに全フレームを確認し、上下テキストの重複、タイピング順序、読める保持時間、文字の欠落、"
        "テロップと人物・イラストの重なり、安全余白、場面転換、音声ナレーションが混入していないこと、BGMの明るさと音切れも確認する。"
        f"{PROFESSIONAL_REVIEW}"
    )
    return {
        "size": size,
        "duration": duration,
        "layout": layout,
        "font_spec": font_spec,
        "output_filename": filename,
        "prompt": prompt,
    }


def _article_image_prompt_item(section: dict, index: int) -> dict:
    heading = _display_text(section.get("heading", ""))
    context = _display_text(section.get("summary", ""))
    layout = "横長16:9。記事の主題を表す一場面を中心に、人物・背景・小物を自然に配置し、余白と奥行きを整える"
    return {
        "size": "1200×675", "catch_copy": "", "sub_copy": "", "labels": [],
        "font_spec": "文字なし", "layout": layout,
        "output_filename": f"ブログ_{section.get('level', 'H2')}_{index:02d}_{_safe_filename_part(heading)}.png",
        "section": index, "heading_level": section.get("level", "H2"), "heading": heading,
        "prompt": (
            "【記事に添える文字なしイメージイラスト】\n"
            f"制作資料の見出し：{heading}\n制作資料の本文：{context}\n"
            "上記は内容を理解するための資料であり、画像内に書き写さない。"
            "記事のテーマや読者の気持ちを想像できる、内容に沿った具体的な一場面を描く。"
            "表情・動作・姿勢・生活環境・背景・小物で主題を伝える。施術や運動の場面は記事に関連する場合だけ使う。"
            "見出し、要約文、細かい説明文、箇条書き、数字ラベル、吹き出し、説明カード、予約CTA、店舗名、ロゴ、透かしは描かない。"
            "文字用の帯や空欄カードも設けない。文章をまとめた図解ポスターではなく、記事を読み進めやすくする挿絵にする。"
            f"{IMAGE_QUALITY} 出力サイズ1200×675。{layout}。"
            "記事内の画像全体で明るさ・色調・タッチを統一し、各セクションで場面・視点・仕草を変える。"
            "記事にない効果や施術結果を連想させる誇張したビフォーアフターは描かない。"
            "制作工程は記事理解→場面設計→生成→記事との一致・顔・手指・身体・見切れ・余白・色調・文字混入を確認→修正→再確認。"
            "デザイナー・イラストレーター・マーケティング担当者の視点で魅力と自然さを確認する。実施していない確認を実施済みと報告しない。"
        ),
    }


def _build_creative_prompts(plan: dict, article: str, brand_name: str) -> dict:
    x_data, facebook = plan.get("x_image", {}), plan.get("facebook", {})
    threads, gbp = plan.get("threads", {}), plan.get("gbp", {})
    reel, youtube, tiktok = plan.get("reel", {}), plan.get("youtube", {}), plan.get("tiktok", {})
    horizontal = "横長の情報図解。見出しを大きく配置し、イラストの周囲に要点カード・吹き出し・ラベルを統合する"
    square = "正方形の情報図解。見出し→図解と要点→具体策の視線順で、余白のあるカードを配置する"
    vertical = "縦長の情報図解。見出しとイラスト内ラベルを統合し、右端と下端は操作UI用の安全余白を確保する"
    article_summary = " / ".join(_display_text(slide.get('body', '')) for slide in plan.get('carousel', {}).get('slides', []))
    reel_cover_visual = (reel.get("scenes") or [{}])[0].get("visual", "")
    youtube_cover_visual = (youtube.get("scenes") or [{}])[0].get("visual", "")
    tiktok_cover_visual = (tiktok.get("scenes") or [{}])[0].get("visual", "")
    prompts = {
        "x_image": _image_prompt_item(x_data.get("title", ""), x_data.get("body", ""), "1200×675", horizontal, "太めゴシック。見出し56〜72px、補足は見出しの約80％、行間1.25〜1.4倍", MEDIA_FILENAMES["x_image"], x_data.get("visual", "")),
        "facebook_eyecatch": _image_prompt_item(facebook.get("image_title", ""), facebook.get("image_body", ""), "1200×630", horizontal, "太めゴシック。見出し56〜72px、補足は見出しの約80％、行間1.25〜1.4倍", MEDIA_FILENAMES["facebook_eyecatch"], facebook.get("visual", "")),
        "gbp_image": _image_prompt_item(gbp.get("image_title", ""), gbp.get("image_body", ""), "1200×900", horizontal, "太めゴシック。見出し64〜82px、補足は見出しの約80％、行間1.25〜1.4倍", MEDIA_FILENAMES["gbp_image"], gbp.get("visual", "")),
        "threads_image": _image_prompt_item(threads.get("image_title", ""), threads.get("image_body", ""), "1080×1080", square, "太めゴシック。見出し64〜80px、補足は見出しの約80％、行間1.25〜1.4倍", MEDIA_FILENAMES["threads_image"], threads.get("visual", "")),
        "reel_cover": _image_prompt_item(reel.get("cover_title", ""), reel.get("cover_body", ""), "1080×1920", vertical, "太めゴシック。見出し72〜96px、補足は見出しの約80％、最大2行", MEDIA_FILENAMES["reel_cover"], reel_cover_visual),
        "youtube_thumbnail": _image_prompt_item(youtube.get("thumbnail_title", ""), youtube.get("thumbnail_body", ""), "1280×720", horizontal, "太めゴシック。見出し80〜110px、補足は見出しの約80％、最大2行", MEDIA_FILENAMES["youtube_thumbnail"], youtube_cover_visual),
        "tiktok_cover": _image_prompt_item(tiktok.get("cover_title", ""), tiktok.get("cover_body", ""), "1080×1920", vertical, "太めゴシック。見出し72〜96px、補足は見出しの約80％、最大2行", MEDIA_FILENAMES["tiktok_cover"], tiktok_cover_visual),
        "reel_video": _video_prompt_item(reel, "1080×1920", "約55〜60秒", MEDIA_FILENAMES["reel_video"], True, brand_name, article_summary),
        "youtube_video": _video_prompt_item(youtube, "1920×1080", "約55〜60秒", MEDIA_FILENAMES["youtube_video"], False, brand_name, article_summary),
        "tiktok_video": _video_prompt_item(tiktok, "1080×1920", "約55〜60秒", MEDIA_FILENAMES["tiktok_video"], True, brand_name, article_summary),
    }
    prompts["instagram_carousel"] = []
    for index, slide in enumerate(plan.get("carousel", {}).get("slides", [])[:9], 1):
        item = _image_prompt_item(
            slide.get("title", ""), slide.get("body", ""), "1080×1350",
            "上部に主張が伝わる見出し、中央に記事の要点を伝える図解イラストと2〜3個のラベル、下部に具体策や注意点。割合は内容に合わせて調整する",
            "太めゴシック。見出し64〜80px、サブテキストは見出しサイズの約80％（目安51〜64px）。ラベルも小さくしすぎずスマートフォンで判読できる大きさ。意味のまとまりを優先",
            f"Instagram_カルーセル_{index:02d}.png",
            slide.get("visual", ""),
            slide.get("labels", []),
        )
        item["slide"] = index
        item["prompt"] += (
            "\n【9枚共通デザイン】白・アイボリーを基調、ミントと温かいコーラルをアクセントにする（提供ブランド指定があれば優先）。"
            "太めの日本語ゴシック、同じ線と陰影のタッチ、同じ人物の顔・髪・服装設定、上部タイトル位置、左右余白、説明カードの形を統一する。"
            "1枚目で確定したスタイルを残り8枚に引き継ぐ。内容に合わせた構図の変化は中央のイラスト・図解で付ける。"
            f"この画像は全9枚中の{index}枚目。"
        )
        if index == 1:
            item["prompt"] += "表紙として、誰のどんな悩みを扱うかが一目で分かるキャッチコピーと主役の絵を最優先する。"
        elif index == 9:
            item["prompt"] += "最終ページとして要点をまとめ、提供された正式な店舗・サービス名と優しい相談・予約CTAを読みやすく配置する。未提供の店舗情報は補わない。"
        prompts["instagram_carousel"].append(item)
    sections = _article_image_sections(article, maximum=6) or [{
        "level": "H2", "heading": "記事のポイント",
        "summary": _plain_text(article, 140) or "記事の要点を視覚的に分かりやすく表現する",
    }]
    prompts["article_section_images"] = []
    for index, section in enumerate(sections, 1):
        item = _article_image_prompt_item(section, index)
        prompts["article_section_images"].append(item)
    brand_rule = (
        f"\n【正式なブランド・店舗名】{str(brand_name).strip()}。この表記をそのまま使用し、略称・英語・別名称へ変更しない。"
        if str(brand_name or "").strip() else
        "\n【店舗情報】記事に明示された正式名称・連絡方法だけを使用する。未提供の場合は一般的な相談CTAとし、架空の店舗情報を加えない。"
    )
    for key, entry in prompts.items():
        if key == "article_section_images":
            continue
        for item in (entry if isinstance(entry, list) else [entry]):
            item["prompt"] += brand_rule
    return prompts


def _validate_social_plan(data: dict) -> None:
    required = ("x_posts", "threads", "facebook", "gbp", "carousel", "reel", "youtube", "tiktok", "creative_prompts")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"SNS構成に必要な項目が不足しています：{', '.join(missing)}")
    if len(data.get("carousel", {}).get("slides", [])) != 9:
        raise ValueError("カルーセル構成が9枚ではありません。")
    for key in ("reel", "youtube", "tiktok"):
        if not data.get(key, {}).get("scenes"):
            raise ValueError(f"{key}の動画構成がありません。")
    prompts = data.get("creative_prompts", {})
    required_prompts = (
        "x_image", "facebook_eyecatch", "gbp_image", "threads_image", "reel_cover",
        "reel_video", "youtube_thumbnail", "youtube_video", "tiktok_cover",
        "tiktok_video", "instagram_carousel", "article_section_images",
    )
    if any(key not in prompts for key in required_prompts):
        raise ValueError("画像・動画制作用プロンプトが不足しています。")


def generate_social_plan(client, model: str, article: str, call_llm, brand_name: str = "") -> dict:
    prompt = f"""【完成記事からSNS投稿文・動画台本を作成】
あなたは、読者心理・購買行動・媒体特性を熟知したプロのマーケティングコンサルタントであり、
広告・出版分野で経験豊富なプロのイラストレーター兼映像ディレクターです。
以下の完成記事だけを情報源として、各SNS向けコンテンツをJSONで作成してください。

共通制作基準：
{PRODUCTION_STANDARDS}
正式なブランド・店舗名：{str(brand_name or '').strip() or '未指定。記事内の提供情報のみ使う'}
名称を勝手に略したり翻訳しない。カルーセル9枚目と動画の最後に、記事にあるサービス紹介と優しいCTAを組み込む。未提供の店舗情報・予約方法は作らない。

完成記事：
---
{article}
---

厳格な条件：
- 記事にない数値、実績、料金、資格、口コミ、効果、人物、店舗情報、研究結果を追加しない
- 医療・健康情報を断定しない
- 出力前に記事全体を内部で要約し、「悩み・原因や背景・重要ポイント・具体策・注意点・まとめ」に整理する
- 投稿文、カルーセル、動画は、記事の一部分だけでなく重要内容の全体像が順番に分かる構成にする
- 同じ文章を使い回さず、媒体ごとに最適化する
- ハッシュタグは文字列配列にする
- カルーセルは必ず9枚。1枚目は表紙、9枚目はまとめ・自然な行動喚起
- カルーセルは、1枚目＝興味を引く表紙、2枚目＝読者の悩み、3〜7枚目＝記事の重要ポイント、8枚目＝具体的な行動や注意点、9枚目＝まとめと自然な行動喚起の流れにする
- 9枚だけを順番に読むことで、元記事の結論・重要ポイント・具体策・注意点まで理解できる内容にする
- 3〜7枚目は元記事の異なるH2または主要テーマを優先して割り当て、同じ説明を言い換えて枚数を埋めない
- 各スライドのtitleは短く、bodyはそのページだけでも意味が通じる具体的な要約にする
- 各スライドにlabels配列を追加し、記事由来の具体的な要点・手順・注意点を2〜3個、各8〜22文字程度の完結した意味単位で入れる。根拠が少なければ無理に増やさない
- title、body、labelsの合計は80〜140文字程度を目安に、表紙だけは短くする。文字数に合わせて語句を切らず、自然な日本語にする
- labelsはbodyの単なる繰り返しではなく、理解や行動に役立つ具体的な情報にする。内容に合う吹き出し・比較カード・矢印・手順・チェックリストの配置をvisualに記す
- 文字はイラストと明確に区切った空白・説明カード・吹き出し内に配置する。人物の顔・身体や重要な動作を隠さず、ラベルと対象の対応を明確にする。画像だけで記事の要点が理解できるようにする
- 記事の結論と読者の悩みをつなぐ具体的な見出しで関心を引き、誇張や恐怖ではなく納得感と前向きな行動で訴求する
- カルーセル各枚のvisualは、そのスライドのtitleとbodyの意味を一目で理解できる具体的な一場面にする
- 各スライドで同じ人物の同じポーズや同じ背景を繰り返さず、表情・動作・視点・背景・小物を内容に合わせて変える
- リールとTikTokは完成したカルーセル9枚を01〜09の順に使用する約55〜60秒の縦型動画にする。既存の見出し・説明・イラストの構成は維持する
- JSONのreel・tiktokのscenesは空配列にする。アプリ側でカルーセル9枚から同じ内容の9シーンを自動作成する
- 縦型動画は1枚目を表紙、2〜8枚目を記事の解説、9枚目をまとめ・自然な行動喚起とする
- YouTubeは1920×1080・16:9専用の約1分動画。記事全体を要約する独立した5〜7シーンをyoutube.scenesに必ず作成する。表紙→悩み・結論→主要ポイント・具体策・注意点→まとめの流れで、場面数や配置をカルーセルへ無理に合わせない
- YouTubeのvisualには横長専用の構図を指定する。人物と図解の左右配置、比較2列、横方向の手順など内容に合う表現を選び、見出しと下部サブテキストの余白を確保する
- 全動画のサブテキストは編集可能な独立レイヤーで1文字ずつタイプ入力風に表示する。見出しと図解ラベルは静止表示。全文の改行位置を先に固定し、入力中のレイアウト移動や文字の二重表示を防ぐ
- 各画像は約6秒を目安に表示し、情報量に応じて延長して本文と図解ラベルを読める時間を確保する
- 縦型動画の動きはカルーセル画像への緩やかなズーム、パン、光、人物・小物の自然な微動を中心とする。YouTubeは横長用に新規制作した構図へ同様の控えめな動きを付ける
- 動画各シーンのvisualは、そのシーンのcaptionとnarrationを具体的に表す人物・表情・動作・背景・小物を指定し、無関係な汎用映像を使わない
- 全画像・全動画を、明るい自然光、透明感のあるパステルカラー、内容に合う鮮やかなアクセントカラー、前向きで親しみやすい雰囲気にする
- 暗い画面、濁った色、灰色一色、重苦しい表情、恐怖をあおる演出、幼すぎるイラストは禁止する
- 人の声や音声ナレーションは使用しない。narration欄には、動画内でタイピング風に表示する日本語テロップ本文を入れる
- 縦型動画のテロップ本文はスライドのbodyを使用する。YouTubeは各専用シーンに合う記事由来の短文をnarrationへ入れる。どちらも見出しと同じ文章を繰り返さない
- テロップ間の空白を最大0.2秒にできる構成とし、不要な間や長い余韻を作らない
- 動画のcaptionは上部に表示する短い場面見出し、narrationは音声にせず下部へ表示する自然な日本語テロップ
- 上部見出しと下部テロップへ同じ文章を重複させない
- 画面テキストは日本語の文節と意味のまとまりで自然に改行できる長さにする。単語途中の分割、助詞・句読点の行頭、1文字だけの行を避ける
- 改行後は各行の見た目の長さが近くなり、中央揃えで視覚的な重心が偏らない短文にする
- visualは人物、表情、動作、背景、小物が分かる具体的な日本語の場面説明
- JSONを途中で省略せず、次の形式以外は出力しない

{{
  "x_posts": [
    {{"text": "投稿文", "hashtags": ["#タグ"]}},
    {{"text": "別角度の投稿文", "hashtags": ["#タグ"]}},
    {{"text": "別角度の投稿文", "hashtags": ["#タグ"]}}
  ],
  "x_image": {{"title": "短い見出し", "body": "60文字以内の説明", "visual": "具体的な場面"}},
  "threads": {{"text": "投稿文", "hashtags": ["#タグ"], "image_title": "短い見出し", "image_body": "60文字以内", "visual": "具体的な場面"}},
  "facebook": {{"text": "詳しい投稿文", "hashtags": ["#タグ"], "image_title": "短い見出し", "image_body": "60文字以内", "visual": "具体的な場面"}},
  "gbp": {{"text": "GBP最新情報の投稿文", "image_title": "短い見出し", "image_body": "80文字以内", "visual": "具体的な場面"}},
  "carousel": {{"caption": "Instagramキャプション", "hashtags": ["#タグ"], "slides": [{{"title": "短い見出し", "body": "具体的な説明を40〜60文字程度", "labels": ["記事由来の具体策", "記事由来の注意点"], "visual": "図解形式・人物・各ラベルの対応先を具体的に指定"}}]}},
  "reel": {{"caption": "リール投稿文", "hashtags": ["#タグ"], "cover_title": "表紙見出し", "cover_body": "短い補足", "scenes": []}},
  "youtube": {{"title": "タイトル", "description": "概要欄", "hashtags": ["#タグ"], "thumbnail_title": "サムネイル見出し", "thumbnail_body": "短い補足", "scenes": [{{"caption": "短い見出し", "narration": "タイプ表示する具体的なサブテキスト", "visual": "横長専用の構図と人物・図解・余白の配置", "labels": ["記事由来の図解ラベル"]}}]}},
  "tiktok": {{"caption": "投稿文", "hashtags": ["#タグ"], "cover_title": "表紙見出し", "cover_body": "短い補足", "scenes": []}}
}}"""
    last_error = None
    for attempt in range(2):
        retry = "" if not attempt else "\n前回はJSONが不完全でした。文章量を調整し、必ず最後まで有効なJSONで出力してください。"
        raw = call_llm(
            client, model, prompt + retry, 16_000,
            response_mime_type="application/json", temperature=0.35,
        )
        try:
            data = _normalize_plan(_load_json_response(raw), article)
            data["creative_prompts"] = _build_creative_prompts(data, article, brand_name)
            _validate_social_plan(data)
            return data
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
    raise ValueError(f"SNS投稿文と制作プロンプトを完成できませんでした：{last_error}")


def _hashtags(value) -> str:
    return " ".join(str(tag) for tag in value) if isinstance(value, list) else str(value or "")


def social_text(plan: dict) -> str:
    parts = ["X（旧Twitter）投稿案"]
    for index, post in enumerate(plan.get("x_posts", []), 1):
        parts.append(f"\n【パターン{index}】\n{post.get('text', '')}\n{_hashtags(post.get('hashtags'))}")
    for key, label in (("threads", "Threads"), ("facebook", "Facebook"), ("gbp", "Googleビジネスプロフィール")):
        item = plan.get(key, {})
        parts.append(f"\n\n{label}投稿\n{item.get('text', '')}\n{_hashtags(item.get('hashtags'))}")
    carousel = plan.get("carousel", {})
    parts.append(f"\n\nInstagram投稿\n{carousel.get('caption', '')}\n{_hashtags(carousel.get('hashtags'))}")
    for key, label in (("reel", "Instagramリール"), ("youtube", "YouTube"), ("tiktok", "TikTok")):
        item = plan.get(key, {})
        parts.append(f"\n\n{label}\n{item.get('title', '')}\n{item.get('caption', item.get('description', ''))}\n{_hashtags(item.get('hashtags'))}")
    return "\n".join(parts).strip()


def creative_prompt_text(plan: dict) -> str:
    prompts = plan.get("creative_prompts", {})
    labels = (
        ("x_image", "X投稿画像"),
        ("facebook_eyecatch", "Facebookアイキャッチ"),
        ("gbp_image", "Googleビジネスプロフィール投稿画像"),
        ("threads_image", "Threads投稿画像"),
        ("reel_cover", "Instagramリール表紙"),
        ("reel_video", "Instagramリール動画"),
        ("youtube_thumbnail", "YouTubeサムネイル"),
        ("youtube_video", "YouTube動画"),
        ("tiktok_cover", "TikTok表紙"),
        ("tiktok_video", "TikTok動画"),
    )
    parts = ["# 画像・動画制作用プロンプト"]
    for key, label in labels:
        item = prompts.get(key, {})
        parts.append(
            f"\n\n## {label}\nサイズ：{item.get('size', '')}\n"
            f"推奨保存ファイル名：{item.get('output_filename', '')}\n"
            f"画像内キャッチコピー：{item.get('catch_copy', '')}\n"
            f"画像内補足：{item.get('sub_copy', '')}\n"
            f"レイアウト：{item.get('layout', '')}\n"
            f"フォント指定：{item.get('font_spec', '')}\n\n{item.get('prompt', '')}"
        )
    parts.append("\n\n## Instagramカルーセル9枚")
    for item in prompts.get("instagram_carousel", []):
        parts.append(
            f"\n\n### {item.get('slide', '')}枚目\nサイズ：{item.get('size', '')}\n"
            f"推奨保存ファイル名：{item.get('output_filename', '')}\n"
            f"画像内見出し：{item.get('catch_copy', '')}\n画像内説明：{item.get('sub_copy', '')}\n"
            f"レイアウト：{item.get('layout', '')}\nフォント指定：{item.get('font_spec', '')}\n\n{item.get('prompt', '')}"
        )
    parts.append("\n\n## ブログ記事内で使うセクション画像")
    for item in prompts.get("article_section_images", []):
        parts.append(
            f"\n\n### セクション{item.get('section', '')}｜{item.get('heading_level', '')}：{item.get('heading', '')}\n"
            f"サイズ：{item.get('size', '')}\n推奨保存ファイル名：{item.get('output_filename', '')}\n"
            f"画像内テキスト：なし（記事に沿ったイメージイラスト）\n"
            f"レイアウト：{item.get('layout', '')}\n\n{item.get('prompt', '')}"
        )
    return "".join(parts).strip()
