import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["groq_api_key"] = os.getenv("groq_api_key")

# Import your existing code
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated
from typing import operator
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Send
from langgraph.graph import StateGraph, START, END

# ================ Your existing code - NO CHANGES ================
### Model 
model = ChatGroq(model = "openai/gpt-oss-120b")

### Structured_Model
class section(BaseModel):
    name : str = Field(description= "It will contain topic in this blog")
    description : str = Field(description= "it will contain description of the name/subtitle")

class sections(BaseModel):
    sec : list[section] = Field(description="here we will have complete section")
    
structured_model = model.with_structured_output(sections)

### State
class State(TypedDict):
    topic : str
    section : list[section]
    complete_sections: Annotated[list[str], operator.add]
    report : str
    final : str

### Node
def get_sections(state:State):
    response = structured_model.invoke([SystemMessage(content=("You are an expert technical blog writer. ""Your task is to generate a clean, well-structured blog outline using the provided schema. ""Each item in the 'sec' list represents one section of the blog. ""For every section, provide: \n""1. 'name' → the section title\n""2. 'description' → a clear, concise explanation of what will be written in that section.\n\n""Guidelines:\n""- Begin with an introductory section.\n""- Follow with 4–8 logical sections covering the full topic.\n""- Keep descriptions short but meaningful (2–4 sentences).\n""- Maintain logical flow from basic to advanced.\n""- Do NOT add content outside the schema. Only return fields defined in the schema.\n""- Output MUST strictly follow the Pydantic 'sections' structure.\n""Wait for the user's query and generate sections accordingly.")),
                                        HumanMessage(content=f"Here is the topic name of my blog {state['topic']}")])
    print(response.sec)
    return {"section" : response.sec}

def each_section_output(state:State):
    response = model.invoke([SystemMessage(content=("You are a professional technical writer. Use Markdown Format to generate. Your job is to generate full blog content ""based strictly on the provided section names and descriptions.\n\n""For each section in the input:\n""- Use the 'name' as the section heading.\n""- Use the 'description' to guide the depth, theme, and direction of writing.\n""- Expand each section into a detailed, well-written explanation (150–300 words per section).\n""- Write in clear, simple, expert-level English.\n""- Do NOT rewrite the outline.\n""- Do NOT add new sections.\n""- Do NOT return JSON.\n""- Only return the final written blog content, properly formatted with headings.\n")),
                             HumanMessage(content=f"here is the name of the subtopic : {state['section'].name} and description is {state['section'].description}")])
    return {"complete_sections" : [response.content]}

def assign_worker(state: State):
    return [Send("each_section_output", {"section": s}) for s in state["section"]]

def report(state : State):
    respose = state["complete_sections"]
    res = '\n\n----\n\n'.join(respose)
    return {"report" : res}

def final(state : State):
    response = model.invoke([SystemMessage(content=("You are an expert editor and technical content specialist. Your task is to take the complete blog ""provided by the user and refine it for final publication.\n\n""Your responsibilities:\n""- Improve clarity, flow, and readability without changing the meaning.\n""- Fix grammar, punctuation, and sentence structure.\n""- Enhance transitions between ideas so the blog reads smoothly.\n""- Strengthen the tone to sound polished, professional, and engaging.\n""- Keep all technical details, facts, and structure exactly as provided.\n""- Do NOT add new sections or new concepts.\n""- Do NOT remove user-provided content unless it is repetitive or unclear.\n""- Do NOT alter the factual meaning.\n""- Return ONLY the improved blog text — no explanations, no bullet points, no commentary.\n\n""Your goal is to make the blog feel complete, publication-ready, and professional.")),
                             HumanMessage(content=f"Here is the full blog {state['report']}")])
    return {"final" : response.content}

### StateGraph
graph = StateGraph(State)
graph.add_node("get_sections", get_sections)
graph.add_node("each_section_output", each_section_output)
graph.add_node("report", report)
graph.add_node("final", final)
graph.add_edge(START, "get_sections")
graph.add_conditional_edges("get_sections", assign_worker, ["each_section_output"])
graph.add_edge("each_section_output", "report")
graph.add_edge("report","final")
graph.add_edge("final", END)
graph = graph.compile()
# ================ END of your existing code ================

