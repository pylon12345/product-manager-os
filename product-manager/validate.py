from pathlib import Path
from urllib.parse import urlsplit
import re, sys, json
root=Path(__file__).parent
required=['SKILL.md','README.md','manifest.yaml','agents/openai.yaml','knowledge/glossary.md','knowledge/glossary.json','references/decision-contract.md','references/project-reality.md','references/mode-reverse-decompose.md','references/mode-improve-os.md','references/mode-delivery-os.md','references/living-sources.md','references/knowledge-base-ops.md','references/knowledge-sources.json','references/operating-loop.md','scripts/pm_kb.py','tests/test_pm_kb.py','workflows/continuous-product-loop.md','workflows/skill-improvement-loop.md','templates/project-reverse-map.md','templates/skill-badcase.md','templates/skill-change-proposal.md','templates/system-reality-map.md','templates/role-task-permission-map.md','templates/cross-surface-acceptance.md','templates/evidence-ledger.md','templates/eval-spec.md','tests/behavior/cases.json','tests/behavior/rubric.json','tests/behavior/score.py','tests/behavior/test_score.py','tests/behavior/README.md']
errors=[]
for f in required:
    if not (root/f).exists(): errors.append(f'missing: {f}')
skill=(root/'SKILL.md').read_text(encoding='utf-8')
if not skill.startswith('---\n'): errors.append('SKILL.md missing YAML frontmatter')
if '`reverse-decompose`' not in skill or '`references/mode-reverse-decompose.md`' not in skill:
    errors.append('reverse-decompose is not routed from SKILL.md')
if '`improve-os`' not in skill or '`references/mode-improve-os.md`' not in skill:
    errors.append('improve-os is not routed from SKILL.md')
refs=re.findall(r'`((?:references|templates|knowledge|workflows)/[^`]+)`', skill)
for r in refs:
    if not (root/r).exists(): errors.append(f'broken reference: {r}')
try:
    data=json.loads((root/'knowledge/glossary.json').read_text(encoding='utf-8'))
    if len(data)!=100: errors.append(f'glossary count != 100: {len(data)}')
except Exception as e: errors.append(f'glossary json invalid: {e}')
try:
    registry=json.loads((root/'references/knowledge-sources.json').read_text(encoding='utf-8'))
    entries=registry.get('sources')
    if registry.get('version') != 1 or not isinstance(entries, list) or not entries:
        errors.append('knowledge source registry schema invalid')
    else:
        ids=[]; urls=[]
        for entry in entries:
            if not isinstance(entry, dict):
                errors.append('knowledge source entry is not an object'); continue
            ids.append(entry.get('id')); urls.append(entry.get('url'))
            url=urlsplit(entry.get('url') or '')
            if url.scheme != 'https' or not url.hostname or url.username or url.password or url.fragment:
                errors.append(f'invalid knowledge source URL: {entry.get("id")}')
            if not isinstance(entry.get('enabled'), bool): errors.append(f'invalid enabled flag: {entry.get("id")}')
        if len(ids) != len(set(ids)) or len(urls) != len(set(urls)):
            errors.append('duplicate knowledge source id or URL')
except Exception as e: errors.append(f'knowledge source registry invalid: {e}')
if errors:
    print('\n'.join(errors)); sys.exit(1)
manifest=(root/'manifest.yaml').read_text(encoding='utf-8')
if not re.search(r'(?m)^version:\s*1\.2\.0\s*$', manifest): errors.append('manifest version is not 1.2.0')
if not re.search(r'(?m)^\s*- reverse-decompose\s*$', manifest): errors.append('manifest missing reverse-decompose mode')
if not re.search(r'(?m)^\s*- improve-os\s*$', manifest): errors.append('manifest missing improve-os mode')
expected_refs={'mode-competitive-intelligence.md','mode-research-ops.md','mode-pricing.md','mode-ai-economics.md','mode-experience.md','mode-reverse-decompose.md'}
missing_refs=expected_refs-{p.name for p in (root/'references').glob('*.md')}
if missing_refs: errors.append('missing core references: '+', '.join(sorted(missing_refs)))
expected_templates={'competitive-intelligence.md','research-plan.md','pricing-decision.md','ai-unit-economics.md','experience-brief.md','project-reverse-map.md'}
missing_templates=expected_templates-{p.name for p in (root/'templates').glob('*.md')}
if missing_templates: errors.append('missing core templates: '+', '.join(sorted(missing_templates)))
for path in (root/'templates').glob('*.md'):
    content=path.read_text(encoding='utf-8')
    if re.search(r"(?m)^\s*(?:Replace-Exact\b|Set-Content\b|Add-Content\b|@'\s*$|'\s*$|\*\*\* Begin Patch)", content):
        errors.append(f'possible editing-command residue in template: {path.name}')
eval_template=(root/'templates/eval-spec.md').read_text(encoding='utf-8')
for section in ('## Decision and task','## Dataset and provenance','## Eval tree and release gates','## Scoring and calibration','## Versioned run and monitoring'):
    if section not in eval_template: errors.append(f'eval template missing section: {section}')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('OK')
