# Próximos passos

Backlog do **Mapa das Ouvidorias Acessíveis do DF** (site: <https://roberto-rodrigues.github.io/ouvidorias-acessiveis-df/>).
Ordem = prioridade. Cada item tem o que fazer, por quê e o critério de "pronto".

Situação atual (base consolidada: 66 ouvidorias):

| Fonte da coordenada | Qtd | Observação |
|---|---|---|
| `validado` (equipe) | 61 | coordenada conferida manualmente |
| `shp` (shapefile SES-DF) | 3 | hospitais regionais HRC, HRG, HRPL |
| `osm` (Nominatim) | 1 | SECOM — ainda sem conferência humana |
| `aprox` | 1 | **ARÁQ (Água Quente)** — sem coordenada |

---

## P0 — Fechar os dados

- [ ] **ARÁQ — Administração Regional de Água Quente**: único ponto sem coordenada (fica no ponto-semente,
  no Plano Piloto). Consequência: o marcador aparece longe da RA real e a RA derivada também sai errada.
  - *Como*: obter o endereço da sede no portal da RA (`aguaquente.df.gov.br` → "Fale com a RA" /
    "Sobre a RA") ou com a própria administração; preencher a linha em
    `data/raw/ouvidorias_coords_validadas.csv` e rodar `make dados site`.
  - *Pronto quando*: `fonte=validado` para ARÁQ e `aprox` = 0 na base.
- [ ] **SECOM — validar a coordenada** hoje vinda do OpenStreetMap (`Anexo do Palácio do Buriti, Praça do Buriti`).
  - *Pronto quando*: linha da SECOM no arquivo validado (`fonte=validado`).
- [ ] **Confirmar 2 divergências entre endereço e RA derivada**:
  - **NOVACAP** — endereço "SAP, Bloco A, Lote 1, SIA" mas o ponto cai na RA **Cruzeiro**.
  - **UNDF** — endereço "Complexo de Ensino Superior, Lago Norte" mas o ponto cai na RA **Plano Piloto**.
  - *Como*: ajustar o ponto ou criar uma lista de exceções de RA (mesma regra já usada para
    Administrações Regionais em `src/build_dados.py`).
  - *Pronto quando*: RA exibida bate com o endereço validado (ou com a justificativa registrada).
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
