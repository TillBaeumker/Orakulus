# %% Imports
import streamlit as st
import random
import json
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings

# OpenAI- und Neo4j-Details aus Streamlit Secrets laden
openai_api_key = st.secrets["OPENAI_API_KEY"]
neo4j_uri = st.secrets["NEO4J_URI"]
neo4j_username = st.secrets["NEO4J_USERNAME"]
neo4j_password = st.secrets["NEO4J_PASSWORD"]

# Pfad zur unstrukturierten Textdatei
text_file_path = "extrahierter_text.txt"

# JSON-Datei mit Losbuch-Daten laden
with open("data_karten.json", "r", encoding="utf-8") as f:
    losbuch_data = json.load(f)["kartenlosbuch"]

# Initialisierung aller Ressourcen (Einmalig)
def initialize_resources():
    """
    Initialisiert Neo4j, LLM und Vektorindex.
    """
    try:
        # Neo4j-Verbindung herstellen
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))
        driver.verify_connectivity()

        # LLM initialisieren
        llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", openai_api_key=openai_api_key)

        # Neo4j Vector Index initialisieren
        vector_index = Neo4jVector.from_existing_graph(
            embedding=OpenAIEmbeddings(openai_api_key=openai_api_key),
            search_type="hybrid",
            node_label="Document",
            text_node_properties=["text"],
            embedding_node_property="embedding"
        )

        # Unstrukturierte Textdatei laden
        with open(text_file_path, "r", encoding="utf-8") as file:
            raw_text = file.read()

        with driver.session() as session:
        result = session.run("MATCH (doc:Document {name: 'extrahierter_text'}) RETURN doc LIMIT 1")
        if not result.single():
        session.run("""
        MERGE (doc:Document {name: "extrahierter_text"})
        ON CREATE SET doc.text = $text
        """, text=raw_text)

        st.success("Ressourcen erfolgreich initialisiert.")
        return driver, llm, vector_index
    except Exception as e:
        st.error(f"Fehler bei der Initialisierung der Ressourcen: {e}")
        st.stop()

# Ressourcen in st.session_state speichern
if "resources_initialized" not in st.session_state:
    with st.spinner("Initialisiere Ressourcen, bitte warten..."):
        neo4j_driver, llm, vector_index = initialize_resources()
        st.session_state.neo4j_driver = neo4j_driver
        st.session_state.llm = llm
        st.session_state.vector_index = vector_index
        st.session_state.resources_initialized = True

# Allgemeiner Modus: Kontext aus Neo4j abrufen
def retrieve_graph_context(question):
    """
    Sucht relevante Inhalte im Neo4j-Graphen basierend auf der Frage.
    """
    try:
        results = st.session_state.vector_index.similarity_search(question)
        if results:
            return "\n\n".join([res.page_content.strip() for res in results])
        else:
            return ""
    except Exception as e:
        return f"Fehler bei der Suche im Graphen: {e}"

# Allgemeiner Modus: Frage basierend auf dem Graph beantworten
def answer_question_from_graph_with_llm(question):
    """
    Beantwortet eine Frage, indem der Kontext aus dem Neo4j-Graph verwendet wird.
    """
    try:
        graph_context = retrieve_graph_context(question)
        if graph_context.strip():
            prompt_template = ChatPromptTemplate.from_template("""
                Du bist ein Experte für das Mainzer Kartenlosbuch und darfst nur Informationen aus dem folgenden Kontext verwenden:
                
                {context}
                
                Wenn die Frage nicht im Kontext beantwortet werden kann, gib die folgende Antwort zurück:
                "Eingehende Anfragen müssen sich auf Informationen in:

                Däumer, Matthias, editor. Mainzer Kartenlosbuch: Eyn losz buch ausz der karten gemacht, gedruckt von Johann Schöffer, Mainz um 1510. S. Hirzel Verlag, 2021. Gedruckte deutsche Losbücher des 15. und 16. Jahrhunderts, edited by Marco Heiles, Björn Reich, and Matthias Standke, vol. 1.

                beziehen."

                Frage: {question}

                Antworte präzise und klar, ohne zusätzliche Informationen hinzuzufügen.
            """)
            chain = LLMChain(llm=st.session_state.llm, prompt=prompt_template)
            answer = chain.run(context=graph_context, question=question)
            if "Eingehende Anfragen müssen sich auf Informationen in:" in answer:
                return "Eingehende Anfragen müssen sich auf Informationen in:\n\nDäumer, Matthias, editor. Mainzer Kartenlosbuch: Eyn losz buch ausz der karten gemacht, gedruckt von Johann Schöffer, Mainz um 1510. S. Hirzel Verlag, 2021. Gedruckte deutsche Losbücher des 15. und 16. Jahrhunderts, edited by Marco Heiles, Björn Reich, and Matthias Standke, vol. 1.\n\nbeziehen."
            return answer.strip()
        else:
            return "Eingehende Anfragen müssen sich auf Informationen in:\n\nDäumer, Matthias, editor. Mainzer Kartenlosbuch: Eyn losz buch ausz der karten gemacht, gedruckt von Johann Schöffer, Mainz um 1510. S. Hirzel Verlag, 2021. Gedruckte deutsche Losbücher des 15. und 16. Jahrhunderts, edited by Marco Heiles, Björn Reich, und Matthias Standke, vol. 1.\n\nbeziehen."
    except Exception as e:
        return f"Fehler bei der Beantwortung der Frage: {e}"

# Losbuch-Modus: Zufälliges Los ziehen
def ziehe_random_karte():
    """
    Wählt zufällig ein Los aus der JSON-Datei.
    """
    try:
        los = random.choice(losbuch_data)
        weissagung_hochdeutsch = st.session_state.llm.predict(
            f"Übersetze die folgende Weissagung in Neuhochdeutsch:\n\n{los['weissagung']}"
        )
        return {
            "symbol": los["symbol"],
            "weissagung": los["weissagung"],
            "neuhochdeutsch_weissagung": weissagung_hochdeutsch.strip(),
            "image_path": los["image_path"]
        }
    except Exception as e:
        return {"error": str(e)}

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
    if st.button("Los ziehen"):
        los = ziehe_random_karte()
        if los and "error" not in los:
            if los.get("image_path"):
                st.image(los["image_path"], caption=los["symbol"], width=200)
            st.write(f"**Weissagung**:\n\n{los['weissagung']}")
            st.write(f"**Weissagung (Neuhochdeutsch)**:\n\n{los['neuhochdeutsch_weissagung']}")
        elif los and "error" in los:
            st.error(f"Fehler beim Ziehen des Loses: {los['error']}")
        else:
            st.error("Es konnte kein Los gezogen werden.")
