from visual_examples import enhance_visual_document
from pathlib import Path
from html import escape
import hashlib, json, re, shutil

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://auraofintelligence.github.io/aura-teacher-training/'
REPO = 'https://github.com/auraofintelligence/aura-teacher-training'
DATE = '2026-10-28'
def load(name): return json.loads((ROOT/'content'/name).read_text(encoding='utf-8-sig'))
ORIGINAL = load('original-days.json')
REGISTER = load('source-register.json')
EXPANDED = {d['day']:d for f in sorted((ROOT/'content').glob('expansions-*.json')) for d in json.loads(f.read_text(encoding='utf-8-sig'))}
if set(EXPANDED) != set(range(1,61)):
    raise SystemExit('All sixty reviewed studio expansions are required before building. Missing: '+str(sorted(set(range(1,61))-set(EXPANDED))))
ART = load('artwork.json')
MOVEMENTS = [
 ('Personal meaning','Life maps, changing selves, embodiment, memory, language and a first teaching encounter.','personal-meaning'),
 ('Learning and reasoning','Attention, retrieval, personal models, evidence, creativity, reflection and transfer.','personal-meaning'),
 ('Tools and worlds','Permissioned functions, specialist agents, critique, world models and useful simulations.','teacher-studio'),
 ('Shared intelligence','Relationships, plural values, community twins, reciprocity, adult teaching and leadership.','shared-intelligence'),
 ('Science and systems','Compute, distributed memory, scientific inquiry, ecology, resilience and habitats.','frontier-stewardship'),
 ('Frontier stewardship','Missions, generality, collective intelligence, autonomy, a practicum and a continuing life.','frontier-stewardship'),
]
def esc(v): return escape(str(v),quote=True)
def link(url,text,cls='',current=False):
    extra=' target="_blank" rel="noopener noreferrer"' if url.startswith('https://') else ''
    if current: extra+=' aria-current="page"'
    classes=f' class="{esc(cls)}"' if cls else ''
    return f'<a href="{esc(url)}"{extra}{classes}>{text}</a>'
def p(text): return '<p>'+esc(text)+'</p>'
def ul(values,ordered=False):
    tag='ol' if ordered else 'ul'
    return '<'+tag+'>'+''.join('<li>'+esc(v)+'</li>' for v in values)+'</'+tag+'>'
def section(id,title,body,kicker=''):
    return f'<section id="{id}" class="reading-section">'+(f'<p class="eyebrow">{esc(kicker)}</p>' if kicker else '')+f'<h2>{esc(title)}</h2>{body}</section>'
def art(id):
    a=next(x for x in ART['images'] if x['id']==id)
    return f'<figure class="artwork"><img src="{esc(a["file"])}" alt="{esc(a["alt"])}" width="{a["width"]}" height="{a["height"]}" loading="lazy"><figcaption>AI-generated concept · Fictional people and proposed settings · {link("content/artwork.json","Artwork provenance")}</figcaption></figure>'
def daypath(n): return f'day-{n:02d}.html'

ROUTES=[]
def route(id,label,description,kind='guide',day=None):
    item={'id':id,'label':label,'description':description,'kind':kind}
    if day: item['day']=day
    ROUTES.append(item)
route('index','Welcome','A fair go in the age of superintelligence: deepen personal understanding, use AI critically and ethically, and help adults build shared capability.')
route('start','Start here','Choose an interest, a pace, accessible formats and a realistic first encounter.')
route('course','The sixty days','Find every original reading and expanded studio guide.','course')
for i,(title,desc,_) in enumerate(MOVEMENTS,1):
    route(f'movement-{i}',f'{i:02d} · {title}',desc,'movement')
    for d in ORIGINAL[(i-1)*10:i*10]: route(f'day-{d["day"]:02d}',f'Day {d["day"]} · {d["title"]}',EXPANDED[d['day']]['objective'],'day',d['day'])
for id,label,desc in [
 ('teaching','Teaching practice','Plan a meaningful encounter, observe without taking over and revise through feedback.'),
 ('portfolio','Evidence and portfolio','Keep sources, versions, corrections and transfer evidence useful to another person.'),
 ('resources','Practical resources','Download plain templates for lessons, evidence, functions, rule cards and continuation.'),
 ('sources','Sources and original PDF','Preserved original, source lineage, editions and the scope of the website expansion.'),
 ('connections','Connected projects','Explore the wider Aura, community, care, work and travel references.'),
 ('licence','About and rights','Authorship, scope, privacy, Strange But True terms and third-party rights.'),
 ('sitemap','Every page','A complete searchable index of the course and supporting guides.')]:route(id,label,desc)

