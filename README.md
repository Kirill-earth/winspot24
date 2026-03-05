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

## Деплой

### Frontend (GitHub Pages)

Используются:
- `.github/workflows/deploy-pages.yml`
- `CNAME`

### Backend

GitHub Pages не исполняет API, поэтому backend нужно поднять отдельно:
- VPS + reverse proxy (`api.winspot24.com`),
- или managed runtime (Render/Fly.io/Cloud Run).

Рекомендованная схема:
1. `winspot24.com` -> GitHub Pages (frontend).
2. `api.winspot24.com` -> backend.
3. В `config.js` указать `apiBaseUrl: "https://api.winspot24.com/api/v1"`.

## Ограничения и риски

- Это не лицензированная gambling-платформа из коробки.
- Перед масштабированием обязательны: юридическая модель, ToS/Privacy финальных версий, аудит, антифрод.
- Для устойчивого real-money режима лучше переносить платежи на dedicated smart contract вместо прямого `USDT transfer`.
