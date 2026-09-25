# Kleeppr

**Discover and read newsletters without giving publishers your personal email address.**

Email newsletters are useful, but finding good ones is scattered across the web and subscribing often means handing every publisher the address of your main inbox. Kleeppr was built around a different flow: find newsletters in one place, subscribe using a Kleeppr address, and read the incoming issues in a dedicated feed.

## How it worked

1. Search or browse a catalog of newsletters.
2. Create an account and receive a Kleeppr email address to use for subscriptions.
3. Subscribe to a publisher with that address instead of your personal one.
4. Kleeppr reads incoming mail from its mailboxes, identifies the newsletter, and adds each issue to your feed.

The app also kept track of followed newsletters, offered search and a bookmarklet, and sent account and subscription notifications. Payment flows were explored during development; the final 2021 release removed the paid subscription requirement.

## In this repository

This is the Django web application from the 2020–2021 Kleeppr project. It includes:

- the catalog, account, subscription, and reading views in `web/`
- newsletter and feed models in `web/models.py`
- email parsing in `scripts/` and `imapbox.py`
- management commands for mailbox creation, feed ingestion, notifications, and catalog import in `web/management/commands/`

The web app depended on PostgreSQL and a separately configured mail server. The tracked code does not include mailbox credentials or a production database.

## Running locally

The dependency pins are from 2020. A Python 3.8 environment is the closest starting point for this version:

```bash
python3.8 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mkdir -p runtime
cp env.example runtime/.env
```

Fill in `runtime/.env` with local values. The app expects PostgreSQL on `127.0.0.1:5432`, with a `postgres` database and user, and reads its mail and payment configuration from the environment. Then:

```bash
python manage.py migrate
python manage.py runserver
```

Browsing an empty catalog is different from running the complete service. Subscription addresses, incoming newsletters, and notifications require the original mail-server setup and management commands. I have not recently verified the full stack with current dependencies.

## Note

This project is archived. The public history retains the original development commits and timestamps, while omitting a saved third-party web page and visual assets whose redistribution rights were unclear. Some historical pages may therefore be missing imagery.