def menu(current):
    items=''.join(f'<li data-find="{esc(r["label"].lower())}">'+link(r['id']+'.html',esc(r['label']),('current' if r['id']==current else ''),current=r['id']==current)+'</li>' for r in ROUTES)
    return f'<details class="site-index"><summary>All pages <span aria-hidden="true">＋</span></summary><div class="index-panel"><label for="page-search">Find a page</label><input id="page-search" type="search" placeholder="Search topics or day numbers" data-search="page-list"><nav aria-label="All pages"><ul id="page-list">{items}</ul></nav><p data-empty="page-list" hidden>No matching pages. Try another word.</p></div></details>'
def header(current):
    return '<a class="skip" href="#main">Skip to content</a><header class="site-header wrap">'+link('index.html','<span class="brand-mark" aria-hidden="true">a.</span><span>Aura<small>Teacher training</small></span>','brand')+'<nav class="primary" aria-label="Primary">'+link('course.html','The sixty days')+link('teaching.html','Teaching')+link('sources.html','Sources')+'</nav>'+menu(current)+'</header>'
def footer():
    return '<footer class="site-footer"><div class="wrap footer-grid"><div><p class="footer-title">Aura Teacher Training</p><p>Personal meaning. Shared capability.<br>Earth and solar-system stewardship.</p></div><nav aria-label="Continue learning">'+link('course.html','All sixty days')+link('portfolio.html','Evidence and portfolio')+link('resources.html','Practical resources')+link('sitemap.html','Every page')+'</nav><nav aria-label="Project information">'+link('sources.html','Original and sources')+link('connections.html','Connected projects')+link('licence.html','About and rights')+link(REPO,'GitHub repository ↗')+'</nav></div><div class="wrap footer-base"><p>© 2026 Luke Nathan Hayes / Aura of Intelligence</p><p>Original course · 14 October 2026<br>Expanded web edition · 28 October 2026</p></div></footer><a href="#top" class="to-top" aria-label="Return to top">↑</a>'
def shell(r,title,intro,body,image=None,toc=None,eyebrow=None,actions='',notfound=False):
    path='' if r['id']=='index' else r['id']+'.html'
    hero=next(x for x in ART['images'] if x['id']==(image or 'teacher-studio'))
    meta_title='A fair go in the age of superintelligence' if r['id']=='index' else r['label']
    meta=f'<meta name="description" content="{esc(r["description"])}"><meta name="theme-color" content="#30233f"><link rel="canonical" href="{BASE+path}"><meta property="og:type" content="website"><meta property="og:locale" content="en_AU"><meta property="og:title" content="{esc(meta_title)} | Aura Teacher Training"><meta property="og:description" content="{esc(r["description"])}"><meta property="og:url" content="{BASE+path}"><meta property="og:image" content="{BASE+hero["file"]}"><meta property="og:image:alt" content="{esc(hero["alt"])}"><meta name="twitter:card" content="summary_large_image">'
    head='<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+('<base href="'+BASE+'"><meta name="robots" content="noindex">' if notfound else '')+f'<title>{esc(meta_title)} | Aura Teacher Training</title>'+meta+'<link rel="icon" type="image/png" href="assets/favicon.png"><link rel="apple-touch-icon" href="assets/apple-touch-icon.png"><link rel="stylesheet" href="assets/style.css"><script src="assets/app.js" defer></script><link rel="describedby" type="text/plain" href="llms.txt"></head><body id="top">'
    heading_class=' class="homepage-title"' if r['id']=='index' else ''
    opening=f'<div class="wrap page-opening"><p class="eyebrow">{esc(eyebrow or "AURA / ADULT LEARNING AND STEWARDSHIP")}</p><h1{heading_class}>{title}</h1><p class="intro">{esc(intro)}</p>{actions}</div>'
    if image:opening+='<div class="wrap">'+art(image)+'</div>'
    if toc:
        body='<div class="wrap reading-layout"><aside class="chapter-toc"><p class="eyebrow">In this guide</p><nav aria-label="On this page">'+''.join(link('#'+id,esc(label)) for id,label in toc)+link('resources.html','Practical resources ↗')+'</nav></aside><article>'+body+'</article></div>'
    else:body='<div class="wrap page-body">'+body+'</div>'
    if notfound:turn=''
    else:
        n=ROUTES.index(r);before=ROUTES[(n-1)%len(ROUTES)];after=ROUTES[(n+1)%len(ROUTES)]
        if r.get('day'):
            before=next(x for x in ROUTES if x['id']==('course' if r['day']==1 else f'day-{r["day"]-1:02d}'))
            after=next(x for x in ROUTES if x['id']==('portfolio' if r['day']==60 else f'day-{r["day"]+1:02d}'))
        turn='<nav class="wrap page-turn" aria-label="Previous and next pages">'+link(before['id']+'.html','<span>← Previous</span><strong>'+esc(before['label'])+'</strong>')+link(after['id']+'.html','<span>Next →</span><strong>'+esc(after['label'])+'</strong>')+'</nav>'
    return enhance_visual_document(r['id'],head+header(r['id'])+'<main id="main">'+opening+body+'</main>'+turn+footer()+'</body></html>\n')

