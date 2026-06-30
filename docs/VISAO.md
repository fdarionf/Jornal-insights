# jornal-insights — Visão do Projeto

Documento vivo que registra **para onde vamos**, **o que já decidimos** e **ideias inteligentes** discutidas durante o desenvolvimento. Atualizar conforme o projeto evolui.

---

## 1. Objetivo

Sistema de **insights para jornalistas**: coletar notícias de feeds RSS configuráveis, organizar o que importa e gerar análises úteis — não só resumir um artigo isolado, mas entender **como um assunto evolui no tempo** e **como diferentes fontes cobrem a mesma história**.

**Público:** redações, jornalistas, editores que precisam de contexto rápido sobre o que está acontecendo agora e nas últimas semanas.

**Foco do valor:** cobertura **atual** e **recente**. Notícia velha perde relevância para o tipo de insight que queremos entregar.

---

## 2. Diferencial (vs produtos existentes)

Produtos parecidos existem **em pedaços**, mas a combinação abaixo é o nicho do projeto:

| Produto / tipo | O que faz | Lacuna para nós |
|---|---|---|
| Google News, Apple News, Feedly | Agregam fontes | Pouco insight editorial profundo |
| Ground News | Mesma história, várias fontes | Menos foco em redação BR + agente customizado |
| Meltwater, Cision, Talkwalker | Monitoramento enterprise | Caro, genérico |
| Feedly Leo | RSS + resumo por IA | Contexto temporal limitado |

**Nosso diferencial:**

1. Fontes **sob medida** (`data/sources.json`)
2. **Dedup** — não inflar com a mesma notícia repetida
3. **Agrupamento por assunto** — cluster de notícias relacionadas
4. **Agente com memória temporal** — insight sobre evolução do tema (ex.: últimos 7–30 dias), não só o artigo de hoje
5. **Motor de pauta** — INSIGHTS on-demand: ideias editoriais, lacunas de cobertura, envolvidos e sugestões de fonte

---

## 3. Premissas de desenvolvimento

- **Aprendizado primeiro:** o produto é consequência do estudo; prioridade em entender cada linha (modo tutor).
- **Ambiente Windows** para codar (Poetry, `.venv` no projeto, Cursor).
- **Docker e banco de dados** (futuro): VM Linux via VirtualBox — evitar WSL2, Hyper-V e Docker Desktop no host Windows.
- **Stack atual:** Python 3.12+, Poetry, httpx, feedparser, Ruff (CLI + Run on Save).

---

## 4. Pipeline (visão geral)

```
sources.json
    → fetch (HTTP)
    → parse (RSS → dict)
    → enriquecer (fonte, categoria)
    → dedup
    → persistir
    → agrupar por assunto (cluster)
    → agente analisa cluster + janela temporal
    → insights
```

### Formato de um artigo (atual — collector)

```python
{
    "title": str,
    "link": str,
    "fonte": str,           # ex.: "Folha - Mundo"
    "categoria": str,       # ex.: "Mundo"
    "published_at": str,    # ISO 8601 UTC, ex.: "2026-06-30T20:13:38+00:00"; None se feed sem data
}
```

### Campos futuros (banco / produto)

| Campo | Uso |
|---|---|
| `collected_at` | quando entrou no sistema |
| `cluster_id` | agrupamento por assunto |
| `summary` | resumo neutro do cluster (sempre visível na UI) |
| `destaque_portal` | ângulo que o portal enfatizou (1 linha, gerado) |
| `content_hash` | dedup alternativo |

---

## 5. Estado atual

**Fase 1 concluída** — collector com persistência em JSON (`src/collector.py`).

| Função | Responsabilidade |
|---|---|
| `load_sources()` | Lê `data/sources.json` |
| `fetch_feed()` | GET no feed via httpx |
| `parse_feed()` | XML → artigos + fonte/categoria + `published_at` ISO |
| `save_articles()` | Grava `all_articles` em `data/articles.json` |
| `main()` | Orquestra coleta, acumula, imprime resumo, salva |

**Resultado validado:** 9 fontes com HTTP 200, ~900 artigos por execução.

**Correções aplicadas:**
- G1 RS: URL corrigida para `https://g1.globo.com/rss/g1/rs/` (faltava `/g1/` no path)
- `published_at`: ISO 8601; `None` quando o feed não traz data

