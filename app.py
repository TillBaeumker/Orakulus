# %% Imports
import streamlit as st
import json
import random
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from neo4j import GraphDatabase
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings

# OpenAI- und Neo4j-Details aus Streamlit Secrets laden
openai_api_key = st.secrets["OPENAI_API_KEY"]
neo4j_uri = st.secrets["NEO4J_URI"]
neo4j_username = st.secrets["NEO4J_USERNAME"]
neo4j_password = st.secrets["NEO4J_PASSWORD"]

# OpenAI-LLM initialisieren
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", openai_api_key=openai_api_key)

# Verbindung zu Neo4j-Datenbank
def connect_to_neo4j(uri, username, password):
    """
    Stellt eine Verbindung zur Neo4j-Datenbank her.
    """
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        print("Verbindung zu Neo4j erfolgreich hergestellt.")
        return driver
    except Exception as e:
        raise ValueError(f"Fehler bei der Verbindung mit Neo4j: {e}")

# Verbindung herstellen
try:
    neo4j_driver = connect_to_neo4j(neo4j_uri, neo4j_username, neo4j_password)
except ValueError as e:
    st.error(f"Fehler bei der Verbindung mit Neo4j: {e}")

# Neo4j-Vektor-Retriever initialisieren
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
    st.error(f"Fehler bei der Initialisierung des Vektor-Retrievers: {e}")

# Kontext aus Neo4j abrufen
def retrieve_graph_context(question):
    """
    Sucht relevante Inhalte im Neo4j-Graphen basierend auf der Frage.
    """
    try:
        results = vector_index.similarity_search(question)
        if results:
            return "\n\n".join([res.page_content.strip() for res in results])
        else:
            return ""
    except Exception as e:
        return f"Fehler bei der Suche im Graphen: {e}"

# Frage basierend auf dem Graph beantworten
def answer_question_from_graph_with_llm(question):
    """
    Beantwortet eine Frage, indem der Kontext aus dem Neo4j-Graph verwendet wird.
    """
    try:
        graph_context = retrieve_graph_context(question)
        if graph_context.strip():
            prompt_template = ChatPromptTemplate.from_template("""Nutze ausschließlich die im Graphen enthaltenen Informationen, um eine Antwort zu generieren:
                {context}

                Frage: {question}

                Antworte präzise und klar.""")
            chain = LLMChain(llm=llm, prompt=prompt_template)
            return chain.run(context=graph_context, question=question)
        else:
            return "Es konnten keine relevanten Informationen im Neo4j-Graphen gefunden werden."
    except Exception as e:
        return f"Fehler bei der Beantwortung der Frage: {e}"

# JSON-basierte Funktion für "Losbuch spielen"
json_file_path = "data_karten.json"

def load_losbuch_data(file_path):
    """
    Lädt die Daten des Kartenlosbuchs aus der JSON-Datei.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data.get("kartenlosbuch", [])
    except Exception as e:
        st.error(f"Fehler beim Laden der JSON-Datei: {e}")
        return []

def translate_to_hochdeutsch(weissagung):
    """
    Übersetzt die Weissagung auf Hochdeutsch mithilfe von GPT-4o-mini.
    """
    try:
        prompt = f"Übersetze den folgenden mittelalterlichen Text ins Hochdeutsche:\n\n{weissagung}"
        response = llm.predict(prompt)
        return response.strip()
    except Exception as e:
        st.error(f"Fehler bei der Übersetzung: {e}")
        return "Fehler bei der Übersetzung."

def ziehe_random_karte(data):
    """
    Wählt zufällig ein Los aus den JSON-Daten.
    """
    if not data:
        return None
    return random.choice(data)

# Streamlit-UI
st.title("🔮 Das Mainzer Kartenlosbuch")

# Auswahl des Modus
mode = st.selectbox("Wähle einen Modus", ["Allgemeine Fragen", "Losbuch spielen"])

if mode == "Allgemeine Fragen":
    st.subheader("Stelle eine Frage zu den Weissagungen:")
    question = st.text_input("Frage eingeben")

    if st.button("Frage stellen"):
        try:
            answer = answer_question_from_graph_with_llm(question)
            st.write(f"**Antwort**: {answer}")
        except Exception as e:
            st.error(f"Fehler: {e}")

elif mode == "Losbuch spielen":
    st.subheader("Ziehe ein Los!")
    losbuch_data = load_losbuch_data(json_file_path)

    if st.button("Los ziehen"):
        los = ziehe_random_karte(losbuch_data)
        if los:
            st.image(los["image_path"], caption=f"Symbol: {los['symbol']}")
            st.write(f"**Original-Weissagung:**\n{los['weissagung']}")

            hochdeutsch_weissagung = translate_to_hochdeutsch(los["weissagung"])
            st.write(f"**Weissagung (Hochdeutsch):**\n{hochdeutsch_weissagung}")
        else:
            st.error("Es konnte kein Los gezogen werden.")