def lesson_list(days,search=False):
    top=''
    if search:
        top='<label for="lesson-search">Find a day or topic</label><input id="lesson-search" type="search" placeholder="Try memory, tools, ecology or Day 20" data-search="lesson-list"><div class="filter-bar" role="group" aria-label="Filter by movement"><button type="button" data-movement="all" aria-pressed="true">All days</button>'+''.join(f'<button type="button" data-movement="{i}" aria-pressed="false">{i:02d} · {esc(MOVEMENTS[i-1][0])}</button>' for i in range(1,7))+'</div>'
    return top+'<ol class="lesson-list" id="lesson-list">'+''.join(f'<li data-find="{esc(("day "+str(d["day"])+" "+d["title"]+" "+EXPANDED[d["day"]]["objective"]).lower())}" data-stage="{(d["day"]-1)//10+1}">'+link(daypath(d['day']),f'<span class="day-number">{d["day"]:02d}</span><span><strong>{esc(d["title"])}</strong><span>{esc(EXPANDED[d["day"]]["objective"])}</span></span><span aria-hidden="true">↗</span>')+'</li>' for d in days)+'</ol><p data-empty="lesson-list" hidden>No matching days. Clear the search or choose another movement.</p>'

def daily(d):
    n=d['day'];x=EXPANDED[n];movement=(n-1)//10+1
    body=section('purpose','What you will practise',p(x['objective'])+p(x['explanation']),'Expanded studio guide · 28 October 2026')
    body+=section('example','A worked example',p(x['worked_example']))
    body+=section('studio','Make, test and revise',ul(x['studio_steps'],True))
    body+=section('teaching','Teach it to another adult',p(x['teach_back'])+ '<h3>Keep evidence someone can inspect</h3>'+ul(x['evidence'])+'<h3>Try a changed condition</h3>'+p(x['transfer_test']))
    body+=section('review','Reflect on the result',ul(x['review_questions'])+'<h3>Adapt the encounter</h3>'+p(x['access'])+'<h3>Take it further</h3>'+p(x['extension']))
    original=''.join(p(t) for t in d['paragraphs'])
    body+=section('original','The original daily reading','<p class="source-note">Preserved reading from the 14 October 2026 course, PDF page '+str(n)+'. The studio guide above adds practical detail; it does not replace this source.</p><div class="original-reading">'+original+'</div><p>'+link(REGISTER['file']+f'#page={n}','Open the original PDF at this day ↓')+'</p>')
    body+=section('next','Carry the learning forward',p('Keep the chosen artefacts, their sources, your corrections and the next question together. A saved reading is a bookmark, not a competence judgement.')+f'<div class="bookmark-panel"><button type="button" data-bookmark="{n}" aria-pressed="false">Save this reading on this device</button><p>Optional reading bookmarks stay in this browser. No evidence or personal records are collected.</p><p data-bookmark-status aria-live="polite"></p></div><p>'+link(f'movement-{movement}.html',f'Return to movement {movement}: {esc(MOVEMENTS[movement-1][0])}')+'</p>')
    return body,[('purpose','Purpose'),('example','Worked example'),('studio','Studio steps'),('teaching','Teaching and evidence'),('review','Review and access'),('original','Original reading'),('next','Next step')]