**Artefatos:**
- `data/sources.json` — fontes RSS (versionado)
- `data/articles.json` — snapshot da coleta (gitignored; sobrescrito a cada run)

**Próximo passo imediato (Fase 2):** PostgreSQL na VM Linux + dedup por `link` na coleta (sem SQLite intermediário).

---

## 6. Roadmap por fases

### Fase 1 — Collector ✅ concluída

- [x] Listar fontes em JSON
- [x] Buscar feeds HTTP
- [x] Parsear RSS com feedparser
- [x] Enriquecer artigo com fonte/categoria
- [x] Acumular todos os artigos numa lista
- [x] Salvar em JSON (`save_articles`)
- [x] Normalizar `published_at` para ISO 8601 (+ `None` se sem data)
- [x] Corrigir URL G1 RS

**Pendente (não bloqueia Fase 2):**

- [ ] **Testes básicos** — prioridade: `parse_feed` com XML mockado (sem rede); ver §6.1
- [ ] Retry de rede no `fetch_feed` (2–3 tentativas em timeout/5xx)
- [ ] User-Agent com email de contato real

### Fase 2 — Persistência e qualidade dos dados (em andamento)

- [ ] **PostgreSQL na VM Linux** (VirtualBox + Docker; dados em volume persistente)
- [ ] Schema `articles` (`link` UNIQUE, `title`, `fonte`, `categoria`, `published_at`, `collected_at`)
- [ ] Módulo `db.py` — conexão + insert/upsert
- [ ] Integrar collector → banco (substituir ou complementar JSON)
- [ ] **Dedup por `link`** (unique constraint + `ON CONFLICT DO NOTHING`)
- [ ] **Retenção (TTL):** apagar ou arquivar notícias > 60–90 dias (máx. 2–3 meses)
- [ ] Job agendado de limpeza (`DELETE WHERE published_at < ...`)
- [ ] Índice em `published_at` e `link`

### 6.1 Testes — escopo mínimo (quando retomar)

| Teste | O quê | Tempo estimado |
|---|---|---|
| `test_parse_feed` | XML fixture → valida title, link, `published_at` | ~30–60 min |
| `test_parse_feed_sem_data` | entry sem `published_parsed` → `published_at` é `None` | incluído acima |
| Mock httpx | opcional; depois do parse | Fase 2+ |

**Não é cobertura completa** — só proteger o parser que mais evolui.

### Fase 3 — Inteligência (agrupamento)

- [ ] **Dedup avançado:** título similar, hash de conteúdo
- [ ] **Clustering:** notícias sobre o mesmo assunto → `cluster_id`
  - Opções: embeddings + similaridade, keywords, ou híbrido
- [ ] Detecção de “mesma história, ângulos diferentes” entre fontes

### Fase 4 — Insights com agente (motor de pauta)

- [ ] UI **História agrupada** — template §9.1 (sempre visível ao abrir cluster)
- [ ] Botão **INSIGHTS** — gera conteúdo on-demand (template §9.2); não carregar por padrão
- [ ] RAG sobre artigos + clusters + janela temporal (dia / semana / mês)
- [ ] Outputs do INSIGHTS:
  - assuntos quentes e evolução no período
  - o que cada portal destacou (com links)
  - **lacunas** — o que foi mal abordado ou ausente na cobertura
  - **envolvidos** — indivíduos e instituições citados
  - **quem procurar** — sugestões de fonte/especialista para entrevista
  - **sugestões de pauta** — bullets acionáveis para o dia
- [ ] Extração de entidades (nomes, cargos) — quando possível
- [ ] Disclaimers na UI: sugestões são heurísticas; jornalista valida antes de publicar

### Fase 5 — Produto

- [ ] Agendamento da coleta (cron / task scheduler)
- [ ] Configuração de fontes via UI (opcional)
- [ ] Métricas e observabilidade

---

## 7. Decisões técnicas registradas

