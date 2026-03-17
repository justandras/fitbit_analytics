"""
================================================================================
Tableau de bord sante Fitbit - Version detaillee continue
================================================================================
Visualisation complete des donnees Fitbit avec graphiques continus detailles.
Affiche tous les points de donnees (seconde par seconde) sur un seul graphique.
"""

import streamlit as st
import pandas as pd
import json
import os
import glob
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# Convert plotly figures to PNG bytes for PDF embedding
def fig_to_png_base64(fig, width=700, height=350):
    """Convert a plotly figure to base64 encoded PNG"""
    try:
        img_bytes = pio.to_image(fig, format="png", width=width, height=height, scale=2)
        return base64.b64encode(img_bytes).decode('utf-8')
    except Exception as e:
        st.warning(f"Erreur conversion graphique: {str(e)}")
        return None

# Generate PDF from HTML using weasyprint
def generate_pdf_from_html(html_content):
    """Convert HTML to PDF using weasyprint (requires packages.txt for system deps)"""
    try:
        from weasyprint import HTML
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            HTML(string=html_content).write_pdf(tmp.name)
            with open(tmp.name, 'rb') as f:
                pdf_bytes = f.read()
            os.unlink(tmp.name)
            return pdf_bytes
    except Exception as e:
        st.error(f"Erreur generation PDF: {str(e)}")
        return None