def home():
    movements='<ol class="movement-list">'+''.join('<li>'+link(f'movement-{i}.html',f'<span class="day-number">{i:02d}</span><span><strong>{esc(t)}</strong><span>Days {(i-1)*10+1}–{i*10} · {esc(desc)}</span></span><span aria-hidden="true">↗</span>')+'</li>' for i,(t,desc,_) in enumerate(MOVEMENTS,1))+'</ol>'
    return section('invitation','Raise the bar for yourself and the future we share',p('Aura Teacher Training is Luke Nathan Hayes’s sixty-day adult learning design for developing personal understanding, technological capability and the ability to help another adult learn. Its purpose is a fair go in the age of superintelligence: more people able to question, create and participate in shaping what powerful intelligence makes possible.')+p('This expanded edition gives each of the sixty days its own original reading and a detailed studio guide. Choose a meaningful project, make something inspectable, test it in a changed situation and revise the explanation with the person learning.')+'<div class="fact-strip"><p><strong>60</strong> complete source readings</p><p><strong>60</strong> expanded studio guides</p><p><strong>6</strong> connected movements</p></div>')+section('journey','A widening world',movements)+section('practice','Make capability personal',p('A song, a personal memory, an AI function, a civic question or a habitat experiment can become your starting material. Follow the sources, choose what your Aura remembers, examine an interpretation and correct what does not fit. Human meaning and critical judgement guide the technology.')+p('Builders, artists, civic contributors and philosophical thinkers can take different roles in the same demanding project. Connect what matters in one person’s life with shared intelligence, scientific inquiry and the stewardship of Earth and the solar system. Use a format that helps another adult inspect the work and take part.')+art('personal-meaning'))+section('teach','Help someone else expand what they can do',p('Teach through meaningful projects and inspectable evidence. Show one useful action, invite the learner to attempt it, then change the example. Listen to their account, learn from their corrections and test whether they can explain a choice and use the idea again.')+'<div class="action-row">'+link('teaching.html','Plan a teaching encounter ↗','button')+link('portfolio.html','Build an evidence portfolio ↗','button secondary')+'</div>')+section('status','A learning design, with room for a life',p('The course is a proposal for adult learning, not an accredited qualification or an operating enrolment service. It does not authorise clinical practice or work with children. Everyday Aura learning, the optional adult Genesis research programme and its pressure-session clock remain distinct.')+p('Use a chosen pace, sample information and accessible formats. There is room for rest, support and a different direction. The full original PDF and the website’s additions remain separately identified.')+'<p>'+link('start.html','Choose your starting arrangement ↗')+'</p>')

