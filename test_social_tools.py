import unittest
import social_tools as s


class PromptTests(unittest.TestCase):
    def test_preserves_copy_and_labels(self):
        title = '検索意図を理解するマーケティングの具体的な進め方'
        body = '長い文章も単語の途中で切らずに保持します。' * 5
        slides = [dict(title=title, body=body, labels=['まず目的を確認', '条件を整理する'], visual='手順図') for _ in range(9)]
        plan = s._normalize_plan({'carousel': {'slides': slides}}, '## 本文\n説明です。')
        prompts = s._build_creative_prompts(plan, '## 本文\n説明です。', '')
        self.assertEqual(len(prompts['instagram_carousel']), 9)
        for image in prompts['instagram_carousel']:
            self.assertEqual(image['catch_copy'], title)
            self.assertEqual(image['sub_copy'], body)
            self.assertIn('まず目的を確認', image['prompt'])
            self.assertIn('途中で分割しない', image['prompt'])
            self.assertNotIn('完全分離', image['prompt'])
        for key in ('reel', 'youtube', 'tiktok'):
            self.assertEqual(len(plan[key]['scenes']), 9)
            self.assertEqual(plan[key]['scenes'][0]['narration'], body)
            self.assertEqual(plan[key]['scenes'][0]['labels'], slides[0]['labels'])
            if key != 'youtube':
                self.assertIn('Instagram_カルーセル_09.png', prompts[key + '_video']['prompt'])
            else:
                self.assertNotIn('Instagram_カルーセル_09.png', prompts[key + '_video']['prompt'])
            self.assertIn('まず目的を確認', prompts[key + '_video']['prompt'])

    def test_youtube_independent_and_typing(self):
        scenes = [dict(caption=f'横長見出し{i}', narration='具体策をタイプ表示する。', visual='左右比較の横長構図') for i in range(6)]
        plan = s._normalize_plan({'youtube': {'scenes': scenes}}, '## 内容\n説明です。')
        prompts = s._build_creative_prompts(plan, '## 内容\n説明です。', '')
        self.assertEqual(plan['youtube']['scenes'], scenes)
        self.assertEqual(len(plan['reel']['scenes']), 9)
        self.assertEqual(len(plan['tiktok']['scenes']), 9)
        youtube = prompts['youtube_video']['prompt']
        self.assertIn('16:9専用構図', youtube)
        self.assertIn('横長見出し5', youtube)
        self.assertNotIn('Instagram_カルーセル_', youtube)
        for key in ('reel_video', 'youtube_video', 'tiktok_video'):
            prompt = prompts[key]['prompt']
            self.assertIn('編集可能な文字レイヤー', prompt)
            self.assertIn('全文を最初から表示しない', prompt)
            self.assertIn('文字が増えても中央位置・行位置・文字サイズを動かさない', prompt)
            self.assertNotIn('その画像を読みやすい時間そのまま表示する', prompt)

    def test_legacy_and_exports(self):
        plan = s._normalize_plan({}, '## 長い見出し\n省略せずに維持する本文。')
        plan['creative_prompts'] = s._build_creative_prompts(plan, '## 内容\n本文。', '')
        self.assertIn('図解', s.creative_prompt_text(plan))
        self.assertEqual(len(plan['carousel']['slides']), 9)
        self.assertEqual(s._labels(None), [])


if __name__ == '__main__':
    unittest.main()
