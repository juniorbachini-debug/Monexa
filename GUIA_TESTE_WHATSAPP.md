# Monexa — Guia para Testar no WhatsApp Real

São só 2 etapas: **colocar o servidor no ar** e **configurar na Meta**.

---

## ETAPA 1: Colocar o servidor no ar (Railway — gratuito)

### 1.1 Suba o código para o GitHub

```bash
# Na pasta do projeto
git init
git add .
git commit -m "Monexa v1"
git remote add origin https://github.com/SEU_USUARIO/monexa.git
git push -u origin main
```

### 1.2 Crie uma conta no Railway

1. Acesse: https://railway.app
2. Faça login com o GitHub
3. Clique em **"New Project"** → **"Deploy from GitHub repo"**
4. Selecione o repositório `monexa`
5. Railway vai detectar o `Dockerfile` e fazer o deploy automaticamente

### 1.3 Configure as variáveis de ambiente no Railway

No painel do Railway, vá em **Variables** e adicione:

```
WHATSAPP_TOKEN=            (pegar na etapa 2)
WHATSAPP_PHONE_NUMBER_ID=  (pegar na etapa 2)
WHATSAPP_VERIFY_TOKEN=monexa-2026
ANTHROPIC_API_KEY=         (para leitura de comprovantes — opcional)
PERPLEXITY_API_KEY=        (para transcrição de áudio — opcional)
PORT=5000
```

### 1.4 Anote a URL pública

O Railway gera uma URL tipo:
```
https://monexa-production.up.railway.app
```
Anote — vai usar na etapa 2.

---

## ETAPA 2: Configurar WhatsApp na Meta (15 minutos)

### 2.1 Crie um App na Meta

1. Acesse: https://developers.facebook.com
2. Clique em **"Criar App"**
3. Selecione tipo **"Empresa"** (Business)
4. Dê o nome **"Monexa"**
5. Após criar, vá na barra lateral e clique em **"Adicionar Produto"**
6. Encontre **"WhatsApp"** e clique **"Configurar"**

### 2.2 Pegue suas credenciais

Na página **WhatsApp > Configuração da API**:

- **Token de acesso temporário**: copie e cole como `WHATSAPP_TOKEN` no Railway
- **ID do número de telefone**: copie e cole como `WHATSAPP_PHONE_NUMBER_ID` no Railway

> ⚠️ O token temporário expira em 24h. Para produção, crie um token permanente via System User.

### 2.3 Configure o Webhook

Na página **WhatsApp > Configuração**:

1. Clique em **"Editar"** no Webhook
2. **URL de callback**: `https://SUA_URL_RAILWAY/api/webhook/whatsapp`
3. **Token de verificação**: `monexa-2026` (o mesmo que você colocou no Railway)
4. Clique em **"Verificar e salvar"**
5. Após verificar, clique em **"Gerenciar"** e marque o campo **"messages"**

### 2.4 Adicione seu número para teste

Na página **WhatsApp > Configuração da API**:

1. Em **"Para"**, clique em **"Gerenciar lista de números de telefone"**
2. Adicione seu número pessoal (ex: +55 11 99999-9999)
3. Você vai receber um código de verificação no WhatsApp — confirme

### 2.5 Teste!

Abra o WhatsApp e mande uma mensagem para o **número de teste da Meta** (aparece na página da API):

```
oi
```

Você deve receber de volta o menu do Monexa. Depois teste:

```
Gastei R$ 50 no mercado
```

```
Relatório do mês
```

```
Agendar reunião amanhã às 14h
```

Envie um áudio: "Paguei cem reais de luz" — ele transcreve e cadastra.

---

## Resumo das URLs

| O que | URL |
|---|---|
| Webhook (Meta configura aqui) | `https://SUA_URL/api/webhook/whatsapp` |
| Verificação do webhook (GET) | Mesmo URL acima |
| Painel web (relatórios) | `https://SUA_URL` |

---

## Troubleshooting

| Problema | Solução |
|---|---|
| Webhook não verifica | Confira que o `WHATSAPP_VERIFY_TOKEN` é igual no Railway e na Meta |
| Mando mensagem e não recebe resposta | Veja os logs no Railway (aba Deployments > Logs) |
| Token expirou | Gere novo token temporário na Meta ou crie System User |
| Áudio não transcreve | Configure `PERPLEXITY_API_KEY` no Railway |
| Foto não lê | Configure `ANTHROPIC_API_KEY` no Railway |

---

## Tempo estimado

- GitHub + Railway: ~10 minutos
- Meta Developer: ~15 minutos
- Primeiro teste: ~5 minutos

**Total: ~30 minutos até mandar "Gastei R$ 50" no WhatsApp e receber confirmação.**