st.set_page_config(
    page_title="Fitbit Health Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

import streamlit.components.v1 as components
import base64
import io

def _load_translations(lang: str) -> dict:
    lang = (lang or "en").lower()
    if lang not in {"en", "fr"}:
        lang = "en"
    i18n_path = Path(__file__).parent / "i18n" / f"{lang}.json"
    try:
        return json.loads(i18n_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _t(translations: dict, key: str, **kwargs) -> str:
    text = translations.get(key, key)
    try:
        return text.format(**kwargs)
    except Exception:
        return text

st.markdown("""
<style>
    /* Base styles */
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        margin: 25px 0 15px 0;
        font-weight: bold;
        font-size: 1.3em;
    }
    
    .print-header {
        text-align: center;
        border-bottom: 3px solid #667eea;
        padding-bottom: 15px;
        margin-bottom: 25px;
    }
    
    .alert-critical {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid #c0392b;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 18px;
        border-radius: 12px;
        margin: 12px 0;
        border-left: 5px solid #e84393;
    }
    
    .alert-caution {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #333;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 5px solid #f39c12;
    }
    
    .alert-good {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #2c3e50;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 5px solid #27ae60;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #2c3e50;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 5px solid #3498db;
    }
    
    .comment-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
        font-size: 0.95em;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# Inject comprehensive print styles using a different method
st.markdown("""
<style id="print-styles">
@media print {
    /* Page setup */
    @page { 
        size: A4 portrait; 
        margin: 15mm; 
    }
    
    /* Reset everything to visible */
    * {
        print-color-adjust: exact !important; 
        -webkit-print-color-adjust: exact !important;
        -webkit-print-fill-color: inherit !important;
    }
    
    /* Force document to be printable */
    html {
        height: auto !important;
        overflow: visible !important;
    }
    
    body {
        height: auto !important;
        overflow: visible !important;
        background: white !important;
        position: static !important;
    }
    
    /* Streamlit app container */
    .stApp {
        height: auto !important;
        overflow: visible !important;
        position: static !important;
    }
    
    /* Main content area */
    .main {
        height: auto !important;
        overflow: visible !important;
        max-width: 100% !important;
        position: static !important;
    }
    
    /* Block container */
    .block-container {
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: visible !important;
        height: auto !important;
    }
    
    /* Hide UI elements */
    header,
    .stApp > header,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stStatusWidget"],
    [data-testid="stSidebar"],
    .stDeployButton,
    .stActionButton,
    .stSpinner,
    #print-btn-container,
    div[style*="position: fixed"],
    iframe {
        display: none !important;
    }
    
    /* Ensure vertical blocks are visible */
    [data-testid="stVerticalBlock"] {
        display: block !important;
        overflow: visible !important;
        height: auto !important;
    }
    
    [data-testid="stVerticalBlock"] > div {
        display: block !important;
        overflow: visible !important;
    }
    
    /* Element containers */
    .element-container {
        display: block !important;
        overflow: visible !important;
        page-break-inside: avoid !important;
    }
    
    /* Markdown content */
    .stMarkdown {
        display: block !important;
        overflow: visible !important;
    }
    
    /* Plotly charts - CRITICAL */
    .stPlotlyChart {
        display: block !important;
        overflow: visible !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }
    
    .js-plotly-plot,
    .plotly-graph-div,
    .user-select-none,
    svg {
        display: block !important;
        overflow: visible !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        display: block !important;
        break-inside: avoid !important;
        page-break-inside: avoid !important;
    }
    
    /* Columns */
    [data-testid="column"] {
        display: block !important;
        overflow: visible !important;
        page-break-inside: avoid !important;
    }
    
    /* Page breaks */
    .page-break {
        page-break-after: always !important;
        break-after: page !important;
    }
    
    /* Remove any transforms that might break printing */
    * {
        transform: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

def find_takeout_folder():
    patterns = [
        "./Takeout*/Fitbit/Global Export Data",
        "./Takeout*/Fitbit",
        "./**/Takeout*/Fitbit/Global Export Data",
        "./**/Takeout*/Fitbit",
        "./Fitbit/Global Export Data",
        "./Fitbit",
    ]
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            return matches[0]
    return None

def load_json_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def load_csv_file(filepath):
    try:
        return pd.read_csv(filepath)
    except:
        return None

def find_files(base_path, pattern):
    if base_path is None:
        return []
    search_path = os.path.join(base_path, "**", pattern)
    return glob.glob(search_path, recursive=True)

# ==============================================================================
# FONCTIONS DE LECTURE - DONNEES CONTINUES DETAILLEES
# ==============================================================================

def parse_detailed_heart_rate(base_path):
    """
    Charge TOUTES les donnees de frequence cardiaque en continu.
    Retourne un DataFrame avec toutes les lectures (toutes les quelques secondes).
    """
    files = find_files(base_path, "heart_rate-*.json")
    all_data = []
    
    for f in files:
        data = load_json_file(f)
        if data and isinstance(data, list):
            for entry in data:
                value_data = entry.get('value', {})
                bpm = value_data.get('bpm', 0)
                if bpm and 30 <= bpm <= 220:
                    all_data.append({
                        'timestamp': entry.get('dateTime'),
                        'bpm': bpm,
                        'confidence': value_data.get('confidence', 0)
                    })
    
    if all_data:
        df = pd.DataFrame(all_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%m/%d/%y %H:%M:%S')
        df = df.sort_values('timestamp')
        return df
    return pd.DataFrame()

def parse_detailed_steps(base_path):
    """
    Charge TOUTES les donnees de pas en continu.
    Retourne un DataFrame avec les pas par minute.
    """
    files = find_files(base_path, "steps-*.json")
    all_data = []
    
    for f in files:
        data = load_json_file(f)
        if data and isinstance(data, list):
            for entry in data:
                try:
                    steps = int(entry.get('value', 0))
                    all_data.append({
                        'timestamp': entry.get('dateTime'),
                        'steps': steps
                    })
                except:
                    pass
    
    if all_data:
        df = pd.DataFrame(all_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%m/%d/%y %H:%M:%S')
        df = df.sort_values('timestamp')
        return df
    return pd.DataFrame()

def parse_detailed_calories(base_path):
    """
    Charge TOUTES les donnees de calories en continu.
    Retourne un DataFrame avec les calories par minute.
    """
    files = find_files(base_path, "calories-*.json")
    all_data = []
    
    for f in files:
        data = load_json_file(f)
        if data and isinstance(data, list):
            for entry in data:
                try:
                    cals = float(entry.get('value', 0))
                    all_data.append({
                        'timestamp': entry.get('dateTime'),
                        'calories': cals
                    })
                except:
                    pass
    
    if all_data:
        df = pd.DataFrame(all_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%m/%d/%y %H:%M:%S')
        df = df.sort_values('timestamp')
        return df
    return pd.DataFrame()

def parse_sleep_data(base_path):
    """Charge les donnees de sommeil."""
    sleep_files = find_files(base_path, "sleep-*.json")
    all_sleep = []
    
    for f in sleep_files:
        data = load_json_file(f)
        if data and isinstance(data, list):
            for entry in data:
                sleep_record = {
                    'date': entry.get('dateOfSleep'),
                    'start_time': entry.get('startTime'),
                    'end_time': entry.get('endTime'),
                    'duration_minutes': entry.get('duration', 0) / 60000 if entry.get('duration') else 0,
                    'minutes_asleep': entry.get('minutesAsleep'),
                    'minutes_awake': entry.get('minutesAwake'),
                    'time_in_bed': entry.get('timeInBed'),
                    'efficiency': entry.get('efficiency'),
                    'type': entry.get('type'),
                    'main_sleep': entry.get('mainSleep', False),
                }
                
                levels = entry.get('levels', {})
                summary = levels.get('summary', {})
                
                if sleep_record['type'] == 'stages':
                    if 'deep' in summary:
                        sleep_record['deep_minutes'] = summary['deep'].get('minutes', 0)
                    if 'light' in summary:
                        sleep_record['light_minutes'] = summary['light'].get('minutes', 0)
                    if 'rem' in summary:
                        sleep_record['rem_minutes'] = summary['rem'].get('minutes', 0)
                    if 'wake' in summary:
                        sleep_record['wake_minutes'] = summary['wake'].get('minutes', 0)
                else:
                    if 'restless' in summary:
                        sleep_record['restless_minutes'] = summary['restless'].get('minutes', 0)
                    if 'awake' in summary:
                        sleep_record['awake_minutes'] = summary['awake'].get('minutes', 0)
                    if 'asleep' in summary:
                        sleep_record['asleep_minutes'] = summary['asleep'].get('minutes', 0)
                
                all_sleep.append(sleep_record)
    
    if all_sleep:
        df = pd.DataFrame(all_sleep)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        return df
    return pd.DataFrame()

def parse_heart_rate_summary(base_path):
    """Charge les resumes de frequence cardiaque au repos."""
    files = find_files(base_path, "resting_heart_rate-*.json")
    all_data = []
    
    for f in files:
        data = load_json_file(f)
        if data and isinstance(data, list):
            for entry in data:
                value_data = entry.get('value', {})
                hr_value = value_data.get('value', 0)
                if hr_value and hr_value > 30:
                    all_data.append({
                        'date': entry.get('dateTime'),
                        'resting_hr': hr_value,
                        'error': value_data.get('error', 0)
                    })
    
    if all_data:
        df = pd.DataFrame(all_data)
        df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y %H:%M:%S')
        df = df.sort_values('date')
        return df
    return pd.DataFrame()

def parse_hrv(base_path):
    """Charge les donnees de variabilite de la frequence cardiaque."""
    search_dirs = [
        base_path.replace("Global Export Data", "Heart Rate Variability"),
        base_path
    ]
    
    all_data = []
    for search_dir in search_dirs:
        files = find_files(search_dir, "Daily Heart Rate Variability Summary*.csv")
        for f in files:
            df = load_csv_file(f)
            if df is not None and not df.empty and 'timestamp' in df.columns:
                all_data.append(df)
    
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        combined['timestamp'] = pd.to_datetime(combined['timestamp'])
        combined = combined.sort_values('timestamp').drop_duplicates(subset=['timestamp'])
        return combined
    return pd.DataFrame()

def parse_spo2(base_path):
    """Charge les donnees de saturation en oxygene."""
    search_dirs = [
        base_path.replace("Global Export Data", "Oxygen Saturation (SpO2)"),
        base_path
    ]
    
    for search_dir in search_dirs:
        files = find_files(search_dir, "Daily SpO2*.csv")
        if files:
            df = load_csv_file(files[0])
            if df is not None and not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                return df
    return pd.DataFrame()

def parse_stress_score(base_path):
    """Charge les donnees de score de stress."""
    search_dirs = [
        base_path.replace("Global Export Data", "Stress Score"),
        base_path
    ]
    
    for search_dir in search_dirs:
        files = find_files(search_dir, "Stress Score.csv")
        if files:
            df = load_csv_file(files[0])
            if df is not None and not df.empty:
                df['DATE'] = pd.to_datetime(df['DATE'])
                return df
    return pd.DataFrame()

def parse_sleep_score(base_path):
    """Charge les donnees de score de sommeil."""
    files = find_files(base_path.replace("Global Export Data", "").rstrip("/"), "*/sleep_score.csv")
    if not files:
        files = find_files(base_path, "sleep_score.csv")
    
    if files:
        df = load_csv_file(files[0])
        if df is not None and not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            return df
    return pd.DataFrame()

def parse_profile(base_path):
    """Charge le profil utilisateur."""
    search_dirs = [
        base_path.replace("Global Export Data", "Your Profile"),
        base_path
    ]
    
    for search_dir in search_dirs:
        files = find_files(search_dir, "Profile.csv")
        if files:
            df = load_csv_file(files[0])
            if df is not None and not df.empty:
                return df.iloc[0].to_dict()
    return {}

# ==============================================================================
# FONCTIONS DE CREATION DE GRAPHES CONTINUS
# ==============================================================================

def create_continuous_hr_chart(hr_df):
    """
    Cree un graphique continu de frequence cardiaque avec TOUTES les donnees.
    """
    if hr_df.empty:
        return None
    
    # Sous-echantillonnage si trop de points pour les performances
    n_points = len(hr_df)
    if n_points > 50000:
        step = n_points // 25000
        plot_df = hr_df.iloc[::step].copy()
    else:
        plot_df = hr_df.copy()
    
    fig = go.Figure()
    
    # Donnees brutes
    fig.add_trace(go.Scatter(
        x=plot_df['timestamp'],
        y=plot_df['bpm'],
        mode='lines',
        name='Frequence cardiaque',
        line=dict(color='#e74c3c', width=1),
        hovertemplate='<b>%{x|%Y-%m-%d %H:%M}</b><br>FC: %{y:.0f} bpm<extra></extra>'
    ))
    
    # Moyenne mobile sur 1 heure
    if n_points > 1000:
        hr_df_sorted = hr_df.sort_values('timestamp')
        hr_df_sorted['hour'] = hr_df_sorted['timestamp'].dt.floor('H')
        hourly_avg = hr_df_sorted.groupby('hour')['bpm'].mean().reset_index()
        
        fig.add_trace(go.Scatter(
            x=hourly_avg['hour'],
            y=hourly_avg['bpm'],
            mode='lines',
            name='Moyenne horaire',
            line=dict(color='#c0392b', width=3),
            hovertemplate='<b>%{x|%Y-%m-%d %H:%M}</b><br>Moyenne: %{y:.1f} bpm<extra></extra>'
        ))
    
    # Zones de frequence cardiaque
    fig.add_hrect(y0=40, y1=60, line_width=0, fillcolor="green", opacity=0.05)
    fig.add_hrect(y0=60, y1=100, line_width=0, fillcolor="green", opacity=0.05)
    fig.add_hrect(y0=100, y1=140, line_width=0, fillcolor="yellow", opacity=0.05)
    fig.add_hrect(y0=140, y1=200, line_width=0, fillcolor="red", opacity=0.05)
    
    fig.add_hline(y=60, line_dash="dot", line_color="green", opacity=0.5)
    fig.add_hline(y=100, line_dash="dot", line_color="orange", opacity=0.5)
    fig.add_hline(y=140, line_dash="dot", line_color="red", opacity=0.5)
    
    min_bpm = hr_df['bpm'].min()
    max_bpm = hr_df['bpm'].max()
    avg_bpm = hr_df['bpm'].mean()
    
    fig.update_layout(
        title=dict(
            text=f"Frequence cardiaque continue - {n_points:,} lectures<br>" +
                 f"<sub>Min: {min_bpm:.0f} bpm | Max: {max_bpm:.0f} bpm | Moyenne: {avg_bpm:.1f} bpm</sub>",
            font=dict(size=16)
        ),
        xaxis_title="Date et heure",
        yaxis_title="Frequence cardiaque (bpm)",
        yaxis=dict(range=[30, max(180, max_bpm + 10)]),
        hovermode='x unified',
        template='plotly_white',
        height=500,
        margin=dict(l=60, r=40, t=80, b=60),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig

def create_continuous_activity_chart(steps_df, calories_df):
    """
    Cree un graphique continu d'activite avec TOUTES les donnees.
    """
    if steps_df.empty:
        return None
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=('Pas par minute', 'Calories par minute'),
        vertical_spacing=0.1
    )
    
    # Sous-echantillonnage si necessaire
    n_steps = len(steps_df)
    if n_steps > 50000:
        step = n_steps // 25000
        steps_plot = steps_df.iloc[::step].copy()
    else:
        steps_plot = steps_df.copy()
    
    # Pas - couleur foncée pour meilleure visibilité en PDF
    fig.add_trace(
        go.Bar(
            x=steps_plot['timestamp'],
            y=steps_plot['steps'],
            name='Pas',
            marker_color='#1e8449',
            marker_line_color='#145a32',
            marker_line_width=0.5,
            hovertemplate='<b>%{x|%Y-%m-%d %H:%M}</b><br>Pas: %{y}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Calories si disponibles
    if not calories_df.empty:
        n_cals = len(calories_df)
        if n_cals > 50000:
            step = n_cals // 25000
            cals_plot = calories_df.iloc[::step].copy()
        else:
            cals_plot = calories_df.copy()
        
        fig.add_trace(
            go.Bar(
                x=cals_plot['timestamp'],
                y=cals_plot['calories'],
                name='Calories',
                marker_color='#1e8449',
                marker_line_color='#145a32',
                marker_line_width=0.5,
                hovertemplate='<b>%{x|%Y-%m-%d %H:%M}</b><br>Cal: %{y:.1f}<extra></extra>'
            ),
            row=2, col=1
        )
    
    total_steps = steps_df['steps'].sum()
    total_cals = calories_df['calories'].sum() if not calories_df.empty else 0
    
    fig.update_layout(
        title=dict(
            text=f"Activite continue<br><sub>Total pas: {int(total_steps):,} | Total calories: {int(total_cals):,}</sub>",
            font=dict(size=16)
        ),
        hovermode='x unified',
        template='plotly_white',
        height=600,
        margin=dict(l=60, r=40, t=100, b=60),
        showlegend=False
    )
    
    return fig

def create_sleep_chart(sleep_df):
    """Cree un graphique continu de sommeil."""
    if sleep_df.empty:
        return None
    
    main_sleep = sleep_df[sleep_df['main_sleep'] == True].copy()
    if main_sleep.empty:
        return None
    
    fig = go.Figure()
    
    # Duree de sommeil
    if 'minutes_asleep' in main_sleep.columns:
        fig.add_trace(go.Bar(
            x=main_sleep['date'],
            y=main_sleep['minutes_asleep'] / 60,
            name='Duree de sommeil',
            marker_color='#667eea',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Sommeil: %{y:.1f} heures<extra></extra>'
        ))
    
    # Ligne de reference pour 7-9 heures
    fig.add_hrect(y0=7, y1=9, line_width=0, fillcolor="green", opacity=0.1,
                  annotation_text="Recommande (7-9h)", annotation_position="right")
    
    fig.update_layout(
        title=dict(text="Duree de sommeil continue", font=dict(size=16)),
        xaxis_title="Date",
        yaxis_title="Heures de sommeil",
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=60, r=40, t=60, b=60)
    )
    
    return fig

def create_sleep_stages_chart(sleep_df):
    """Cree un graphique des phases de sommeil."""
    if sleep_df.empty:
        return None
    
    main_sleep = sleep_df[sleep_df['main_sleep'] == True].copy()
    if main_sleep.empty:
        return None
    
    has_stages = 'deep_minutes' in main_sleep.columns and main_sleep['deep_minutes'].notna().any()
    has_classic = 'restless_minutes' in main_sleep.columns and main_sleep['restless_minutes'].notna().any()
    
    fig = go.Figure()
    
    if has_stages:
        stages = [
            ('deep_minutes', 'Sommeil profond', '#4c1d95'),
            ('light_minutes', 'Sommeil leger', '#7c3aed'),
            ('rem_minutes', 'Sommeil REM', '#c084fc'),
            ('wake_minutes', 'Eveille', '#fca5a5')
        ]
        
        for col, name, color in stages:
            if col in main_sleep.columns:
                fig.add_trace(go.Bar(
                    x=main_sleep['date'],
                    y=main_sleep[col],
                    name=name,
                    marker_color=color,
                    hovertemplate=f'<b>%{{x|%Y-%m-%d}}</b><br>{name}: %{{y:.0f}} min<extra></extra>'
                ))
        
        title = "Phases de sommeil continue"
        
    elif has_classic:
        stages = [
            ('asleep_minutes', 'Endormi', '#7c3aed'),
            ('restless_minutes', 'Agite', '#fbbf24'),
            ('awake_minutes', 'Eveille', '#fca5a5')
        ]
        
        for col, name, color in stages:
            if col in main_sleep.columns:
                fig.add_trace(go.Bar(
                    x=main_sleep['date'],
                    y=main_sleep[col],
                    name=name,
                    marker_color=color,
                    hovertemplate=f'<b>%{{x|%Y-%m-%d}}</b><br>{name}: %{{y:.0f}} min<extra></extra>'
                ))
        
        title = "Phases de sommeil continue (mode classique)"
    else:
        return None
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis_title="Date",
        yaxis_title="Minutes",
        barmode='stack',
        hovermode='x unified',
        template='plotly_white',
        height=450,
        margin=dict(l=60, r=40, t=60, b=60),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig

def create_hrv_chart(hrv_df):
    """Cree un graphique de VFC."""
    if hrv_df.empty or 'rmssd' not in hrv_df.columns:
        return None
    
    fig = make_subplots(
        rows=2 if 'nremhr' in hrv_df.columns and hrv_df['nremhr'].notna().any() else 1,
        cols=1,
        shared_xaxes=True,
        subplot_titles=('VFC (RMSSD)', 'Frequence cardiaque sommeil (NREM)') if 'nremhr' in hrv_df.columns else ('VFC (RMSSD)',),
        vertical_spacing=0.12
    )
    
    fig.add_trace(
        go.Scatter(
            x=hrv_df['timestamp'],
            y=hrv_df['rmssd'],
            mode='lines+markers',
            name='RMSSD',
            line=dict(color='#9b59b6', width=2),
            marker=dict(size=6),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>RMSSD: %{y:.1f} ms<extra></extra>'
        ),
        row=1, col=1
    )
    
    if 'nremhr' in hrv_df.columns:
        valid_nrem = hrv_df[hrv_df['nremhr'] > 0]
        if not valid_nrem.empty:
            fig.add_trace(
                go.Scatter(
                    x=valid_nrem['timestamp'],
                    y=valid_nrem['nremhr'],
                    mode='lines+markers',
                    name='FC NREM',
                    line=dict(color='#e74c3c', width=2),
                    marker=dict(size=6),
                    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>FC NREM: %{y:.1f} bpm<extra></extra>'
                ),
                row=2, col=1
            )
    
    fig.update_layout(
        title=dict(text="Variabilite de la frequence cardiaque", font=dict(size=16)),
        hovermode='x unified',
        template='plotly_white',
        height=500,
        margin=dict(l=60, r=40, t=80, b=60),
        showlegend=False
    )
    
    return fig

def create_spo2_chart(spo2_df):
    """Cree un graphique de SpO2."""
    if spo2_df.empty or 'average_value' not in spo2_df.columns:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=spo2_df['timestamp'],
        y=spo2_df['average_value'],
        mode='lines+markers',
        name='SpO2 moyenne',
        line=dict(color='#3498db', width=2),
        marker=dict(size=6),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>SpO2: %{y:.1f}%<extra></extra>'
    ))
    
    if 'lower_bound' in spo2_df.columns and 'upper_bound' in spo2_df.columns:
        fig.add_trace(go.Scatter(
            x=spo2_df['timestamp'],
            y=spo2_df['upper_bound'],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=spo2_df['timestamp'],
            y=spo2_df['lower_bound'],
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(52, 152, 219, 0.2)',
            name='Plage',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Min: %{y:.1f}%<extra></extra>'
        ))
    
    fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Normal (95%)")
    fig.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="Bas (90%)")
    
    fig.update_layout(
        title=dict(text="Saturation en oxygene (SpO2)", font=dict(size=16)),
        xaxis_title="Date",
        yaxis_title="SpO2 (%)",
        yaxis=dict(range=[85, 100]),
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=60, r=40, t=60, b=60),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig

def create_stress_chart(stress_df):
    """Cree un graphique de stress."""
    if stress_df.empty or 'STRESS_SCORE' not in stress_df.columns:
        return None
    
    valid_stress = stress_df[stress_df['STRESS_SCORE'] > 0]
    if valid_stress.empty:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=valid_stress['DATE'],
        y=valid_stress['STRESS_SCORE'],
        mode='lines+markers',
        name='Score de stress',
        line=dict(color='#e67e22', width=2),
        marker=dict(size=8),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Stress: %{y:.0f}/100<extra></extra>'
    ))
    
    fig.add_hrect(y0=0, y1=25, line_width=0, fillcolor="red", opacity=0.1, annotation_text="Eleve")
    fig.add_hrect(y0=25, y1=50, line_width=0, fillcolor="orange", opacity=0.1)
    fig.add_hrect(y0=50, y1=75, line_width=0, fillcolor="yellow", opacity=0.1)
    fig.add_hrect(y0=75, y1=100, line_width=0, fillcolor="green", opacity=0.1, annotation_text="Faible")
    
    fig.update_layout(
        title=dict(text="Score de stress continu", font=dict(size=16)),
        xaxis_title="Date",
        yaxis_title="Score (0-100)",
        yaxis=dict(range=[0, 100]),
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=60, r=40, t=60, b=60)
    )
    
    return fig

def create_hr_histogram(hr_df):
    """Cree un histogramme de distribution de la frequence cardiaque."""
    if hr_df.empty or 'bpm' not in hr_df.columns:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=hr_df['bpm'],
        nbinsx=50,
        marker_color='#667eea',
        opacity=0.7,
        hovertemplate='<b>%{x:.0f} bpm</b><br>Occurrences: %{y}<extra></extra>'
    ))
    
    avg_hr = hr_df['bpm'].mean()
    fig.add_vline(x=avg_hr, line_dash="dash", line_color="red",
                  annotation_text=f"Moyenne: {avg_hr:.1f}")
    
    fig.update_layout(
        title=dict(text="Distribution de la frequence cardiaque", font=dict(size=16)),
        xaxis_title="Frequence cardiaque (bpm)",
        yaxis_title="Nombre d'occurrences",
        template='plotly_white',
        height=350,
        margin=dict(l=60, r=40, t=60, b=60),
        bargap=0.1
    )
    
    return fig

# ==============================================================================
# ANALYSE DE SANTE SIMPLIFIEE (SANS RECOMMANDATIONS MEDICALES)
# ==============================================================================

def analyze_health(hr_summary, sleep_df, hrv_df, spo2_df, stress_df):
    """Analyse simplifiee sans recommandations medicales."""
    alerts = []
    warnings = []
    info = []
    
    # Analyse FC
    if not hr_summary.empty and 'resting_hr' in hr_summary.columns:
        recent_hr = hr_summary['resting_hr'].dropna()
        if len(recent_hr) > 0:
            latest_hr = recent_hr.iloc[-1]
            avg_hr = recent_hr.mean()
            
            if latest_hr > 100:
                alerts.append(_t(st.session_state.get("_i18n", {}), "analysis.hr_rest_high", value=latest_hr))
            elif latest_hr < 50:
                warnings.append(_t(st.session_state.get("_i18n", {}), "analysis.hr_rest_low", value=latest_hr))
            else:
                info.append(_t(st.session_state.get("_i18n", {}), "analysis.hr_rest_normal", value=latest_hr, avg=avg_hr))
    
    # Analyse SpO2
    if not spo2_df.empty and 'average_value' in spo2_df.columns:
        avg_spo2 = spo2_df['average_value'].mean()
        min_spo2 = spo2_df['lower_bound'].min() if 'lower_bound' in spo2_df.columns else spo2_df['average_value'].min()
        
        if min_spo2 < 90:
            alerts.append(_t(st.session_state.get("_i18n", {}), "analysis.spo2_low_detected", value=min_spo2))
        elif avg_spo2 < 94:
            warnings.append(_t(st.session_state.get("_i18n", {}), "analysis.spo2_avg_low", value=avg_spo2))
        else:
            info.append(_t(st.session_state.get("_i18n", {}), "analysis.spo2_normal", value=avg_spo2))
    
    # Analyse sommeil
    if not sleep_df.empty and 'minutes_asleep' in sleep_df.columns:
        main_sleep = sleep_df[sleep_df['main_sleep'] == True]
        if not main_sleep.empty:
            avg_sleep = main_sleep['minutes_asleep'].mean() / 60
            
            if avg_sleep < 5:
                alerts.append(_t(st.session_state.get("_i18n", {}), "analysis.sleep_too_low", value=avg_sleep))
            elif avg_sleep < 6:
                warnings.append(_t(st.session_state.get("_i18n", {}), "analysis.sleep_short", value=avg_sleep))
            elif avg_sleep > 10:
                warnings.append(_t(st.session_state.get("_i18n", {}), "analysis.sleep_long", value=avg_sleep))
            else:
                info.append(_t(st.session_state.get("_i18n", {}), "analysis.sleep_ok", value=avg_sleep))
    
    # Analyse HRV
    if not hrv_df.empty and 'rmssd' in hrv_df.columns:
        avg_hrv = hrv_df['rmssd'].mean()
        if avg_hrv < 20:
            warnings.append(_t(st.session_state.get("_i18n", {}), "analysis.hrv_low", value=avg_hrv))
        else:
            info.append(_t(st.session_state.get("_i18n", {}), "analysis.hrv_ok", value=avg_hrv))
    
    # Analyse stress
    if not stress_df.empty and 'STRESS_SCORE' in stress_df.columns:
        stress_data = stress_df[stress_df['STRESS_SCORE'] > 0]['STRESS_SCORE']
        if len(stress_data) > 0:
            avg_stress = stress_data.mean()
            if avg_stress < 30:
                warnings.append(_t(st.session_state.get("_i18n", {}), "analysis.stress_high", value=avg_stress))
            else:
                info.append(_t(st.session_state.get("_i18n", {}), "analysis.stress_level", value=avg_stress))
    
    return alerts, warnings, info

def display_alert(text, level):
    """Affiche une alerte sans recommandation medicale."""
    css_class = {
        'alert': 'alert-critical',
        'warning': 'alert-warning',
        'info': 'alert-good'
    }.get(level, 'alert-info')
    
    st.markdown(f'<div class="{css_class}">{text}</div>', unsafe_allow_html=True)

def display_note(text):
    """Affiche une note explicative."""
    st.markdown(f'<div class="comment-box">{text}</div>', unsafe_allow_html=True)

# ==============================================================================
# GENERATION HTML POUR IMPRESSION
# ==============================================================================

def generate_printable_html(profile, hr_summary, sleep_df, hrv_df, spo2_df, stress_df,
                            detailed_hr_df, detailed_steps_df, chart_images=None, tr=None):
    """
    Genere un HTML autonome optimise pour l'impression A4 avec graphiques PNG integres.
    """
    from datetime import datetime
    
    tr = tr or st.session_state.get("_i18n", {})
    gen_date = datetime.now().strftime('%Y-%m-%d')
    chart_images = chart_images or {}
    
    # Infos utilisateur
    name = profile.get('display_name', 'N/A') if profile else 'N/A'
    age_gender = "N/A"
    height_weight_bmi = "N/A"
    
    if profile and 'date_of_birth' in profile:
        try:
            dob = datetime.strptime(profile['date_of_birth'], '%Y-%m-%d')
            age = int((datetime.now() - dob).days / 365.25)
            gender = profile.get('gender', '')
            age_gender = f"{age} ans / {gender}"
        except:
            pass
    
    # Calculate BMI if height and weight available
    if profile:
        height = profile.get('height')
        weight = profile.get('weight')
        if isinstance(height, (int, float)) and isinstance(weight, (int, float)) and height > 0:
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            height_weight_bmi = f"{int(height)} cm / {int(weight)} kg / IMC {bmi:.1f}"
    
    # Helper to create chart HTML
    def chart_html(chart_name, title):
        if chart_name in chart_images and chart_images[chart_name]:
            return f'''
            <div class="chart-container">
                <div class="chart-title">{title}</div>
                <img src="data:image/png;base64,{chart_images[chart_name]}" alt="{title}" />
            </div>
            '''
        return ''
    
    # Statistiques et graphiques
    sections = []
    
    if not detailed_hr_df.empty:
        hr_chart = chart_html('heart_rate', 'Frequence cardiaque continue')
        sections.append(f"""
        <div class="section">
            <div class="section-header">Frequence cardiaque</div>
            <div class="metrics">
                <div class="metric"><div class="metric-label">Lectures</div><div class="metric-value">{len(detailed_hr_df):,}</div></div>
                <div class="metric"><div class="metric-label">Moyenne</div><div class="metric-value">{detailed_hr_df['bpm'].mean():.1f} bpm</div></div>
                <div class="metric"><div class="metric-label">Min/Max</div><div class="metric-value">{detailed_hr_df['bpm'].min():.0f}/{detailed_hr_df['bpm'].max():.0f}</div></div>
            </div>
            {hr_chart}
        </div>
        """)
    
    if not sleep_df.empty:
        sleep_chart = chart_html('sleep', 'Analyse du sommeil')
        main_sleep = sleep_df[sleep_df['main_sleep'] == True]
        if not main_sleep.empty and 'minutes_asleep' in main_sleep.columns:
            avg_sleep = main_sleep['minutes_asleep'].mean() / 60
            sections.append(f"""
            <div class="section">
                <div class="section-header">Sommeil</div>
                <div class="metrics">
                    <div class="metric"><div class="metric-label">Nuits</div><div class="metric-value">{len(main_sleep)}</div></div>
                    <div class="metric"><div class="metric-label">Moyenne</div><div class="metric-value">{avg_sleep:.1f}h</div></div>
                </div>
                {sleep_chart}
            </div>
            """)
    
    if not spo2_df.empty:
        spo2_chart = chart_html('spo2', 'Saturation en oxygene')
        avg_spo2 = spo2_df['average_value'].mean()
        min_spo2 = spo2_df['lower_bound'].min() if 'lower_bound' in spo2_df.columns else spo2_df['average_value'].min()
        sections.append(f"""
        <div class="section">
            <div class="section-header">Saturation oxygene</div>
            <div class="metrics">
                <div class="metric"><div class="metric-label">Moyenne</div><div class="metric-value">{avg_spo2:.1f}%</div></div>
                <div class="metric"><div class="metric-label">Minimum</div><div class="metric-value">{min_spo2:.1f}%</div></div>
            </div>
            {spo2_chart}
        </div>
        """)
    
    if not hrv_df.empty and 'rmssd' in hrv_df.columns:
        hrv_chart = chart_html('hrv', 'Variabilite de la frequence cardiaque')
        avg_hrv = hrv_df['rmssd'].mean()
        sections.append(f"""
        <div class="section">
            <div class="section-header">Variabilite FC</div>
            <div class="metrics">
                <div class="metric"><div class="metric-label">RMSSD</div><div class="metric-value">{avg_hrv:.1f} ms</div></div>
            </div>
            {hrv_chart}
        </div>
        """)
    
    if not detailed_steps_df.empty:
        activity_chart = chart_html('activity', 'Activite continue')
        total_steps = detailed_steps_df['steps'].sum()
        sections.append(f"""
        <div class="section">
            <div class="section-header">Activite</div>
            <div class="metrics">
                <div class="metric"><div class="metric-label">Total pas</div><div class="metric-value">{int(total_steps):,}</div></div>
            </div>
            {activity_chart}
        </div>
        """)
    
    # Alertes
    alerts, warnings, info = analyze_health(hr_summary, sleep_df, hrv_df, spo2_df, stress_df)
    alert_html = ""
    for alert in alerts:
        alert_html += f'<div class="alert alert-critical">{alert}</div>'
    for warning in warnings:
        alert_html += f'<div class="alert alert-warning">{warning}</div>'
    for i in info:
        alert_html += f'<div class="alert alert-good">{i}</div>'
    
    # HTML complet avec CSS integre optimise pour l'impression
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{_t(tr, "report.title")} - {name}</title>
    <style>
        /* Reset et base */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #333;
            background: white;
            padding: 15px;
            max-width: 210mm;
            margin: 0 auto;
        }}
        
        /* Page A4 */
        @page {{
            size: A4 portrait;
            margin: 15mm;
        }}
        
        @media print {{
            body {{ 
                padding: 10px !important;
                font-size: 9pt !important;
            }}
            .no-print {{ display: none !important; }}
            .section {{ 
                margin-bottom: 15px !important;
                page-break-inside: avoid !important;
            }}
            .section-header {{
                font-size: 12pt !important;
                padding: 10px 15px !important;
                margin-bottom: 12px !important;
            }}
            .metrics {{
                gap: 10px !important;
                margin-bottom: 12px !important;
            }}
            .metric {{
                padding: 10px 15px !important;
                min-width: 120px !important;
            }}
            .metric-value {{
                font-size: 14pt !important;
            }}
            .chart-container {{
                margin: 15px 0 !important;
                page-break-inside: avoid !important;
            }}
            .chart-container img {{
                max-height: 280px !important;
                width: 100% !important;
            }}
            .footer {{
                margin-top: 30px !important;
                padding: 20px !important;
            }}
            .alert {{
                padding: 10px 15px !important;
                margin: 8px 0 !important;
            }}
        }}
        
        /* En-tete */
        .header {{
            text-align: center;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            color: #667eea;
            font-size: 28pt;
            margin-bottom: 5px;
        }}
        
        .header .date {{
            color: #666;
            font-size: 11pt;
        }}
        
        /* Sections */
        .section {{
            margin-bottom: 20px;
            page-break-inside: avoid;
        }}
        
        .section-header {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 18px;
            border-radius: 8px;
            font-size: 14pt;
            font-weight: 600;
            margin-bottom: 15px;
        }}
        
        /* Metriques */
        .metrics {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .metric {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 12px 18px;
            border-radius: 6px;
            min-width: 140px;
            flex: 1;
        }}
        
        .metric-label {{
            font-size: 9pt;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        
        .metric-value {{
            font-size: 16pt;
            font-weight: 700;
            color: #333;
        }}
        
        /* Alertes */
        .alert {{
            padding: 12px 16px;
            border-radius: 6px;
            margin: 10px 0;
            font-size: 10pt;
            border-left: 4px solid;
        }}
        
        .alert-critical {{
            background: #ffebee;
            border-color: #c62828;
            color: #c62828;
        }}
        
        .alert-warning {{
            background: #fff3e0;
            border-color: #ef6c00;
            color: #ef6c00;
        }}
        
        .alert-good {{
            background: #e8f5e9;
            border-color: #2e7d32;
            color: #2e7d32;
        }}
        
        /* Bouton impression */
        .print-btn {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #FF4B4B 0%, #e74c3c 100%);
            color: white;
            padding: 14px 28px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            border: none;
            box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
            font-size: 14px;
            z-index: 1000;
        }}
        
        .print-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(231, 76, 60, 0.5);
        }}
        
        /* Pied de page */
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 25px;
            color: #666;
            border-top: 1px solid #ddd;
            font-size: 9pt;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        /* Instructions */
        .instructions {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 6px 6px 0;
            font-size: 10pt;
        }}
        
        .instructions strong {{
            color: #1565c0;
        }}
        
        /* Chart containers */
        .chart-container {{
            margin: 20px 0;
            text-align: center;
            page-break-inside: avoid;
        }}
        
        .chart-title {{
            font-size: 10pt;
            color: #666;
            margin-bottom: 10px;
            text-align: center;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #eee;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <button class="print-btn no-print" onclick="window.print()">
        {_t(tr, "report.print_button")}
    </button>
    
    <div class="instructions no-print">
        <strong>{_t(tr, "report.instructions_title")}</strong><br>
        {_t(tr, "report.instructions_body").replace("\\n", "<br>")}
    </div>
    
    <div class="header">
        <h1>{_t(tr, "report.title")}</h1>
        <div class="date">{_t(tr, "report.subtitle")} - {_t(tr, "app.generated_on", datetime=gen_date)}</div>
    </div>
    
    <div class="section">
        <div class="section-header">{_t(tr, "report.section.information")}</div>
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">{_t(tr, "metric.name")}</div>
                <div class="metric-value">{name}</div>
            </div>
            <div class="metric">
                <div class="metric-label">{_t(tr, "metric.age_gender")}</div>
                <div class="metric-value">{age_gender}</div>
            </div>
            <div class="metric">
                <div class="metric-label">{_t(tr, "metric.weight_bmi")}</div>
                <div class="metric-value">{height_weight_bmi}</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-header">{_t(tr, "report.section.health_analysis")}</div>
        {alert_html if alert_html else f'<p style="color: #666; padding: 10px;">{_t(tr, "report.no_alerts")}</p>'}
    </div>
    
    <div class="section">
        <div class="section-header">{_t(tr, "report.section.detailed_stats")}</div>
        {''.join(sections)}
    </div>
    
    <div class="footer">
        <p><strong>{_t(tr, "footer.title")}</strong></p>
        <p>{_t(tr, "app.generated_on", datetime=gen_date)}</p>
        <p style="margin-top: 10px; font-size: 8pt;">
            {_t(tr, "footer.disclaimer")}
        </p>
    </div>
    
    <script>
        // Preparation automatique pour l'impression
        window.addEventListener('beforeprint', function() {{
            document.body.style.padding = '0';
        }});
        
        // Masquer le bouton et les instructions apres impression
        window.addEventListener('afterprint', function() {{
            document.body.style.padding = '20px';
        }});
    </script>
</body>
</html>"""
    
    return html

# ==============================================================================
# APPLICATION PRINCIPALE
# ==============================================================================

def extract_and_process_upload(uploaded_file):
    """
    Traite le fichier uploade (ZIP ou dossier).
    Retourne le chemin vers les donnees Fitbit.
    """
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    
    if uploaded_file.name.endswith('.zip'):
        import zipfile
        zip_path = os.path.join(temp_dir, uploaded_file.name)
        with open(zip_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        os.remove(zip_path)
    else:
        return None
    
    # Cherche le dossier Fitbit
    patterns = [
        os.path.join(temp_dir, "Takeout*", "Fitbit", "Global Export Data"),
        os.path.join(temp_dir, "Takeout*", "Fitbit"),
        os.path.join(temp_dir, "Fitbit", "Global Export Data"),
        os.path.join(temp_dir, "Fitbit"),
        os.path.join(temp_dir, "**", "Fitbit", "Global Export Data"),
        os.path.join(temp_dir, "**", "Fitbit"),
    ]
    
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            return matches[0]
    
    # Si pas de dossier Fitbit trouve, retourne le temp_dir
    return temp_dir

def main():
    # Language / i18n (default: English)
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    st.session_state["_i18n"] = _load_translations(st.session_state.get("lang", "en"))
    tr = st.session_state["_i18n"]

    # Initialiser session state
    if 'report_ready' not in st.session_state:
        st.session_state['report_ready'] = False
    if 'html_report' not in st.session_state:
        st.session_state['html_report'] = ''
    if 'generate_clicked' not in st.session_state:
        st.session_state['generate_clicked'] = False
    
    # Callback pour le bouton de generation
    def on_generate_click():
        st.session_state['generate_clicked'] = True
    
    # Sidebar - tout dans UN SEUL bloc
    with st.sidebar:
        lang_label = _t(tr, "language.label")
        lang = st.selectbox(
            lang_label,
            options=["en", "fr"],
            format_func=lambda v: _t(tr, f"language.{v}"),
            index=0 if st.session_state.get("lang") == "en" else 1,
        )
        if lang != st.session_state.get("lang"):
            st.session_state["lang"] = lang
            st.session_state["_i18n"] = _load_translations(lang)
            tr = st.session_state["_i18n"]

        st.header(_t(tr, "sidebar.data_upload"))
        
        uploaded_file = st.file_uploader(
            _t(tr, "sidebar.upload_label"),
            type=['zip'],
            help=_t(tr, "sidebar.upload_help")
        )
        
        if uploaded_file is not None:
            st.success(_t(tr, "sidebar.file_uploaded", filename=uploaded_file.name))
        
        st.markdown("---")
        st.markdown(f"**{_t(tr, 'sidebar.privacy_title')} :**")
        st.info(_t(tr, "sidebar.privacy_body"))
        
        st.markdown(f"**{_t(tr, 'sidebar.instructions_title')} :**")
        st.markdown(_t(tr, "sidebar.instructions_body"))
        
        st.markdown("---")
        st.markdown(f"**{_t(tr, 'sidebar.export_pdf_title')}**")
        
        # Bouton de generation
        st.button(_t(tr, "sidebar.generate_report"), type="primary", use_container_width=True, on_click=on_generate_click)
    
    st.markdown(f'''
    <div class="print-header">
        <h1 style="color:#667eea; margin-bottom:5px">{_t(tr, "app.title")}</h1>
        <p style="color:#666; font-size:1em; margin:0">
            {_t(tr, "app.generated_on", datetime=datetime.now().strftime('%Y-%m-%d %H:%M'))}
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Determiner la source des donnees
    if uploaded_file is not None:
        with st.spinner(_t(tr, "status.extracting_zip")):
            base_path = extract_and_process_upload(uploaded_file)
        if base_path is None:
            st.error(_t(tr, "error.extract_failed"))
            return
        st.success(_t(tr, "success.data_extracted"))
    else:
        base_path = find_takeout_folder()
        if base_path is None:
            st.info(_t(tr, "info.no_data"))
            return
    
    with st.spinner(_t(tr, "status.loading_data")):
        profile = parse_profile(base_path)
        
        # Chargement des donnees continues detaillees
        detailed_hr_df = parse_detailed_heart_rate(base_path)
        detailed_steps_df = parse_detailed_steps(base_path)
        detailed_cals_df = parse_detailed_calories(base_path)
        
        # Chargement des resumes
        hr_summary_df = parse_heart_rate_summary(base_path)
        sleep_df = parse_sleep_data(base_path)
        sleep_score_df = parse_sleep_score(base_path)
        hrv_df = parse_hrv(base_path)
        spo2_df = parse_spo2(base_path)
        stress_df = parse_stress_score(base_path)
    
    # Generation du rapport si demande - avec conversion des graphiques en PNG
    if st.session_state.get('generate_clicked', False):
        # Reset pour permettre regeneration
        st.session_state['generate_clicked'] = False
        
        with st.spinner(_t(tr, "status.generating_report")):
            # Generer les graphiques et les convertir en PNG
            chart_images = {}
            
            # Graphique FC
            if not detailed_hr_df.empty:
                fig_hr = create_continuous_hr_chart(detailed_hr_df)
                if fig_hr:
                    chart_images['heart_rate'] = fig_to_png_base64(fig_hr)
            
            # Graphique sommeil
            if not sleep_df.empty:
                fig_sleep = create_sleep_chart(sleep_df)
                if fig_sleep:
                    chart_images['sleep'] = fig_to_png_base64(fig_sleep)
            
            # Graphique SpO2
            if not spo2_df.empty:
                fig_spo2 = create_spo2_chart(spo2_df)
                if fig_spo2:
                    chart_images['spo2'] = fig_to_png_base64(fig_spo2)
            
            # Graphique HRV
            if not hrv_df.empty:
                fig_hrv = create_hrv_chart(hrv_df)
                if fig_hrv:
                    chart_images['hrv'] = fig_to_png_base64(fig_hrv)
            
            # Graphique activite
            if not detailed_steps_df.empty:
                fig_activity = create_continuous_activity_chart(detailed_steps_df, detailed_cals_df)
                if fig_activity:
                    chart_images['activity'] = fig_to_png_base64(fig_activity)
            
            # Generer le HTML avec les images
            html_content = generate_printable_html(
                profile, hr_summary_df, sleep_df, hrv_df, spo2_df, stress_df,
                detailed_hr_df, detailed_steps_df, chart_images, tr=tr
            )
            
            # Generer le PDF avec weasyprint
            pdf_bytes = generate_pdf_from_html(html_content)
            
            if pdf_bytes:
                st.success(_t(tr, "success.pdf_generated"))
                
                # Auto-download using HTML/JS
                import base64
                b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                filename = f"Rapport_sante_Fitbit_{datetime.now().strftime('%Y%m%d')}.pdf"
                
                download_link = f'''
                <script>
                    var link = document.createElement('a');
                    link.href = 'data:application/pdf;base64,{b64_pdf}';
                    link.download = '{filename}';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                </script>
                <p style="color: green; font-size: 14px;">
                    ✅ Le PDF a ete telecharge automatiquement. Si ce n\'est pas le cas, 
                    <a href="data:application/pdf;base64,{b64_pdf}" download="{filename}">cliquez ici</a>.
                </p>
                '''
                st.markdown(download_link, unsafe_allow_html=True)
                
                # Also show download button as fallback
                st.download_button(
                    label=_t(tr, "download.fallback_manual_pdf"),
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                # Fallback to HTML si PDF echoue
                st.warning(_t(tr, "warning.pdf_unavailable"))
                st.download_button(
                    label=_t(tr, "download.html_report"),
                    data=html_content.encode('utf-8'),
                    file_name=f"Rapport_sante_Fitbit_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html",
                    use_container_width=True
                )
    
    # Informations
    st.markdown(f'<div class="section-header">{_t(tr, "section.information")}</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        name = profile.get('display_name', 'N/A') if profile else 'N/A'
        st.metric(_t(tr, "metric.name"), name)
    
    with col2:
        if profile and 'date_of_birth' in profile:
            try:
                dob = datetime.strptime(profile['date_of_birth'], '%Y-%m-%d')
                age = int((datetime.now() - dob).days / 365.25)
                gender = profile.get('gender', '')
                st.metric(_t(tr, "metric.age_gender"), f"{age} / {gender}")
            except:
                st.metric(_t(tr, "metric.age_gender"), _t(tr, "common.na"))
        else:
            st.metric(_t(tr, "metric.age_gender"), _t(tr, "common.na"))
    
    with col3:
        if profile:
            height = profile.get('height', 'N/A')
            if isinstance(height, (int, float)):
                st.metric(_t(tr, "metric.height"), f"{int(height)} cm")
            else:
                st.metric(_t(tr, "metric.height"), str(height))
        else:
            st.metric(_t(tr, "metric.height"), _t(tr, "common.na"))
    
    with col4:
        if profile:
            weight = profile.get('weight', 'N/A')
            if isinstance(weight, (int, float)):
                height_m = profile.get('height', 175) / 100
                bmi = weight / (height_m ** 2)
                st.metric(_t(tr, "metric.weight_bmi"), f"{int(weight)} kg / {bmi:.1f}")
            else:
                st.metric(_t(tr, "metric.weight"), str(weight))
        else:
            st.metric(_t(tr, "metric.weight_bmi"), _t(tr, "common.na"))
    
    # Resume des donnees disponibles
    data_info = []
    if not detailed_hr_df.empty:
        data_info.append(_t(tr, "data.hr_readings", count=len(detailed_hr_df)))
    if not detailed_steps_df.empty:
        data_info.append(_t(tr, "data.steps_minutes", count=len(detailed_steps_df)))
    if not sleep_df.empty:
        data_info.append(_t(tr, "data.sleep_nights", count=len(sleep_df)))
    if not hrv_df.empty:
        data_info.append(_t(tr, "data.hrv_days", count=len(hrv_df)))
    if not spo2_df.empty:
        data_info.append(_t(tr, "data.spo2_days", count=len(spo2_df)))
    
    if data_info:
        st.markdown(_t(tr, "data.available", items=" | ".join(data_info)))
    
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    
    # Alertes sante
    st.markdown(f'<div class="section-header">{_t(tr, "section.health_analysis")}</div>', unsafe_allow_html=True)
    
    alerts, warnings, info = analyze_health(hr_summary_df, sleep_df, hrv_df, spo2_df, stress_df)
    
    if alerts:
        for alert in alerts:
            display_alert(alert, 'alert')
    
    if warnings:
        for warning in warnings:
            display_alert(warning, 'warning')
    
    if info:
        for i in info:
            display_alert(i, 'info')
    
    if not any([alerts, warnings, info]):
        st.info(_t(tr, "info.insufficient_data_analysis"))
    
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    
    # Frequence cardiaque continue
    st.markdown(f'<div class="section-header">{_t(tr, "section.hr_continuous")}</div>', unsafe_allow_html=True)
    
    display_note(_t(tr, "note.hr_continuous"))
    
    if not detailed_hr_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(_t(tr, "metric.total_readings"), f"{len(detailed_hr_df):,}")
        with col2:
            st.metric(_t(tr, "metric.avg_hr"), f"{detailed_hr_df['bpm'].mean():.1f} bpm")
        with col3:
            st.metric(_t(tr, "metric.min_hr"), f"{detailed_hr_df['bpm'].min():.0f} bpm")
        with col4:
            st.metric(_t(tr, "metric.max_hr"), f"{detailed_hr_df['bpm'].max():.0f} bpm")
        
        fig = create_continuous_hr_chart(detailed_hr_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Distribution
        hist_fig = create_hr_histogram(detailed_hr_df)
        if hist_fig:
            st.plotly_chart(hist_fig, use_container_width=True)
    else:
        st.info(_t(tr, "info.no_hr_detailed"))
    
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    
    # Activite continue
    st.markdown(f'<div class="section-header">{_t(tr, "section.activity_continuous")}</div>', unsafe_allow_html=True)
    
    display_note(_t(tr, "note.activity_continuous"))
    
    if not detailed_steps_df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            total_steps = detailed_steps_df['steps'].sum()
            st.metric(_t(tr, "metric.total_steps"), f"{int(total_steps):,}")
        with col2:
            avg_daily = detailed_steps_df.groupby(detailed_steps_df['timestamp'].dt.date)['steps'].sum().mean()
            st.metric(_t(tr, "metric.daily_average"), f"{int(avg_daily):,}")
        with col3:
            active_minutes = len(detailed_steps_df[detailed_steps_df['steps'] > 0])
            st.metric(_t(tr, "metric.active_minutes"), f"{active_minutes:,}")
        
        fig = create_continuous_activity_chart(detailed_steps_df, detailed_cals_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(_t(tr, "info.no_activity_detailed"))
    
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    
    # Sommeil
    st.markdown(f'<div class="section-header">{_t(tr, "section.sleep_analysis")}</div>', unsafe_allow_html=True)
    
    display_note(_t(tr, "note.sleep_analysis"))
    
    if not sleep_df.empty:
        main_sleep = sleep_df[sleep_df['main_sleep'] == True]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'minutes_asleep' in main_sleep.columns:
                avg_hours = main_sleep['minutes_asleep'].mean() / 60
                st.metric(_t(tr, "metric.avg_duration"), f"{avg_hours:.1f} {_t(tr, 'unit.hours')}")
        with col2:
            if 'efficiency' in main_sleep.columns:
                avg_eff = main_sleep['efficiency'].mean()
                st.metric(_t(tr, "metric.efficiency"), f"{avg_eff:.0f}%")
        with col3:
            if not sleep_score_df.empty and 'overall_score' in sleep_score_df.columns:
                avg_score = sleep_score_df['overall_score'].mean()
                st.metric(_t(tr, "metric.sleep_score"), f"{avg_score:.0f}/100")
        
        # Graphique de duree
        fig = create_sleep_chart(sleep_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Graphique des phases
        stages_fig = create_sleep_stages_chart(sleep_df)
        if stages_fig:
            st.plotly_chart(stages_fig, use_container_width=True)
    else:
        st.info(_t(tr, "info.no_sleep"))
    
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    
    # VFC
    st.markdown(f'<div class="section-header">{_t(tr, "section.hrv")}</div>', unsafe_allow_html=True)
    
    display_note(_t(tr, "note.hrv"))
    
    if not hrv_df.empty and 'rmssd' in hrv_df.columns:
        col1, col2 = st.columns(2)
        with col1:
            avg_hrv = hrv_df['rmssd'].mean()
            st.metric(_t(tr, "metric.avg_rmssd"), f"{avg_hrv:.1f} ms")
        with col2:
            latest_hrv = hrv_df['rmssd'].iloc[-1]
            st.metric(_t(tr, "metric.latest_rmssd"), f"{latest_hrv:.1f} ms")
        
        fig = create_hrv_chart(hrv_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(_t(tr, "info.no_hrv"))
    
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    
    # SpO2
    st.markdown(f'<div class="section-header">{_t(tr, "section.spo2")}</div>', unsafe_allow_html=True)
    
    display_note(_t(tr, "note.spo2"))
    
    if not spo2_df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_spo2 = spo2_df['average_value'].mean()
            st.metric(_t(tr, "metric.avg_spo2"), f"{avg_spo2:.1f}%")
        with col2:
            min_spo2 = spo2_df['lower_bound'].min() if 'lower_bound' in spo2_df.columns else spo2_df['average_value'].min()
            st.metric(_t(tr, "metric.min_spo2"), f"{min_spo2:.1f}%")
        with col3:
            max_spo2 = spo2_df['upper_bound'].max() if 'upper_bound' in spo2_df.columns else spo2_df['average_value'].max()
            st.metric(_t(tr, "metric.max_spo2"), f"{max_spo2:.1f}%")
        
        fig = create_spo2_chart(spo2_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(_t(tr, "info.no_spo2"))
    
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    
    # Stress
    st.markdown(f'<div class="section-header">{_t(tr, "section.stress")}</div>', unsafe_allow_html=True)
    
    display_note(_t(tr, "note.stress"))
    
    if not stress_df.empty:
        stress_data = stress_df[stress_df['STRESS_SCORE'] > 0]
        if not stress_data.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_stress = stress_data['STRESS_SCORE'].mean()
                st.metric(_t(tr, "metric.avg_stress"), f"{avg_stress:.0f}/100")
            with col2:
                if 'SLEEP_POINTS' in stress_data.columns:
                    avg_sleep_pts = stress_data['SLEEP_POINTS'].mean()
                    st.metric(_t(tr, "metric.sleep_points"), f"{avg_sleep_pts:.0f}")
            with col3:
                if 'EXERTION_POINTS' in stress_data.columns:
                    avg_exert = stress_data['EXERTION_POINTS'].mean()
                    st.metric(_t(tr, "metric.exertion_points"), f"{avg_exert:.0f}")
            
            fig = create_stress_chart(stress_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(_t(tr, "info.stress_invalid"))
    else:
        st.info(_t(tr, "info.no_stress"))
    
    # Pied de page
    st.markdown(f'''
    <div style="text-align: center; margin-top: 50px; padding: 25px; color: #666;
                border-top: 2px solid #eee; background: #f8f9fa; border-radius: 10px;">
        <p style="font-size: 1.1em; margin-bottom: 10px;"><b>{_t(tr, "footer.title")}</b></p>
        <p style="font-size: 0.9em; color: #888;">
            {_t(tr, "app.generated_on", datetime=datetime.now().strftime('%Y-%m-%d %H:%M'))}
        </p>
        <p style="font-size: 0.85em; color: #999; margin-top: 15px;">
            {_t(tr, "footer.disclaimer")}
        </p>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
