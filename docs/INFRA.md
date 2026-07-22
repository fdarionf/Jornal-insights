# Infraestrutura — VM + PostgreSQL

Guia operacional para subir/desligar o ambiente de banco. Detalhes de produto e roadmap em [VISAO.md](VISAO.md).

**Não commitar senhas.** Use `.env` local (gitignored). Modelo em `.env.example`.

---

## Visão geral

```
Windows (Cursor, collector.py)
    │
    │  Host-only (ex.: 192.168.56.x)
    ▼
VM Ubuntu (VirtualBox)
    └── Docker → container jornal-db (PostgreSQL 16)
            └── volume jornal_pgdata (dados persistentes)
```

| Componente | Onde |
|---|---|
| Código Python | Windows — `G:\Project\jornal-insights` |
| PostgreSQL | VM — porta `5432` |
| Rede VM → Windows | Adaptador **Host-only** (`enp0s8`) |
| Internet na VM | Adaptador **NAT** (`enp0s3`) |

---

## Rede (VirtualBox)

| Adaptador | Modo | Função |
|---|---|---|
| Adapter 1 | NAT | VM acessa internet (`apt`, `docker pull`) |
| Adapter 2 | Host-only | Windows conecta em SSH e Postgres |

**IP do Host-only muda?** Pode. Sempre confira na VM:

```bash
ip a
```

Use o IP de `enp0s8` (faixa `192.168.56.x`), não o `10.0.2.15` do NAT.

---

## Subir tudo (checklist)

1. **VirtualBox** → selecionar VM → **Iniciar**
2. **SSH** (Windows PowerShell):
   ```powershell
   ssh dev@192.168.56.102
   ```
   (Substitua pelo IP atual do `enp0s8`.)
3. **Postgres** (na VM):
   ```bash
   docker start jornal-db
   docker ps
   ```
   Container `jornal-db` deve estar `Up`.
4. **Teste do Windows**:
   ```powershell
   Test-NetConnection 192.168.56.102 -Port 5432
   ```
   `TcpTestSucceeded : True`
5. **Projeto** (quando for codar):
   ```powershell
   cd G:\Project\jornal-insights
   poetry shell
   poetry run python src/collector.py
   ```

---

## Desligar tudo (checklist)

1. **Na VM** (SSH ou console):
   ```bash
   docker stop jornal-db
   sudo shutdown -h now
   ```
2. Aguardar VM **Desligada** no VirtualBox
3. Fechar VirtualBox / Cursor — nada extra no Windows

**Dados persistem** no disco da VM e no volume Docker `jornal_pgdata`.

---

## PostgreSQL (Docker)

Container criado manualmente na VM:

```bash
docker run -d \
  --name jornal-db \
  -e POSTGRES_USER=jornal \
  -e POSTGRES_PASSWORD=<sua_senha> \
  -e POSTGRES_DB=jornal_insights \
  -p 5432:5432 \
  -v jornal_pgdata:/var/lib/postgresql/data \
  postgres:16
```

| Item | Valor |
|---|---|
| Container | `jornal-db` |
| Volume | `jornal_pgdata` |
| Banco | `jornal_insights` |
| Usuário | `jornal` |
| Porta | `5432` |

**Connection string** (copiar para `.env`):

```
DATABASE_URL=postgresql://jornal:<senha>@<IP_HOST_ONLY>:5432/jornal_insights
```

---

## SSH

- Instalado na VM: `openssh-server`
- Usuário de dev: `dev`
- Verificar serviço na VM:
  ```bash
  sudo systemctl status ssh
  ```

---

## Instalação da VM (referência — já feito)

1. Ubuntu Server 24.04+ LTS no VirtualBox
2. Instalar **só com NAT** (evita loop do instalador); Host-only **depois**
3. Marcar **Install OpenSSH server** na instalação
4. Após instalar: ativar Adapter 2 (Host-only)
5. `sudo apt update && sudo apt upgrade -y`
6. `sudo apt install docker.io -y` + `sudo usermod -aG docker $USER`
7. Criar container Postgres (comando acima)

---

## Próximo passo de desenvolvimento

Infra pronta. Falta no código (Fase 2):

1. Schema `articles` (`link` UNIQUE)
2. `src/db.py` — conexão + insert com dedup
3. Integrar `collector.py` → banco

Ver [VISAO.md](VISAO.md) §5 e §6.
