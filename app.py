# %% Imports
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
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

# Funktion: Kontext aus dem Graphen abrufen
def retrieve_graph_context(question):
    """
    Sucht nach relevanten Inhalten im Neo4j-Graphen basierend auf der Frage.
    """
    try:
        results = vector_index.similarity_search(question)
        if results:
            contexts = [res.page_content.strip() for res in results]
            return "\n\n".join(contexts)
        else:
            return ""
    except Exception as e:
        return f"Fehler bei der Suche im Graphen: {e}"

# Funktion: Antwort generieren basierend auf Graph-Daten
def answer_question_strictly_from_graph(question):
    """
    Beantwortet Fragen ausschließlich basierend auf Graph-Daten.
    Keine Antwort wird generiert, wenn keine relevanten Daten gefunden werden.
    """
    try:
        graph_context = retrieve_graph_context(question)

        if graph_context.strip():
            # Antwort basierend auf Graph-Daten generieren
            prompt_template = ChatPromptTemplate.from_template("""
                Nutze ausschließlich die folgenden Informationen, um eine Antwort zu generieren:
                {context}

                Frage: {question}

                Antworte präzise und klar.
            """)
            chain = LLMChain(llm=llm, prompt=prompt_template)
            return chain.run(context=graph_context, question=question)
        else:
            # Keine Antwort, wenn keine relevanten Daten gefunden werden
            return "Es konnten keine relevanten Informationen im Neo4j-Graphen gefunden werden. Bitte stelle eine spezifische Frage, die sich auf die verfügbaren Daten bezieht."
    except Exception as e:
        return f"Fehler bei der Beantwortung der Frage: {e}"

# Anpassung der Streamlit-UI
st.title("🔮 Das Mainzer Kartenlosbuch")

st.subheader("Stelle eine Frage basierend auf den verfügbaren Graph-Daten")
question = st.text_input("Frage eingeben")

if st.button("Frage stellen"):
    try:
        answer = answer_question_strictly_from_graph(question)
        st.write(f"**Antwort**: {answer}")
    except Exception as e:
        st.error(f"Fehler: {e}")

# Neo4j-Driver schließen
if neo4j_driver:
    neo4j_driver.close()
