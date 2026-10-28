"""Check the generated course, original readings and explicit Pages snapshot.

Standard-library only. This checker never imports the builder or rewrites sources.
"""
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree as ET
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://auraofintelligence.github.io/aura-teacher-training/'
PDF_SHA256 = '13bb521a9f754aedb2cb88c5af981efa778bd7ec844297d92d7256534ea2418c'
ORIGINAL_DAYS_SHA256 = '4ca7bd13a47ddcc2a348d3277348dbf89f555c8356ff3fbd71dab51bfb5b0fe2'
EXPANSION_KEYS = {'day', 'objective', 'explanation', 'worked_example', 'studio_steps', 'teach_back', 'evidence', 'transfer_test', 'review_questions', 'access', 'extension'}
PUBLIC_IDS = {'index', 'start', 'course', 'teaching', 'portfolio', 'resources', 'sources', 'connections', 'licence', 'sitemap'} | {f'movement-{n}' for n in range(1, 7)} | {f'day-{n:02d}' for n in range(1, 61)}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
TEXT_BLOCKS = {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'label', 'summary', 'pre', 'td', 'th', 'figcaption'}
errors = []
warnings = []


def require(condition, message):
    if not condition:
        errors.append(message)


def normal(text):
    return re.sub(r'\s+', ' ', text).strip()


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def project_file(value, context):
    """Resolve an explicitly relative register path without machine dependencies."""
    require(isinstance(value, str) and not re.match(r'^(?:[A-Za-z]:|/|\\)', value), f'{context}: expected a project-relative path')
    if not isinstance(value, str):
        return None
    path = (ROOT / value).resolve()
    require(path.is_relative_to(ROOT), f'{context}: path leaves the project')
    require(path.is_file(), f'{context}: missing {value}')
    return path if path.is_file() and path.is_relative_to(ROOT) else None


class Page(HTMLParser):
    """Collect visible block text without inserting spaces around inline markup."""

    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.stack = []
        self.captures = []
        self.blocks = []
        self.original_paragraphs = []
        self.original_containers = 0
        self.ids = set()
        self.references = []
        self.menu_links = []
        self.canonical = []
        self.base = None
        self.noindex = False
        self.h1 = 0
        self.skip = False
        self.feed(path.read_text(encoding='utf-8-sig'))
        self.close()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        parent = self.stack[-1] if self.stack else {}
        classes = set(a.get('class', '').split())
        hidden = parent.get('hidden', False) or 'hidden' in a or a.get('aria-hidden') == 'true' or tag in {'script', 'style', 'template'} or 'sr-only' in classes
        original = parent.get('original', False) or 'original-reading' in classes
        menu = parent.get('menu', False) or (tag == 'nav' and a.get('aria-label') == 'All pages')
        if tag not in VOID:
            self.stack.append({'tag': tag, 'hidden': hidden, 'original': original, 'menu': menu})
        depth = len(self.stack)
        if 'id' in a:
            require(a['id'] not in self.ids, f'{self.path.name}: duplicate id {a["id"]}')
            self.ids.add(a['id'])
        if tag == 'h1' and not hidden:
            self.h1 += 1
        if 'original-reading' in classes:
            self.original_containers += 1
        if tag == 'base':
            self.base = a.get('href')
        if tag == 'meta' and a.get('name') == 'robots':
            self.noindex = 'noindex' in a.get('content', '')
        if tag == 'a':
            self.references.append(('a', a.get('href', ''), a))
            if menu:
                self.menu_links.append(a.get('href', ''))
            if a.get('href') == '#main':
                self.skip = True
        if tag == 'link':
            if a.get('rel') == 'canonical':
                self.canonical.append(a.get('href'))
            elif a.get('href'):
                self.references.append(('link', a['href'], a))
        if tag in {'img', 'script', 'source', 'video', 'audio'} and a.get('src'):
            self.references.append((tag, a['src'], a))
        if tag == 'video' and a.get('poster'):
            self.references.append(('img', a['poster'], a))
        if tag == 'img':
            require(bool(a.get('alt')), f'{self.path.name}: artwork needs meaningful alt text')
            require(bool(a.get('width')) and bool(a.get('height')), f'{self.path.name}: image lacks intrinsic dimensions')
        if tag == 'form':
            require(False, f'{self.path.name}: unexpected participant-submission form')
        if tag == 'input':
            require(a.get('type') in {'search', 'button', 'checkbox', 'radio'}, f'{self.path.name}: unexpected data-entry input type {a.get("type")}')
        if tag in TEXT_BLOCKS and not hidden:
            # Block separators belong between block children, never between inline spans.
            for capture in self.captures:
                capture['parts'].append('\n')
            self.captures.append({'tag': tag, 'depth': depth, 'parts': [], 'original': original})
        if tag == 'br' and not hidden:
            for capture in self.captures:
                capture['parts'].append('\n')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1]['tag'] != tag:
            require(False, f'{self.path.name}: mismatched closing tag {tag}')
            return
        depth = len(self.stack)
        finished = [c for c in self.captures if c['depth'] == depth]
        for capture in finished:
            text = normal(''.join(capture['parts']))
            self.blocks.append(text)
            if capture['original'] and capture['tag'] == 'p':
                self.original_paragraphs.append(text)
            self.captures.remove(capture)
        self.stack.pop()

    def handle_data(self, data):
        if self.stack and self.stack[-1]['hidden']:
            return
        for capture in self.captures:
            capture['parts'].append(data)