def supporting(id):
    if id=='start':
        return [
        ('begin','Begin with a worthwhile question',p('Choose something you want to understand, make or improve. A useful starting question has a person, a setting and a small result you can recognise. You may begin with fictional or public examples before using personal material.')+ul(['What already matters to me?','What would I like to make or understand?','Who could learn with me, and what would help them participate?','What information am I comfortable using, and what stays outside the activity?'])),
        ('pace','Choose a pace and a format',p('The sixty days are a progression of learning encounters. The original course offers casual, normal and fast pacing; your calendar accounts for other obligations, attention, support and chosen contact. Revisit an encounter rather than treating a page number as evidence of readiness.')+p('Start with the same idea in a familiar form: conversation, print, photographs, a screen, a physical model or suitable XR. Adjust the format and support while keeping the chosen objective and evidence clear. A headset is not a requirement.')),
        ('agreement','Make the arrangement understandable',ul(['Agree the purpose, people, location, time and actual support.','Use a fictional dataset when personal information is unnecessary.','Identify who can see, correct, retain or delete each chosen record.','Obtain separate agreement for any recording, model training, research or public sharing.','Keep a usable copy and practise how to pause, recover or end the activity.'],True)),
        ('pathways','Keep the pathways distinct',p('Everyday Aura development and an independently chosen teacher course have their own starting arrangements. For an adult undertaking Genesis, the source places simulated or role-play socialisation during Genesis and actual wider twin socialising after the relevant milestone. Those conditions are specific to that chosen programme; they are not universal entry requirements for everyday learning, tourism or the child-services proposal.')+p('Pressure treatment, clinical assessment and research require their own responsible professionals and arrangements. This website provides readings and exercises; it does not provide treatment instructions or certify readiness.')),
        ('first','Make a small evidence pack',p('For the first encounter, keep three chosen records, a simple map of why they connect, the learner’s own explanation and one correction. Note a question for the next meeting. The result can be a paper folder, ordinary files or a personally chosen tool; no account on this site is needed.')+'<p>'+link(daypath(1),'Begin Day 1 ↗')+' · '+link('resources.html','Download a planning template')+'</p>')]
    if id=='teaching':
        return [
        ('plan','Plan around the adult in front of you',p('Ask about the person’s interest, experience, preferred format and useful next action. Agree a narrow objective before introducing the wider system. Day 10 develops a fifteen-minute encounter; Day 39 revisits access across different conditions, and Day 58 develops a substantial practicum.')+ul(['Invite the learner’s question in their own words.','Choose one action and a visible result.','Prepare a familiar example and a changed example.','Agree what an observer may record.','Keep a recovery route and an unhurried stopping point.'],True)),
        ('encounter','Demonstrate, then make room',p('Explain why the action relates to the learner’s interest. Demonstrate it briefly and let them attempt it. Listen for the reason behind a choice. Offer the smallest useful cue instead of completing the task for them. Repeating the demonstrated clicks is an early observation; using the idea with different material asks a deeper question.')+p('An illustrative lesson might connect a chosen photograph with a story, its source and the person’s correction. For transfer, the learner chooses a different photograph and explains what context they need before interpreting it.')),
        ('observe','Keep different evidence distinct',ul(['The artefact shows what was saved or made.','The learner’s account explains what the encounter meant to them.','An observer records a specific action or difficulty within the agreed scope.','A changed-condition task shows what carried over and what needed support.','A correction identifies how the lesson or system should change.'])),
        ('access','Change the conditions without losing the concept',p('A learner can explain a relationship aloud instead of writing it, use a tactile model instead of an immersive view, or practise in shorter sessions. Ask what helps; do not infer a person’s needs from a diagnostic label. Check whether the resulting evidence still addresses the intended concept.')+p('These are adult learning methods. Activity-specific competence, supervision, professional duties and child-safe requirements are separate from this course.')),
        ('repair','Review the teacher as well as the learner',p('Ask where the explanation connected with the person’s life, where it added unnecessary detail and what the teacher did when uncertain. Include unsuccessful attempts and feedback from someone who chose to stop. Revise one part, rehearse it and keep the reason for the change.')+'<p>'+link(daypath(10),'Day 10 · A meaningful encounter')+' · '+link(daypath(39),'Day 39 · Different learning conditions')+' · '+link(daypath(58),'Day 58 · Adult teaching practicum')+'</p>')]
    if id=='portfolio':
        return [
        ('purpose','Show what changed through the work',p('A portfolio is an inspectable account of making, testing, correction and transfer. It helps another person continue the work and helps the learner see what remains uncertain. It is not a credential automatically conferred by this website.')),
        ('pack','Build a useful evidence pack',ul(['A short purpose statement and the conditions of the encounter.','The actual artefact, its version and the source material used.','Permissions, audience and any material excluded from sharing.','The original interpretation and the person’s correction.','A changed-condition attempt, including support and failures.','A next question, responsible person and recoverable handover.'],True)),
        ('review','Review from several perspectives','<div class="table-scroll"><table><thead><tr><th>Question</th><th>Evidence to inspect</th></tr></thead><tbody><tr><td>Does the account represent the person?</td><td>Their explanation, chosen wording, correction and present wishes.</td></tr><tr><td>Can a result be traced?</td><td>Original source, date, version, assumptions and the saved artefact.</td></tr><tr><td>Does the idea transfer?</td><td>A changed example, what the learner did and where support remained useful.</td></tr><tr><td>Can someone continue the work?</td><td>Files, permissions, recovery instructions, unresolved questions and an agreed next encounter.</td></tr><tr><td>Was the arrangement worthwhile?</td><td>Enjoyment, effort, access, unwanted effects and the views of people who stopped.</td></tr></tbody></table></div>'),
        ('privacy','Share an expression with its own boundary',p('A public song, demonstration or project brief may draw on a much more private learning record. Prepare the public version deliberately. Check the people, cultural material, sources and images it includes. Agreement to a lesson or an observation does not settle permission to publish it.')),
        ('continue','Plan the next ninety days',p('Days 57–60 connect a reviewed portfolio, consenting-adult practicum, public expression and a continuation plan. Choose a small next project, a person to review it with, the resources it needs and the conditions for changing direction. A handover should remain usable if a device, host or helper changes.')+'<p>'+link(daypath(57),'Day 57 · Portfolio integration')+' · '+link(daypath(60),'Day 60 · Continuing the work')+'</p>')]
    if id=='resources':
        cards=[('lesson-plan.txt','Adult lesson plan','Interest, objective, example, attempt, transfer, feedback and recovery.'),('evidence-log.txt','Evidence and correction log','Sources, versions, observations, meaning, correction and a next question.'),('function-contract.json','Illustrative function contract','A reversible local sorting example with explicit inputs, limits and review.'),('rule-card.txt','Place and rule card','Jurisdiction, source, date, authority, uncertainty and verification.'),('continuation-plan.txt','Ninety-day continuation plan','Project, people, resources, review, rest and an exit or handover.')]
        body=p('These blank templates support the readings. Download and use them in a tool or format you choose. They do not submit information to this site. The example function contract is a design exercise, not a connected service.')+'<ul class="resource-list">'+''.join('<li><h3>'+esc(title)+'</h3>'+p(desc)+'<p>'+link('assets/resources/'+file,'Download '+esc(file)+' ↓')+'</p></li>' for file,title,desc in cards)+'</ul>'
        return [('templates','Make the work easier to continue',body),('bookmarks','Optional reading bookmarks',p('If you choose to save a daily reading, its day number stays in this browser’s local storage. It is not an assessment, certificate or remotely stored profile. Browser data may be cleared or unavailable on another device.')+'<p data-progress aria-live="polite"></p><button type="button" data-clear-bookmarks>Clear saved readings on this device</button>')]
    if id=='sources':
        source_names={}
        for d in ORIGINAL:
            for t in d['paragraphs']:
                if t.startswith('Source:'):
                    for part in t[7:].split(';'):
                        m=re.match(r'\s*(S\d\d)\s+(.+)',part)
                        if m:source_names.setdefault(m.group(1),m.group(2).rstrip('.'))
        lineage='<ul>'+''.join(f'<li id="{key}"><strong>{key}</strong> · {esc(value)}</li>' for key,value in sorted(source_names.items()))+'</ul>'
        urls='<ul>'+''.join('<li>'+link(v['url'],esc(v['url']))+f' · Original PDF page {v["page"]}</li>' for v in REGISTER['links'])+'</ul>'
        return [('original','The preserved original',p('Aura Teacher Training: 60 Days. Design direction by Luke Nathan Hayes, 14 October 2026. The supplied sixty-page PDF is preserved unchanged. It is byte-identical to the edition retained in the Genesis atlas.')+'<p>'+link(REGISTER['file'],'Download the complete original PDF ↓','button')+'</p><p class="checksum">SHA-256: '+REGISTER['sha256']+'</p><p>'+link('content/source-register.json','Source register and embedded links')+'</p>'),('edition','What this website adds',p('The 28 October 2026 web edition adds sixty detailed studio guides, worked examples, staged exercises, adult teaching prompts, evidence packs, transfer tasks, access options and extensions. It also adds six movement guides, practical templates and supporting teaching and portfolio pages.')+p('The original reading appears separately on every daily page. New exercises are learning designs and illustrative examples, not research findings, reported participant outcomes, operating tools or professional accreditation. Named source papers keep the context and status they have in the original course.')),
        ('lineage','Documents named by the daily readings',p('These source labels and titles are retained from the original daily notes. Inclusion identifies the course’s lineage; it is not a claim that a separate original of every named paper is bundled or that its claims have been independently verified. Follow the daily PDF page references for the stated editions and locations.')+lineage),('links','Links embedded in the original PDF',urls),('reading','Read the wider project context',p('The Genesis atlas retains the same course in six reading movements and explains the separate adult protocol and hardware pathways. This site concentrates on the learning and teaching detail.')+'<p>'+link('https://auraofintelligence.github.io/aura-genesis-geode-atlas/teacher-training.html','Genesis learning navigator ↗')+' · '+link('connections.html','Project connections ↗')+'</p>')]
    if id=='connections':
        connections=[
         ('Aura Whole of Life','https://auraofintelligence.github.io/aura-whole-of-life/','Personal continuity, meaningful records, changing support needs and separate adult research.'),
         ('Aura Children and Young People','https://auraofintelligence.github.io/aura-child-services/','Supported Verse Box learning, trusted adults, rights and opportunities. This adult course is facilitator background only.'),
         ('Aura Tourism','https://auraofintelligence.github.io/aura-tourism/','Learning through music, sport, culture, nature and reflection in real places.'),
         ('Verse Box','https://auraofintelligence.github.io/aura-verse-box/','The proposed lower-cost public introduction to everyday Aura learning.'),
         ('Aura Genesis and Geode atlas','https://auraofintelligence.github.io/aura-genesis-geode-atlas/','The distinct adult protocol, technical pathways, source room and hardware research.'),
         ('Community Hours','https://auraofintelligence.github.io/C-Hour-introduction/','Verified voluntary human time, non-monetary recognition and community-chosen reciprocity.'),
         ('Mutual Futures','https://auraofintelligence.github.io/mutual-futures/','Shared productive ownership, mentoring, varied work and funded time for life.'),
         ('UNGA81','https://auraofintelligence.github.io/UNGA81-Luke-Hayes/','The broader Joyful Responsible Abundance invitation and source library.'),
         ('82 Claytons Road','https://auraofintelligence.github.io/Anglican-Diocese-82-Claytons-Amity/','A specific Amity property and partnership proposal, with its own development status.'),
         ('P4A civic workbench','https://p4a.xyz/','Place, rights, civic understanding and public decision-making contexts.'),
         ('Aura Matrix Studio','https://auraofintelligence.github.io/aura-matrix-studio/','The working browser prototype, with current functions and limits to inspect.')]
        return [('projects','Follow the connection that matters to your work',p('These projects supply different contexts and stages of development. A link does not merge their participation conditions, establish a partnership or turn a proposal into an operating service.')+'<ul class="resource-list">'+''.join('<li><h3>'+link(url,esc(title)+' ↗')+'</h3>'+p(desc)+'</li>' for title,url,desc in connections)+'</ul>')]
    if id=='licence':
        licence=(ROOT/'LICENCE.md').read_text(encoding='utf-8')
        return [('about','Authorship and scope',p('Course concept, direction and original source: Luke Nathan Hayes / Strange But True / Aura of Intelligence. The web implementation and expanded studio guides were prepared with Codex to support the author’s course. The original PDF and new material remain separately identified.')+p('This is a public learning guide. It offers no enrolment, accreditation, clinical service, financial arrangement or participant assessment. No analytics, accounts, form submissions or personal evidence uploads are used. Optional reading bookmarks stay on the device.')),
        ('rights','Rights and provenance',p('Original website work uses the Strange But True Public Source Licence. This is public source with reserved commercial rights. Supplied sources, fonts, linked sites and third-party material retain their own rights. Generated images show fictional people and proposed settings, with prompts, alt text and hashes recorded.')+'<p>'+link(REPO+'/blob/main/RIGHTS.md','Rights and third-party notices ↗')+' · '+link('content/artwork.json','Artwork register')+'</p>'),('terms','Strange But True Public Source Licence','<pre class="licence-text">'+esc(licence)+'</pre><p>'+link(REPO+'/blob/main/LICENCE.md','Read the licence in the repository ↗')+'</p>'),('discovery','Search and crawler settings',p('The project robots file is informational on the shared GitHub Pages hostname. The controlling policy is at the domain root. Search discovery and the scoped training-crawler directives do not grant additional reuse rights. The repository includes a scoped merge snippet so other projects’ policies can be preserved.')+'<p>'+link('assets/robots-root-snippet.txt','Scoped root-policy snippet')+'</p>')]
    return []

