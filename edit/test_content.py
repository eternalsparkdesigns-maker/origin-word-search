"""Content tests for this game. Run from the repo root:  python3 -m unittest discover -s edit -v"""
import json, random, re, sys, unittest, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'edit'))
from bundle import enc, split

def js_list(src, name):
    body = re.search(name + r' = \[(.*?)\];', src, re.S).group(1)
    return re.findall(r"'([A-Z]+)'", body)

SRC = (ROOT / 'edit/template.html').read_text()

class WordSearch(unittest.TestCase):
    def setUp(self):
        body = re.search(r'WORDS = \[(.*?)\];', SRC, re.S).group(1)
        self.items = re.findall(r"word: '([A-Z]+)',\s*label: '([^']+)'", body)

    def test_sixteen_unique_words(self):
        words = [w for w, _ in self.items]
        self.assertEqual(len(words), 16); self.assertEqual(len(set(words)), 16)

    def test_labels_match_words(self):
        for w, l in self.items:
            self.assertEqual(re.sub(r'[^A-Z]', '', l.upper()), w)

    def test_fit_grid_boundary(self):
        size = int(re.search(r'const SIZE = (\d+)', SRC).group(1))
        for w, _ in self.items:
            self.assertLessEqual(len(w), size, w)
            self.assertGreaterEqual(len(w), 2, w)  # selection needs 2+ cells

    def test_no_old_words(self):
        old = {'POSTPARTUM','PRENATAL','WELLNESS','STRENGTH','BLADDER','POSTURE','BREATHE','HEALING',
               'THERAPY','TENSION','PELVIC','PELVIS','FASCIA','MUSCLE','KEGEL','CORE'}
        self.assertFalse(old & {w for w, _ in self.items})

    def test_placement_retries_until_all_fit(self):
        self.assertIn('if (this.buildGrid()) return;', SRC)
        self.assertIn('Object.keys(wordPlacements).length !== this.WORDS.length) return false', SRC)

    def test_placement_success_rate(self):
        """Port of buildGrid(): with 50 rebuilds the chance of a missing word must be ~0."""
        words = sorted((w for w, _ in self.items), key=len, reverse=True)
        DIRS = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        rng = random.Random(7); S = 15; ok = 0; N = 400
        for _ in range(N):
            g = [['']*S for _ in range(S)]; placed = 0
            for w in words:
                for _ in range(400):
                    dr, dc = rng.choice(DIRS); r, c = rng.randrange(S), rng.randrange(S)
                    er, ec = r+dr*(len(w)-1), c+dc*(len(w)-1)
                    if not (0 <= er < S and 0 <= ec < S): continue
                    cells = [(r+dr*i, c+dc*i) for i in range(len(w))]
                    if all(g[a][b] in ('', w[i]) for i, (a, b) in enumerate(cells)):
                        for i, (a, b) in enumerate(cells): g[a][b] = w[i]
                        placed += 1; break
            ok += placed == len(words)
        p_fail = 1 - ok / N
        self.assertGreater(ok / N, 0.5)
        self.assertLess(p_fail ** 50, 1e-9)
class Bundle(unittest.TestCase):
    def test_index_matches_template(self):
        s = (ROOT / 'index.html').read_text(); m = split(s)
        self.assertEqual(json.loads(m.group(2)), SRC)
        self.assertEqual(enc(json.loads(m.group(2))), m.group(2))  # re-pack is byte-exact
        self.assertNotIn('</script', m.group(2))  # must not close the island early

    def test_duplicate_page_in_sync(self):
        self.assertEqual((ROOT / 'index.html').read_bytes(), (ROOT / 'Pelvic Floor Word Search.html').read_bytes())

if __name__ == '__main__':
    unittest.main()
