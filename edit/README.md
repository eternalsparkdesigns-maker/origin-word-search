# Editing this game

`index.html` is a single-file claude.ai/design bundle: fonts, React and the page runtime are
packed in a manifest, and the game itself is one JSON-encoded HTML island
(`<script type="__bundler/template">`). To change the puzzle you edit the readable copy here
and re-pack it. Everything else in `index.html` stays byte-for-byte the same.

```
 edit/template.html ──(you edit)──┐
                                  ▼
 index.html (current) ──► edit/bundle.py ──► index.html (new)
                          swaps ONLY the        │
                          template island       ▼
                                         edit/test_content.py
                                    (word rules + byte-exact re-pack)
                                                │ pass
                                                ▼
                                    push to main ─► GitHub Pages ─► Google Site embed
```

## Steps

1. Edit `edit/template.html`: the `WORDS` list (16 entries, max 15 letters, `label` is the display text), and the title and completion text.
2. Re-pack: `python3 edit/bundle.py index.html edit/template.html index.html`
3. Test: `python3 -m unittest discover -s edit -v` (must pass before pushing).
4. Push to `main`. GitHub Pages serves it and the Today at Origin Games page picks it up, no Site edit.

## Design choices and boundaries

- Only the template island is rewritten. The encoder matches the bundle's own escaping
  (`</` becomes `<\u002F`) so an unchanged template re-packs to identical bytes; the test checks this.
- No data, tracking or network calls are added. The page is public, so content stays non-sensitive:
  no patient or staff names.
- `Pelvic Floor Word Search.html` is a duplicate of `index.html`. Copy `index.html` over it after
  re-packing; a test keeps the two in sync.
- Grid fill retries up to 50 times until every word is placed (the original could silently drop a
  word, leaving the puzzle impossible to finish).
