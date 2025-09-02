import streamlit as st
import pandas as pd
import json
import yaml
import os
import logic.regex_detection as regex_detection
import logic.llm_detection as llm_detection
import logic.acoustic_analysis as acoustic_analysis
import logic.acoustic_visualization as acoustic_visualization

def load_file_to_df(uploaded_file):
    if uploaded_file is None:
        return pd.DataFrame()
    filename = uploaded_file.name
    try:
        if filename.endswith('.json'):
            data = json.load(uploaded_file)
        elif filename.endswith('.yaml') or filename.endswith('.yml'):
            data = yaml.safe_load(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a .json or .yaml file.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to parse file: {e}")
        return pd.DataFrame()
   
    if isinstance(data, dict) and 'utterances' in data:
        utterances = data['utterances']
    elif isinstance(data, list):
        utterances = data
    else:
        st.error("File structure not recognized. Must be a list or dict with 'utterances' key.")
        return pd.DataFrame()
    call_id = os.path.splitext(filename)[0]
    rows = []
    for utt in utterances:
        rows.append({
            'call_id': call_id,
            'speaker': utt.get('speaker'),
            'text': utt.get('text'),
            'stime': utt.get('stime'),
            'etime': utt.get('etime')
        })
    return pd.DataFrame(rows)

def file_uploader_ui():
    st.set_page_config(page_title="Prodigal Conversation Analytics", layout="centered")
    st.markdown("""
        <h1 style='text-align: center; color: #4F8BF9;'>Prodigal Debt Conversation Analytics</h1>
        <hr>
    """, unsafe_allow_html=True)

    st.sidebar.title("About")
    st.sidebar.info("""
    **Prodigal Debt Conversation Analytics Tool**
    Upload a call transcript file and see the magic!!!
    """)

    # Initialize session state
    if 'detection_results' not in st.session_state:
        st.session_state.detection_results = None
    if 'current_file_name' not in st.session_state:
        st.session_state.current_file_name = None

    uploaded_file = st.file_uploader("Choose a YAML file", type=["json", "yaml", "yml"])


    if uploaded_file is None:

        if st.session_state.detection_results is not None or st.session_state.current_file_name is not None:
            st.session_state.detection_results = None
            st.session_state.current_file_name = None
            st.rerun()
    else:

        if st.session_state.current_file_name != uploaded_file.name:
            st.session_state.detection_results = None
            st.session_state.current_file_name = uploaded_file.name

    detection_approach = st.selectbox(
        "Entity Detection Approach",
        ["Regex", "LLM"]
    )

    if uploaded_file:
        df = load_file_to_df(uploaded_file)
        if not df.empty:
            st.success(f"File '{uploaded_file.name}' loaded successfully!")
            st.dataframe(df, use_container_width=True)
            utterances = df.to_dict(orient="records")
            

            st.markdown("---")
            st.markdown("### Acoustic Analysis")
            

            overtalk_pct, silence_pct = acoustic_analysis.get_acoustic_metrics(utterances)
            

            col1, col2 = st.columns(2)
            with col1:
                st.metric("🔴 Overtalk", f"{overtalk_pct:.1f}%", help="Percentage of time with simultaneous speaking")
            with col2:
                st.metric("⚪ Silence", f"{silence_pct:.1f}%", help="Percentage of time with awkward pauses/gaps")
            

            fig = acoustic_visualization.create_acoustic_pie_chart(overtalk_pct, silence_pct)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            

            insights = acoustic_visualization.get_acoustic_insights(overtalk_pct, silence_pct)
            st.info(insights)
            
            st.markdown("---")
            

            run_detection = st.button("Run Detection", type="primary")
            

            if run_detection:
                if detection_approach == "Regex":
                    prof = regex_detection.detect_profanity(utterances)
                    priv = regex_detection.detect_privacy_violations(utterances)
                    agent_prof_ids = regex_detection.detect_agent_profanity_call_ids(utterances)
                    borrower_prof_ids = regex_detection.detect_borrower_profanity_call_ids(utterances)
                    agent_privacy_ids = regex_detection.detect_agent_privacy_violation_call_ids(utterances)
                    
                    st.session_state.detection_results = {
                        'approach': detection_approach,
                        'filename': uploaded_file.name,
                        'profanity': prof,
                        'privacy': priv,
                        'agent_prof_ids': agent_prof_ids,
                        'borrower_prof_ids': borrower_prof_ids,
                        'agent_privacy_ids': agent_privacy_ids
                    }
                else: 
                    with st.spinner('Analyzing...'):
                        try:
                            profanity_results = llm_detection.detect_profanity_llm(utterances)
                            privacy_results = llm_detection.detect_privacy_violations_llm(utterances)
                            
                            st.session_state.detection_results = {
                                'approach': detection_approach,
                                'filename': uploaded_file.name,
                                'profanity': profanity_results['profanity_utterances'],
                                'privacy': privacy_results['privacy_violations'],
                                'agent_prof_ids': profanity_results['agent_profanity_call_ids'],
                                'borrower_prof_ids': profanity_results['borrower_profanity_call_ids'],
                                'agent_privacy_ids': privacy_results['agent_privacy_violation_call_ids']
                            }
                        except Exception as e:
                            st.error(f"LLM detection failed: {str(e)}")
                            st.session_state.detection_results = {
                                'approach': detection_approach,
                                'filename': uploaded_file.name,
                                'profanity': [],
                                'privacy': [],
                                'agent_prof_ids': [],
                                'borrower_prof_ids': [],
                                'agent_privacy_ids': []
                            }
            

            if (st.session_state.detection_results is not None and 
                st.session_state.current_file_name == uploaded_file.name):
                
                st.markdown("---")
                st.markdown(f"### 📊 Analysis Results for: **{uploaded_file.name}**")
                st.caption(f"Detection approach: {st.session_state.detection_results['approach']}")
                
                results = st.session_state.detection_results
                

                st.subheader(":red[Profanity Detected]")
                st.markdown(f"<b>Agent Profanity Detected: {'Yes' if results['agent_prof_ids'] else 'No'}</b>", unsafe_allow_html=True)
                st.markdown(f"<b>Customer Profanity Detected: {'Yes' if results['borrower_prof_ids'] else 'No'}</b>", unsafe_allow_html=True)
                

                st.subheader(":orange[Privacy Violations Detected]")
                st.markdown(f"<b>Agent Privacy Violations Count: {len(results['privacy'])}</b>", unsafe_allow_html=True)
                
                if results['privacy']:
                    st.markdown("<b>Privacy Violations Detected: Yes</b>", unsafe_allow_html=True)
                    st.dataframe(results['privacy'], use_container_width=True)
                    st.info(f"{len(results['privacy'])} utterance(s) flagged for privacy violations.")
                else:
                    st.markdown("<b>Privacy Violations Detected: No</b>", unsafe_allow_html=True)
        else:
            st.warning("No data to display. Please check your file format.")
    else:
        st.markdown("""
        <div style='text-align: center; margin-top: 40px;'>
            <p style='color: #aaa; font-size: 1.1em;'>No file uploaded yet.<br>Use the uploader above to get started.</p>
        </div>
        """, unsafe_allow_html=True)

file_uploader_ui()