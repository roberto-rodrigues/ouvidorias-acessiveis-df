# Ouvidorias acessíveis DF — instruções locais

## Escopo

Mapa estático Leaflet gerado por `src/build_site.py`, publicado em `docs/`. Antes de editar, ler `git status --short --branch` e preservar alterações alheias. Documentação não exige reconstruir site ou dados. Verificar Makefile antes de executar o build solicitado.

## Requisitos deste mapa (não regras universais de Leaflet)

- Visão geral com limites das RAs visíveis, sem rótulos permanentes que poluam o mapa.
- Basemap OSM detalhado a partir do zoom 13, com atribuição legível.
- Clicar em pino ou cartão aproxima ao zoom 16 e abre popup; cobrir pontos isolados e agrupados.
- Hover do pino mostra nome da ouvidoria; não depender exclusivamente de hover em touch/teclado.
- Preservar busca sem acento/caixa, botão de limpeza e responsividade.
- Alterar esses requisitos somente se o pedido atual os modificar.

## Dados e validação humana

Preservar registros válidos, proveniência e os campos sensíveis fora da publicação. Coordenadas validadas pela equipe têm precedência. Inferência por endereço, proximidade ou geocodificação é candidata/aproximada, nunca validação humana. Aplicar planilha devolvida pelo usuário no escopo solicitado; não corrigir outros pontos silenciosamente. Não decidir pendências antigas sem nova autorização.

## Evidência e publicação

- Documentação: revisar diff e caminhos; `git diff --check`.
- Lógica: testes focados; visual/interação: navegador e screenshots nos tamanhos pertinentes.
- `marker.fire`, `dispatchEvent`, `map.setView` e probes DOM são testes programáticos, não cliques reais. Viewport móvel não equivale a aparelho físico.
- Preservar exit code de builds/testes; não encadear `| tail`, `| head` ou `|| echo`.
- No fluxo de alterações UI solicitado pelo usuário, verificar antes de publicar conforme autorização vigente; revisão documental isolada não implica push/deploy.
- Após publicação autorizada, verificar o conteúdo servido, não só o sucesso de git push. Não afirmar resultado visual sem inspecioná-lo.