| Decisão | Motivo |
|---|---|
| **httpx** para HTTP | Cliente moderno, reutiliza conexão com `Client` |
| **feedparser** em vez de XML manual | RSS tem variações; lib madura abstrai formatos |
| **Poetry** | Gerenciamento de deps e venv |
| **Ruff via CLI + Run on Save** | Extensão Ruff trava no Cursor ([issue #943](https://github.com/astral-sh/ruff-vscode/issues/943)); workaround com script `.vscode/ruff-format.cmd` |
| **Funções separadas** (`load` / `fetch` / `parse`) | Uma responsabilidade por função; testável |
| **`extend` vs `append`** | `extend` achata a lista; `append` aninharia listas |
| **Passar `source` para `parse_feed`** | Parser não sabe a fonte só pela response HTTP |
| **PostgreSQL direto (sem SQLite)** | Evitar refatoração dupla; VM Linux + volume persistente |
| **`published_at` ISO via `calendar.timegm`** | `published_parsed` do feedparser é UTC struct |
| **JSON como snapshot temporário** | `articles.json` gitignored; banco será fonte de verdade na Fase 2 |
| **G1 RS URL** | Padrão `/rss/g1/{região}/`, não `/rss/{região}/` |

---

## 8. Regras de negócio (ideias validadas)

### Retenção de dados

- Não acumular notícias **indefinidamente**
- Manter janela **quente** de ~30–90 dias (até 2–3 meses no máximo)
- Considerar **arquivar** (JSON frio) antes de deletar do banco ativo

### Dedup

| Nível | Como | Quando |
|---|---|---|
| 1 | URL única (`link`) | Desde o banco |
| 2 | Título normalizado / similar | Coleta ou pós-processo |
| 3 | Similaridade semântica | Fase de clustering |

Objetivo: não coletar 15 vezes a mesma matéria republicada; não confundir o agente.

### Agrupamento e contexto temporal

- Notícias sobre **o mesmo assunto** → um **cluster**
- Agente analisa o **cluster** + artigos da **janela temporal**, não só 1 RSS
- Exemplo de insight desejado: *“Reforma X: Folha enfatizou impacto fiscal; G1 focou reação política; esta semana entrou novo elemento Y.”*

Isso é o coração do produto — separa “agregador” de “ferramenta de redação”.

### INSIGHTS = motor de pauta (não é resumo extra)

Objetivo: o jornalista **não precisa sair do produto** para montar a pauta do dia. Ao clicar em **INSIGHTS**, o agente usa o **cluster atual** + **notícias relacionadas no período** (semana, mês) e entrega ideias editoriais acionáveis.

| Camada | Visibilidade | Propósito |
|---|---|---|
| **História agrupada** | Sempre | Ver o fato, comparar portais, acessar links |
| **INSIGHTS** | Só após botão | Ideias para pauta, lacunas, envolvidos, quem procurar |

**Resumo geral** = o que aconteceu (neutro). **INSIGHTS** = o que o jornalista pode fazer com isso hoje.

---

## 9. Experiência do jornalista (templates UX)

Referência de UI para Fase 4. Dois blocos distintos: visualização do cluster (passiva) e geração de pauta (ativa).

### 9.1 História agrupada (sempre visível)

```
📰 Reforma tributária — 4 fontes · atualizado hoje

── Resumo geral ──
Síntese neutra do fato, sem opinião. 2–4 frases.
(Gerado ao agrupar o cluster.)

── O que cada portal destacou ──
• [Folha](link-folha)      → impacto fiscal nas empresas de médio porte
• [G1](link-g1)            → reação de governadores do Nordeste
• [Estadão](link-estadao)  → cronograma de votação no Congresso
• [Valor](link-valor)      → efeito no mercado e nos ADRs

── Fontes ──
• Folha — "Reforma mira empresas e muda alíquota…" [abrir ↗]
• G1 — "Governadores criticam proposta…" [abrir ↗]
• Estadão — "Câmara prevê votação em julho…" [abrir ↗]
• Valor — "Mercado reage com cautela…" [abrir ↗]

┌─────────────────────────────────────┐
│  💡 INSIGHTS                        │  ← botão; conteúdo só após clicar
└─────────────────────────────────────┘
```

**Regras de UX (história agrupada):**

| Elemento | Regra |
|---|---|
| Cabeçalho | Título canônico + N fontes + data da atualização |
| Resumo geral | Sempre visível; neutro; curto (2–4 frases) |
| Destaques por portal | Nome do portal = **link âncora** para a matéria; 1 bullet com o ângulo destacado |
| Fontes | Lista completa (portal, título, link) — redundante de propósito, para quem não clicou no nome nos destaques |
| INSIGHTS | Botão visível; **não** expandir nem gerar conteúdo até o clique |

### 9.2 INSIGHTS — motor de pauta (on-demand)

Exibido **somente** após o jornalista clicar em **INSIGHTS**. Entradas: cluster + artigos relacionados na janela temporal (configurável: dia / semana / mês).

```
── Contexto (últimos 7 dias) ──
• Tema em alta: reforma tributária (+3 fontes vs semana passada)
• Relacionado: votação no Congresso, reação de governadores

── Lacunas (mal abordado) ──
• Nenhum portal ouviu especialistas em impacto regional
• G1 e Folha não mencionaram efeito em MEIs
• Cronograma citado sem confirmar com fonte oficial

── Envolvidos ──
• [Nome] — relator da proposta
• [Nome] — presidente da comissão
• Governadores citados: X, Y (só reação genérica nas matérias)

── Quem procurar ──
• Economista [área] — contraponto ao enfoque fiscal
• Assessoria do relator — confirmar data de votação
• Sindicato [setor] — impacto em empregos (não apareceu na cobertura)

── Sugestões de pauta ──
1. Matéria: "O que falta na cobertura da reforma esta semana"
2. Entrevista: [Nome] sobre impacto em [região/setor]
3. Comparativo: por que Valor fala mercado e G1 fala política
```

**Regras de UX (INSIGHTS):**

| Output | Descrição |
|---|---|
| Contexto temporal | Assuntos quentes; evolução vs período anterior |
| Lacunas | O que foi superficial, omitido ou mal abordado — **não** substitui fact-check |
| Envolvidos | Pessoas e instituições extraídas das matérias (quando possível) |
| Quem procurar | Sugestões heurísticas de fonte/especialista; **validação humana obrigatória** |
| Sugestões de pauta | Bullets acionáveis para o dia de redação |

Links das matérias originais permanecem na história agrupada (§9.1); INSIGHTS referencia o cluster, não substitui a leitura na fonte.

**Dependências técnicas:** clustering (Fase 3), janela temporal no banco, RAG + prompts editoriais, extração de entidades (fase posterior).

---

## 10. Arquitetura alvo (esboço)

```
┌─────────────┐     ┌──────────┐     ┌─────────┐     ┌──────────┐
│ sources.json│────▶│ collector│────▶│  dedup  │────▶│   DB     │
└─────────────┘     └──────────┘     └─────────┘     └────┬─────┘
                                                          │
                     ┌──────────┐     ┌─────────┐         │
                     │  agent   │◀────│ cluster │◀────────┘
                     └──────────┘     └─────────┘
                          │
                          ▼
                     insights
```

---

## 11. Backlog de ideias (não priorizado)

- User-Agent com email de contato real
- Classe `Source` / `Article` (dataclass) em vez de `dict` puro
- Pre-commit com Ruff
- CI mínimo (lint + test)
- Comparar enfoque editorial entre fontes no mesmo cluster
- Alertas: “assunto X subiu de volume esta semana”

---

## 12. Como usar este documento

1. **Antes de implementar uma feature nova** — checar se encaixa na fase atual
2. **Depois de decisões importantes** — adicionar seção ou item no roadmap
3. **Ao retomar após pausa** — ler §5 (estado atual) e §6 (próxima fase)
4. **Ao desenhar UI ou prompts do agente** — consultar §9 (templates UX)

### Manutenção automática (regra do Cursor)

O agent pergunta se mudanças de código, escopo ou ideias devem ser registradas aqui. Regra em `.cursor/rules/update-visao.mdc`.

Respostas esperadas (teor de ação):

- *"Altere o VISAO.md — …"*
- *"Acrescente no escopo (Fase N)"*
- *"Coloque nas ideias (backlog §10)"*
- *"Registre como decisão técnica (§7)"*
- *"Não inclua agora"*

Sem confirmação explícita, o doc **não** é alterado.

Última atualização: junho/2026 — **Fase 1 concluída** (collector + JSON); **Fase 2** inicia com PostgreSQL na VM; testes básicos sinalizados em §6.1 (pendente).
