# Erlaubte Commit Scopes für Dockhand Guardian

## Scope-Übersicht

Dockhand Guardian verwendet spezifische Scopes in Commit-Messages, um Änderungen klar zu kategorisieren. Jeder Commit MUSS einen Scope haben.

### Verfügbare Scopes

| Scope | Beschreibung | Beispiele |
|-------|-------------|-----------|
| `guardian` | Änderungen an der Guardian-Hauptlogik | Monitoring-Logik, Zustandsverwaltung |
| `docker` | Docker-spezifische Anpassungen | Dockerfile, Docker-Konfiguration |
| `compose` | Docker Compose Konfiguration | docker-compose.yml Änderungen |
| `webhook` | Webhook/Benachrichtigungssystem | Apprise-Integration, Notification-Logik |
| `monitoring` | Health-Check Funktionalität | HTTP-Checks, Container-Status |
| `recovery` | Recovery-Mechanismen | Stack-Neustart, Pull-Logik |
| `ci` | CI/CD Pipeline Änderungen | GitHub Actions, Test-Workflows |
| `deps` | Dependency Updates | requirements.txt, npm Pakete |
| `docs` | Dokumentation | README, Inline-Dokumentation |
| `config` | Konfigurationsoptionen | Umgebungsvariablen, Settings |

## Entscheidungsbaum

```
Ändere ich...
├─ Code der Guardian-Hauptlogik? → guardian
├─ Dockerfile oder Docker-Build? → docker
├─ docker-compose.yml? → compose
├─ Webhook/Notification System? → webhook
├─ Health-Check Funktionen? → monitoring
├─ Recovery-Prozesse? → recovery
├─ CI/CD Workflows? → ci
├─ Abhängigkeiten? → deps
├─ Dokumentation? → docs
└─ Konfigurationsoptionen? → config
```

## Beispiele für Commit-Messages

```
feat(guardian): add maintenance mode check
fix(webhook): correct apprise notification format
docs(monitoring): update health check documentation
chore(deps): update docker SDK to 7.0.0
ci(workflow): add automated testing pipeline
refactor(recovery): simplify stack restart logic
```

## Regeln

1. **Scope ist Pflicht**: Jeder Commit muss einen Scope haben
2. **Nur erlaubte Scopes**: Nutze nur Scopes aus der Liste oben
3. **Singular-Form**: Scopes immer in Singular (nicht `webhooks` sondern `webhook`)
4. **Lowercase**: Scopes immer kleingeschrieben
5. **Granularität**: Wähle den spezifischsten Scope für deine Änderung

## Commit-Typen

- `feat`: Neues Feature
- `fix`: Bugfix
- `docs`: Nur Dokumentation
- `style`: Code-Formatierung
- `refactor`: Code-Umstrukturierung
- `perf`: Performance-Verbesserung
- `test`: Tests hinzufügen/ändern
- `build`: Build-System Änderungen
- `ci`: CI-Konfiguration
- `chore`: Wartungsarbeiten
- `revert`: Commit zurücknehmen
