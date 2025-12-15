import streamlit as st
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated
from typing import operator

from langgraph.types import Send
from langgraph.graph import StateGraph, START, END

# PDF Generation
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Streamlit UI
st.set_page_config(page_title="AI Report Generator", layout="wide")

st.title("AI Report Generator")
st.header("Generate a complete AI-written technical report and export it as PDF")

# Environment Setup
load_dotenv()
os.environ["groq_api_key"] = os.getenv("groq_api_key")

# Model
model = ChatGroq(model="openai/gpt-oss-120b")

# Structured Output Model
class section(BaseModel):
    name: str = Field(description="It will contain topic in this blog")
    description: str = Field(description="it will contain description of the name/subtitle")

class sections(BaseModel):
    sec: list[section] = Field(description="here we will have complete section")

structured_model = model.with_structured_output(sections)

# State Definition
class State(TypedDict):
    topic: str
    section: list[section]
    complete_sections: Annotated[list[str], operator.add]
    report: str
    final: str

# Nodes
def get_sections(state: State):
    response = structured_model.invoke([
        SystemMessage(content=(
            "You are an expert technical blog writer. "
            "Your task is to generate a clean, well-structured blog outline using the provided schema. "
            "Each item in the 'sec' list represents one section of the blog. "
            "For every section, provide:\n"
            "1. 'name' → the section title\n"
            "2. 'description' → a clear explanation.\n\n"
            "Guidelines:\n"
            "- Begin with an introductory section.\n"
            "- Follow with 4–8 logical sections.\n"
            "- Keep descriptions short.\n"
            "- Maintain logical flow.\n"
            "- Output MUST follow schema."
        )),
        HumanMessage(content=f"Here is the topic name of my blog {state['topic']}")
    ])
    return {"section": response.sec}

def each_section_output(state: State):
    response = model.invoke([
        SystemMessage(content=(
            "You are a professional technical writer. Use Markdown Format. "
            "Expand each section into 150–300 words. "
            "Do NOT add new sections."
        )),
        HumanMessage(
            content=f"here is the name of the subtopic : {state['section'].name} "
                    f"and description is {state['section'].description}"
        )
    ])
    return {"complete_sections": [response.content]}

def assign_worker(state: State):
    return [Send("each_section_output", {"section": s}) for s in state["section"]]

def report(state: State):
    res = '\n\n----\n\n'.join(state["complete_sections"])
    return {"report": res}

def final(state: State):
    response = model.invoke([
        SystemMessage(content=(
            "You are an expert editor. Improve clarity and flow. "
            "Do NOT add or remove content."
        )),
        HumanMessage(content=f"Here is the full blog {state['report']}")
    ])
    return {"final": response.content}

# Graph Construction
graph = StateGraph(State)

graph.add_node("get_sections", get_sections)
graph.add_node("each_section_output", each_section_output)
graph.add_node("report", report)
graph.add_node("final", final)

graph.add_edge(START, "get_sections")
graph.add_conditional_edges("get_sections", assign_worker, ["each_section_output"])
graph.add_edge("each_section_output", "report")
graph.add_edge("report", "final")
graph.add_edge("final", END)

graph = graph.compile()

# ===============================
# PDF Generator
# ===============================
def generate_pdf(text, filename="AI_Report.pdf"):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    story = []

    for para in text.split("\n\n"):
        story.append(Paragraph(para.replace("\n", "<br/>"), styles["Normal"]))

    doc.build(story)
    return filename

# ===============================
# Streamlit Interaction
# ===============================
topic = st.text_input("Enter Blog / Report Topic", placeholder="e.g. AI: Innovation")

if st.button("Generate Report"):
    with st.spinner("Generating report... Please wait ⏳"):
        response = graph.invoke({"topic": topic})

        final_report = response["final"]

        st.subheader("Generated Report")
        st.markdown(final_report)

        pdf_file = generate_pdf(final_report)

        with open(pdf_file, "rb") as f:
            st.download_button(
                label="Download PDF",
                data=f,
                file_name="AI_Report.pdf",
                mime="application/pdf"
            )
