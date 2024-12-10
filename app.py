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

# Initialisierung aller Ressourcen
def initialize_resources():
    try:
        # Neo4j-Verbindung herstellen
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))
        driver.verify_connectivity()

        # LLM initialisieren
        llm = ChatOpenAI(temperature=0, model_name="gpt-4", openai_api_key=openai_api_key)

        # Neo4j Vector Index initialisieren
        vector_index = Neo4jVector.from_existing_graph(
            embedding=OpenAIEmbeddings(openai_api_key=openai_api_key),
            search_type="hybrid",
            node_label="Document",
            text_node_properties=["text"],
            embedding_node_property="embedding"
        )

        st.success("Ressourcen erfolgreich initialisiert.")
        return driver, llm, vector_index
    except Exception as e:
        st.error(f"Fehler bei der Initialisierung der Ressourcen: {e}")
        st.stop()

# Ressourcen initialisieren und in Session-State speichern
if "resources_initialized" not in st.session_state:
    with st.spinner("Initialisiere Ressourcen, bitte warten..."):
        neo4j_driver, llm, vector_index = initialize_resources()
        st.session_state.neo4j_driver = neo4j_driver
        st.session_state.llm = llm
        st.session_state.vector_index = vector_index
        st.session_state.resources_initialized = True

# Unstrukturierte Daten abrufen
def retrieve_unstructured_context(question):
    try:
        results = st.session_state.vector_index.similarity_search(question)
        return "\n\n".join([res.page_content.strip() for res in results]) if results else ""
    except Exception as e:
        return f"Fehler bei der Suche in unstrukturierten Daten: {e}"

# Strukturierte Daten abrufen
def retrieve_structured_context(question):
    try:
        llm = st.session_state.llm
        # Entitäten aus der Frage extrahieren
        entity_extraction_prompt = ChatPromptTemplate.from_template("""
            Extrahiere alle relevanten Entitäten (Personen, Orte, Organisationen) aus der Frage:
            {question}
        """)
        entity_chain = LLMChain(llm=llm, prompt=entity_extraction_prompt)
        entities = entity_chain.run(question=question)

        # Abfrage in Neo4j für die extrahierten Entitäten
        graph_context = ""
        for entity in entities.split(","):
            query = f"""
            CALL db.index.fulltext.queryNodes('entity', '{entity.strip()}') YIELD node
            MATCH (node)-[r]->(neighbor)
            RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
            LIMIT 50
            """
            with st.session_state.neo4j_driver.session() as session:
                results = session.run(query)
                for record in results:
                    graph_context += record["output"] + "\n"
        return graph_context.strip()
    except Exception as e:
        return f"Fehler bei der Suche in strukturierten Daten: {e}"

# Hybrid-Kontext erstellen
def hybrid_retrieve_context(question):
    structured_context = retrieve_structured_context(question)
    unstructured_context = retrieve_unstructured_context(question)
    return f"""
    Strukturierte Daten:
    {structured_context}

    Unstrukturierte Daten:
    {unstructured_context}
    """.strip()

# Frage beantworten
def answer_question_with_hybrid_context(question):
    """
    Beantwortet eine Frage basierend auf einem komprimierten hybriden Kontext.
    """
    try:
        hybrid_context = hybrid_retrieve_context(question, max_results=3)  # Max 3 relevante Ergebnisse
        if hybrid_context.strip():
            prompt_template = ChatPromptTemplate.from_template("""
                Beantworte die folgende Frage basierend auf dem gegebenen Kontext (maximal 4000 Zeichen):
                
                {context}

                Frage: {question}

                Wenn die Frage nicht beantwortet werden kann, antworte:
                "Die Antwort kann nicht aus dem gegebenen Kontext abgeleitet werden."
            """)
            chain = LLMChain(llm=st.session_state.llm, prompt=prompt_template)
            return chain.run(context=hybrid_context[:4000], question=question).strip()  # Kontext begrenzen
        else:
            return "Keine ausreichenden Daten im Kontext, um die Frage zu beantworten."
    except Exception as e:
        return f"Fehler bei der Beantwortung der Frage: {e}"

# Los ziehen
def ziehe_random_karte():
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

# Streamlit UI
st.title("🔮 Das Mainzer Kartenlosbuch")

# Modus auswählen
mode = st.selectbox("Wähle einen Modus", ["Allgemeine Fragen", "Losbuch spielen"])

if mode == "Allgemeine Fragen":
    st.subheader("Stelle eine Frage zu den Weissagungen:")
    question = st.text_input("Frage eingeben")

    if st.button("Frage stellen"):
        try:
            answer = answer_question_with_hybrid_context(question)
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
