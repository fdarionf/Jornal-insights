# 📰 jornal-insights

Sistema de insights para jornalistas: coleta notícias de fontes RSS, agrupa por assunto e (em desenvolvimento) sugere pautas com base em como a cobertura evolui ao longo do tempo.

## 💡 Por que esse projeto existe

Ferramentas como Google News ou Feedly agregam notícias, mas entregam pouco insight editorial. O jornal-insights tenta ir além: em vez de só resumir uma notícia isolada, o objetivo é entender como um assunto evolui no tempo e como diferentes portais cobrem a mesma história — e a partir disso, sugerir pautas reais pro jornalista.

## 🚧 Status atual

Projeto em desenvolvimento ativo, seguindo um roadmap em fases:

- ✅ Fase 1 — Coletor de feeds RSS (concluída)
- ✅ Fase 2 — Persistência em PostgreSQL com deduplicação por link (concluída)
- 🔹 Fase 3 — Agrupamento de notícias por assunto (clustering)
- 🔹 Fase 4 — API + motor de insights com IA
- 🔹 Fase 5 — Produto (agendamento automático, painel de configuração)

- ## 🛠️ Stack

- - Python 3.12+
  - PostgreSQL
  - httpx + feedparser (coleta de feeds)
  - Poetry (gerenciamento de dependências)
  - Docker (infraestrutura)
 
  - ## 📬 Contato
 
  - [LinkedIn](https://www.linkedin.com/in/darion-forte-franco/)
 
  - ---

  Projeto pessoal em desenvolvimento — feedback é bem-vindo.
  
