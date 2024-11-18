# %% Imports
import streamlit as st
import random
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings

# OpenAI- und Neo4j-Details aus Streamlit Secrets laden
openai_api_key = st.secrets["OPENAI_API_KEY"]
neo4j_uri = st.secrets["NEO4J_URI"]
neo4j_username = st.secrets["NEO4J_USERNAME"]
neo4j_password = st.secrets["NEO4J_PASSWORD"]

# Verbindung zu Neo4j herstellen
def connect_to_neo4j(uri, username, password):
    try:
        graph = Neo4jGraph(uri=neo4j_uri, auth=(neo4j_username, neo4j_password))
        print("Verbindung zu Neo4j erfolgreich hergestellt.")
        return graph
    except Exception as e:
        raise ValueError(f"Fehler bei der Verbindung mit Neo4j: {e}")

graph = connect_to_neo4j(uri=neo4j_uri, neo4j_username, neo4j_password)

# OpenAI-LLM initialisieren
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", openai_api_key=openai_api_key)

# Hybrid Retrieval Setup
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

# Kontext aus dem Graphen abrufen
def retrieve_graph_context(question):
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
    try:
        graph_context = retrieve_graph_context(question)
        if graph_context.strip():
            prompt_template = ChatPromptTemplate.from_template("""
                Nutze ausschließlich die folgenden Informationen, um eine Antwort zu generieren:
                {context}

                Frage: {question}

                Antworte präzise und klar.
            """)
            chain = LLMChain(llm=llm, prompt=prompt_template)
            return chain.run(context=graph_context, question=question)
        else:
            return "Es konnten keine relevanten Informationen im Neo4j-Graphen gefunden werden."
    except Exception as e:
        return f"Fehler bei der Beantwortung der Frage: {e}"

# Funktion für "Losbuch spielen"
def ziehe_random_karte():
    """
    Wählt zufällig ein Los aus den gespeicherten Daten im Neo4j-Graphen.
    """
    try:
        query = """
        MATCH (l:Los)
        RETURN l.symbol AS symbol, l.original_weissagung AS original_weissagung,
               l.hochdeutsch_weissagung AS hochdeutsch_weissagung,
               l.deutung AS deutung, l.image_path AS image_path
        ORDER BY rand()
        LIMIT 1
        """
        result = graph.query(query)
        if result:
            los = result[0]  # Es wird ein zufälliges Los zurückgegeben
            return {
                "symbol": los["symbol"],
                "original_weissagung": los["original_weissagung"],
                "hochdeutsch_weissagung": los["hochdeutsch_weissagung"],
                "deutung": los["deutung"],
                "image_path": los["image_path"]
            }
        else:
            return None
    except Exception as e:
        return f"Fehler beim Ziehen eines Loses: {e}"

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
        if los:
            st.write(f"**Symbol**: {los['symbol']}")
            st.write(f"**Weissagung (Original)**: {los['original_weissagung']}")
            st.write(f"**Weissagung (Hochdeutsch)**: {los['hochdeutsch_weissagung']}")
            st.write(f"**Deutung**: {los['deutung']}")
            if los["image_path"]:
                st.image(los["image_path"])
        else:
            st.error("Es konnte kein Los gezogen werden.")

