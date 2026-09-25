# Kleeppr

> **Archived project.** This is an older project and is no longer maintained. I have not recently verified that the full application and mail-server stack work with current dependency versions.

**A dedicated inbox and reader for email newsletters.**

Kleeppr let you subscribe to newsletters without using your personal email address.

When you created an account, Kleeppr gave you a unique email address. You could use that address to subscribe to newsletters anywhere on the web. Incoming issues were collected automatically and presented in a clean reading feed.

## How it worked

1. Create a Kleeppr account and get your own Kleeppr email address.
2. Use that address when subscribing to newsletters.
3. Kleeppr receives and processes the incoming email.
4. New issues appear automatically in your reading feed.

You could browse all issues from a particular publication, follow newsletters, and discover new ones through a curated catalog.

Kleeppr also included a browser bookmarklet. When you were on a newsletter signup page, the bookmarklet could fill in your Kleeppr email address with one click, so you did not need to remember or copy it manually.

## Under the hood

Kleeppr ran its own mail infrastructure rather than forwarding newsletters through a third-party inbox.

The application handled:

- unique email addresses for users
- incoming newsletter email
- parsing and ingestion
- publication and issue organization
- personalized reading feeds
- newsletter discovery and cataloging
- account and subscription management
- a bookmarklet for newsletter signup forms

The web application is built with Django and PostgreSQL.

## Repository

The main Django application lives in `web/`.

Relevant pieces include:

- newsletter, publication, and feed models in `web/models.py`
- email processing in `scripts/` and `imapbox.py`
- mailbox, ingestion, notification, and catalog management commands in `web/management/commands/`

Running the complete system requires mail-server configuration in addition to the web application and database.

## Running locally

The dependencies in this repository are old. Python 3.8 is a reasonable starting point for running this version:

```bash
python3.8 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mkdir -p runtime
cp env.example runtime/.env
```

Configure the required database and environment variables in `runtime/.env`, then run:

```bash
python manage.py migrate
python manage.py runserver
```

This starts the web application. Receiving newsletters and populating feeds requires the corresponding mail-server setup and ingestion commands.

## Mail server setup

Kleeppr operated its own mail server using [`docker-mailserver`](https://github.com/tomav/docker-mailserver). This allowed each user to have a dedicated Kleeppr email address that could receive newsletter subscriptions directly.

Running the complete service required more than starting the Django application. The mail domain also needed DNS, email authentication, and TLS configuration.

> **Historical note:** These are abbreviated deployment notes from the original project, not a current `docker-mailserver` setup guide. Configuration options and recommended practices may have changed.

### DNS and email authentication

The mail setup used the standard email authentication mechanisms:

- **MX** — directed incoming email for the domain to the Kleeppr mail server.
- **SPF** — declared which servers were authorized to send email for the domain.
- **DKIM** — cryptographically signed outgoing messages so receiving servers could verify their origin and integrity.
- **DMARC** — defined how SPF and DKIM results should be interpreted and provided reporting for authentication failures.

A simplified DNS setup looked roughly like:

```text
MX    example.com              -> mail.example.com

TXT   example.com              "v=spf1 mx ~all"

TXT   <selector>._domainkey.example.com
      <DKIM public key>

TXT   _dmarc.example.com
      "v=DMARC1; p=none; rua=mailto:dmarc@example.com"
```

The DKIM private key remained on the mail server, while the corresponding public key was published through DNS.

During setup, tools such as MXToolbox and DNS lookup utilities were useful for checking DNS propagation and authentication records. Gmail's **Show original** view was also useful for verifying SPF, DKIM, and DMARC results on received messages.

### TLS

The mail server used a Let's Encrypt certificate for its fully qualified hostname, for example:

```text
mail.example.com
```

The hostname configured for the mail container needed to match the hostname covered by the certificate.

The original deployment obtained certificates using Certbot in Docker:

```bash
docker run --rm -it \
  -v "$PWD/letsencrypt:/etc/letsencrypt" \
  -v "$PWD/log:/var/log/letsencrypt" \
  -p 80:80 \
  certbot/certbot certonly \
  --standalone \
  -d mail.example.com
```

`docker-mailserver` was then configured to use the Let's Encrypt certificates:

```text
SSL_TYPE=letsencrypt
```

Certificate renewal was run periodically with Certbot.

For debugging an IMAP TLS endpoint, OpenSSL was useful for inspecting the certificate presented by the server:

```bash
openssl s_client \
  -showcerts \
  -connect mail.example.com:993 \
  -servername mail.example.com
```

The full mail-server configuration is not included as a turnkey deployment in this repository. These notes are retained to document how the original Kleeppr service received mail and managed its own mailboxes.
