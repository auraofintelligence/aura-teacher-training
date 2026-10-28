# Aura Teacher Training

A sixty-day adult learning progression by Luke Nathan Hayes, with an expanded studio guide for every day. Raise human capability, deepen self-understanding and engage with increasingly powerful AI critically and ethically. The purpose is a fair go and a shared Protopian future in the age of superintelligence, connecting personal Aura development and adult teaching with civic space stewardship of Earth and the solar system.

Canonical website: https://auraofintelligence.github.io/aura-teacher-training/

## What is included

76 public pages plus a custom 404: sixty original daily readings and sixty expanded studio guides, six movements, a searchable course, adult teaching and portfolio guidance, downloadable templates, sources, related projects, rights and a complete sitemap. Original PDF and embedded links are preserved; website additions are clearly dated. Four original concept images have prompt, alt-text and checksum provenance.

Every daily expansion adds a concrete worked example, four studio steps, adult teach-back, three evidence items, a changed-condition test, review questions, access options and an extension. These are learning designs, not reported outcomes or an accreditation service.

## Visual and editorial direction

The light reading design uses plum/violet for links and primary controls, with blue and gold accents. The artwork follows the author's supplied visual references and A Protopian Gambit lyric collection: cinematic humanistic futurism, meaningful personal intelligence, constructive civic ambition, joy and consent. Four distinct scenes connect adult teaching, revisable personal meaning, critical civic collaboration and Earth/space habitat experiments. Warm timber, nature and human relationships coexist with purposeful technology.

Active illustrations use versioned `*-protopia-v3.webp` files. Original images remain available; previous active metadata, exact new prompts and the basenames and hashes of the supplied style/concept references are recorded in `content/artwork.json`. Earlier paused neutral-purple drafts were not promoted. The images show fictional people and imagined capabilities, not operating services, reported outcomes or official endorsement.

## Build and preview

Use Python 3.12 or newer and Node for the browser-script syntax check. No package installation or build-time network access is required.

    python scripts/build.py
    python scripts/check.py
    node --check assets/app.js
    python -m http.server 4198 --bind 127.0.0.1

The generator reads content/ and writes complete root HTML plus an ignored public/ deployment snapshot. The GitHub Pages workflow builds, verifies and deploys that snapshot. Source extraction was prepared once from the supplied PDF; CI uses the reviewed JSON and unchanged original, without a PDF dependency.

## Scope and privacy

Adult learning, everyday Aura and the optional Genesis research pathway have distinct arrangements. This course does not confer a clinical or professional qualification or authorise work with children. Examples are illustrative. C-Hours recognise verified voluntary contribution without monetary conversion.

No accounts, analytics, personal records, evidence uploads or form submissions. Optional reading bookmarks store only chosen day numbers in the current browser and can be cleared. They are not competence assessments.

## Rights and discovery

Strange But True Public Source Licence; original sources and third-party fonts keep their rights. See LICENCE.md, RIGHTS.md and content/artwork.json. The project robots.txt is informational on GitHub Pages. The controlling shared-host policy is at https://auraofintelligence.github.io/robots.txt; .github/robots-root-snippet.txt supplies only this project's scoped rules. Discovery grants no additional reuse or training rights.
