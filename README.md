# Orakulus: Interaktive Wissensvermittlung mit einem KI-gestützten Chatbot

Orakulus ist ein Chatbot, der eine innovative Möglichkeit bietet, Inhalte in der digitalen Editionswissenschaft interaktiv zugänglich zu machen. Der Schwerpunkt liegt auf der Verbindung von Technologie und Wissenschaft, um komplexe historische und literarische Inhalte einfach und verständlich zu vermitteln. Orakulus basiert auf einer Kombination aus Neo4j, das Wissensgraphen für eine Datenstrukturierung und Abfrage nutzt, und OpenAI, das die natürliche Sprachverarbeitung übernimmt. Dadurch können Benutzer auf intuitive Weise mit den Inhalten interagieren.

Der Chatbot bietet zwei Hauptmodi:

Allgemeiner Fragenmodus:
In diesem Modus können Benutzer semantische Anfragen zur digitalen Edition stellen. Orakulus nutzt den Neo4j-Wissensgraphen, um präzise Informationen zu den Inhalten der Edition zu liefern. Dies ermöglicht eine interaktive Erforschung der Themen, die im Zusammenhang mit dem Mainzer Kartenlosbuch (1510) stehen, und bietet eine detaillierte, kontextbezogene Antwort auf spezifische Fragen.

Losbuchmodus:
Dieser Modus ist inspiriert von der ursprünglichen Funktion des Mainzer Kartenlosbuchs als Weissagungsinstrument. Benutzer können in einer interaktiven Sitzung ein Los ziehen, und der Chatbot interpretiert dieses basierend auf den historischen Texten und Bedeutungen. Dies bietet eine Funktionen des Kartenlosbuchs auf spielerische Weise zu erleben.

## Online-Nutzung

Der Chatbot ist online verfügbar unter:  
[**Orakulus**](https://orakulusmainz.streamlit.app)

## Lokale Installation
## Voraussetzungen

Bevor du startest, stelle sicher, dass folgende Anforderungen erfüllt sind:
1. **Python 3.9 oder höher** ist installiert. [Python herunterladen](https://www.python.org/downloads/)
2. **pip** (Python-Paketmanager) ist installiert.
3. **Neo4j** ist verfügbar (lokal oder in der Cloud). [Neo4j herunterladen](https://neo4j.com/download-center/) oder [Neo4j Aura nutzen](https://neo4j.com/cloud/aura/).
4. Du hast Zugriff auf **OpenAI API-** und **Neo4j-Zugangsdaten** (eigenen Account erstellen).

## Installation
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
Erstelle eine Datei `.streamlit/secrets.toml` im Projektverzeichnis mit folgendem Inhalt:  
 
OPENAI_API_KEY = "Dein_OpenAI_API_Key"  
NEO4J_URI = "neo4j+s://Dein_Neo4j_Host"  
NEO4J_USER = "Dein_Neo4j_Benutzername"  
NEO4J_PASSWORD = "Dein_Neo4j_Passwort"  

> Hinweis: Bitte füge deine eigenen API-Keys und Zugangsdaten ein.

### Anwendung ausführen
```bash
streamlit run app.py  
```

## Hinweise

### Eigene OpenAI- und Neo4j-Zugangsdaten verwenden
Falls du noch keine OpenAI- oder Neo4j-Zugangsdaten hast:
- **OpenAI API:** Erstelle einen Account und generiere einen API-Schlüssel auf der [OpenAI Website](https://platform.openai.com/).
- **Neo4j:** Nutze entweder eine lokale Installation oder erstelle ein kostenloses Konto bei [Neo4j Aura](https://neo4j.com/cloud/aura/).
- Wenn du einen eigenen Neo4j-Graphen nutzt, beachte bitte, dass die Inhalte deines Graphen nicht mit denen der Webversion übereinstimmen. Die Webversion verwendet einen speziell erstellten Graphen, der Informationen aus dem Mainzer Kartenlosbuch (1510) enthält. Um die Funktionalitäten des Losbuchmodus und die spezifischen Inhalte der Webversion zu reproduzieren, müssen die Daten des Mainzer Kartenlosbuchs in deinem eigenen Graphen vorhanden sein.

## Lizenz
Dieses Projekt steht unter der MIT-Lizenz. Weitere Informationen findest du in der Datei `LICENSE`.
