"""EX47: gerador real, sem navegador e sem dependências simuladas."""
import unittest
from html.parser import HTMLParser
import engine

class Rows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.rows = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        row = [] if a.get('role') == 'row' else None
        if row is not None:
            self.rows.append(row)
        if a.get('role') in ('cell', 'columnheader'):
            for _, ancestor in reversed(self.stack):
                if ancestor is not None:
                    ancestor.append(a)
                    break
        if tag not in ('input', 'br', 'hr', 'img', 'meta', 'link'):
            self.stack.append((tag, row))
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

class MenuColumn(unittest.TestCase):
    def test_header_total_and_tracks(self):
        for menu in (False, True):
            for delete in (False, True):
                for selection in (False, True):
                    with self.subTest(menu=menu, delete=delete, selection=selection):
                        s = engine.grid(
                            [dict(k='nome', l='Nome'), dict(k='q', l='Quantidade', t='num', agg='sum')],
                            [dict(id='a', v=dict(nome='Registro', q=2))],
                            gid='ex47', menu_linha=menu, dele=delete, sel=selection, search=False)
                        p = Rows(); p.feed(s)
                        # sc-for representa as colunas de dados; a célula extra alinha cabeçalho e total.
                        expected = 1 + int(selection) + int(menu or delete)
                        self.assertEqual(len(p.rows[0]), expected)
                        self.assertEqual(len(p.rows[-1]), expected)
                        self.assertIn('repeat('+str(2+int(selection)+int(menu or delete))+', auto)', s)
                        self.assertEqual(engine.GRIDS[-1]['del'], delete)

if __name__ == '__main__':
    unittest.main()
