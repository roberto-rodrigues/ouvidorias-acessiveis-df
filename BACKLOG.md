# Próximos passos

Backlog do **Mapa das Ouvidorias Acessíveis do DF** (site: <https://roberto-rodrigues.github.io/ouvidorias-acessiveis-df/>).
Ordem = prioridade. Cada item tem o que fazer, por quê e o critério de "pronto".

Situação atual (base consolidada: 66 ouvidorias):

| Fonte da coordenada | Qtd | Observação |
|---|---|---|
| `validado` (equipe) | 62 | coordenada conferida manualmente |
| `shp` (shapefile SES-DF) | 3 | hospitais regionais HRC, HRG, HRPL |
| `aprox` | 1 | **ARÁQ (Água Quente)** — posicionada na RA; falta confirmar a sede |
| `osm` | 0 | — |

---

## P0 — Fechar os dados

- [x] **SECOM** — validada com a coordenada do complexo do Buriti já usada pela equipe em outros
  5 órgãos (mesmo endereço). `fonte=validado`.
- [x] **ARÁQ (Água Quente)** — posicionada dentro da própria RA (área urbana do Setor Habitacional
  Água Quente, DF-280), em vez do ponto-semente no Plano Piloto. A RA passou a aparecer no filtro
  do mapa, mesmo não existindo na base oficial das 33 RAs.
  - *Falta*: confirmar o **endereço da sede da Administração Regional** com a própria RA
    (`aguaquente.df.gov.br` → "Fale com a RA" não abre de fora; pedir por telefone/e-mail:
    (61) 98279-0076 / lucia.silva@aguaquente.df.gov.br). Enquanto isso o ponto fica como `aprox`.
- [ ] **DECISÃO PENDENTE — corrigir as coordenadas de UNDF e NOVACAP** (linhas prontas em
  `data/processed/coordenadas_a_confirmar.csv`; **não aplicadas**, aguardando aprovação):
  - **UNDF**: `-15.7369/-47.8864` (Plano Piloto) → candidato `-15.72518/-47.88460` (**Lago Norte**).
    Endereço oficial SHIN CA 2, CEP 71503-502 (contrato UNdF 053858/2025, acordo CLDF 14/2024);
    o bloco SHIN QI 2 do OSM tem o mesmo CEP e fica a ~1,3 km do ponto atual.
  - **NOVACAP**: `-15.8033/-47.9356` (Cruzeiro) → candidato `-15.81753/-47.95289` (**Guará**).
    Endereço oficial SAP Lote B, CEP 71215-000 (site da NOVACAP); o POI "Novacap" do OSM (CEP
    71215-246) fica a ~1,7 km do ponto atual.
  - *Pronto quando*: coordenada aplicada (ou divergência registrada como aceita) e RA exibida
    coerente com o endereço.
- [ ] (Opcional) marcar os 3 hospitais regionais como `validado`, já que a origem é o shapefile oficial
  da SES-DF — ou pedir confirmação de coordenada à SES.

## P1 — Qualidade do produto (site)

- [ ] **Revisão de acessibilidade do próprio site** (o projeto é sobre acessibilidade — precisa dar exemplo):
  - rodar verificação automatizada (axe-core/Lighthouse) e corrigir violações;
  - navegação completa por teclado (Tab/Enter) na lista, pinos, agrupamentos e controles;
  - `aria-live` no contador de resultados, rótulos nos botões, foco visível, contraste AA;
  - testar com leitor de tela (NVDA/VoiceOver) numa amostra de fluxos.
  - *Pronto quando*: zero violações críticas/sérias no axe e os fluxos principais operáveis só com teclado.
- [ ] **Filtro "somente pendentes de validação"** com contador visível, para a equipe acompanhar a
  qualidade do dado sem abrir planilha.
- [ ] **Exportar a lista filtrada** (CSV/planilha) — a CGDF usa muito isso para ofícios.
  - *Pronto quando*: botão "Baixar CSV" respeitando busca + RA + filtros de recurso ativos.
- [ ] **Link direto para uma ouvidoria** (`#/ouvidoria/<sigla>`) para compartilhar em e-mail/ofício.
- [ ] **Ajustes finos de mobile** em aparelho real (altura do mapa, legenda recolhida, alvos de toque).

## P2 — Engenharia e processo

- [ ] **Testes automatizados do pipeline** (`pytest`): contagem final de registros, fontes por registro,
  colunas obrigatórias, dedupe de respostas repetidas e regra de RA para Administração Regional.
  - *Pronto quando*: `make test` falha se uma nova planilha quebrar qualquer uma dessas regras.
- [ ] **`make validar`**: regenerar `pontos_pendentes_validacao_template.csv` + relatório de
  divergências (RA x endereço) numa tacada só.
- [ ] **GitHub Actions**: rodar build + checagens (e opcionalmente o axe) a cada push na `main`.
- [ ] **Runbook de atualização anual**: passo a passo da planilha nova do Selo Acessibilidade
  (consolidar 2024/2025 já está automatizado em `data/processed/merge_selo_2025_report.json`).

## P3 — Publicação e adoção

- [ ] **Publicar em endereço institucional** (ou embutir no portal da CGDF / `ouvidoria.df.gov.br`)
  em vez do GitHub Pages.
- [ ] **Avaliar tornar o repositório público** — a planilha publicada já está redigida (sem nomes de
  servidores nem links de certificados), mas o repositório é privado hoje.
- [ ] **Painel de indicadores** por RA (quantas ouvidorias, quantas com Libras presencial, quantas
  capacitadas) para leitura rápida da gestão.

---

## Comandos úteis

```bash
make dados site           # reconstrói base -> dados -> docs/index.html
make                      # base (shapefiles) + dados + site
.venv/bin/python src/build_dados.py   # só os dados
```

Arquivos-chave:

```text
data/raw/ouvidorias_coords_validadas.csv        coordenadas conferidas (precedência máxima)
data/raw/selo_acessibilidade_2024.csv           respostas consolidadas 2024/2025
data/processed/pontos_pendentes_validacao_template.csv   template para novas validações
data/processed/merge_selo_2025_report.json      relatório da consolidação das planilhas
```
