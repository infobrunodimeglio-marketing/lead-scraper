import streamlit as st
import pandas as pd
from scraper import LeadScraper
import time

# Page setup
st.set_page_config(
    page_title="Lead Scraper & Problem Identifier",
    page_icon="🎯",
    layout="wide"
)

# Title and description
st.title("🎯 Lead Scraper: Trova Clienti con Problemi Specifici")
st.markdown("""
Questa applicazione cerca attività che hanno discusso di problemi specifici sul web (social, forum, siti) negli ultimi 30 giorni.
""")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Impostazioni")
    max_results = st.slider("Numero Massimo di Risultati", min_value=10, max_value=100, value=20, step=10)
    time_limit = st.selectbox("Intervallo Temporale", ["m (Ultimo Mese)", "w (Ultima Settimana)", "d (Ultimo Giorno)"], index=0)
    time_code = time_limit.split()[0] # 'm', 'w', or 'd'

# Main input form
with st.form("search_form"):
    col1, col2 = st.columns(2)
    with col1:
        activity_input = st.text_input("Tipo di Attività (Es. Ristorante, Palestra, Hotel)", placeholder="Ristorante")
    with col2:
        problem_input = st.text_input("Problematica Manifestata (Es. recensioni negative, tasse, personale)", placeholder="Carenza personale")
    
    sites_input = st.text_input("Siti Specifici (Opzionale, separati da virgola)", placeholder="facebook.com, linkedin.com, twitter.com")
    
    submitted = st.form_submit_button("🔍 Cerca Leads")

if submitted:
    if not activity_input or not problem_input:
        st.error("Per favore inserisci sia il Tipo di Attività che la Problematica.")
    else:
        st.info(f"Ricerca in corso per: **{activity_input}** con problema **{problem_input}**...")
        
        # Initialize scraper
        scraper = LeadScraper()
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Perform search (This wraps the process_leads which handles the logic)
            # We might want to pass the time_limit to process_leads too in a real scenario, defaults to 'm' there currently.
            # Let's update scraper.search_leads call inside logic if needed, but 'm' is hardcoded in process_leads default?
            # Actually process_leads in scraper.py didn't take days arg, I should fix that or handle it.
            # I'll update the scraper code later to be cleaner, but for now I'll assuming search_leads handles it.
            # Wait, I wrote `process_leads` in scraper.py to take max_results but not `days`.
            # I should patch scraper.py to accept `days`.
            
            # Temporary fix: we will instantiate and call search_leads directly or allow passing days to process_leads.
            # Let's just assume I'll fix scraper.py in next step or now.
            # I'll re-write scraper.py properly in a moment if needed. 
            # For now let's pretend process_leads accepts days or I'll pass it to search method manually.
            
            # Check scraper.py content just written: 
            # def process_leads(self, activity, problem, sites=None, days='m', max_results=20):
            
            df = scraper.process_leads(activity_input, problem_input, sites_input, days=time_code, max_results=max_results)
            
            progress_bar.progress(100)
            
            if not df.empty:
                st.success(f"Trovati {len(df)} risultati!")
                
                # Show data
                st.dataframe(df, use_container_width=True)
                
                # Excel export
                file_name = f"leads_{activity_input}_{problem_input}.xlsx"
                # Use a buffer or temp file? Pandas to_excel works better with file path usually, 
                # but streamlit download button needs bytes.
                
                # Convert to Excel in memory
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Leads')
                
                st.download_button(
                    label="📥 Scarica Excel",
                    data=buffer.getvalue(),
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("Nessun risultato trovato. Prova a cambiare i termini di ricerca.")
                
        except Exception as e:
            st.error(f"Si è verificato un errore: {e}")

st.markdown("---")
st.caption("Nota: Questa app utilizza dati pubblici. Rispetta la privacy e le normative locali durante l'utilizzo dei contatti.")
