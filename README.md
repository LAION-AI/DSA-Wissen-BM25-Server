Perfekt, ich habe verstanden, was du möchtest: ein klares, kompaktes README, das erklärt, wie **Wissen aus der Wiki Aventurica** strukturiert wurde und was der **BM25-Server** damit macht. Ohne Marketing-Blabla, sondern auf den Punkt.

Hier ist mein Vorschlag für dein `README.md`:

````markdown
# DSA-Wissen BM25-Server

Dieses Projekt stellt einen BM25-basierten Suchserver für Wissen rund um **Das Schwarze Auge (DSA)** bereit.  
Die Daten stammen aus der **Wiki Aventurica** (https://de.wiki-aventurica.de) und wurden mithilfe von Large Language Models strukturiert aufbereitet.

## Datenaufbereitung

Aus den Wiki-Aventurica-Artikeln wurde Wissen extrahiert und in eine standardisierte JSON-Struktur überführt.  
Jede Entität (z. B. **Ort, Charakter, Gruppe, Ereignis, Konzept, Regel**) erhält:

- eine kurze **Beschreibung**,  
- eine Menge von **Fakten** in Form von Aussagen, jeweils mit **Quellenangabe** (entweder die entsprechende Wiki-Aventurica-Seite oder Referenzen aus den dort angegebenen Quellenmaterialien),  
- eine Liste von **verwandten Entitäten**,  
- sowie **Stichworte**, die thematisch passen.

### Beispiel

```json
"Gründung_des_Theaterordens": {
  "type": "Ereignis",
  "description": "Die Gründung des Theaterordens erfolgte 3 BF im Amphitheater zu Arivor...",
  "facts": [
    {
      "statement": "Das Ereignis 'Gründung des Theaterordens' fand im Zeitraum 3 BF statt.",
      "source": "HA S.191; LdsB S.13; WikiAventurica:Heiliger_Orden..."
    },
    {
      "statement": "Lutisana von Kullbach wird erste Marschallin des Theaterordens.",
      "source": "HA S.191; LdsB S.13; WikiAventurica:Heiliger_Orden..."
    }
  ],
  "related_entities": [
    "Theaterorden",
    "Arivor",
    "Rondra-Geweihte",
    "Lutisana_von_Kullbach"
  ]
}
````

## Nutzung

Der BM25-Server ermöglicht die **schnelle Abfrage** dieses Wissensbestands.
Ein Language Model kann so mit einem **Systemprompt** über Aventurien kombiniert werden und anschließend:

* gezielt Detailfragen zu Orten, Personen, Ereignissen oder Regeln stellen,
* Kontextwissen für **Spieler\*innen und Spielleiter-Bots** bereitstellen,
* Quellenhinweise für weitere Exploration liefern.

## Ziel

Das Projekt bildet die Grundlage, um **Language-Model-Agenten** zu befähigen, Aventurien-spezifisches Fachwissen **on the fly** abzurufen und für Abenteuer, Regelwerk-Fragen oder Spielleiter-Unterstützung nutzbar zu machen.

```

---

👉 Soll ich dir auch gleich noch einen **Usage-Abschnitt** mit Beispiel-Query gegen den BM25-Server (`curl` oder Python-Snippet) ins README schreiben, damit Leute sofort sehen, wie man es abfragt?
```
