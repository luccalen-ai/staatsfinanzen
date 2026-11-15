# Staatsfinanzen Österreich

Ein offenes, nachvollziehbares Modell der österreichischen Staatsfinanzen: woher das Geld kommt, wohin es fließt, welche Ausgaben gesetzlich gebunden sind und welche frei gestaltbar, und wo Doppelgleisigkeiten oder Einsparpotenziale liegen. Grundlage sind ausschließlich öffentlich verfügbare Daten und Anfragen nach dem Informationsfreiheitsgesetz.

Träger des Projekts ist ein Verein (in Gründung).

## Module

1. **Geldfluss** – Einnahmen, Ausgaben nach Funktion und Ebene (Bund, Länder, Gemeinden, Sozialversicherung), Transfers zwischen den Ebenen. Wien ist von Beginn an als Land und Gemeinde abgebildet.
2. **Bindungsgrad** – jede Budgetposition nach dem, was eine Änderung erfordert (A Verfassung/EU/Staatsvertrag, B einfaches Gesetz, C Vertrag oder Mehrjahresbindung, D Ermessen).
3. **Förderungen** – jedes Förderprogramm mit Fördergeber, Rechtsgrundlage, Volumen, Ziel, Evaluierung und Überschneidungen, inklusive indirekter Förderungen.
4. **Grenzüberschreitende Flüsse** – EU-Beitrag und Rückflüsse, gesamte Entwicklungshilfe (ODA, nicht nur ADA), internationale Organisationen.
5. **Vergleiche** – Österreich gegenüber Vergleichsländern und gegenüber sich selbst seit 2019.
6. **Befunde** – quantifizierte Einspar- und Reformoptionen mit Quelle und Status.

## Grundsätze

- Jede Zahl hat Quelle, Abrufdatum, Stand, Rechnungsbasis und Verlässlichkeitsstufe.
- Jeder Euro wird nur einmal gezählt.
- Darstellung so intuitiv und klar wie möglich, ohne die Daten zu verzerren.
- Keine personenbezogenen Daten natürlicher Personen. Keine Vorwürfe ohne Feststellung durch Rechnungshof, Gericht oder Staatsanwaltschaft.
- Politisch neutral: derselbe Maßstab für jedes Ministerium, jede Partei, jedes Land.

## Aufbau

| Ordner | Inhalt |
| --- | --- |
| `docs/` | Master-Prompt, Methodik |
| `agents/` | Arbeitsanweisungen der spezialisierten Agenten |
| `registry/` | Quellenverzeichnis |
| `ops/` | Aufgaben, Entscheidungen, Datenlücken |
| `ingest/` | Download- und Parser-Skripte, eines pro Quelle |
| `models/` | SQL-Transformationen von Staging zu Core |
| `data/` | `raw` (unverändert, nicht im Repo), `staging`, `core` |
| `site/` | Öffentliche Website |
| `tests/` | Abgleich mit Kontrollsummen, Datentests |

## Technik

Python für den Datenimport, DuckDB und Parquet als Speicher, SQL für Transformationen, statische Website für die Veröffentlichung. Rohdateien werden unverändert mit Prüfsumme abgelegt; jede Grafik ist aus dem Repository reproduzierbar.

---

*Working language of this repository is English; all public-facing output is German first.*
