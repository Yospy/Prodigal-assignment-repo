import plotly.graph_objects as go
import plotly.express as px
from typing import Tuple

def create_acoustic_pie_chart(overtalk_pct: float, silence_pct: float) -> go.Figure:
    
    labels = ['Overtalk', 'Silence']
    values = [overtalk_pct, silence_pct]
    colors = ['#FF6B6B', '#95A5A6'] # red for overtalk, gray for silence
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,  
        hole=0.3,  # pie chart
        marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)),
        textinfo='label+percent',
        textposition='auto',
        hovertemplate='<b>%{label}</b><br>' +
                      'Percentage: %{percent}<br>' +
                      'Value: %{value:.1f}%<br>' +
                      '<extra></extra>'
    )])
    
    fig.update_layout(
        title={
            'text': 'Call Quality Metrics',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2C3E50'}
        },
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=60, b=40, l=40, r=40),
        height=400,
        font=dict(size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def format_acoustic_metrics_display(overtalk_pct: float, silence_pct: float) -> Tuple[str, str]:

    overtalk_text = f"🔴 **Overtalk**: {overtalk_pct:.1f}%"
    silence_text = f"⚪ **Silence**: {silence_pct:.1f}%"
    
    return overtalk_text, silence_text

def get_acoustic_insights(overtalk_pct: float, silence_pct: float) -> str:

    insights = []
    
    if overtalk_pct > 15:
        insights.append("⚠️ **High overtalk** detected - speakers frequently interrupt each other")
    elif overtalk_pct > 8:
        insights.append("📊 **Moderate overtalk** - some interruptions present")
    else:
        insights.append("✅ **Low overtalk** - good conversation flow")
    
    if silence_pct > 20:
        insights.append("🤐 **High silence** - long pauses may indicate disengagement")
    elif silence_pct > 10:
        insights.append("⏸️ **Moderate silence** - some awkward pauses")
    else:
        insights.append("💬 **Active conversation** - minimal awkward silences")
    
    return " | ".join(insights)