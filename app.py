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

# Initialisierung von OpenAI LLM
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", openai_api_key=openai_api_key)

# Verbindung zu Neo4j herstellen
try:
    graph = Neo4jGraph(
        uri=neo4j_uri,
        username=neo4j_username,
        password=neo4j_password
    )
    print("Neo4j-Graph erfolgreich initialisiert.")
except Exception as e:
    raise ValueError(f"Fehler bei der Initialisierung des Neo4j-Graphen: {e}")

# Initialisierung des Vektor-Retrievers
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
with open("data_karten.json", "r", encoding="utf-8") as file:
    karten_data = json.load(file)["kartenlosbuch"]

# %% Funktionen zur Verarbeitung
def get_uebersetzung_und_deutung(weissagung_text):
    """LLM für Hochdeutsch-Übersetzung und Deutung der Weissagung."""
    prompt_uebersetzung = f"Übersetze diesen alten deutschen Text ins moderne Hochdeutsch: '{weissagung_text}'"
    prompt_deutung = f"Basierend auf dieser Weissagung, was könnte sie in 2 Sätzen bedeuten oder andeuten? '{weissagung_text}'"

    uebersetzung_response = llm.predict(prompt_uebersetzung)
    deutung_response = llm.predict(prompt_deutung)

    return uebersetzung_response.strip(), deutung_response.strip()

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

def answer_general_question(question):
    """Nutze den Neo4j-Graphen und den Vector-Index, um allgemeine Fragen zu beantworten."""
    try:
        unstructured_results = vector_index.similarity_search(question)
        context = "\n".join([res.page_content for res in unstructured_results])

        prompt = ChatPromptTemplate.from_template("""
            Hier ist der Kontext:
            {context}

            Frage: {question}
            Antwort:
        """)
        answer_chain = LLMChain(prompt=prompt, llm=llm)
        return answer_chain.run(context=context, question=question)
    except Exception as e:
        raise ValueError(f"Fehler beim Beantworten der Frage: {e}")

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
            st.write(f"Fehler beim Abrufen der Antwort: {e}")

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
            st.write(f"Fehler beim Ziehen des Loses: {e}")
