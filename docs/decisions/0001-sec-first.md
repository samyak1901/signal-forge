# 0001: SEC-First Data Foundation

## Status

Accepted

## Context

SignalForge needs reliable, legal, source-backed public-company data. Many attractive market and transcript sources are unofficial, paid, rate-limited, or have unclear redistribution terms.

## Decision

The MVP uses SEC data as the primary foundation:

- ticker mappings
- submissions API
- XBRL company facts
- filing archives
- structured disclosure feeds

Transcripts, market prices, news, and academic papers are optional connectors added after the SEC core works.

## Consequences

- The first release can be built without vendor keys.
- Research outputs can cite official filings.
- The platform avoids fragile scraping in its core path.
- Price charts and transcripts are deferred until explicit connectors are added.
