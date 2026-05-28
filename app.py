import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. 頁面基本設定
# ==========================================
st.set_page_config(page_title="Pillow Selection System", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 2. 終極美學、手機支援 CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');
    
    :root { --bg: #f8f9fa; --surface: #ffffff; --text: #1f2937; --primary: #2563eb; }
    .stApp { background-color: var(--bg) !important; color: var(--text); font-family: 'Inter', sans-serif; }
    .block-container { max-width: 1200px !important; padding: 2rem 1rem !important; }

    /* 系統說明文字 */
    .system-desc { font-size: 14px; color: #64748b; font-weight: 500; margin-bottom: 25px; line-height: 1.5; margin-top: 10px; }

    /* 控制面板標籤 */
    .control-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 5px; }
    
    /* Streamlit Slider (滑動條) 美化 */
    div[data-baseweb="slider"] { margin-top: 5px; padding-bottom: 5px; }
    div[data-baseweb="slider"] > div { background-color: #e2e8f0; }
    
    div[data-baseweb="slider"] [role="slider"] {
        background-color: var(--primary) !important; 
        border: 2px solid #ffffff !important;
        box-shadow: 0 0 0 5px rgba(37, 99, 235, 0.15) !important; 
        width: 20px !important; 
        height: 20px !important;
        transition: box-shadow 0.2s ease, transform 0.2s ease !important;
    }
    div[data-baseweb="slider"] [role="slider"]:hover {
        box-shadow: 0 0 0 8px rgba(37, 99, 235, 0.25) !important;
        cursor: grab !important;
    }
    div[data-testid="stThumbValue"] { display: none !important; } 
    
    /* 卡片設計 */
    .loft-head-box { text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; padding-top: 10px; }
    .loft-title { font-size: 36px; font-weight: 800; color: #0f172a; line-height: 1; }
    .loft-sub { font-size: 12px; font-weight: 600; color: #64748b; margin-top: 5px; }

    .custom-card { 
        background: #f8fafc; padding: 15px 10px; border-radius: 12px; text-align: center; 
        transition: all 0.3s ease; border: 2px solid #f1f5f9; height: 100%; 
        display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: default; 
    }
    .custom-card:hover { 
        transform: translateY(-4px); 
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); 
    }
    
    /* 卡片三色分區樣式 */
    .custom-card.zone-soft { background-color: #f0f9ff; border-color: #bae6fd; }
    .custom-card.zone-soft:hover { background-color: #e0f2fe; border-color: #7dd3fc; }
    
    .custom-card.zone-med { background-color: #fefce8; border-color: #fde047; }
    .custom-card.zone-med:hover { background-color: #fef08a; border-color: #facc15; }
    
    .custom-card.zone-firm { background-color: #fef2f2; border-color: #fecaca; }
    .custom-card.zone-firm:hover { background-color: #fee2e2; border-color: #fca5a5; }

    .custom-card.empty:hover { background-color: #f1f5f9 !important; }

    .badge { padding: 5px 14px; border-radius: 20px; font-size: 11px; font-weight: 800; color: white; text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.5px; }
    .badge.std { background: #3b82f6; }
    .badge.q { background: #f97316; }
    .badge.k { background: #10b981; }

    .oz-val { font-size: 28px; font-weight: 800; color: #0f172a; line-height: 1; }
    .oz-unit { font-size: 13px; color: #64748b; font-weight: 600; text-transform: uppercase; margin-left: 4px; position: relative; top: -2px;} 
    .no-data-text { font-size: 13px; color: #94a3b8; font-weight: 500; }

    /* 列印模式隱藏不必要的元素 */
    @media print {
        .controls-row, .system-desc { display: none !important; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        .custom-card { box-shadow: none; break-inside: avoid; border-width: 1px; }
        iframe { display: none !important; }
    }

    @media (max-width: 768px) {
        .block-container { padding-top: 1rem !important; }
        .loft-head-box { border-bottom: 2px solid #f1f5f9; margin-bottom: 15px; padding-top: 0; }
        .oz-val { font-size: 24px; }
        [data-testid="column"] { margin-bottom: 10px; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 頂部標題與 Print 按鈕
# ==========================================
col_title, col_print = st.columns([5, 1])
with col_title:
    st.markdown("<h1 style='font-size: 32px; font-weight: 800; color: #0f172a; margin: 0;'>Pillow Selection System</h1>", unsafe_allow_html=True)

with col_print:
    components.html(
        """
        <style>
            body { margin: 0; padding: 0; display: flex; justify-content: flex-end; align-items: center; height: 100%; }
            .print-btn { 
                background-color: #ffffff; border: 1px solid #cbd5e1; color: #475569; 
                padding: 8px 16px; border-radius: 8px; font-size: 14px; font-weight: 600; 
                cursor: pointer; transition: all 0.2s ease; display: flex; align-items: center; gap: 6px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05); font-family: -apple-system, sans-serif;
            }
            .print-btn:hover { background-color: #f1f5f9; color: #0f172a; border-color: #94a3b8; }
        </style>
        <button class="print-btn" onclick="window.parent.print()">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
            Print Report
        </button>
        """,
        height=45
    )

st.markdown("""
<div class="system-desc">
    Please set the target compression depth first. Adjust the target firmness force below. <b>You can also drag the horizontal dashed line directly on the chart</b> to use it as a weight reference.
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. 連接 Google Sheets
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1X-uD1yVdzgRpN_j0k0NPzjcWylgRyxZdPqdapG92fNk/edit?gid=0#gid=0"
    df = conn.read(spreadsheet=sheet_url, usecols=[0, 1, 2, 3, 4])
    return df

df = load_data()
df = df.dropna(how="all")
for col in ['Loft', 'Weight_Oz', 'Force_50_g', 'Force_33_g']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna(subset=['Weight_Oz', 'Force_50_g', 'Force_33_g'])

ALL_LOFTS = [600, 700, 750, 800, 850, 950]
ALL_SIZES_SHORT = ['Std', 'Q', 'K']
SIZE_FULL_NAMES = {'Std': 'Standard Size', 'Q': 'Queen Size', 'K': 'King Size'}

# ==========================================
# 4. 極簡控制面板 (只有 Depth 同 Force，絕無多餘 Slider)
# ==========================================
controls_container = st.container()

with controls_container:
    st.markdown('<div class="controls-row">', unsafe_allow_html=True)
    
    c_mode, c_f_slide, c_f_num = st.columns([1.5, 2.5, 1])
    
    with c_mode:
        st.markdown("<div class='control-label'>1. Compression Depth</div>", unsafe_allow_html=True)
        mode = st.radio("Mode", ['50% (Half of Pillow)', '33% (One-Third of Pillow)'], label_visibility="collapsed")

    if '50%' in mode:
        min_f, max_f, def_f, force_col = 1000, 3000, 2000, 'Force_50_g'
        z_soft, z_med, z_firm = [1000, 1500], [1500, 2500], [2500, 3000]
    else:
        min_f, max_f, def_f, force_col = 2000, 4000, 3000, 'Force_33_g'
        z_soft, z_med, z_firm = [2000, 2500], [2500, 3500], [3500, 4000]

    if "my_slider" not in st.session_state: st.session_state.my_slider = def_f
    if "my_num" not in st.session_state: st.session_state.my_num = def_f
    if st.session_state.my_slider < min_f or st.session_state.my_slider > max_f:
        st.session_state.my_slider = def_f
        st.session_state.my_num = def_f

    def update_from_slider(): st.session_state.my_num = st.session_state.my_slider
    def update_from_num(): st.session_state.my_slider = st.session_state.my_num

    with c_f_slide:
        st.markdown("<div class='control-label'>2. Target Firmness Force (X-Axis)</div>", unsafe_allow_html=True)
        st.slider("Force Slider", min_f, max_f, key="my_slider", step=1, on_change=update_from_slider, label_visibility="collapsed")
    with c_f_num:
        st.markdown("<div class='control-label' style='text-align:right;'>Force (g)</div>", unsafe_allow_html=True)
        st.number_input("Force Input", min_f, max_f, key="my_num", step=1, on_change=update_from_num, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

target_force = st.session_state.my_slider

# 判定卡片Zone
if target_force <= z_soft[1]: current_zone_class = "zone-soft"
elif target_force <= z_med[1]: current_zone_class = "zone-med"
else: current_zone_class = "zone-firm"

st.markdown("<hr style='border:none; border-top:1px solid #e2e8f0; margin: 15px 0 25px 0;'>", unsafe_allow_html=True)

# ==========================================
# 5. 超巨型圖表 (內置可拖動橫線)
# ==========================================
fig = go.Figure()

# 繪製背景顏色區塊 (加入 editable=False 防止被誤拉)
fig.add_vrect(x0=z_soft[0], x1=z_soft[1], fillcolor="#e0f2fe", opacity=0.6, layer="below", line_width=0, 
              annotation_text="<b>SOFT</b>", annotation_position="top left", annotation_font_color="#0369a1", annotation_font_size=13, editable=False)
fig.add_vrect(x0=z_med[0], x1=z_med[1], fillcolor="#fef08a", opacity=0.4, layer="below", line_width=0, 
              annotation_text="<b>MEDIUM</b>", annotation_position="top left", annotation_font_color="#a16207", annotation_font_size=13, editable=False)
fig.add_vrect(x0=z_firm[0], x1=z_firm[1], fillcolor="#fee2e2", opacity=0.6, layer="below", line_width=0, 
              annotation_text="<b>FIRM</b>", annotation_position="top left", annotation_font_color="#b91c1c", annotation_font_size=13, editable=False)

grid_data = {}

for loft in ALL_LOFTS:
    grid_data[loft] = {}
    for short_size in ALL_SIZES_SHORT:
        subset = df[(df['Loft'] == loft) & (df['Size'] == short_size)].sort_values(by='Weight_Oz')
        if len(subset) >= 2:
            m, c = np.polyfit(subset[force_col], subset['Weight_Oz'], 1)
            pred = m * target_force + c
            if pred > 0:
                grid_data[loft][short_size] = pred
                color = {'Std': '#3b82f6', 'Q': '#f97316', 'K': '#10b981'}[short_size]
                fig.add_trace(go.Scatter(x=[min_f, max_f], y=[m*min_f+c, m*max_f+c], mode='lines', name=f"{loft} {short_size}", line=dict(width=2, color=color)))
            else: grid_data[loft][short_size] = "Range Error"
        else: grid_data[loft][short_size] = "No Data"

fig.update_layout(
    height=700, # 圖表巨型化！
    margin=dict(t=10, b=40, l=40, r=10),
    plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=True, gridcolor='#f1f5f9', zeroline=False),
    yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
    legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center")
)

# 1. 直向力度紅線 (加入 editable=False 防止被誤拉)
fig.add_vline(x=target_force, line_dash="solid", line_color="#ef4444", line_width=2.5, editable=False)

# 2. 【魔法新功能】橫向重量虛線 (可以直接喺圖入面用 Mouse 拉上拉落！)
fig.add_shape(
    type="line", 
    xref="paper", x0=0, x1=1, 
    yref="y", y0=15, y1=15, 
    line=dict(color="#4b5563", width=2, dash="dash"),
    editable=True # 唯一允許被拖曳嘅圖形
)

# Plotly 互動設定：開啟圖形拖拉功能，但封鎖更改標題等操作
plot_config = {
    'displayModeBar': False,
    'editable': True,
    'edits': {
        'titleText': False,
        'axisTitleText': False,
        'annotationPosition': False,
        'annotationTail': False,
        'annotationText': False,
        'colorbarPosition': False,
        'colorbarTitleText': False,
        'legendPosition': False,
        'legendText': False,
        'shapePosition': True,
    }
}

st.plotly_chart(fig, width='stretch', config=plot_config)


# ==========================================
# 6. Grid 顯示區 
# ==========================================
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

for loft in ALL_LOFTS:
    with st.container():
        row_cols = st.columns([1, 3, 3, 3])
        
        with row_cols[0]:
            st.markdown(f"""
                <div class="loft-head-box">
                    <div class="loft-title">{loft}</div>
                    <div class="loft-sub">LOFT SERIES</div>
                </div>
            """, unsafe_allow_html=True)
            
        for idx, short_size in enumerate(ALL_SIZES_SHORT):
            result = grid_data[loft][short_size]
            badge_color_class = short_size.lower() 
            full_size_name = SIZE_FULL_NAMES[short_size] 
            
            with row_cols[idx + 1]:
                if isinstance(result, (int, float)):
                    st.markdown(f"""
                        <div class="custom-card {current_zone_class}">
                            <span class="badge {badge_color_class}">{full_size_name}</span>
                            <div style="display: flex; align-items: baseline; justify-content: center;">
                                <span class="oz-val" style="margin: 0; padding: 0; line-height: 1;">{result:.1f}</span>
                                <span class="oz-unit" style="margin: 0; padding: 0; line-height: 1;">oz</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="custom-card empty" style="border-style: dashed; background: transparent !important; border-color: #cbd5e1 !important;">
                            <span class="badge {badge_color_class}" style="opacity: 0.5;">{full_size_name}</span>
                            <div class="no-data-text" style="margin: 0; padding: 0;">{result}</div>
                        </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-bottom: 25px; border-bottom: 1px solid #f1f5f9;'></div>", unsafe_allow_html=True)