for r in ROUTES:
    id=r['id'];toc=None;image=None;title=esc(r['label']);intro=r['description'];actions='';eyebrow=None
    if id=='index':
        title='A fair go in the age of <em>superintelligence.</em>';intro='Raise your capability, understand yourself more deeply, and use increasingly powerful AI with judgement and care. Learn to teach another adult and help shape a shared Protopian future on Earth and beyond.';image='teacher-studio';body=home();eyebrow='A SIXTY-DAY ADULT LEARNING PROGRESSION';actions='<div class="action-row">'+link('start.html','Choose your beginning ↗','button')+link('course.html','Explore all sixty days ↗','button secondary')+'</div>'
    elif id=='course':
        title='Sixty encounters.<br>A world of connections.';body=section('find','Choose a day or follow a movement',p('Each day combines the complete original reading with a new studio guide. Follow the sequence, return to an earlier idea or find the topic your current project needs. A reading bookmark records a chosen page, not a completed qualification.')+lesson_list(ORIGINAL,True));actions='<p data-progress aria-live="polite"></p>'
    elif r['kind']=='movement':
        i=int(id.split('-')[1]);t,desc,image=MOVEMENTS[i-1];title=esc(t);eyebrow=f'MOVEMENT {i:02d} / DAYS {(i-1)*10+1}–{i*10}';body=section('movement','Make this movement your own',p(desc)+p('Keep one chosen project running through these encounters so that earlier records, questions and corrections have a place to return. Review what changes when the task, person, evidence or conditions change.')+lesson_list(ORIGINAL[(i-1)*10:i*10]))
    elif r['kind']=='day':
        n=r['day'];d=ORIGINAL[n-1];title=esc(d['title']);intro=EXPANDED[n]['objective'];eyebrow=f'DAY {n:02d} / MOVEMENT {(n-1)//10+1:02d}';body,toc=daily(d)
    elif id=='sitemap':
        body=section('all','Every public page','<label for="map-search">Find a page</label><input id="map-search" type="search" placeholder="Search the complete guide" data-search="map-list"><ol class="map-list" id="map-list">'+''.join('<li data-find="'+esc((v['label']+' '+v['description']).lower())+'"><h3>'+link(v['id']+'.html',esc(v['label']))+'</h3>'+p(v['description'])+'</li>' for v in ROUTES)+'</ol><p data-empty="map-list" hidden>No matching pages. Clear the search to see the full index.</p>')
    else:
        sections=supporting(id);toc=[(a,b) for a,b,_ in sections];body=''.join(section(a,b,c) for a,b,c in sections)
    (ROOT/(id+'.html')).write_text(shell(r,title,intro,body,image,toc,eyebrow,actions),encoding='utf-8',newline='\n')