# ================ Streamlit UI with DARK THEME ================
def main():
    # Page configuration
    st.set_page_config(
        page_title="AI Blog Generator",
        page_icon="✍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for DARK THEME
    st.markdown("""
    <style>
    /* Main app background */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(45deg, #00D4FF, #0095FF, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1.5rem;
        padding: 10px;
        letter-spacing: 0.5px;
    }
    
    .sub-header {
        font-size: 1.3rem;
        color: #B0B7C3;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 300;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #0095FF, #7C3AED);
        color: white !important;
        border: none;
        padding: 0.7rem 2.5rem;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
        font-size: 1.1rem;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 149, 255, 0.4);
        background: linear-gradient(45deg, #00D4FF, #0095FF);
    }
    
    .stButton>button:disabled {
        background: #2A2D34;
        color: #6B7280 !important;
    }
    
    /* Cards */
    .blog-card {
        background: linear-gradient(145deg, #1A1D23, #16181E);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        margin: 1.2rem 0;
        border: 1px solid #2A2D34;
        color: #FFFFFF;
    }
    
    .outline-card {
        background: linear-gradient(135deg, #1E3A8A 0%, #7C3AED 100%);
        color: white;
        border-radius: 16px;
        padding: 1.8rem;
        margin: 1.2rem 0;
        border: 1px solid #3B82F6;
    }
    
    .section-card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border-left: 5px solid #3B82F6;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        color: #E2E8F0;
    }
    
    /* Progress container */
    .progress-container {
        background: #1A1D23;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.2rem 0;
        border: 1px solid #2A2D34;
    }
    
    /* Text input */
    .stTextInput>div>div>input {
        background-color: #1A1D23;
        color: #FFFFFF;
        border: 2px solid #2A2D34;
        border-radius: 12px;
        padding: 0.8rem 1rem;
        font-size: 1rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1A1D23;
        color: #B0B7C3;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        border: 1px solid #2A2D34;
        border-bottom: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        font-weight: 600;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1A1D23;
        color: #FFFFFF;
        border: 1px solid #2A2D34;
        border-radius: 10px;
        font-weight: 600;
    }
    
    .streamlit-expanderContent {
        background-color: #16181E;
        color: #FFFFFF;
        border-radius: 0 0 10px 10px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1D23, #0F172A);
    }
    
    [data-testid="stSidebar"] .stButton>button {
        background: linear-gradient(45deg, #7C3AED, #3B82F6);
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #FFFFFF;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #FFFFFF;
    }
    
    .stMarkdown p {
        color: #D1D5DB;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background-color: #1E293B;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #FFFFFF;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #B0B7C3;
    }
    
    /* Divider */
    hr {
        border-color: #2A2D34;
        margin: 2rem 0;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #3B82F6 transparent transparent transparent;
    }
    
    /* Success/Error/Info messages */
    .stAlert {
        background-color: #1A1D23;
        border: 1px solid #2A2D34;
        border-radius: 12px;
        color: #FFFFFF;
    }
    
    /* Download button */
    .stDownloadButton>button {
        background: linear-gradient(45deg, #10B981, #059669);
        color: white !important;
        border: none;
        padding: 0.7rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        margin-top: 1rem;
    }
    
    .stDownloadButton>button:hover {
        background: linear-gradient(45deg, #34D399, #10B981);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Blog Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Generate professional, well-structured blog posts with AI assistance</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        st.markdown("---")
        
        # API Key check
        api_key = os.getenv("groq_api_key")
        if not api_key:
            st.error("⚠️ GROQ API Key not found!")
            st.info("Please set your GROQ_API_KEY in the .env file")
        else:
            st.success("✅ GROQ API Key loaded")
        
        st.markdown("---")
        st.markdown("## 📝 How it works")
        st.markdown("""
        1. **Enter your blog topic**
        2. **Click Generate Blog**
        3. **AI will:**
           - Create an outline
           - Write each section
           - Edit and polish
        
        This process uses LangGraph to orchestrate multiple AI steps for the best results.
        """)
        st.markdown("---")
        st.markdown("### 🚀 Features")
        st.markdown("""
        - 🤖 **AI-Powered Writing**
        - 📋 **Smart Outline Generation**
        - ✍️ **Section-by-Section Writing**
        - ✨ **Professional Editing**
        - 📥 **Download Ready**
        """)
        st.markdown("---")
        st.markdown("Made with ❤️ using Streamlit & LangGraph")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### ✨ Blog Topic")
        topic = st.text_input(
            "What would you like to write about?",
            placeholder="e.g., The Future of Artificial Intelligence, Benefits of Meditation, Python Programming Tips...",
            help="Enter a topic for your blog post. The more specific, the better!"
        )
        
        # Topic examples
        with st.expander("💡 Topic Ideas", expanded=False):
            st.markdown("""
            - **Technology:** How to Get Started with Machine Learning
            - **Health:** The Impact of AI on Modern Healthcare
            - **Lifestyle:** Sustainable Living in Urban Areas
            - **Finance:** Blockchain Technology Explained
            - **Personal Development:** Mindfulness Techniques for Daily Life
            """)
        
        # Generate button
        generate_button = st.button(
            "🚀 Generate Blog Post",
            disabled=not topic,
            help="Click to start generating your blog post" if topic else "Please enter a topic first"
        )
    
    with col2:
        st.markdown("### 📊 Preview")
        if topic:
            st.markdown(f"""
            <div class="blog-card">
                <h4 style="color: #00D4FF; margin-bottom: 1rem;">Topic Preview</h4>
                <h3 style="color: #FFFFFF; margin-bottom: 1rem;">"{topic}"</h3>
                <p style="color: #B0B7C3; line-height: 1.6;">
                This topic will be expanded into a full blog post with multiple sections, 
                each professionally written and edited by AI.
                </p>
                <div style="display: flex; gap: 10px; margin-top: 1rem;">
                    <span style="background: #3B82F6; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">AI-Powered</span>
                    <span style="background: #7C3AED; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">Multi-Section</span>
                    <span style="background: #10B981; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">Professional</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="blog-card">
                <h4 style="color: #00D4FF; margin-bottom: 1rem;">👈 Enter a Topic</h4>
                <p style="color: #B0B7C3; line-height: 1.6;">
                Your blog preview will appear here once you enter a topic in the left column.
                <br><br>
                <strong style="color: #FFFFFF;">Try these ideas:</strong><br>
                • Artificial Intelligence in Education<br>
                • Climate Change Solutions<br>
                • Digital Marketing Strategies<br>
                • Remote Work Best Practices
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Main generation area
    if generate_button and topic:
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create tabs for different outputs
        tab1, tab2, tab3 = st.tabs(["📋 Blog Outline", "✍️ Generated Blog", "✨ Final Polished Version"])
        
        # Step 1: Generate outline
        with st.spinner("Creating blog outline..."):
            status_text.text("Step 1/4: Creating blog outline...")
            progress_bar.progress(25)
            
            # Run the graph
            result = graph.invoke({"topic": topic})
            
            # Display outline in first tab
            with tab1:
                st.markdown("### 📋 Blog Outline")
                st.markdown(f"**Topic:** {topic}")
                st.markdown("---")
                
                if 'section' in result and result['section']:
                    for i, sec in enumerate(result['section'], 1):
                        with st.expander(f"**Section {i}: {sec.name}**", expanded=i==1):
                            st.markdown(f"""
                            <div class="section-card">
                                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                    <span style="background: #3B82F6; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; margin-right: 10px;">
                                        Section {i}
                                    </span>
                                    <span style="color: #60A5FA; font-size: 0.9rem;">
                                        {len(sec.description.split())} words planned
                                    </span>
                                </div>
                                <p style="color: #E2E8F0; line-height: 1.6; margin: 0;">
                                <strong>Description:</strong><br>
                                {sec.description}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No outline generated yet")
        
        # Step 2: Writing sections
        with st.spinner("Writing blog sections..."):
            status_text.text("Step 2/4: Writing individual sections...")
            progress_bar.progress(50)
            
            # Display draft in second tab
            with tab2:
                st.markdown("### ✍️ Draft Version")
                if 'report' in result and result['report']:
                    st.markdown("""
                    <div class="blog-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                            <h4 style="color: #00D4FF; margin: 0;">Draft Version</h4>
                            <span style="background: #F59E0B; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">
                                AI-Generated Draft
                            </span>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(result['report'])
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("Draft not available yet")
        
        # Step 3: Final editing
        with st.spinner("Polishing final version..."):
            status_text.text("Step 3/4: Editing and polishing...")
            progress_bar.progress(75)
            
            # Display final version in third tab
            with tab3:
                st.markdown("### ✨ Final Polished Blog")
                if 'final' in result and result['final']:
                    st.markdown("""
                    <div class="blog-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                            <h4 style="color: #10B981; margin: 0;">Final Version</h4>
                            <span style="background: #10B981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">
                                Publication Ready
                            </span>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(result['final'])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Blog (Markdown)",
                        data=result['final'],
                        file_name=f"{topic.replace(' ', '_').lower()}_blog.md",
                        mime="text/markdown",
                    )
                else:
                    st.info("Final version not available yet")
        
        # Completion
        status_text.text("✅ Blog generation complete!")
        progress_bar.progress(100)
        
        # Success message
        st.success("🎉 Your blog has been generated successfully!")
        
        # Stats in a nice card
        st.markdown("""
        <div class="blog-card">
            <h4 style="color: #00D4FF; text-align: center; margin-bottom: 1.5rem;">📊 Generation Statistics</h4>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sections_count = len(result.get('section', []))
            st.metric("Sections", sections_count, delta=f"{sections_count} sections")
        with col2:
            word_count = len(result.get('final', '').split())
            st.metric("Words", word_count, delta=f"{word_count} words")
        with col3:
            st.metric("Status", "Complete", delta="Ready to use")
        
        st.markdown("</div></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()