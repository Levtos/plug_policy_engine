# Einhornzentrale: Plug- und Power-Switch-Inventar

Stand: 2026-07-17

Scope: Benni / Einhornzentrale (`192.168.178.106:8123`)

Arbeitsnachweis: `ha-platform/control#38`

## Quellen und Abgrenzung

Die Tabelle basiert auf einer Read-only-Abfrage der Home-Assistant-Entity- und
Device-Registry, dem geladenen `plug_policy_engine`-Statussensor und dem
reviewten Lastenheft `steckdosen/lastenheft.md` Version 1.2. Erfasst sind alle
physischen Steckdosen sowie die beiden Shelly-Ausgänge, die reale Verbraucher
schalten. Netzwerkzugangs-, Kindersicherungs-, Geräteoptions-, Helper- und
Policy-Switches sind keine Steckdosen und werden nicht automatisch aufgenommen.

Von 116 aktiv gelisteten `switch.*`-Entities entfallen 42 auf FRITZ-Netzzugang,
29 auf MQTT/Zigbee2MQTT, 5 auf Tuya, 2 auf Shelly und 38 auf rein logische oder
Geräteoptions-Plattformen. Zusätzlich existiert der bewusst deaktivierte
physische TV-Ausgang `switch.living_tv_plug`. Damit ergeben sich 19 physische
Plug-/Power-Switch-Ausgänge. Sieben MQTT-`*_child_lock`-Entities sind
Geräteoptionen derselben Plugs und keine zusätzlichen Steckdosen.

## Direktiven

- `AO`: permanent versorgt; ein `off`, HA-Neustart oder Reconnect führt zu
  `turn_on`. Eine manuelle Abschaltung am Entity wird deshalb wieder aufgehoben.
- `CS`: funktional wie AO, fachlich als dauerhaft verfügbarer Ladepfad benannt.
- `HB`: Baseline-Schutz; kein automatischer Away-Cut.
- `AC`: nur bei echter Abwesenheit und nachgewiesenem Idle abschaltbar.
- `SC`: zeit-/kontextgesteuert.
- `SPECIAL`: gerätespezifischer Contract oder explizit externer Owner.
- `UNMANAGED`: bewusst nicht durch Plug Policy gesteuert; kein impliziter
  Fallback.

## Vollständige physische Inventartabelle

| Entity | Gerät/Funktion | Aktuelle Abdeckung | Vorgeschlagene Direktive | Begründung / Entscheidung |
|---|---|---|---|---|
| `switch.bath_diffuser_plug` | Duftstecker Bad | nein | `SPECIAL` / Klima-Owner | Laut Lastenheft außerhalb der Plug Policy; keine Doppelsteuerung. |
| `switch.bath_fan` | Badlüfter (Shelly) | nein | `SPECIAL` / Klima-Owner | Fest verdrahteter Lüfterausgang, keine Steckdose; Klima-/Lüfterlogik besitzt den Aktor. |
| `switch.kitchen_coffee_machine_plug` | Kaffeevollautomat | ja: `AO/coffee_maker` | `AO` | 0 W im Aus-Zustand und Wake-Indikator; Versorgung bleibt verfügbar. |
| `switch.kitchen_diffuser_plug` | Duftstecker Küche | ja: `SC/diffuser` | `SC` | 15/15-Kontexttakt gemäß Lastenheft. |
| `switch.kitchen_dishwasher_plug` | Spülmaschine | ja: live `AO/appliance` | `AC` | Lastenheft: nur echt abwesend + stabil idle; laufendes Programm ist geschützt. Live-Direktive ist bewusst zu migrieren, nicht still zu überschreiben. |
| `switch.kitchen_dryer_plug` | Trockner | ja: live `AO/appliance` | `AC` | Wie Spülmaschine; laufende Programme dürfen nie getrennt werden. |
| `switch.kitchen_washing_machine_plug` | Waschmaschine | ja: live `AO/appliance` | `AC` | Wie Spülmaschine; Power-Unknown gilt als aktiv. |
| `switch.lichtschalter_bad` | Badlicht (Shelly) | nein | `SPECIAL` / Light-Owner | Fest verdrahteter Lichtaktor; kein Plug-Policy-Verbraucher. |
| `switch.living_bias_light_plug` | Govee T2 Bias Light | ja: `SPECIAL/bias_light` | `SC` (implementiert als `SPECIAL/bias_light`) | Activity-/TV-Kontext steuert den Ausgang; Kind-Branch besitzt die SC-Semantik. |
| `switch.living_blind_plug` | Rollo-Lader | ja: `SPECIAL/blind` | `SPECIAL` | 40/80-Akkulogik des Rollo-Laders, kein generischer Plug-Zeitplan. |
| `switch.living_denon_plug` | Denon AVR | nein | `HB` | Aktuelle Entity war im Profil durch den veralteten Suffix `_denon` nicht bindbar; aktiver/unklarer AVR bleibt geschützt. |
| `switch.living_pc_plug` | PC | ja: `HB/pc` | `SPECIAL` (implementiert als `HB/pc`) | Eigene Sleep-, Aktivitäts- und Manual-on-Cooldown-Regeln. |
| `switch.living_ps5_plug` | PlayStation 5 | ja: `AO/generic` | `AO` | Standby-Ersparnis rechtfertigt keine automatische Trennung. |
| `switch.living_subwoofer_plug` | Subwoofer | nein | `SPECIAL` / Media-Apply-Owner | Lastenheft schließt ihn aus; Media Policy/Apply besitzt die Versorgungskette. |
| `switch.living_tv_plug` | OLED TV | nein; Entity bewusst deaktiviert | `AO`, Entity deaktiviert lassen | Lastenheft: dauerhaft an, kein aktiver Steuerfall. Die korrigierte Profilbindung greift nur, falls die Entity bewusst aktiviert wird. |
| `switch.smart_power_strip_steckdose_1_tablet` | Wall-Dashboard-Tablet | ja: `SPECIAL/tablet` | `SPECIAL` | 40/80-Ladehysterese und Tiefentladungsschutz, unabhängig von Anwesenheit. |
| `switch.smart_power_strip_steckdose_2` | Smart-Power-Strip Steckdose 2 | nein | `UNMANAGED` bis Verbraucher zugeordnet | Registry enthält weder Funktionsname noch belastbaren Verbraucher-Nachweis. Bewusste Reserve statt geratenem Steuerfall. |
| `switch.smart_power_strip_dualsense` | DualSense-/PS5-Controller-Lader | ja: live `AO/generic` | `CS` | Ladepfad soll stabil verfügbar bleiben; CS ist funktional AO, aber fachlich präziser. |
| `switch.smart_power_strip_usb_1` | Aqara Hub M3 | nein | `AO` | Kritische Matter-/U200-Infrastruktur; Versorgung muss nach Off, Neustart und Reconnect wiederhergestellt werden. |

