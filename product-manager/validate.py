from pathlib import Path
import re, sys, json
root=Path(__file__).parent
required=['SKILL.md','README.md','manifest.yaml','agents/openai.yaml','knowledge/glossary.md','knowledge/glossary.json','references/decision-contract.md','references/project-reality.md','references/mode-reverse-decompose.md','references/mode-delivery-os.md','references/living-sources.md','references/operating-loop.md','workflows/continuous-product-loop.md','templates/project-reverse-map.md','templates/system-reality-map.md','templates/role-task-permission-map.md','templates/cross-surface-acceptance.md','templates/evidence-ledger.md','templates/eval-spec.md','tests/behavior/cases.json','tests/behavior/rubric.json','tests/behavior/score.py','tests/behavior/test_score.py','tests/behavior/README.md']
errors=[]
for f in required:
    if not (root/f).exists(): errors.append(f'missing: {f}')
skill=(root/'SKILL.md').read_text(encoding='utf-8')
if not skill.startswith('---\n'): errors.append('SKILL.md missing YAML frontmatter')
if '`reverse-decompose`' not in skill or '`references/mode-reverse-decompose.md`' not in skill:
    errors.append('reverse-decompose is not routed from SKILL.md')
refs=re.findall(r'`((?:references|templates|knowledge|workflows)/[^`]+)`', skill)
for r in refs:
    if not (root/r).exists(): errors.append(f'broken reference: {r}')
try:
    data=json.loads((root/'knowledge/glossary.json').read_text(encoding='utf-8'))
    if len(data)!=100: errors.append(f'glossary count != 100: {len(data)}')
except Exception as e: errors.append(f'glossary json invalid: {e}')
if errors:
    print('\n'.join(errors)); sys.exit(1)
manifest=(root/'manifest.yaml').read_text(encoding='utf-8')
version_match = re.search(r'(?m)^version:\s*(\d+\.\d+\.\d+)\s*$', manifest)
if version_match is None:
    errors.append('manifest version is not a valid release version')
else:
    version = version_match.group(1)
    if f'# Product Manager Skill v{version}' not in skill.splitlines():
        errors.append('SKILL.md version differs from manifest')
    readme = (root/'README.md').read_text(encoding='utf-8')
    if f'# AI Product Manager OS v{version}' not in readme.splitlines():
        errors.append('README.md version differs from manifest')
if not re.search(r'(?m)^\s*- reverse-decompose\s*$', manifest): errors.append('manifest missing reverse-decompose mode')
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
