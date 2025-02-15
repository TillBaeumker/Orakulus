![Orakulus Chatbot(Erstellt mit Dall-E)](orakulus_chatbot.png)

# Orakulus: Ein Chatbot-Prototyp für die digitale Editionswissenschaft

Orakulus demonstriert, wie ein Chatbot auf Basis von Wissensgraphen (Neo4j) und KI (GPT 4-o-mini) historische Inhalte interaktiv zugänglich machen kann. Eine Edition des 1510 von Johann Schöffer gedruckten *Mainzer Kartenlosbuches*, die 2021 von Matthias Däumer ediert wurde, dient dabei als Datenbasis.

## Funktionen

- **Allgemeiner Fragenmodus**  
  Hier können Nutzer:innen natürlichsprachige Anfragen zur Edition stellen. Orakulus greift auf den Wissensgraphen in \textit{Neo4j} zu und liefert kontextbezogene Antworten.

- **Losbuchmodus**  
  Dieser Modus ist inspiriert vom historischen Kartenlosbuch: Ein zufälliges Los wird gezogen und die zugehörige Weissagung wird angezeigt. 

Orakulus versteht sich als Prototyp: Er zeigt Potenziale eines KI-gestützten Chatbots in der digitalen Editionswissenschaft. Weitere technische Details und Evaluationsergebnisse finden sich im [Paper](./Paper_EinZugangZuEditionen.pdf).

## Online-Nutzung

Der Chatbot ist online verfügbar unter:  [**Orakulus**](https://orakulusmainz.streamlit.app)

## Lokale Installation
**Hinweis:** Eine lokale Installation ist nicht erforderlich, wenn du den Chatbot nur über die Streamlit Community Cloud nutzen möchtest. Die folgenden Schritte beschreiben die **optionale** lokale Installation.

### Voraussetzungen
Bevor du startest, stelle sicher, dass folgende Anforderungen erfüllt sind:
1. **Python 3.9 oder höher** ist installiert. [Python herunterladen](https://www.python.org/downloads/)
2. **pip** (Python-Paketmanager) ist installiert.
3. **Neo4j** ist verfügbar (lokal oder in der Cloud). [Neo4j herunterladen](https://neo4j.com/download-center/) oder [Neo4j Aura nutzen](https://neo4j.com/cloud/aura/).
4. Du hast Zugriff auf **OpenAI API-** und **Neo4j-Zugangsdaten** (eigenen Account erstellen).

### Installation
### Repository klonen
```bash
git clone https://github.com/TillBaeumker/Orakulus.git  
cd Orakulus  
```

### Abhängigkeiten installieren
```bash
pip install -r requirements.txt  
```

### OpenAI- und Neo4j-Zugangsdaten hinzufügen
Füge in die Datei "secrets.toml" im Ordner ".streamlit" im Projektverzeichnis den folgenden Inhalt ein:
 
OPENAI_API_KEY = "Dein_OpenAI_API_Key"  
NEO4J_URI = "neo4j+s://Dein_Neo4j_Host"  
NEO4J_USERNAME = "Dein_Neo4j_Benutzername"  
NEO4J_PASSWORD = "Dein_Neo4j_Passwort"  

> Hinweis: Bitte füge deine eigenen API-Keys und Zugangsdaten ein.

### Anwendung ausführen
```bash
streamlit run app.py  
```

## Hinweise

### Eigene OpenAI- und Neo4j-Zugangsdaten verwenden
Falls du noch keine OpenAI- oder Neo4j-Zugangsdaten hast:
- **OpenAI API:** Erstelle einen Account und generiere einen API-Schlüssel unter OpenAI API. Stelle sicher, dass das Modell gpt-4.0-mini verfügbar ist, da der Code dieses Modell nutzt.
- **Neo4j:** Nutze entweder eine lokale Installation oder erstelle ein kostenloses Konto bei [Neo4j Aura](https://neo4j.com/cloud/aura/).
- Wenn du einen eigenen Neo4j-Graphen nutzt, beachte bitte, dass die Inhalte deines Graphen nicht mit denen der Webversion übereinstimmen. Die Webversion nutzt einen speziell erstellten Graphen mit Informationen aus der Edition des Mainzer Kartenlosbuchs (1510) von Matthias Däumer (2021). Um die Funktionalitäten des Losbuchmodus und die spezifischen Inhalte der Webversion zu reproduzieren, müssen die Daten des Mainzer Kartenlosbuchs in deinem eigenen Graphen vorhanden sein.

### Literatur:
Däumer, Matthias (2021). „Mainzer Kartenlosbuch: Eyn losz buch ausz der karten gemacht“. In: Gedruckte deutsche Losbücher des 15. und 16. Jahrhunderts. Hrsg. von Marco Heiles, Björn Reich und Matthias Standke. Bd. 1, S. 87–122

## Lizenz
Dieses Projekt steht unter der MIT-Lizenz. Weitere Informationen findest du in der Datei `LICENSE`.
