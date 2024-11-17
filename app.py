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

# %% Erweiterte Kontextsuche
def retrieve_graph_context(question):
    """
    Ruft kontextbezogene Daten aus dem Neo4j-Graphen ab.
    Nutzt sowohl Full-Text-Suche als auch Vektor-Suche.
    """
    try:
        query = """
        CALL db.index.fulltext.queryNodes('entity', $query)
        YIELD node, score
        RETURN node.id AS entity, score
        LIMIT 5
        """
        full_text_results = neo4j_driver.session().run(query, query=question).data()

        vector_results = vector_index.similarity_search(question)
        combined_results = set(
            [result["entity"] for result in full_text_results]
            + [res.page_content for res in vector_results]
        )
        return "\n".join(combined_results)
    except Exception as e:
        return f"Fehler beim Abrufen von Daten aus dem Graphen: {e}"

# %% Losbuch-Daten abrufen
def get_losbuch_details(symbol):
    """
    Ruft Details zu einem spezifischen Symbol aus dem Neo4j-Graphen ab.
    """
    try:
        query = """
        MATCH (los:Los {symbol: $symbol})
        RETURN los.symbol AS symbol,
               los.original_weissagung AS original,
               los.hochdeutsch_weissagung AS hochdeutsch,
               los.deutung AS deutung,
               los.image_path AS image_path
        LIMIT 1
        """
        result = neo4j_driver.session().run(query, symbol=symbol).data()
        return result[0] if result else None
    except Exception as e:
        return f"Fehler beim Abrufen der Losbuch-Daten: {e}"

# %% Fragen basierend auf dem Graphen beantworten
def answer_question_from_graph_with_llm(question):
    """
    Beantwortet Fragen basierend auf Daten aus dem Neo4j-Graphen und formuliert
    eine klare, verständliche Antwort mithilfe des LLM.
    """
    try:
        graph_context = retrieve_graph_context(question)

        if graph_context:
            prompt_template = ChatPromptTemplate.from_template("""
                Hier sind die Informationen aus dem Graphen:
                {context}

                Formuliere eine klare und prägnante Antwort auf die folgende Frage:
                {question}
            """)
            chain = LLMChain(llm=llm, prompt=prompt_template)
            return chain.run(context=graph_context, question=question)
        else:
            return "Es konnten keine relevanten Informationen im Neo4j-Graphen gefunden werden."
    except Exception as e:
        return f"Fehler bei der Beantwortung der Frage: {e}"

# %% UI-Anpassungen
st.title("🔮 Das Mainzer Kartenlosbuch")

# Auswahl der Modus
mode = st.selectbox("Wähle einen Modus", ["Allgemeine Fragen", "Losbuch spielen"])

if mode == "Allgemeine Fragen":
    st.subheader("Stelle eine allgemeine Frage")
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
        try:
            # Generiere ein zufälliges Symbol
            random_symbol = random.choice(["Symbol1", "Symbol2", "Symbol3"])  # Beispiel
            los = get_losbuch_details(random_symbol)
            if los:
                st.write(f"**Symbol**: {los['symbol']}")
                st.write(f"**Weissagung (Original)**: {los['original']}")
                st.write(f"**Weissagung (Hochdeutsch)**: {los['hochdeutsch']}")
                st.write(f"**Deutung**: {los['deutung']}")
                st.image(los['image_path'])
            else:
                st.write("Keine Daten für das Los gefunden.")
        except Exception as e:
            st.error(f"Fehler: {e}")

# Neo4j-Driver schließen
if neo4j_driver:
    neo4j_driver.close()
