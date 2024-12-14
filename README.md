# Orakulus: Interaktive Wissensvermittlung mit einem KI-gestützten Chatbot

Orakulus ist ein Chatbot, der interaktive Wissensvermittlung in der digitalen Editionswissenschaft ermöglicht. Der Chatbot verwendet Neo4j für Wissensgraphen und OpenAI zur Generierung natürlicher Sprache. Diese Anleitung beschreibt, wie du die Anwendung lokal ausführen kannst.

## Voraussetzungen

Bevor du startest, stelle sicher, dass folgende Anforderungen erfüllt sind:
1. **Python 3.9 oder höher** ist installiert. [Python herunterladen](https://www.python.org/downloads/)
2. **pip** (Python-Paketmanager) ist installiert.
3. **Neo4j** ist verfügbar (lokal oder in der Cloud). [Neo4j herunterladen](https://neo4j.com/download-center/) oder [Neo4j Aura nutzen](https://neo4j.com/cloud/aura/).
4. Du hast Zugriff auf **OpenAI API-** und **Neo4j-Zugangsdaten** (eigenen Account erstellen).

## Installation
```bash
# Repository klonen
git clone https://github.com/TillBaeumker/Orakulus.git  
cd Orakulus  

# Abhängigkeiten installieren
pip install -r requirements.txt  

# OpenAI- und Neo4j-Zugangsdaten hinzufügen
# Erstelle eine Datei `.streamlit/secrets.toml` im Projektverzeichnis mit folgendem Inhalt:  
 
OPENAI_API_KEY = "Dein_OpenAI_API_Key"  
NEO4J_URI = "neo4j+s://Dein_Neo4j_Host"  
NEO4J_USER = "Dein_Neo4j_Benutzername"  
NEO4J_PASSWORD = "Dein_Neo4j_Passwort"  

> Hinweis: Bitte füge deine eigenen API-Keys und Zugangsdaten ein.

# Anwendung ausführen
streamlit run app.py  
```

## Hinweise

### Eigene OpenAI- und Neo4j-Zugangsdaten verwenden
Falls du noch keine OpenAI- oder Neo4j-Zugangsdaten hast:
- **OpenAI API:** Erstelle einen Account und generiere einen API-Schlüssel auf der [OpenAI Website](https://platform.openai.com/).
- **Neo4j:** Nutze entweder eine lokale Installation oder erstelle ein kostenloses Konto bei [Neo4j Aura](https://neo4j.com/cloud/aura/).

## Lizenz
Dieses Projekt steht unter der MIT-Lizenz. Weitere Informationen findest du in der Datei `LICENSE`.
