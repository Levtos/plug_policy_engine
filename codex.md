# Codex Instructions - Plug Policy Engine

Lies zuerst `CLAUDE.md` in diesem Repo.

## MCP-Server

Nutze fuer Home-Assistant-Kontext `einhornzentrale`, nicht `haos_benni`.

## Repo-Stand

Dieses Repo ist die eigenstaendige HACS-Integration fuer die Domain
`plug_policy_engine`. Der Domain-Slug bleibt stabil; keine Umbenennung zu
`benni_*`.

## Arbeitsregeln

- Engine-Logik bleibt HA-frei und wird mit den pure Tests abgesichert.
- HA-State, Services, Storage, WebSocket und Panel gehoeren in Integration/
  Coordinator-Schichten, nicht in die pure Engine.
- `enable_control=false` ist der sichere Default. Live-Schalten laeuft nur ueber
  das Control-Gate.
- Cross-Modul-Inputs kommen als HA-Entity-IDs aus Config/Options, nicht als
  Python-Imports aus anderen Repos.
- Bei UI-Arbeit das vorhandene Vanilla-Web-Component-Panel ohne Build-Step
  erweitern.
