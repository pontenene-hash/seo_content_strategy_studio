import json
import unittest
from io import BytesIO
from zipfile import ZipFile
import social_tools as s
from download_tools import social_download_bundle
from reset_tools import reset_article_state

class NewFeatureTests(unittest.TestCase):
    def test_generated_gbp_export_and_zip(self):
        data={k:{} for k in ('threads','facebook','gbp')}
        data['x_posts']=[]
        data['gbp_video']={'scenes':[{'caption':f'要点{i}','narration':'記事のポイントを確認します。','visual':'明るい相談の場面'} for i in range(5)]}
        prompts=[]
        def model(*args,**kwargs):
            prompts.append(args[2]);return json.dumps(data,ensure_ascii=False)
        plan=s.generate_social_plan(None,'test','## 記事\n記事本文です。',model,'ぽんて')
        p=plan['creative_prompts']['gbp_video']['prompt']
        for word in ('30秒以内','1200×900','タイプライター','ぽんて','24〜30秒','要点4'): self.assertIn(word,p)
        self.assertNotIn('約55〜60秒',p)
        with ZipFile(BytesIO(social_download_bundle(plan,'20261022_170000'))) as z:
            text=z.read(z.namelist()[0]).decode('utf-8-sig')
            self.assertIn('Googleビジネスプロフィール動画',text)
            self.assertIn('要点4',text)
    def test_reset_keeps_settings_only(self):
        state={'social_brand_name':'ぽんて','integrated_brand_name':'ぽんて','url_use_ipv4':True,'api_key':'secret','model':'test','keyword_article_keyword':'古い','url_result':{},'seo_work':{},'social_article_upload':b'old','rewrite_result':{},'research_keyword':'前','competitor_result':{}}
        reset_article_state(state)
        self.assertEqual(set(state),{'social_brand_name','integrated_brand_name','url_use_ipv4','api_key','model'})