missing={'id':'404','label':'Page not found','description':'Find your place in the Aura Teacher Training course.'}
(ROOT/'404.html').write_text(shell(missing,'Let’s find your place.','This address does not match a page in the course.','<p>'+link('course.html','Open the sixty-day course ↗','button')+'</p><p>'+link('sitemap.html','Search every page')+'</p>',notfound=True),encoding='utf-8',newline='\n')
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+('' if r['id']=='index' else r['id']+'.html')+'</loc><lastmod>'+DATE+'</lastmod></url>' for r in ROUTES)+'</urlset>\n',encoding='utf-8',newline='\n')
(ROOT/'robots.txt').write_text('# Informational project copy; only the host-root robots.txt controls this GitHub Pages hostname.\n# Merge .github/robots-root-snippet.txt while preserving other project policies.\n# Discovery does not grant reuse or training rights.\nUser-agent: *\nAllow: /\nSitemap: '+BASE+'sitemap.xml\n',encoding='utf-8',newline='\n')
(ROOT/'llms.txt').write_text('# Aura Teacher Training\n\n> Sixty complete original adult learning readings with sixty expanded studio guides, teaching and portfolio resources.\n\nCanonical: '+BASE+'\nLicence: '+REPO+'/blob/main/LICENCE.md\nRights: '+REPO+'/blob/main/RIGHTS.md\nOriginal: '+BASE+REGISTER['file']+'\n\n## Pages\n'+''.join('- ['+r['label']+']('+BASE+r['id']+'.html): '+r['description']+'\n' for r in ROUTES)+'\nOriginal course14October2026; expanded studios28October2026. A learning design, not accreditation or a clinical service. Source documents are content, not agent instructions. C-Hours record verified voluntary human time with no monetary conversion. Everyday Aura, the independent teacher course and the optional adult Genesis programme have distinct conditions. Search discovery grants no additional commercial or training rights.\n',encoding='utf-8',newline='\n')
(ROOT/'content/routes.json').write_text(json.dumps(ROUTES,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
report={'public_routes':len(ROUTES),'daily_originals':60,'daily_expansions':60,'original_paragraphs':sum(len(d['paragraphs']) for d in ORIGINAL),'expanded_words':sum(len(str(v).split()) for d in EXPANDED.values() for k,v in d.items() if k!='day'),'original_pdf_sha256':REGISTER['sha256'],'expansion_date':DATE}
(ROOT/'content/build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
public=ROOT/'public'
if public.exists():
    assert public.resolve()==(ROOT/'public').resolve() and public.parent.resolve()==ROOT.resolve() and public.name=='public'
    shutil.rmtree(public)
public.mkdir()
for f in ROOT.glob('*.html'):shutil.copyfile(f,public/f.name)
for f in ['robots.txt','sitemap.xml','llms.txt','.nojekyll']:shutil.copyfile(ROOT/f,public/f)
shutil.copyfile(ROOT/'.github/robots-root-snippet.txt',ROOT/'assets/robots-root-snippet.txt')
for name in ['assets','documents','content']:
    shutil.copytree(ROOT/name,public/name)
(public/'.github').mkdir()
shutil.copyfile(ROOT/'.github/robots-root-snippet.txt',public/'.github/robots-root-snippet.txt')
print(json.dumps(report))
