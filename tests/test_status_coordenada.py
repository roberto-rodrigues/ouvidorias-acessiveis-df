"""A confiabilidade da coordenada deve aparecer também no pino e na legenda."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EstadoCoordenadaNoMapa(unittest.TestCase):
    def test_status_aproximado_em_pino_legenda_e_acessibilidade(self):
        for name in ('src/build_site.py', 'docs/index.html'):
            page = (ROOT / name).read_text(encoding='utf-8')
            with self.subTest(name=name):
                self.assertTrue("'pino pino-aprox'" in page, 'falta classe visual no pino')
                self.assertTrue('Contorno âmbar = localização aproximada' in page, 'falta legenda')
                self.assertTrue('alt:p.nome' in page, 'falta nome acessível')
                self.assertTrue("el.setAttribute('aria-label',m.options.alt)" in page, 'pino SVG sem rótulo acessível')
                self.assertTrue("p.fonte==='aprox'?' — localização aproximada'" in page, 'falta aviso no tooltip')
                self.assertTrue('.pino-aprox svg path' in page, 'falta contorno âmbar')
                self.assertFalse('#map .leaflet-pane,#map .leaflet-control-container{z-index:2}' in page, 'camadas sobrepostas bloqueiam clique no pino')
                self.assertTrue('autoPan:true,maxWidth:330' in page, 'popup pode ficar atrás dos controles')
                self.assertTrue('role="region" aria-label="Mapa das ouvidorias do DF"' in page, 'modo aplicação desnecessário')
                self.assertTrue("d.classList.add('recolhida');" in page, 'legenda aberta cobre o pino na visão geral')
                self.assertFalse("if(window.innerWidth<800){d.classList.add('recolhida')}" in page, 'legenda precisa iniciar recolhida também no desktop')
                self.assertTrue("c.setAttribute('aria-label','Abrir ouvidoria: '+p.nome)" in page, 'cartão sem ação anunciada')


if __name__ == '__main__':
    unittest.main()