def resolve_reference(page, value):
    resolved = urlsplit(urljoin(page.base or BASE + page.path.name, value))
    base = urlsplit(BASE)
    if resolved.scheme not in {'http', 'https'}:
        return None, resolved
    if resolved.netloc != base.netloc or not resolved.path.startswith(base.path):
        return None, resolved
    relative = unquote(resolved.path[len(base.path):]) or 'index.html'
    if relative.endswith('/'):
        relative += 'index.html'
    target = (ROOT / relative).resolve()
    require(target.is_relative_to(ROOT), f'{page.path.name}: reference leaves project: {value}')
    return target, resolved


def check():
    register = load(ROOT / 'content/source-register.json')
    require(register.get('sha256') == PDF_SHA256, 'Source register changed the immutable original PDF checksum')
    pdf = project_file(register.get('file'), 'Original PDF')
    if pdf:
        require(digest(pdf) == PDF_SHA256, 'Original PDF bytes changed')
    require(register.get('original_days_sha256') == ORIGINAL_DAYS_SHA256, 'Source register changed the immutable original-days checksum')
    original_path = ROOT / 'content/original-days.json'
    require(digest(original_path) == ORIGINAL_DAYS_SHA256, 'Original daily extraction bytes changed')
    original = load(original_path)
    require(len(original) == 60 and [d.get('day') for d in original] == list(range(1, 61)), 'Original days must cover 1–60 once, in source order')
    require(sum(len(d.get('paragraphs', [])) for d in original) == 537, 'Expected all 537 original daily paragraphs')

    expansion_files = sorted((ROOT / 'content').glob('expansions-*.json'))
    require(len(expansion_files) == 3, 'Expected three reviewed expansion files')
    expansions = [d for path in expansion_files for d in load(path)]
    counts = Counter(d.get('day') for d in expansions)
    require(counts == Counter(range(1, 61)), 'Expansions must cover each day 1–60 exactly once')
    expanded_by_day = {}
    word_counts = {}
    for d in expansions:
        day = d.get('day')
        require(type(day) is int, f'Expansion day must be an integer: {day!r}')
        require(set(d) == EXPANSION_KEYS, f'Day {day}: expansion does not have the exact eleven fields')
        for key in EXPANSION_KEYS - {'day', 'studio_steps', 'evidence', 'review_questions'}:
            require(isinstance(d.get(key), str) and bool(d.get(key, '').strip()), f'Day {day}: empty or invalid {key}')
        for key, length in [('studio_steps', 4), ('evidence', 3), ('review_questions', 3)]:
            value = d.get(key)
            require(isinstance(value, list) and len(value) == length and all(isinstance(v, str) and bool(v.strip()) for v in value), f'Day {day}: {key} requires {length} nonempty strings')
        strings = [s for key, value in d.items() if key != 'day' for s in (value if isinstance(value, list) else [value]) if isinstance(s, str)]
        require(not any(re.search(r'<\s*/?\s*[A-Za-z][^>]*>', s) for s in strings), f'Day {day}: expansion fields must contain plain text')
        word_counts[day] = len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b", ' '.join(strings)))
        expanded_by_day[day] = strings

    routes = load(ROOT / 'content/routes.json')
    ids = [r.get('id') for r in routes]
    require(len(ids) == 76 and set(ids) == PUBLIC_IDS, 'Expected the exact 76 public routes')
    require(len(ids) == len(set(ids)), 'Repeated route identifiers')
    expected_html = {f'{id}.html' for id in PUBLIC_IDS} | {'404.html'}
    require({p.name for p in ROOT.glob('*.html')} == expected_html, 'Root HTML files differ from public routes plus custom 404')
    pages = {p.name: Page(p) for p in ROOT.glob('*.html')}
    all_menu = Counter(f'{id}.html' for id in PUBLIC_IDS)
    for name, page in pages.items():
        require(page.h1 == 1, f'{name}: expected exactly one visible h1, found {page.h1}')
        require(page.skip and 'main' in page.ids and 'top' in page.ids, f'{name}: missing skip/main/top navigation')
        require(Counter(page.menu_links) == all_menu, f'{name}: All pages menu does not contain each of the 76 routes exactly once')
        require(page.canonical == [BASE + ('' if name == 'index.html' else name)], f'{name}: incorrect canonical URL')
        for tag, value, attributes in page.references:
            require(bool(value), f'{name}: empty {tag} destination')
            split = urlsplit(value)
            if split.scheme in {'http', 'https'} and tag == 'a':
                require(attributes.get('target') == '_blank' and {'noopener', 'noreferrer'} <= set(attributes.get('rel', '').split()), f'{name}: external link lacks new-tab/rel policy: {value}')
            if split.scheme in {'http', 'https'} and tag in {'script', 'img', 'video', 'audio', 'source'}:
                require(False, f'{name}: unexpected remotely loaded media/script: {value}')
            target, resolved = resolve_reference(page, value)
            if target is None:
                if not split.scheme and not value.startswith('//'):
                    require(False, f'{name}: local link resolves outside the project: {value}')
                continue
            require(target.is_file(), f'{name}: missing local asset/destination {value}')
            if target.suffix == '.html' and resolved.fragment and target.is_file():
                other = pages.get(target.name)
                require(other is not None and unquote(resolved.fragment) in other.ids, f'{name}: missing HTML fragment {value}')

    require(pages['404.html'].noindex and pages['404.html'].base == BASE, 'Custom 404 needs noindex and an absolute project base for nested recovery')
    for day in original:
        n = day['day']
        page = pages[f'day-{n:02d}.html']
        require(page.original_containers == 1, f'Day {n}: expected one separately identified original-reading container')
        require(page.original_paragraphs == [normal(t) for t in day['paragraphs']], f'Day {n}: original paragraphs changed, hidden, reordered or missing')
        visible_blocks = set(page.blocks)
        for text in expanded_by_day.get(n, []):
            require(normal(text) in visible_blocks, f'Day {n}: expanded field absent from the visible daily guide: {text[:90]!r}')

    links = register.get('links', [])
    require(len(links) == 8, 'Expected all eight original embedded PDF link records, including duplicates')
    embedded_counts = Counter(v.get('url') for v in links)
    source_counts = Counter(value for tag, value, a in pages['sources.html'].references if tag == 'a')
    for value, count in embedded_counts.items():
        require(source_counts[value] >= count, f'Source page lost an embedded link occurrence: {value}')

    tree = ET.parse(ROOT / 'sitemap.xml')
    locs = [element.text for element in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    expected_locs = Counter(BASE + ('' if id == 'index' else id + '.html') for id in PUBLIC_IDS)
    require(Counter(locs) == expected_locs, 'XML sitemap must list the exact 76 canonical public pages, excluding 404')
    map_links = {value for tag, value, a in pages['sitemap.html'].references if tag == 'a'}
    require(set(all_menu) <= map_links, 'Readable sitemap omits public pages')

    artwork = load(ROOT / 'content/artwork.json')
    images = artwork.get('images', []) if isinstance(artwork, dict) else artwork
    require(bool(images), 'Missing original artwork register')
    for image in images:
        identifier = image.get('id', image.get('file', '?'))
        path = project_file(image.get('file'), f'Artwork {identifier}')
        recorded_hash = image.get('sha256', image.get('sha256_webp'))
        require(isinstance(recorded_hash, str) and bool(re.fullmatch(r'[0-9a-fA-F]{64}', recorded_hash)), f'Artwork {identifier}: missing SHA-256')
        if path and recorded_hash:
            require(digest(path) == recorded_hash.lower(), f'Artwork {identifier}: output checksum changed')
        require(bool(image.get('prompt')) and bool(image.get('alt')), f'Artwork {identifier}: missing prompt or alt provenance')
        require(isinstance(image.get('width'), int) and isinstance(image.get('height'), int), f'Artwork {identifier}: missing intrinsic dimensions')
    rights = ROOT / 'RIGHTS.md'
    require(rights.is_file(), 'Missing source, artwork and font rights register')
    font_files = [p for p in (ROOT / 'assets').rglob('*') if p.suffix.lower() in {'.ttf', '.woff', '.woff2', '.otf'}]
    if font_files:
        font_notices = [p for p in (ROOT / 'assets').rglob('*') if p.is_file() and re.search(r'(?:OFL|LICEN[CS]E)', p.name, re.I)]
        require(bool(font_notices), 'Bundled font files require their font licence notices')
        if rights.is_file():
            require('font' in rights.read_text(encoding='utf-8-sig').lower(), 'Rights register must explain the font provenance')
    if register.get('licence_sha256'):
        require(digest(ROOT / 'LICENCE.md') == register['licence_sha256'], 'Strange But True licence checksum changed')
    else:
        warnings.append('No licence_sha256 recorded; the checker will enforce it once the reviewed source register contains it.')

    # Follow only styles actually used by pages, avoiding unused historical source CSS.
    css_queue = {(ROOT / value).resolve() for page in pages.values() for tag, value, a in page.references if tag == 'link' and a.get('rel') == 'stylesheet' and not urlsplit(value).scheme}
    seen_css = set()
    combined_css = ''
    while css_queue:
        path = css_queue.pop()
        if path in seen_css or not path.is_file():
            continue
        seen_css.add(path)
        css = path.read_text(encoding='utf-8-sig')
        combined_css += '\n' + css
        for value in re.findall(r'url\(\s*[\'\"]?([^\)\'\"]+)[\'\"]?\s*\)', css):
            if value.startswith(('data:', '#')):
                continue
            require(not urlsplit(value).scheme, f'{path.name}: unexpected remote font/style asset {value}')
            if urlsplit(value).scheme:
                continue
            asset = (path.parent / unquote(urlsplit(value).path)).resolve()
            require(asset.is_relative_to(ROOT) and asset.is_file(), f'{path.name}: missing CSS asset {value}')
            if asset.suffix == '.css':
                css_queue.add(asset)
    require(bool(re.search(r'font-size\s*:\s*(?:18px|1\.125rem)\b', combined_css)), 'CSS must declare the 18px paragraph minimum; browser review checks computed text sizes')
    for script in (ROOT / 'assets').rglob('*.js'):
        text = script.read_text(encoding='utf-8-sig')
        if script == ROOT / 'assets/matrix-studio/vendor/three.min.js':
            # The unchanged Studio rendering dependency contains optional resource loaders.
            # Pin its reviewed bytes; sample hosts do not call those network loaders.
            require(sha256(script.read_bytes()).hexdigest() == '9274bbcec8d96168626c732b5d31c775aa8cfb7eaa0599bec0c175908a2c1ce2', 'Unexpected Three.js dependency bytes')
            require((script.parent / 'THREE-LICENSE.txt').is_file(), 'Missing Three.js licence notice')
            continue
        require(not re.search(r'\bfetch\s*\(|\bXMLHttpRequest\b|\bsendBeacon\s*\(|\bWebSocket\s*\(|https?://[^\s\'\"]*(?:analytics|tagmanager|doubleclick)', text, re.I), f'{script.name}: unexpected network/data-upload or analytics code')

    public = ROOT / 'public'
    expected_package = {ROOT / filename for filename in expected_html} | {ROOT / filename for filename in ['robots.txt', 'sitemap.xml', 'llms.txt', '.nojekyll', '.github/robots-root-snippet.txt']}
    for directory in ['assets', 'documents', 'content']:
        expected_package.update(path for path in (ROOT / directory).rglob('*') if path.is_file())
    expected_relative = {path.relative_to(ROOT).as_posix() for path in expected_package}
    actual_relative = {path.relative_to(public).as_posix() for path in public.rglob('*') if path.is_file()}
    require(expected_relative == actual_relative, f'Public snapshot file inventory differs: missing {sorted(expected_relative-actual_relative)}, extra {sorted(actual_relative-expected_relative)}')
    for path in expected_package:
        published = public / path.relative_to(ROOT)
        require(path.is_file() and published.is_file() and digest(path) == digest(published), f'Public snapshot differs: {path.relative_to(ROOT).as_posix()}')
    return {'status': 'passed' if not errors else 'failed', 'public_routes': len(routes), 'html_files': len(pages), 'original_paragraphs': sum(len(d['paragraphs']) for d in original), 'expanded_days': len(expansions), 'expansion_words': {'total': sum(word_counts.values()), 'minimum': min(word_counts.values()), 'maximum': max(word_counts.values())}, 'original_embedded_link_records': len(links), 'artwork_records': len(images), 'font_files': len(font_files), 'public_files': len(actual_relative), 'checks': ['local links/assets/fragments including 404 base', 'external new-tab/rel policy', 'one visible h1 and all 76 menu entries', 'canonical and XML/readable sitemap coverage', 'immutable PDF and original-days hashes', '537 exact visible original paragraphs in day order', 'all expansion schema fields visible on correct days', 'all eight embedded source-link records', 'artwork provenance/hashes and font notices', '18px CSS declaration with browser review required', 'no analytics or network upload code', 'public snapshot inventory and byte equality'], 'warnings': warnings, 'errors': errors}


if __name__ == '__main__':
    try:
        report = check()
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as exc:
        errors.append(f'Unable to complete checks: {exc}')
        report = {'status': 'failed', 'warnings': warnings, 'errors': errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(1 if errors else 0)
