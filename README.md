# Winspot24 (Real-Money MVP)

Версия с реальным flow:
- покупка билетов только через реальную on-chain оплату `USDT (ERC-20, Ethereum Mainnet)`,
- treasury-адрес: `0xC5AbC4ffE1d53d480dcadcdc4d2ccb66Fe96C47a`,
- backend верифицирует `tx_hash` через Ethereum RPC,
- билеты и раунды хранятся на сервере (не в `localStorage`),
- розыгрыш выполняется на сервере детерминированно по `block hash` после sold-out,
- публичная шкала доставки из Дубая (старт отправки с `2026-03-11`).

## Где держим базу

Сейчас:
- `SQLite` в файле `backend/data/winspot24.db` (быстро для MVP).

Для production:
- `PostgreSQL` (рекомендуется на отдельном managed сервисе: Supabase/Neon/RDS).

## Структура

- `index.html`, `styles.css`, `app.js`, `config.js` — frontend.
- `backend/main.py` — FastAPI backend + DB + on-chain verification.
- `backend/requirements.txt` — python зависимости.
- `backend/.env.example` — конфиг окружения.
- `terms.html`, `privacy.html`, `refund.html`, `eligibility.html` — базовые legal-драфты.

## Запуск backend локально

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Важно: в `.env` обязательно выставить рабочий `ETH_RPC_URL`.

## Запуск frontend локально

В корне проекта:

```bash
python3 -m http.server 8080
```

Открой `http://localhost:8080`.

Для локальной связки с backend поставь в `config.js`:

```js
apiBaseUrl: "http://localhost:8000/api/v1"
```

## API (основное)

- `GET /api/v1/public/config` — публичные параметры раунда.
- `GET /api/v1/round/current` — текущий раунд (с wallet tickets при `?wallet=0x...`).
- `GET /api/v1/round/history` — завершенные раунды.
- `POST /api/v1/purchases` — фиксация покупки после on-chain tx.
- `POST /api/v1/round/finalize` — завершение sold-out раунда.
- `GET /api/v1/round/{round_number}/shipping` — публичный delivery timeline.
- `GET /api/v1/account/session` — текущая account-сессия и профиль.
- `PUT /api/v1/account/profile` — сохранение профиля доставки и связанного кошелька.
- `POST /api/v1/auth/email/request` — отправка magic link на email.
- `GET /api/v1/auth/email/verify` — вход по одноразовой ссылке из письма.
- `POST /api/v1/auth/logout` — завершение account-сессии.

## Деплой

### Frontend + Backend на AWS VPS

Текущая схема:
1. `winspot24.com` -> Caddy на VPS, который отдает статику сайта.
2. `www.winspot24.com` -> редирект на `https://winspot24.com`.
3. `api.winspot24.com` -> тот же Caddy, reverse proxy на FastAPI.
4. В `config.js` используется `apiBaseUrl: "https://api.winspot24.com/api/v1"`.

### Backend через GitHub Actions (автодеплой на VPS)

В репозитории добавлен workflow:
- `.github/workflows/deploy-api-vps.yml`

Он запускается при пуше в `main` (когда меняется `backend/**` или `deploy/api/**`) и делает:
1. Заливает `backend` и `deploy/api` на сервер.
2. Поднимает `api + caddy` через Docker Compose.
3. Кладет статические файлы сайта в `deploy/site/public`.
4. Выпускает/обновляет TLS сертификаты для `winspot24.com`, `www.winspot24.com`, `api.winspot24.com`.

Нужно заполнить в GitHub (`Settings -> Secrets and variables -> Actions`):

Repository Variables:
- `VPS_HOST` — IP сервера.
- `VPS_USER` — SSH user (можно не задавать, по умолчанию `root`).
- `VPS_PORT` — обычно `22` (можно не задавать).
- `VPS_PATH` — путь деплоя, например `/opt/winspot24-api` (можно не задавать).
- `API_DOMAIN` — `api.winspot24.com` (можно не задавать).
- `ACME_EMAIL` — email для Let's Encrypt (можно не задавать, по умолчанию `admin@winspot24.com`).
- `APP_URL` — фронтенд-домен, по умолчанию `https://winspot24.com`.
- `SESSION_COOKIE_NAME` — имя cookie, по умолчанию `winspot24_session`.
- `SESSION_COOKIE_SECURE` — `true` для production.
- `SESSION_DAYS` — TTL account-сессии в днях, по умолчанию `30`.
- `SMTP_HOST` — SMTP host для отправки magic links.
- `SMTP_PORT` — SMTP port, обычно `587`.
- `SMTP_SENDER_EMAIL` — email отправителя.
- `SMTP_SENDER_NAME` — имя отправителя, по умолчанию `Winspot24`.
- `SMTP_STARTTLS` — `true`, если нужен STARTTLS.
- `SMTP_USE_SSL` — `true`, если нужен SMTPS вместо STARTTLS.
- `MAGIC_LINK_TTL_MINUTES` — срок жизни одноразовой ссылки, по умолчанию `20`.

Repository Secrets:
- `VPS_SSH_KEY` — приватный SSH-ключ для входа на сервер.
- `ETH_RPC_URL` — RPC URL Ethereum Mainnet.
- `SMTP_USERNAME` — SMTP username.
- `SMTP_PASSWORD` — SMTP password / app password.

После этого любой push в `main` с изменениями backend автоматически задеплоит API.

### Что нужно для авторизации

Для текущей версии используется только email magic link:
- пользователь вводит email в личном кабинете,
- backend отправляет одноразовую ссылку через SMTP,
- после перехода по ссылке backend ставит cookie-сессию и возвращает пользователя в `#account`.

Минимум, который нужно заполнить для запуска:
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_SENDER_EMAIL`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`

## Ограничения и риски

- Это не лицензированная gambling-платформа из коробки.
- Перед масштабированием обязательны: юридическая модель, ToS/Privacy финальных версий, аудит, антифрод.
- Для устойчивого real-money режима лучше переносить платежи на dedicated smart contract вместо прямого `USDT transfer`.
