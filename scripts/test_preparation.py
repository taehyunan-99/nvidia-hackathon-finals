import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock
from lookup import load_entries,search
from classify_skills import DOMAINS,FUNCTIONS,generate
from fetch_skill import safe_path
from probe_nim import probe
from sync_guides import synchronize,git,guide_case_errors
ROOT=Path(__file__).resolve().parents[1]

class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.entries=load_entries()
    def test_domain_missions_are_discoverable(self):
        for q,expected in [('문서','documents'),('배차','routing'),('일정','allocation'),('영상','video'),('음성','voice'),('바이오','biology'),('장애','operations'),('격리','sandbox')]:
            with self.subTest(q=q):self.assertEqual(search(self.entries,q,kind='recipe',limit=1)[0]['id'],'recipe:'+expected)
    def test_declared_name_differs_from_folder(self):
        rows=search(self.entries,'bionemo-boltz2-nim',kind='skill')
        self.assertEqual(rows[0]['name'],'boltz2-nim');self.assertIn('--skill boltz2-nim',rows[0]['install'])
    def test_full_coverage_and_taxonomy(self):
        data=json.loads((ROOT/'docs/catalog/skills-index.json').read_text())
        self.assertEqual(len(data['skills']),sum(s['expected']for s in data['sources']))
        self.assertEqual(len(data['skills']),len({s['id'] for s in data['skills']}))
        for s in data['skills']:
            self.assertTrue(s['domains'] and set(s['domains'])<=DOMAINS.keys())
            self.assertTrue(s['functions'] and set(s['functions'])<=FUNCTIONS.keys())
    def test_domain_function_filter(self):
        rows=search(self.entries,kind='skill',domain='vision',function='setup',limit=50)
        self.assertTrue(rows)
        self.assertTrue(all('vision' in r['domains'] and 'setup' in r['functions'] for r in rows))
    def test_important_cross_domain_routes(self):
        skills={s['folder']:s for s in self.entries if s['kind']=='skill'}
        self.assertIn('speech',skills['nemotron-speech']['domains'])
        self.assertIn('setup',skills['nemo-retriever']['functions'])
        self.assertIn('biology',skills['bionemo-boltz2-nim']['domains'])
        self.assertIn('data',skills['data-designer']['domains'])
    def test_agent_reference_is_not_a_work_guide(self):
        for agent in (e for e in self.entries if e['kind']=='agent'):
            path=ROOT/agent['guide']
            self.assertEqual(path.name,'agent-types.md')
            self.assertIn('`'+agent['nat_type']+'`',path.read_text())
    def test_generated_navigation_avoids_reserved_guide_names(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);catalog=root/'docs/catalog';catalog.mkdir(parents=True)
            sample=next(s for s in self.entries if s['kind']=='skill' and s['folder']=='nat-installation')
            (catalog/'skills-index.json').write_text(json.dumps({'skills':[sample]}))
            generate(root)
            generated=[p for p in root.rglob('*.md')]
            self.assertTrue(generated)
            self.assertFalse(any(p.name.casefold() in {'agents.md','claude.md'} for p in generated))
            self.assertTrue((catalog/'skills/domains/agent-workflows.md').is_file())
    def test_unknown_query_no_fake_match(self):self.assertEqual(search(self.entries,'zzunregistered123'),[])
    def test_download_path_escape_rejected(self):
        for value in ['../key','/tmp/key','safe/../../key','a\\b']:
            with self.assertRaises(ValueError):safe_path(value)

class ProbeTests(unittest.TestCase):
    def responses(self):
        return [{'choices':[{'message':{'role':'assistant','content':None,'tool_calls':[{'id':'call_1','type':'function','function':{'name':'add','arguments':'{"a":17,"b":25}'}}]}}]}, {'choices':[{'message':{'content':'{"result":42}'}}]}]
    def test_actual_tool_cycle(self):
        send=Mock(side_effect=self.responses());r=probe(send,'test-model')
        self.assertTrue(r['passed']);self.assertEqual(send.call_count,2)
        self.assertEqual(send.call_args.args[0]['messages'][-1]['role'],'tool')
    def test_text_only_is_not_success(self):
        first={'choices':[{'message':{'content':'42'}}]};send=Mock(return_value=first)
        with self.assertRaises(ValueError):probe(send,'test-model')
        self.assertEqual(send.call_count,1)
    def test_wrong_result_rejected(self):
        rows=self.responses();rows[1]['choices'][0]['message']['content']='{"result":43}'
        with self.assertRaises(ValueError):probe(Mock(side_effect=rows),'test-model')
    def test_unapproved_tool_rejected(self):
        rows=self.responses();rows[0]['choices'][0]['message']['tool_calls'][0]['function']['name']='shell'
        with self.assertRaises(ValueError):probe(Mock(side_effect=rows),'test-model')

class SyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        git(self.root,'init','-q');(self.root/'scripts').mkdir()
        (self.root/'scripts/guide-pairs.json').write_text(json.dumps([['left.md','right.md']]))
    def tearDown(self):self.tmp.cleanup()
    def put(self,name,text): (self.root/name).write_text(text)
    def test_create_missing_partner_without_commit(self):
        self.put('left.md','approved');git(self.root,'add','left.md')
        self.assertEqual(synchronize(self.root),1)
        self.assertEqual((self.root/'right.md').read_text(),'approved')
        self.assertNotEqual(git(self.root,'rev-parse','--verify','HEAD').returncode,0)
    def test_reverse_direction(self):
        self.put('right.md','approved');git(self.root,'add','right.md')
        self.assertEqual(synchronize(self.root),1)
    def test_untracked_conflict_not_overwritten(self):
        self.put('left.md','new');self.put('right.md','other');git(self.root,'add','left.md')
        with self.assertRaises(ValueError):synchronize(self.root)
        self.assertEqual((self.root/'right.md').read_text(),'other')
    def test_partial_stage_is_preserved(self):
        self.put('left.md','staged');git(self.root,'add','left.md');self.put('left.md','unstaged')
        with self.assertRaises(ValueError):synchronize(self.root)
        self.assertEqual((self.root/'left.md').read_text(),'unstaged')
        self.assertFalse((self.root/'right.md').exists())
    def test_both_staged_differ_rejected(self):
        self.put('left.md','one');self.put('right.md','two');git(self.root,'add','left.md','right.md')
        with self.assertRaises(ValueError):synchronize(self.root)
    def test_lowercase_guide_is_rejected_without_overwrite(self):
        self.put('agents.md','existing content')
        self.put('right.md','existing content')
        with self.assertRaises(ValueError):synchronize(self.root,check=True)
        self.assertEqual((self.root/'agents.md').read_text(),'existing content')
    def test_nested_lowercase_guide_is_detected(self):
        nested=self.root/'docs/nested';nested.mkdir(parents=True)
        (nested/'claude.md').write_text('existing content')
        self.assertTrue(guide_case_errors(self.root,[]))
    def test_check_is_read_only(self):
        self.put('left.md','same');self.put('right.md','same')
        self.assertEqual(synchronize(self.root,check=True),0)
        self.assertEqual(git(self.root,'diff','--cached','--name-only').stdout,b'')
class GuideImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        git(self.root,'init','-q');(self.root/'scripts').mkdir()
        (self.root/'scripts/guide-pairs.json').write_text(json.dumps([['AGENTS.md','CLAUDE.md']]))
        (self.root/'AGENTS.md').write_text('canonical rules')
        (self.root/'CLAUDE.md').write_text('@./AGENTS.md\n')
    def tearDown(self):self.tmp.cleanup()
    def test_check_does_not_stage_or_expand_import(self):
        self.assertEqual(synchronize(self.root,check=True),0)
        self.assertEqual(git(self.root,'diff','--cached','--name-only').stdout,b'')
        self.assertEqual((self.root/'CLAUDE.md').read_text(),'@./AGENTS.md\n')
    def test_canonical_edits_never_copy_into_claude(self):
        git(self.root,'add','AGENTS.md','CLAUDE.md')
        (self.root/'AGENTS.md').write_text('new canonical rules')
        git(self.root,'add','AGENTS.md')
        self.assertEqual(synchronize(self.root),0)
        self.assertEqual(git(self.root,'show',':CLAUDE.md').stdout,b'@./AGENTS.md\n')
    def test_claude_edits_are_rejected_without_overwriting_canonical(self):
        (self.root/'CLAUDE.md').write_text('unreviewed rules')
        git(self.root,'add','AGENTS.md','CLAUDE.md')
        with self.assertRaises(ValueError):synchronize(self.root)
        self.assertEqual((self.root/'AGENTS.md').read_text(),'canonical rules')
        self.assertEqual((self.root/'CLAUDE.md').read_text(),'unreviewed rules')
    def test_unstaged_import_fix_cannot_hide_invalid_index(self):
        (self.root/'CLAUDE.md').write_text('old duplicated rules')
        git(self.root,'add','AGENTS.md','CLAUDE.md')
        (self.root/'CLAUDE.md').write_text('@./AGENTS.md\n')
        with self.assertRaises(ValueError):synchronize(self.root)
        self.assertEqual(git(self.root,'show',':CLAUDE.md').stdout,b'old duplicated rules')
    def test_missing_canonical_is_rejected(self):
        (self.root/'AGENTS.md').unlink()
        with self.assertRaises(ValueError):synchronize(self.root,check=True)
    def test_import_conflict_prevents_other_pair_mutation(self):
        (self.root/'scripts/guide-pairs.json').write_text(json.dumps([
            ['left.md','right.md'],['AGENTS.md','CLAUDE.md']]))
        (self.root/'left.md').write_text('skill copy');git(self.root,'add','left.md')
        (self.root/'CLAUDE.md').write_text('conflict')
        with self.assertRaises(ValueError):synchronize(self.root)
        self.assertFalse((self.root/'right.md').exists())

if __name__=='__main__':unittest.main()
