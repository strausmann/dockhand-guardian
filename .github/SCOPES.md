# Erlaubte Commit Scopes für Dockhand Guardian

## Scope-Übersicht

Dockhand Guardian verwendet spezifische Scopes in Commit-Messages, um Änderungen klar zu
kategorisieren. Jeder Commit MUSS einen Scope haben.

### Verfügbare Scopes

| Scope        | Beschreibung                          | Beispiele                               |
| ------------ | ------------------------------------- | --------------------------------------- |
| `guardian`   | Änderungen an der Guardian-Hauptlogik | Monitoring-Logik, Zustandsverwaltung    |
| `docker`     | Docker-spezifische Anpassungen        | Dockerfile, Docker-Konfiguration        |
| `compose`    | Docker Compose Konfiguration          | docker-compose.yml Änderungen           |
| `webhook`    | Webhook/Benachrichtigungssystem       | Apprise-Integration, Notification-Logik |
| `monitoring` | Health-Check Funktionalität           | HTTP-Checks, Container-Status           |
| `recovery`   | Recovery-Mechanismen                  | Stack-Neustart, Pull-Logik              |
| `ci`         | CI/CD Pipeline Änderungen             | GitHub Actions, Test-Workflows          |
| `deps`       | Dependency Updates                    | pyproject.toml, npm Pakete              |
| `docs`       | Dokumentation                         | README, Inline-Dokumentation            |
| `config`     | Konfigurationsoptionen                | Umgebungsvariablen, Settings            |
| `release`    | Release Management                    | Semantic-Release, Versioning            |

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
├─ Konfigurationsoptionen? → config
└─ Release/Versioning? → release
```

## Type + Scope Kombinationen

Je nach Commit-Type sind unterschiedliche Scopes sinnvoll:

### `feat` (Neue Features)

Hauptsächlich für Feature-Code, nicht für Infrastruktur:

- ✅ `guardian` - Neue Guardian-Features
- ✅ `webhook` - Neue Notification-Features
- ✅ `monitoring` - Neue Health-Check-Features
- ✅ `recovery` - Neue Recovery-Mechanismen
- ⚠️ Andere Scopes möglich, aber seltener

**Beispiele:**

```bash
feat(guardian): add maintenance mode support
feat(webhook): integrate Telegram notifications via Apprise
feat(monitoring): add TCP port health checks
feat(recovery): implement graceful shutdown handling
```

### `fix` (Bugfixes)

Kann alle Scopes betreffen:

- ✅ `guardian` - Bugfixes in Core-Logik
- ✅ `docker` - Docker-Build/-Runtime Fixes
- ✅ `compose` - Docker Compose Konfigurationsfixes
- ✅ `webhook` - Notification-Bugs
- ✅ `monitoring` - Health-Check Fehler
- ✅ `recovery` - Recovery-Probleme

**Beispiele:**

```bash
fix(guardian): prevent duplicate recovery attempts
fix(docker): correct volume mount permissions
fix(compose): fix healthcheck interval syntax
fix(webhook): handle webhook timeout errors correctly
fix(monitoring): fix HTTP check timeout handling
fix(recovery): prevent recovery during cooldown period
```

### `docs` (Dokumentation)

Nutze entsprechenden Scope für dokumentierten Bereich:

- ✅ `docs` - Allgemeine/Projekt-Dokumentation
- ✅ `guardian`, `webhook`, etc. - Feature-spezifische Docs

**Beispiele:**

```bash
docs(docs): update README with new deployment examples
docs(guardian): add docstrings to ContainerGuardian class
docs(webhook): document Apprise URL format requirements
docs(monitoring): explain health check precedence
```

### `refactor` (Code-Umstrukturierung)

Für technische Verbesserungen ohne Funktionsänderung:

- ✅ `guardian` - Core-Refactoring
- ✅ `monitoring` - Health-Check Code-Optimierung
- ✅ `recovery` - Recovery-Code-Cleanup
- ✅ `webhook` - Notification-Refactoring

**Beispiele:**

```bash
refactor(guardian): extract health check logic to separate methods
refactor(monitoring): simplify HTTP check error handling
refactor(recovery): use subprocess context manager
refactor(webhook): consolidate notification formatting
```

### `perf` (Performance-Verbesserungen)

Performance-kritische Bereiche:

- ✅ `guardian` - Haupt-Loop Optimierung
- ✅ `monitoring` - Schnellere Health-Checks
- ✅ `recovery` - Schnellere Recovery

**Beispiele:**

```bash
perf(guardian): reduce Docker API call frequency
perf(monitoring): parallelize container health checks
perf(recovery): optimize image pull with --quiet flag
```

### `test` (Tests)

Test-Scope oder getesteter Bereich:

- ✅ `guardian` - Guardian-Tests
- ✅ `monitoring` - Health-Check Tests
- ✅ `recovery` - Recovery-Tests

**Beispiele:**

```bash
test(guardian): add tests for failure tracking
test(monitoring): add HTTP check timeout tests
test(recovery): mock docker compose commands in tests
```

### `ci` (CI/CD)

Immer CI-Scope:

- ✅ `ci` - GitHub Actions, Workflows, Linting, Tools

**Beispiele:**

```bash
ci(ci): add prettier formatting check to workflow
ci(ci): configure cz-customizable with scope selection
ci(ci): integrate Docker build into release workflow
ci(ci): add mypy type checking to lint workflow
```

### `chore` (Wartung)

Je nach Wartungsbereich:

- ✅ `deps` - Dependency Updates
- ✅ `config` - Konfigurationsänderungen
- ✅ Andere Scopes je nach Kontext

**Beispiele:**

```bash
chore(deps): update docker SDK to 7.1.0
chore(config): adjust default grace period to 300s
chore(docker): update base image to python 3.11-slim
```

### `build` (Build-System)

Build-relevante Scopes:

- ✅ `docker` - Dockerfile, Build-Prozess
- ✅ `deps` - Build-Dependencies

**Beispiele:**

```bash
build(docker): add multi-platform build support
build(deps): pin dependency versions in Dockerfile
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
