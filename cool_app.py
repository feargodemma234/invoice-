import streamlit as st

st.set_page_config(page_title="Future UI", layout="wide", page_icon="✨")

# FUTURISTIC THEME
st.markdown("""
<style>
   .stApp {
        background: linear-gradient(135deg, #0A0A1A 0%, #1A0A2E 100%);
        color: #E0E0FF;
    }
    
   .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 240, 255, 0.3);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.2);
        text-align: center;
    }
    
   .glow-text {
        background: linear-gradient(90deg, #00F0FF 0%, #A855F7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 48px;
        font-weight: 800;
    }
    
   .stButton>button {
        background: linear-gradient(90deg, #A855F7 0%, #00F0FF 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 15px 40px;
        font-size: 18px;
        font-weight: 700;
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.5);
        width: 100%;
    }
   .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.8);
    }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown('<p class="glow-text">NEXUS INTERFACE</p>', unsafe_allow_html=True)
st.caption("Welcome to the future")

col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # SHOW AN IMAGE HERE
    st.image("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop", 
             caption="Futuristic City 2042", 
             use_container_width=True)
    
    st.markdown("<h3>System Online</h3>", unsafe_allow_html=True)
    st.write("All systems are operational. Neural link active.")
    
    if st.button("ACTIVATE PROTOCOL"):
        st.success("Protocol Activated ✓")
        st.balloons()
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.centered = st.columns(3)[1]
with st.centered:
    st.write("Built with Streamlit | 2026")