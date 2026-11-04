# GT7: Automatisk mandagsopdatering til Discord 🇩🇰

Dette projekt henter **Race A, B og C** fra GT-GridStats API og offentliggør dem automatisk i Discord-kanalen **#gt-race-stats** på **HeisyTTV**-serveren, hver **mandag kl. 10.00 (Europe/Copenhagen)**.

## Det skal du bruge

- En GitHub-konto: https://github.com
- En personlig **GT-GridStats API-nøgle**, som du skal anmode om via https://gt-gridstats.com/contact eller gtgridstats@gmail.com. De beskriver adgangen som tidlig API-adgang. Du kan ikke bruge Discord-bottens adgang som API-nøgle.
- En Discord-webhook til kanalen `#gt-race-stats`.
- GitHub Desktop (anbefales på Mac): https://desktop.github.com/

### Trin 1: Opret Discord-webhook

1. Gå til HeisyTTV → **Serverindstillinger → Integrationer → Webhooks**.
2. Vælg **Ny webhook/Opret webhook**.
3. Navngiv den fx `GT7 Race Center` og vælg **#gt-race-stats** som destination.
4. Klik på **Kopiér webhook-URL**. Opbevar den privat. **Del aldrig webhook-URL'en i en offentlig besked eller et screenshot.**

### Trin 2: Få din API-nøgle

1. Du har allerede skrevet til GT-GridStats. Afvent svar med API-adgang. Se https://gt-gridstats.com/contact eller https://gt-gridstats.com/api-docs.
2. Når udvikleren giver dig en personlig API-nøgle, gem den som `GT_GRIDSTATS_API_KEY` under GitHub Actions secrets. Del den aldrig i chatten.
3. Programmet kan ikke hente løb via API før nøglen er udstedt.

### Trin 3: Læg filer i dit EKSISTERENDE GitHub-repository

Du har allerede oprettet `gt7-discord-dailies` på GitHub. **Opret ikke et nyt repository.**

1. Download ZIP-filen fra ChatGPT og dobbeltklik på den for at pakke ud.
2. Installer/åbn **GitHub Desktop** (https://desktop.github.com/) og log ind med din GitHub-konto.
3. Vælg **File → Clone Repository**, fanen **GitHub.com**, og vælg `gt7-discord-dailies`. Klik **Clone**.
4. Vælg **Repository → Show in Finder**. Åbn derefter den udpakkede mappe `gt7-discord-automation`.
5. Kopiér filerne `gt7_dailies.py`, `README_DANSK.md`, mappen `tests` og **mappen `.github`** til *roden* af den klonede repository-mappe. Tip: `Cmd + Shift + .` viser skjulte mapper på Mac. Hvis README allerede findes, må du erstatte den med denne README.
6. Gå tilbage til GitHub Desktop. Skriv `Tilføj GT7 automatisk mandagsoversigt` i Summary, klik **Commit to main** og dernæst **Push origin**.
7. Bekræft på GitHub.com, at filen `.github/workflows/gt7-monday.yml` findes i dit repository.

### Trin 4: Gem nøglerne sikkert i GitHub

1. Åbn dit eksisterende repository `gt7-discord-dailies` på github.com.
2. Vælg **Settings → Secrets and variables → Actions**.
3. Under **Repository secrets** klik **New repository secret**.
4. Opret hemmeligheden **DISCORD_WEBHOOK_URL** med den fulde **nye** webhook-URL (den gamle blev delt i chat og skal slettes/roteres).
5. Når du får API-adgangen fra udvikleren, opret **GT_GRIDSTATS_API_KEY** med din personlige API-nøgle.
6. Under **Variables** skal du ikke oprette noget.
7. Disse værdier skal **ikke** skrives i Python-koden eller uploades som filer.

### Trin 5: Test uden at sende beskeder

1. Åbn repository på GitHub → **Actions**.
2. Vælg workflow **GT7 Daily Races - mandag kl. 10** → **Run workflow**.
3. Lad `publish` stå på **false** → **Run workflow**.
4. Åbn kørslen og læs loggen. Ved succes vises **FORHÅNDSVISNING** med Race A/B/C.
5. Hvis der står `HTTP-fejl 401/403`, er API-nøglen forkert/mangler adgang. Hvis der står `mangler begyndelsesdato` eller `alle tre`, har API'et ikke returneret komplette aktuelle løbsdata i det dokumenterede format.

### Trin 6: Test rigtig offentliggørelse

1. Gå igen til **Actions → GT7 Daily Races - mandag kl. 10 → Run workflow**.
2. Vælg `publish` = **true**.
3. Kontroller i **#gt-race-stats**, at opslaget er kommet med tre separate embeds.
4. Fra nu af kører workflow automatisk hver mandag kl. 10 dansk tid – GitHub kan dog starte planlagte jobs lidt senere.

## Hvilke oplysninger vises?

For Race A, B og C: bane, bilklasse, antal omgange, dæk, brændstofforbrug, dækslid og populær bil (hvis API'et indeholder den). **Verdensrekorder offentliggøres ikke**, fordi det dokumenterede API-eksempel ikke indeholder disse felter. Medlemmer kan fortsat bruge den eksisterende `!twd`-kommando til flere oplysninger.

## Beskyttelse mod fejl

- Scriptet kræver **alle 3 aktuelle løb** og startdato fra **denne uges mandag**, ellers sender det intet.
- Workflow kører én gang om mandagen; ved API-fejl sender GitHub ikke automatisk igen. Du kan genkøre manuelt under Actions. Manuel kørsel med `publish=true` kan sende en ekstra besked.
- GitHub Actions' tidsplan er ikke en garanti for udsendelse **præcis** kl. 10.00.
- Webhook-URL og API-nøgle er kun i GitHub Secrets.
- Ingen eksterne Python-pakker eller betalte servere er nødvendige; GitHubs gældende Action-kvoter kan gælde.

## Kildegrundlag

- https://gt-gridstats.com/ (API-eksempel: `/api/dailies/this-week`)
- https://gt-gridstats.com/api-docs
- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks
