import json
import re


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
    "イラスト内への文字配置を許可する。背景に説明カードや十分な余白を設け、文字と対象を近づけて対応関係を明確にする。"
    "1画像1主題、強い見出し1つ、具体的な要点2〜3つを基本とし、情報源が少ない場合は水増ししない。"
    "本文を丸ごと貼らず、見出し→図解→具体策の順で視線を誘導する。画像内の同じ文章の重複や装飾だけのラベルは禁止。"
    "読者自身の悩みと得られる理解を結び付け、明るい表情や具体的な行動場面で共感を生む。誇張、恐怖訴求、根拠のない効果保証は禁止。"
    "指定された記事由来の情報だけを使い、数値・口コミ・比較結果・因果関係を創作しない。条件や注意点を削って意味を変えない。"
    "情報量は小さい文字で増やさず、図解と階層化で増やす。スマートフォン表示で読める余白と高コントラストを確保する。"
    "日本語を正確に描けない生成ツールでは、文字なしの図解素材を作り、指定文言を編集可能なテキストレイヤーで後から配置する。"
)

PROFESSIONAL_REVIEW = (
    "納品前に、プロのイラストレーター兼アートディレクターとして100％表示とスマートフォン縮小表示の両方で最終検品する。"
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
    for video_key in ("reel", "youtube", "tiktok"):
        video = data.setdefault(video_key, {})
        if not isinstance(video, dict):
            video = {}
            data[video_key] = video
        video["scenes"] = [dict(scene) for scene in video_scenes]
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
        f"{INFOGRAPHIC_RULES}"
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
        layout = "横型の図解カードへ再配置し、人物の周囲の吹き出しやラベルを維持する。画像を引き伸ばしたり文字を切り落とさない"
        font_spec = "太めの日本語ゴシック体。表紙メイン88〜112px、表紙サブはメインの約80％、場面見出し64〜80px、下部補足は見出しの約80％、最大2行、行間1.25〜1.4倍"
        cta = "最後の3〜4秒は、記事内で確認できる次の行動を自然に案内し、必要に応じて概要欄のリンクへ誘導する"
    brand = _plain_text(brand_name, 30)
    brand_rule = f"ブランド名『{brand}』は必要な場合のみ控えめに表示する。" if brand else ""
    prompt = (
        f"{INFOGRAPHIC_RULES}"
        "あなたは読者心理と視聴維持を熟知したプロのマーケティングコンサルタントであり、"
        "プロのイラストレーター兼映像ディレクターである。情報の優先順位と視線誘導を設計した、求心力のある高品質なイラスト動画を制作する。"
        f"動画全体で伝える記事の要約は『{_display_text(article_summary)}』。"
        "動画はこの要約の重要点を順番に理解できるミニストーリーとして構成し、記事と無関係な一般映像で埋めない。"
        "入力素材としてInstagram_カルーセル_01.pngからInstagram_カルーセル_09.pngまでの9枚を使用する。"
        "9枚を01→09の順番で並べ替えずに使い、画像の内容・イラスト・見出し・説明を動画の中心にする。"
        "カルーセルと別の内容や別の結論を作らず、この9枚で記事の内容を要約した一本の動画にする。"
        "画像内の見出しは所定位置を維持し、説明文は同じ説明カード内でタイピング表示する。"
        "元画像に文字が焼き込まれていてタイピング化できない場合は、追加テロップを重ねず、その画像を読みやすい時間そのまま表示する。"
        f"出力は{size}、長さは{duration}を目安とし、情報量が多い場合は読む時間を優先して延長する。{layout}。文字は固定レイヤーで保護し、ズームで欠けたり変形しない。"
        "再生開始0.0秒の最初のフレームから、完成した表紙イラストと短いキャッチコピーを明るく鮮明に表示する。"
        "冒頭の黒画面、空白画面、無地背景、読み込み待ち、暗転、黒からのフェードインを一切入れない。"
        "1枚目の表紙は5〜6秒間表示する。最初の0.5秒以内に完成した表紙を表示し、視聴者がキャッチコピーとイラストを落ち着いて読める時間を確保する。"
        f"{font_spec}。上部は場面見出し、下部は具体的な補足説明とし、同じ文章を上下へ重複表示しない。"
        "下部の補足（サブテキスト）のフォントサイズは、上部の見出し（メインテキスト）の約80％に統一する。"
        f"すべての画面テキストは日本語にする。{TEXT_LAYOUT_RULES}"
        f"場面構成：{scene_script} "
        "各シーンは対応するカルーセル画像の構図・人物・表情・背景・小物を維持し、記事の別の要点を視覚化する。"
        "すべての場面を明るいハイキー照明、透明感のあるパステルカラー、内容に合う鮮やかなアクセントカラーで統一する。"
        "暗い、くすんだ、重苦しい、無関係な汎用映像、同じ場面の使い回しは禁止する。"
        "人の声、音声ナレーション、読み上げ音声、会話音声は一切入れない。元のnarration欄の文章はすべて画面テロップとして使用する。"
        "テロップ本文は、パソコンやスマートフォンで文字を入力しているように、左から右へ1文字ずつ現れるタイピング演出にする。"
        "1文字の表示間隔は0.04〜0.07秒を目安とし、1行を打ち終えた後は1.5〜2秒読める状態で保持する。点滅カーソルは控えめにし、読みにくい高速表示は禁止する。"
        "テロップは元画像の説明カード内、ラベルは対応する図解の近くに配置し、顔・手・重要な動作を隠さない。図解ラベルは静止表示し読む時間を確保する。"
        "前のテロップが消えてから次のテロップが始まるまでの空白は最大0.2秒とし、場面転換は0.2〜0.4秒で行う。"
        "明るくポップで前向きな、著作権上利用可能なインストゥルメンタルBGMを0.0秒から入れる。"
        "メジャーキーの軽快なピアノ、ウクレレ、柔らかなギター、控えめな手拍子と軽いパーカッションを使い、親しみ・安心感・期待感が伝わる曲調にする。"
        "子ども向けすぎる音、騒がしい音、コミカルすぎる音、暗い・不安・悲しい・重い曲調は禁止する。"
        "BGMは場面転換中も途切れさせず、テロップのタイピング演出と映像の切り替えをリズムに合わせ、終了時だけ自然にフェードアウトする。"
        "意味のない静止、BGMの音切れ、冒頭の黒フレームは禁止し、問題があれば再生成する。"
        f"{cta}。{brand_rule} Instagram、YouTube、TikTok、X、FacebookなどのSNS名、SNSロゴ、アプリアイコン、"
        "ユーザー名、保存ファイル名、拡張子、透かしを画面に表示しない。不自然な身体変形、激しい点滅、過剰な動き、元画像にない人物や文字の追加を避ける。"
        "画面転換は明るいクロスディゾルブまたはスライドで統一し、9枚の連続性が分かるテンポにする。"
        "映像の検品では、9枚すべてが順番通り使用され、記事の主要内容が動画全体で要約されていることを確認する。"
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
            "太めゴシック。見出し64〜80px、本文40〜52px、図解ラベル36〜44pxを目安に、スマートフォン縮小表示で判読できる大きさ。行数より意味のまとまりを優先",
            f"Instagram_カルーセル_{index:02d}.png",
            slide.get("visual", ""),
            slide.get("labels", []),
        )
        item["slide"] = index
        prompts["instagram_carousel"].append(item)
    sections = _article_image_sections(article, maximum=6) or [{
        "level": "H2", "heading": "記事のポイント",
        "summary": _plain_text(article, 140) or "記事の要点を視覚的に分かりやすく表現する",
    }]
    prompts["article_section_images"] = []
    for index, section in enumerate(sections, 1):
        item = _image_prompt_item(
            section.get("heading", ""), section.get("summary", ""), "1200×675", horizontal,
            "太めゴシック。見出し56〜72px、補足は見出しの約80％、1行15〜18文字以内、行間1.25〜1.4倍",
            f"ブログ_{section.get('level', 'H2')}_{index:02d}_{_safe_filename_part(section.get('heading', ''))}.png",
            f"記事の{section.get('level', 'H2')}『{section.get('heading', '')}』。要点：{section.get('summary', '')}",
        )
        item.update({"section": index, "heading_level": section.get("level", "H2"), "heading": section.get("heading", "")})
        prompts["article_section_images"].append(item)
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
- イラスト内に文字を入れてよい。人物の顔・手や重要な動作を隠さず、ラベルと対象の対応を明確にする。画像だけで記事の要点が理解できるようにする
- 記事の結論と読者の悩みをつなぐ具体的な見出しで関心を引き、誇張や恐怖ではなく納得感と前向きな行動で訴求する
- カルーセル各枚のvisualは、そのスライドのtitleとbodyの意味を一目で理解できる具体的な一場面にする
- 各スライドで同じ人物の同じポーズや同じ背景を繰り返さず、表情・動作・視点・背景・小物を内容に合わせて変える
- リール、TikTok、YouTubeは、完成したカルーセル9枚を01〜09の順に使用する約55〜60秒の動画にする
- 動画はカルーセル9枚と同じ見出し・説明・イラストを使い、別の要約や別のストーリーへ変更しない
- JSONのreel・youtube・tiktokのscenesは空配列にする。アプリ側でカルーセル9枚から同じ内容の9シーンを自動作成する
- 1枚目を表紙、2〜8枚目を記事の解説、9枚目をまとめ・自然な行動喚起として、記事の内容を一本の動画で要約する
- 各画像は約6秒を目安に表示し、情報量に応じて延長して本文と図解ラベルを読める時間を確保する
- 動画の動きはカルーセル画像への緩やかなズーム、パン、光、人物・小物の自然な微動を中心とし、元画像を別物へ描き直さない
- 動画各シーンのvisualは、そのシーンのcaptionとnarrationを具体的に表す人物・表情・動作・背景・小物を指定し、無関係な汎用映像を使わない
- 全画像・全動画を、明るい自然光、透明感のあるパステルカラー、内容に合う鮮やかなアクセントカラー、前向きで親しみやすい雰囲気にする
- 暗い画面、濁った色、灰色一色、重苦しい表情、恐怖をあおる演出、幼すぎるイラストは禁止する
- 人の声や音声ナレーションは使用しない。narration欄には、動画内でタイピング風に表示する日本語テロップ本文を入れる
- テロップ本文はスライドのbodyをそのまま使用し、見出しと同じ文章を繰り返さない。ラベルも同じ内容を維持する
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
  "youtube": {{"title": "タイトル", "description": "概要欄", "hashtags": ["#タグ"], "thumbnail_title": "サムネイル見出し", "thumbnail_body": "短い補足", "scenes": []}},
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
            f"画像内見出し：{item.get('catch_copy', '')}\n画像内補足：{item.get('sub_copy', '')}\n"
            f"レイアウト：{item.get('layout', '')}\nフォント指定：{item.get('font_spec', '')}\n\n{item.get('prompt', '')}"
        )
    return "".join(parts).strip()
