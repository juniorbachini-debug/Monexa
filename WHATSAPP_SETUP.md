# Guia de Configuração — WhatsApp Business API (Meta Cloud API)

## O que foi implementado

O backend já está pronto. Quando um cliente mandar mensagem no WhatsApp:

| Tipo de mensagem | O que acontece |
|---|---|
| **Texto** | Detecta valor, tipo e categoria → cadastra transação → responde confirmação |
| **Áudio** | Transcreve via IA (ElevenLabs Scribe) → processa como texto → cadastra |
| **Foto/Comprovante** | Claude Vision lê o comprovante → extrai valor e dados → cadastra |
| **"relatório do mês"** | Retorna resumo com totais e categorias |
| **"ajuda" / "oi"** | Retorna menu de instruções |

Cada número de telefone vira um usuário automaticamente (sem cadastro manual).

---

## Passo a Passo: Ativar o WhatsApp real

### 1. Criar conta Meta for Developers

Acesse: https://developers.facebook.com
- Crie um App do tipo **Business**
- Adicione o produto **WhatsApp**

### 2. Obter as credenciais

No painel do seu App Meta, vá em **WhatsApp > API Setup**:

| Variável | Onde encontrar |
|---|---|
| `WHATSAPP_TOKEN` | "Temporary access token" (ou token permanente via System User) |
| `WHATSAPP_PHONE_NUMBER_ID` | "Phone number ID" (ex: `123456789012345`) |
| `WHATSAPP_VERIFY_TOKEN` | Você define (qualquer string secreta, ex: `meu-assessor-2026`) |

### 3. Configurar o Webhook no Meta

No painel Meta: **WhatsApp > Configuration > Webhook**

- **Callback URL:** `https://SEU_SERVIDOR/api/webhook/whatsapp`
- **Verify token:** o mesmo valor de `WHATSAPP_VERIFY_TOKEN`
- **Campos a subscrever:** `messages`

> O servidor precisa estar em HTTPS público. Use Railway, Render, ou um VPS com domínio.

### 4. Variáveis de ambiente no servidor de produção

```bash
WHATSAPP_TOKEN=EAAxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=meu-assessor-2026
```

### 5. Iniciar os servidores

```bash
# Servidor de transcrição + Vision (porta 5001)
python3 transcription_server.py &

# Servidor principal Express (porta 5000)
NODE_ENV=production node dist/index.cjs
```

---

## Arquitetura do produto

```
Cliente WhatsApp
      │
      ▼
Meta Cloud API
      │ webhook POST
      ▼
Express (porta 5000)
  /api/webhook/whatsapp
      │
      ├─ Texto ──────────────────────► parser → SQLite → resposta
      │
      ├─ Áudio ──► Flask Sidecar (5001) /transcribe
      │                │ (ElevenLabs Scribe)
      │                ▼
      │            texto → parser → SQLite → resposta
      │
      └─ Imagem ──► Flask Sidecar (5001) /analyze-image
                       │ (Claude Sonnet Vision)
                       ▼
                   texto → parser → SQLite → resposta

Painel Web (PC/notebook do cliente)
  Dashboard com gráficos, totais e histórico
```

---

## Custo estimado (Meta)

- **1.000 conversas/mês:** gratuito (primeiras 1.000 são grátis pela Meta)
- Acima disso: ~R$ 0,30–0,50 por conversa (varia por país)

---

## Próximos passos opcionais

- [ ] Número de WhatsApp Business dedicado (via Meta ou BSP como Twilio/360dialog)
- [ ] Deploy em servidor permanente (Railway, Render, VPS)
- [ ] Painel de admin para ver todos os clientes
- [ ] Relatório em PDF enviado por WhatsApp
- [ ] Notificações proativas (ex: "Você já gastou 80% do seu orçamento")