## Abdeckungs- und Bindungsbefunde

- Aktuell verwaltet: 11 eindeutige Switch-Entities; keine Doppelbindung.
- Fehlende kritische Bindung: `switch.smart_power_strip_usb_1` (Aqara M3).
- Fehlende fachliche Bindung: `switch.living_denon_plug`.
- Veraltet und aus dem Profil entfernt: `switch.living_denon_plug_denon`,
  `switch.hall_h14_pro_plug`, `switch.living_switch_plug` und
  `switch.wohnbereich_steckdose_tv` sowie deren alte Atomic-Power-Bindungen.
- H14-Dock und Nintendo-Switch-Plugs sind im aktuellen physischen Entity-Inventar
  nicht vorhanden. Sie bleiben Lastenheft-Historie, werden aber nicht als tote
  Profilkandidaten weitergeführt.
- Die drei Haushaltsgeräte sind live noch AO, fachlich aber AC. Eine Änderung
  erfolgt operativ bewusst im Options-Flow, weil bestehende Einträge von einem
  Profil-Prefill niemals still überschrieben werden.

## Neustart, Stromausfall und manuelle Abschaltung

Der Coordinator evaluiert beim HA-Start, bei jedem beobachteten Zustandswechsel
und zyklisch. AO/CS liefert für jeden Zustand außer `on` das Ziel `on`.
Wiederholte Befehle bleiben auf mindestens 30 Sekunden gedrosselt. Ab Version
0.3.3 darf der Non-Latching-Schutz einen AO/CS-`turn_on`-Pfad nicht mehr
suspendieren; nach Rückkehr von Strom, Tuya-Verbindung oder Entity-Verfügbarkeit
wird weiter reconciled, bis der Ausgang `on` meldet.

Eine bewusste manuelle Entity-Abschaltung ist bei AO/CS kein Override: Sie wird
gemäß bestehendem Always-On-Contract wieder eingeschaltet. Für eine geplante
Außerbetriebnahme muss die Direktive geändert, das Gerät aus der Policy entfernt
oder die Policy administrativ suspendiert werden. Ein bloßes Ausschalten des
Relais ist für kritische Infrastruktur kein zulässiger Dauerzustand.

## Tests und operative Verifikation

Automatisiert zu prüfen:

1. kompletter Pytest-Lauf;
2. AO/CS-Entscheidung für `off`, `unknown` und `unavailable` ist `on`;
3. fünf wiederholte AO/CS-`turn_on`-Versuche lösen keine Suspension aus;
4. andere Non-Latching-Pfade behalten den bisherigen Schutz;
5. Benni-Prefill liefert M3=`AO`, DualSense=`CS`, Denon=`HB` und die aktuellen
   Entity-IDs.

Nach Installation durch Benni:

1. Plug Policy → Optionen → Profilgeräte vorausfüllen; M3 und Denon hinzufügen;
2. bestehende Haushaltsgeräte bewusst von AO auf AC sowie DualSense von AO auf
   CS umstellen;
3. kontrolliert `switch.smart_power_strip_usb_1` ausschalten und prüfen, dass
   Plug Policy ihn wieder einschaltet und der M3/U200 erreichbar bleibt;
4. HA neu starten und denselben Sollzustand prüfen;
5. bei einem geplanten Wartungsfenster die Power-Strip-Versorgung trennen,
   wiederherstellen und den Reconcile nach Tuya-Reconnect beobachten.

Produktionsstatus bleibt bis zu dieser Verifikation `testing`, nicht `live`.

## Release- und Wiki-Auswirkung

Patch-Release `0.3.3`; keine Config-Schema-Migration und keine allgemeine
Produktisierung. Die Änderungen liegen ausschließlich in den vorhandenen
Benni-Profilvorgaben und im generischen AO/CS-Sicherheitscontract. Bestehende
Options-Einträge werden nicht automatisch überschrieben.

Eine zentrale Wiki-Seite ist für diesen wohnungsspezifischen Entity-Snapshot
nicht sinnvoll. Dieses versionierte Inventar ist der technische Nachweis; das
reviewte Lastenheft bleibt die fachliche Wahrheit. Im GitLab-Issue werden MR,
Release, Tests und die spätere Live-Verifikation verlinkt.
