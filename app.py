import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# 1. 頁面基本設定
st.set_page_config(page_title="Pillow Selection System", layout="wide", initial_sidebar_state="collapsed")

# 2. 原汁原味舊 HTML 核心樣式注入 (這次只專注卡片內部與全網頁背景，骨架交給 Streamlit)
st.markdown("""
<style>
    /* 全局背景與字體還原 */
    :root { --bg: #f8f9fa; --surface: #ffffff; --text: #1f2937; }
    .stApp { background-color: var(--bg) !important; color: var(--text); font-family: -apple-system, system-ui, sans-serif; }
    
    /* 調整 Streamlit 內建容器的間距，令畫面更緊湊 */
    .block-container { max-width: 1200px !important; padding-top: 1.5rem !important; }
    
    /* 橫向 Row 容器樣式 (比照原版 HTML 陰影與圓角) */
    .html-row-container {
        background: var(--surface);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        width: 100%;
    }
    
    /* 左邊 Loft 標題大字 */
    .loft-head-box {
        width: 100px;
        text-align: center;
        border-right: 2px solid #eee;
        padding-right: 15px;
        flex-shrink: 0;
    }
    .loft-title { font-size: 32px; font-weight: 900; line-height: 1; color: #333; margin: 0; }
    .loft-sub { font-size: 12px; font-weight: 600; color: #888; margin-top: 4px; text-transform: uppercase; }
    
    /* 每張獨立卡片的設計 (完全倒模舊 HTML 的內襯與外觀) */
    .custom-card { 
        background: #f9f9f9; 
        padding: 12px 10px; 
        border-radius: 8px; 
        text-align: center; 
        border: 1px solid transparent;
        width: 100%;
    }
    
    /* 無數據卡片樣式 */
    .custom-card.empty {
        background: transparent;
        border: 1px dashed #ccc;
        width: 100%;
    }
    
    /* 顏色標籤 Badge */
    .badge { 
        padding: 4px 12px; 
        border-radius: 99px; 
        font-size: 11px; 
        font-weight: 800; 
        color: white; 
        text-transform: uppercase; 
        margin-bottom: 8px; 
        display: inline-block; 
    }
    .badge.std { background: #0056b3 !important; }
    .badge.q { background: #d35400 !important; }
    .badge.k { background: #1e8449 !important; }
    
    /* 重量數字與單位 */
    .oz-val { font-size: 26px; font-weight: 800; color: #111; line-height: 1.1; margin-bottom: 2px; }
    .oz-unit { font-size: 12px; color: #666; font-weight: 600; text-transform: uppercase; }
    .no-data-text { font-size: 12px; color: #aaa; padding-top: 5px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# 頂部標題
st.markdown("<h1 style='font-size: 24px; font-weight: 800; color: #1f2937; margin-bottom: 25px;'>Pillow Selection</h1>", unsafe_allow_html=True)

# 3. 連接 Google Sheets 及數據清洗
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1X-uD1yVdzgRpN_j0k0NPzjcWylgRyxZdPqdapG92fNk/edit?gid=0#gid=0"
    df = conn.read(spreadsheet=sheet_url, usecols=[0, 1, 2, 3, 4])
    return df

df = load_data()
df = df.dropna(how="all")
cols_to_convert = ['Loft', 'Weight_Oz', 'Force_50_g', 'Force_33_g']
for col in cols_to_convert:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna(subset=['Weight_Oz', 'Force_50_g', 'Force_33_g'])

ALL_LOFTS = [600, 700, 750, 800, 850, 950]
ALL_SIZES = ['Std', 'Q', 'K']

# 4. 控制面板 (新版 Streamlit 唯一標準：獨立 Key + 雙向 Callback 同步)

# 用 Streamlit Columns 做外層骨架，比例設定為 2 : 4 : 2
col1, col2, col3 = st.columns([2, 4, 2], gap="large")

with col1:
    st.markdown("<span style='font-size: 11px; font-weight: 700; color: #999; text-transform: uppercase; letter-spacing: 0.5px;'>Target Firmness At</span>", unsafe_allow_html=True)
    mode = st.radio("", ['50%', '33%'], horizontal=True, label_visibility="collapsed")

# 根據 50% 或 33% 決定 min, max 同埋 default 數值
if '50%' in mode:
    min_f, max_f, default_f = 1000, 3000, 2000
    force_col = 'Force_50_g'
else:
    min_f, max_f, default_f = 2000, 4000, 3000
    force_col = 'Force_33_g'

# --- 核心同步大腦初始化 ---
if "current_force" not in st.session_state:
    st.session_state.current_force = default_f

# 如果切換模式導致數值超界，即時重設
if st.session_state.current_force < min_f or st.session_state.current_force > max_f:
    st.session_state.current_force = default_f

st.session_state.current_force = max(min_f, min(st.session_state.current_force, max_f))

# 事先將全域數值塞入各自的組件暫存區
st.session_state.slider_f = st.session_state.current_force
st.session_state.num_f = st.session_state.current_force

# 定義雙向同步 Callback
def sync_slider():
    st.session_state.current_force = st.session_state.slider_f

def sync_num():
    st.session_state.current_force = st.session_state.num_f
# --- 同步大腦結束 ---


with col2:
    st.markdown("<div style='text-align: center;'><span style='font-size: 11px; font-weight: 700; color: #999; text-transform: uppercase; letter-spacing: 0.5px;'>Target Firmness</span></div>", unsafe_allow_html=True)
    # 使用獨立 Key "slider_f"，並綁定 on_change 函數
    st.slider(
        "", 
        min_value=min_f, 
        max_value=max_f, 
        key="slider_f", 
        step=50,
        on_change=sync_slider,
        label_visibility="collapsed"
    )

with col3:
    st.markdown("<div style='text-align: right;'><span style='font-size: 11px; font-weight: 700; color: #999; text-transform: uppercase; letter-spacing: 0.5px;'>Current Force</span></div>", unsafe_allow_html=True)
    # 使用獨立 Key "num_f"，並綁定 on_change 函數
    st.number_input(
        "", 
        min_value=min_f, 
        max_value=max_f, 
        key="num_f", 
        step=50,
        on_change=sync_num,
        label_visibility="collapsed"
    )
    st.markdown("<div style='font-size: 11px; color: #888; font-weight: 600; margin-top: 2px; text-align: right; text-transform: uppercase; letter-spacing: 0.5px;'>FORCE UNIT</div>", unsafe_allow_html=True)

# 最終將徹底同步的數值交給下方的圖表與運算系統
target_force = st.session_state.current_force

st.markdown("<br>", unsafe_allow_html=True)

# 5. 核心運算與圖表
fig = go.Figure()
grid_data = {}

for loft in ALL_LOFTS:
    grid_data[loft] = {}
    for size in ALL_SIZES:
        subset = df[(df['Loft'] == loft) & (df['Size'] == size)].sort_values(by='Weight_Oz')
        
        if len(subset) >= 2:
            x_forces = subset[force_col].astype(float).values
            y_weights = subset['Weight_Oz'].astype(float).values
            
            m, c = np.polyfit(x_forces, y_weights, 1) 
            predicted_weight = m * target_force + c
            
            if predicted_weight > 0:
                grid_data[loft][size] = predicted_weight
                
                color_map = {'Std': '#0056b3', 'Q': '#d35400', 'K': '#1e8449'}
                line_color = color_map.get(size, '#333')
                
                trend_x = np.array([min_f, max_f])
                trend_y = m * trend_x + c
                
                fig.add_trace(go.Scatter(
                    x=trend_x, y=trend_y, mode='lines',
                    name=f"{loft} {size}",
                    line=dict(width=3, color=line_color),
                ))
            else:
                 grid_data[loft][size] = "Out of Range"
        else:
            grid_data[loft][size] = "No Data"

fig.update_layout(
    xaxis_title="Force (grams)",
    yaxis_title="Weight (oz)",
    height=400,
    plot_bgcolor='white',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=True, gridcolor='#eee', zeroline=False, range=[min_f, max_f]),
    yaxis=dict(showgrid=True, gridcolor='#eee'),
    margin=dict(t=20, b=40, l=40, r=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
fig.add_vline(x=target_force, line_dash="dash", line_color="red", line_width=1.5)

# 圖表外層白色容器
st.markdown("<div style='background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 30px;'>", unsafe_allow_html=True)
st.plotly_chart(fig, width='stretch')
st.markdown("</div>", unsafe_allow_html=True)


# 6. Grid 顯示區 (Streamlit 骨架 + 原生 HTML 卡片完美的混合體！)
# 採用 [1, 3, 3, 3] 比例：Loft佔1格，Std, Q, K 各霸佔相等的三格，保證完美對齊並100%填滿！
for loft in ALL_LOFTS:
    row_cols = st.columns([1, 3, 3, 3], gap="medium")
    
    # 第一欄：放入左邊的 Loft 標題大字
    with row_cols[0]:
        st.markdown(f"""
        <div class="loft-head-box" style="border-right: none; width: 100%;">
            <div class="loft-title">{loft}</div>
            <div class="loft-sub">LOFT</div>
        </div>
        """, unsafe_allow_html=True)
        
    # 第二、三、四欄：平分剩餘空間，各自放入對應的卡片
    for idx, size in enumerate(ALL_SIZES):
        result = grid_data[loft][size]
        badge_class = size.lower()
        
        with row_cols[idx + 1]:
            if type(result) != str:
                # 倒模原版 HTML卡片
                st.markdown(f"""
                <div class="custom-card">
                    <span class="badge {badge_class}">{size}</span>
                    <div class="oz-val">{result:.1f}</div>
                    <div class="oz-unit">oz</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # 倒模原版 虛線卡片
                st.markdown(f"""
                <div class="custom-card empty">
                    <span class="badge {badge_class}">{size}</span>
                    <div class="no-data-text">{result}</div>
                </div>
                """, unsafe_allow_html=True)
                
    # 每一行結束後，加一條淡淡的底線（可自由選擇留不留，用來做視覺區隔）
    st.markdown("<hr style='border:none; border-top:1px solid #eee; margin:10px 0 15px 0;'>", unsafe_allow_html=True)