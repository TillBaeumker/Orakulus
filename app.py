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


# %% Funktionen zur Verarbeitung
def answer_general_question(question):
    """
    Beantwortet allgemeine Fragen. Fügt einen Disclaimer hinzu, falls die Informationen
    nicht aus dem Buch 'Mainzer Kartenlosbuch' stammen.
    """
    try:
        # Unstrukturierte Suche im Vektor-Index
        unstructured_results = vector_index.similarity_search(question)

        # Wenn es Ergebnisse gibt, Kontext aus diesen generieren
        if unstructured_results:
            context = "\n".join([res.page_content for res in unstructured_results])
            prompt = ChatPromptTemplate.from_template("""
                Hier ist der Kontext:
                {context}

                Frage: {question}
                Antwort:
            """)
            answer_chain = LLMChain(prompt=prompt, llm=llm)
            return answer_chain.run(context=context, question=question)
        else:
            # Generiere Antwort auf die Frage
            response = llm(f"Beantworte die folgende Frage: '{question}'")
            disclaimer = (
                "Hinweis: Diese Antwort basiert nicht auf dem Buch "
                "'Mainzer Kartenlosbuch: Eyn losz buch ausz der karten gemacht, "
                "gedruckt von Johann Schöffer, Mainz um 1510. Herausgegeben von Matthias Däumer, "
                "S. Hirzel Verlag, 2021. Gedruckte deutsche Losbücher des 15. und 16. Jahrhunderts'."
            )
            return f"{disclaimer}\n\nAntwort: {response}"
    except Exception as e:
        return f"Fehler bei der Beantwortung der Frage: {e}"



# %% Streamlit UI
st.title("🔮 Das Mainzer Kartenlosbuch")

# Auswahl der Modus
mode = st.selectbox("Wähle einen Modus", ["Allgemeine Fragen", "Losbuch spielen"])

if mode == "Allgemeine Fragen":
    st.subheader("Stelle eine allgemeine Frage")
    question = st.text_input("Frage eingeben")

    if st.button("Frage stellen"):
        try:
            answer = answer_general_question(question)
            st.write(f"**Antwort**: {answer}")
        except Exception as e:
            st.error(f"Fehler: {e}")

elif mode == "Losbuch spielen":
    st.subheader("Ziehe ein Los! (Diese Funktion ist derzeit deaktiviert)")
    st.write("Weitere Informationen werden in einer zukünftigen Version hinzugefügt.")

# Neo4j-Driver schließen
if neo4j_driver:
    neo4j_driver.close()
