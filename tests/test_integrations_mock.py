"""Simulações das integrações. NÃO são homologação de OpenAI/Higgsfield reais."""
from __future__ import annotations
import base64
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _common import SkillError, save_json, load_json
import editar_imagem_openai as image_api
import higgsfield_runner as higgs

class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload=payload; self.status_code=status
        self.headers={"x-request-id":"simulated-request"}
    def json(self): return self.payload

class ImageMockTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.image=self.root/'original.png'
        Image.new("RGB",(160,288),"white").save(self.image)
        b=io.BytesIO(); Image.new("RGB",(160,288),"blue").save(b,format="PNG")
        self.payload={"data":[{"b64_json":base64.b64encode(b.getvalue()).decode()}],"usage":{"total_tokens":1}}
    def tearDown(self): self.temp.cleanup()
    def test_decode_real_image_bytes(self):
        data=image_api.parse_result(self.payload)
        with Image.open(io.BytesIO(data)) as im: self.assertEqual(im.size,(160,288))
    def test_invalid_image_response_rejected(self):
        with self.assertRaises(SkillError): image_api.parse_result({"data":[]})
    @patch.dict(os.environ,{"OPENAI_API_KEY":"fake-local-unit-test"})
    def test_generation_mock_receipt_and_duplicate_guard(self):
        out=self.root/'imagem1.png'; ledger=self.root/'ledger.json'
        with patch.object(image_api.requests,"post",return_value=FakeResponse(self.payload)) as call:
            state=image_api.edit_image([self.image],"Teste",out,"fake-test-model","auto","high",ledger,1)
            self.assertTrue(out.exists()); self.assertEqual(call.call_count,1)
            self.assertEqual(state['status'],'image_generated_not_visually_reviewed')
            with self.assertRaises(SkillError):
                image_api.edit_image([self.image],"Teste",out,"fake-test-model","auto","high",ledger,1)
            self.assertEqual(call.call_count,1)
    @patch.dict(os.environ,{"OPENAI_API_KEY":"fake-local-unit-test"})
    def test_timeout_not_retried(self):
        out=self.root/'imagem1.png'; ledger=self.root/'ledger.json'
        with patch.object(image_api.requests,"post",side_effect=image_api.requests.Timeout("simulated")) as call:
            with self.assertRaises(SkillError):
                image_api.edit_image([self.image],"Teste",out,"fake-test-model","auto","high",ledger,1)
            self.assertEqual(call.call_count,1)
            self.assertEqual(load_json(out.with_suffix('.request-state.json'))['status'],'uncertain_do_not_resubmit')

class HiggsMockTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        for file in ('original.mp4','imagem1.png','schema.json'):
            (self.root/file).write_text('SYNTHETIC TEST ONLY',encoding='utf8')
        (self.root/'prompt.txt').write_text('Edite @video1 usando @imagem1.',encoding='utf8')
        self.plan={'mode':'automatic','operation':'model','id':'fake-test-model','schema_file':'schema.json',
             'video':'original.mp4','images':['imagem1.png'],'prompt_file':'prompt.txt',
             'input_mapping':{'video_flag':'video-references','image_flag':'image-references'},
             'parameters':{'aspect_ratio':'9:16','generate_audio':False},
             'review':{'schema_verified':True,'supports_video_edit':True,'references_reviewed':True,
                'source_properties_checked':True,'input_mapping_verified':True,'notes':'Simulação local, sem consulta de modelo.'}}
        self.path=self.root/'plan.json'; save_json(self.path,self.plan)
    def tearDown(self): self.temp.cleanup()
    def test_command_has_files_and_no_shell(self):
        command,plan=higgs.build_command(self.path)
        self.assertEqual(command[:3],['generate','create','fake-test-model'])
        self.assertIn(str(self.root/'original.mp4'),command)
        self.assertIn('--image-references',command)
        self.assertNotIn('--wait',command)
    def test_manual_mode_cannot_submit(self):
        self.plan['mode']='manual'; save_json(self.path,self.plan)
        with self.assertRaises(SkillError): higgs.build_command(self.path)
    def test_unreviewed_schema_rejected(self):
        self.plan['review']['schema_verified']=False; save_json(self.path,self.plan)
        with self.assertRaises(SkillError): higgs.build_command(self.path)
    def test_reserved_flags_rejected(self):
        self.plan['parameters']['prompt']='override'; save_json(self.path,self.plan)
        with self.assertRaises(SkillError): higgs.build_command(self.path)
    def test_quoted_cost_cannot_exceed_authorized_limit(self):
        with self.assertRaises(SkillError):
            higgs.submit(self.path,self.root/'ledger.json',1,150,100)
        self.assertFalse((self.root/'ledger.json').exists())
    def test_submit_mock_receipt_prevents_duplicate(self):
        response=subprocess.CompletedProcess([],0,json.dumps({'job_id':'fake-job-123'}),'')
        with patch.object(higgs.shutil,'which',return_value='/fake/higgsfield'),patch.object(higgs,'run_cli',return_value=response) as call:
            state=higgs.submit(self.path,self.root/'ledger.json',1,20,30)
            self.assertEqual(state['job_id'],'fake-job-123')
            with self.assertRaises(SkillError):
                higgs.submit(self.path,self.root/'ledger.json',1,20,30)
            self.assertEqual(call.call_count,1)
    def test_unknown_response_blocks_blind_resubmission(self):
        response=subprocess.CompletedProcess([],0,'different format','')
        with patch.object(higgs.shutil,'which',return_value='/fake/higgsfield'),patch.object(higgs,'run_cli',return_value=response) as call:
            with self.assertRaises(SkillError):
                higgs.submit(self.path,self.root/'ledger.json',1,20,30)
            self.assertTrue(self.path.with_suffix('.higgs-state.json').exists())
            self.assertEqual(call.call_count,1)
