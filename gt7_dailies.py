#!/usr/bin/env python3
"""Post this week's GT7 Daily Races to one Discord channel via webhook.

Requires a personal GT-GridStats API key. No third-party Python packages.
"""
import json
import os
import sys
import time
from datetime import date, datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

API_URL = "https://gt-gridstats.com/api/dailies/this-week"
TIMEZONE = ZoneInfo("Europe/Copenhagen")


def fetch_json(url, *, headers=None, payload=None, attempts=3):
    """Retry transient HTTP/rate-limit issues; never print credentials or webhook URLs."""
    encoded = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=encoded, headers=headers or {}, method="POST" if payload is not None else "GET")
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=25) as response:
                content = response.read(2_000_000)
                return json.loads(content) if content else {}
        except HTTPError as exc:
            # Never log the request URL: Discord webhook URLs are sensitive.
            if exc.code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                raise RuntimeError(f"HTTP-fejl {exc.code} under hentning/afsendelse") from None
        except (URLError, TimeoutError) as exc:
            if attempt == attempts - 1:
                raise RuntimeError(f"Netværksfejl: {type(exc).__name__}") from None
        time.sleep(5 * (attempt + 1))
    raise RuntimeError("Kunne ikke gennemføre netværkskald")


def validate_races(data, today=None):
    """Prevent stale/partial weekly data from being published as current."""
    if not isinstance(data, dict) or not isinstance(data.get("data"), list):
        raise ValueError("API-svaret mangler 'data'-listen")
    today = today or datetime.now(TIMEZONE).date()
    monday = today - timedelta(days=today.weekday())
    by_type = {}
    for race in data["data"]:
        if not isinstance(race, dict):
            continue
        kind = str(race.get("race_type", "")).strip().upper()
        if kind not in {"A", "B", "C"}:
            continue
        if kind in by_type:
            raise ValueError(f"Dubleret Race {kind} i API")
        if not race.get("track_name"):
            raise ValueError(f"Race {kind} mangler banenavn")
        if race.get("status") not in (None, "live"):
            raise ValueError(f"Race {kind} er endnu ikke live")
        start = race.get("begin_date")
        if not start:
            raise ValueError(f"Race {kind} mangler begyndelsesdato; afbryder for at undgå gamle data")
        try:
            start_date = date.fromisoformat(str(start)[:10])
        except ValueError:
            raise ValueError(f"Race {kind} har en ugyldig begyndelsesdato") from None
        if start_date != monday:
            raise ValueError(f"Race {kind} begynder {start_date}, men denne uges mandag er {monday}")
        by_type[kind] = race
    if set(by_type) != {"A", "B", "C"}:
        raise ValueError("API'et har endnu ikke alle tre aktuelle løb (A, B, C)")
    return [by_type[kind] for kind in "ABC"], monday


def format_tyres(race):
    regulation = (race.get("raw_payload") or {}).get("regulation") or {}
    tyre = regulation.get("tire")
    compounds = regulation.get("compounds") or []
    if not tyre:
        return None
    suffix = ", ".join(str(x) for x in compounds if x)
    return f"{tyre} {suffix}" if suffix else str(tyre)


def race_embed(race):
    kind = race["race_type"]
    body = []
    if race.get("car_class"):
        body.append(f"**Bilklasse:** {race['car_class']}")
    if race.get("laps") is not None:
        body.append(f"**Omgang:** {race['laps']}")
    tyres = format_tyres(race)
    if tyres:
        body.append(f"**Dæk:** {tyres}")
    setup = (race.get("raw_payload") or {}).get("race") or {}
    fuel, wear = setup.get("consume_fuel"), setup.get("consume_tire")
    if fuel is not None:
        body.append(f"**Brændstofforbrug:** x{fuel}")
    if wear is not None:
        body.append(f"**Dækslid:** x{wear}")
    meta = race.get("meta_car") or {}
    if isinstance(meta, dict) and meta.get("name"):
        body.append(f"**Mest brugte bil (Top 100):** {meta['name']}")
    return {
        "title": f"🏎️ Race {kind} — {race['track_name']}",
        "description": "\n".join(body) or "Se flere detaljer på GT-GridStats.",
        "color": {"A": 0x24B47E, "B": 0x4599EB, "C": 0xD69E41}[kind],
    }


def create_payload(races, monday):
    # Discord accepts up to 10 embeds per message. Only three are sent.
    return {
        "username": "GT7 Race Center",
        "content": (
            f"🏁 **DANISH GRAN TURISMO COMMUNITY — UGENS DAILY RACES** 🇩🇰\n"
            f"📅 Ugen starter mandag **{monday.strftime('%d-%m-%Y')}**.\n"
            "Her er Race A, B og C. Del jeres tider og setups! 🏎️\n"
            "Flere detaljer: https://gt-gridstats.com/dailies\n"
            "Du kan også skrive `!twd` eller `!dgtl DIT_PSN_ID` i kanalen."
        ),
        "embeds": [race_embed(race) for race in races],
        "allowed_mentions": {"parse": []},
    }


def main():
    api_key = os.environ.get("GT_GRIDSTATS_API_KEY", "").strip()
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    publish = os.environ.get("PUBLISH", "false").lower() == "true"
    if not api_key:
        raise RuntimeError("GitHub Secret GT_GRIDSTATS_API_KEY mangler")
    if publish and not webhook_url:
        raise RuntimeError("GitHub Secret DISCORD_WEBHOOK_URL mangler")
    if publish and not webhook_url.startswith("https://discord.com/api/webhooks/"):
        raise RuntimeError("Discord-webhookens format er ikke gyldigt")

    result = fetch_json(API_URL, headers={
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "HeisyTTV-GT7-Race-Scheduler/1.0",
    })
    races, monday = validate_races(result)
    payload = create_payload(races, monday)
    if not publish:
        print("FORHÅNDSVISNING (ingen Discord-besked sendt):")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    fetch_json(webhook_url, headers={"Content-Type": "application/json"}, payload=payload)
    print(f"Offentliggjort: Race A, B og C for uge med mandag {monday}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError) as err:
        print(f"FEJL: {err}", file=sys.stderr)
        sys.exit(1)
