# Orakulus: Interaktiver Chatbot für die digitale Editionswissenschaft

Orakulus ist ein interaktiver Chatbot, der die Inhalte des Mainzer Kartenlosbuchs (1510) digital zugänglich macht. Mit einer Kombination aus Neo4j-Wissensgraphen, Retrieval-Augmented Generation (RAG) und Large Language Models (LLMs) ermöglicht er eine intuitive Wissensvermittlung in zwei Modi: dem allgemeinen Fragenmodus für semantische Anfragen zur Edition und dem Losbuchmodus, der eine interaktive Weissagungsfunktion basierend auf dem Kartenlosbuch bereitstellt.

## Online-Nutzung

Der Chatbot ist online verfügbar unter: [**Orakulus Anwendung**](https://orakulusmainz.streamlit.app)

## Lokale Installation

Voraussetzungen sind Python 3.9 oder höher, pip (Paketmanager) und Neo4j (lokal oder Cloud). Zum Starten: 

1. Repository klonen:  
   `git clone https://github.com/TillBaeumker/Orakulus.git && cd Orakulus`

2. Virtuelle Umgebung erstellen:  
   `python -m venv venv && source venv/bin/activate` (macOS/Linux)  
   `venv\Scripts\activate` (Windows)

3. Abhängigkeiten installieren:  
   `pip install -r requirements.txt`

4. Neo4j starten und konfigurieren. 

5. Anwendung ausführen:  
   `streamlit run app.py`

Viel Spaß mit Orakulus!
