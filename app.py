# %% Imports
import streamlit as st
import json
import random
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from neo4j import GraphDatabase

# OpenAI- und Neo4j-Details aus Streamlit Secrets laden
openai_api_key = st.secrets["OPENAI_API_KEY"]
neo4j_uri = st.secrets["NEO4J_URI"]
neo4j_username = st.secrets["NEO4J_USERNAME"]
neo4j_password = st.secrets["NEO4J_PASSWORD"]

# Überprüfen, ob Secrets geladen wurden
if not openai_api_key:
    raise ValueError("Fehler: OpenAI API-Schlüssel konnte nicht geladen werden.")
if not neo4j_uri or not neo4j_username or not neo4j_password:
    raise ValueError("Fehler: Neo4j-Verbindungsdetails konnten nicht geladen werden.")

# Initialisierung von OpenAI LLM
try:
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", openai_api_key=openai_api_key)
    print("OpenAI LLM erfolgreich initialisiert.")
except Exception as e:
    raise ValueError(f"Fehler bei der Initialisierung des LLM: {e}")

# Verbindung herstellen
def connect_to_neo4j(uri, username, password):
    try:
        # Erstellen eines Treiberobjekts
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        print("Verbindung erfolgreich hergestellt.")
        return driver
    except Exception as e:
        raise ValueError(f"Fehler bei der Verbindung mit Neo4j: {e}")

# Verbindung zu Neo4j herstellen
neo4j_driver = connect_to_neo4j(neo4j_uri, neo4j_username, neo4j_password)

# Initialisierung des Neo4j Vector Index
try:
    vector_index = Neo4jVector.from_existing_graph(
        embedding=OpenAIEmbeddings(openai_api_key=openai_api_key),
        search_type="hybrid",
        node_label="Document",
        text_node_properties=["text"],
        embedding_node_property="embedding"
    )
    print("Neo4j Vector Index erfolgreich initialisiert.")
except Exception as e:
    raise ValueError(f"Fehler bei der Initialisierung des Vektor-Retrievers: {e}")

# %% Lese JSON-Daten für das Kartenlosbuch
try:
    with open("./data_karten.json", "r", encoding="utf-8") as file:
        karten_data = json.load(file)["kartenlosbuch"]
except Exception as e:
    raise ValueError(f"Fehler beim Laden der Karten-Daten: {e}")

# %% Neue Funktion: Nur Daten aus dem Graphen verwenden
def answer_question_from_graph(question):
    """
    Beantwortet Fragen ausschließlich basierend auf Daten aus dem Neo4j-Graphen.
    Wenn keine relevanten Informationen gefunden werden, wird dies klar kommuniziert.
    """
    try:
        # Suche nach relevanten Inhalten im Neo4j-Graphen
        results = vector_index.similarity_search(question)

        if results:
            # Kontext aus den Suchergebnissen extrahieren
            context = "\n".join([res.page_content for res in results])
            return (
                f"Antwort basierend auf dem Neo4j-Graphen:\n\n{context}"
            )
        else:
            # Keine relevanten Informationen im Graphen gefunden
            return (
                "Die gesuchten Informationen sind nicht im verfügbaren Neo4j-Graphen enthalten."
            )
    except Exception as e:
        # Fehlerbehandlung
        return f"Fehler bei der Beantwortung der Frage: {e}"

# %% Funktionen zur Verarbeitung
def get_uebersetzung_und_deutung(weissagung_text):
    """LLM für Hochdeutsch-Übersetzung und Deutung der Weissagung."""
    prompt_uebersetzung = f"Übersetze diesen alten deutschen Text ins moderne Hochdeutsch: '{weissagung_text}'"
    prompt_deutung = f"Basierend auf dieser Weissagung, was könnte sie in 2 Sätzen bedeuten oder andeuten? '{weissagung_text}'"

    try:
        # Übersetzung
        uebersetzung_response = llm(prompt_uebersetzung)
        # Deutung
        deutung_response = llm(prompt_deutung)
        return uebersetzung_response.strip(), deutung_response.strip()
    except Exception as e:
        raise ValueError(f"Fehler bei der Verarbeitung der Weissagung: {e}")

def ziehe_random_karte():
    """Ziehe ein zufälliges Los und liefere Symbol, Weissagung, Übersetzung und Deutung."""
    karte = random.choice(karten_data)
    uebersetzung, deutung = get_uebersetzung_und_deutung(karte["weissagung"])

    return {
        "symbol": karte["symbol"],
        "original_weissagung": karte["weissagung"],
        "hochdeutsch_weissagung": uebersetzung,
        "deutung": deutung,
        "image_path": karte["image_path"]
    }

# %% Streamlit UI
st.title("🔮 Das Mainzer Kartenlosbuch")

# Auswahl der Modus
mode = st.selectbox("Wähle einen Modus", ["Allgemeine Fragen", "Losbuch spielen"])

if mode == "Allgemeine Fragen":
    st.subheader("Stelle eine allgemeine Frage")
    question = st.text_input("Frage eingeben")

    if st.button("Frage stellen"):
        try:
            answer = answer_question_from_graph(question)
            st.write(f"**Antwort**: {answer}")
        except Exception as e:
            st.error(f"Fehler: {e}")

elif mode == "Losbuch spielen":
    st.subheader("Ziehe ein Los!")
    if st.button("Los ziehen"):
        try:
            los = ziehe_random_karte()
            st.write(f"**Symbol**: {los['symbol']}")
            st.write(f"**Weissagung (Original)**: {los['original_weissagung']}")
            st.write(f"**Weissagung (Hochdeutsch)**: {los['hochdeutsch_weissagung']}")
            st.write(f"**Deutung**: {los['deutung']}")
            st.image(los['image_path'])
        except Exception as e:
            st.error(f"Fehler: {e}")

# Neo4j-Driver schließen
if neo4j_driver:
    neo4j_driver.close()
