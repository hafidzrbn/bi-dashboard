"""
streamlit_app.py — Dashboard Business Intelligence (Streamlit Version)
Remedial UAS BI | Universitas Islam Indonesia
Tech Stack: Python + Streamlit + Plotly
Deploy Target: Streamlit Community Cloud
Converted from: app.py (Dash version — final)
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

st.set_page_config(
    page_title="ShopInsight - E-Commerce Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    for name in ['df_dashboard.csv', 'df_clean.csv']:
        path = os.path.join(base, name)
        if os.path.exists(path):
            df = pd.read_csv(path, encoding='utf-8-sig')
            break
    else:
        st.error("File df_dashboard.csv atau df_clean.csv tidak ditemukan!")
        st.stop()
    df['Date'] = pd.to_datetime(df['Date'])
    df['TransactionNo'] = df['TransactionNo'].astype(str)
    df['CustomerNo'] = df['CustomerNo'].astype(str)
    df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce').fillna(0)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
    if 'YearMonth' not in df.columns:
        df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)
    return df

df = load_data()

PRODUCT_GROUPS = ['Very Frequently Purchased','Frequently Purchased','Moderately Purchased','Rarely Purchased','Very Rarely Purchased']
CUSTOMER_SEGMENTS = ['Loyal','Active','Occasional','Inactive']
COUNTRY_GROUPS = ['Transaksi Tinggi','Transaksi Sedang','Transaksi Rendah']
COLOR_PRODUCT = {'Very Frequently Purchased':'#10b981','Frequently Purchased':'#0ea5e9','Moderately Purchased':'#f59e0b','Rarely Purchased':'#fb923c','Very Rarely Purchased':'#f43f5e'}
COLOR_SEGMENT = {'Loyal':'#10b981','Active':'#0ea5e9','Occasional':'#f59e0b','Inactive':'#f43f5e'}
COLOR_COUNTRY = {'Transaksi Tinggi':'#10b981','Transaksi Sedang':'#f59e0b','Transaksi Rendah':'#f43f5e'}

BASE_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter, sans-serif', color='#94a3b8', size=12),
    title_font=dict(family='Inter, sans-serif', color='#f1f5f9', size=15),
    xaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.06)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.06)'),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(font=dict(size=11, color='#94a3b8')),
    hoverlabel=dict(bgcolor='#1e2235', bordercolor='#6366f1',
                    font=dict(family='Inter, sans-serif', size=13, color='#f1f5f9')),
    height=400,
)

def apply_layout(fig, **kw):
    fig.update_layout(**{**BASE_LAYOUT, **kw})
    return fig

def fmt(n, prefix='', decimals=0):
    if n >= 1_000_000: return f"{prefix}{n/1_000_000:,.{decimals}f}M"
    if n >= 1_000: return f"{prefix}{n/1_000:,.{decimals}f}K"
    return f"{prefix}{n:,.{decimals}f}"

def fdf(df_src, pg, cs, cg):
    dff = df_src.copy()
    if pg and pg != 'All': dff = dff[dff['Product_Group'] == pg]
    if cs and cs != 'All': dff = dff[dff['Customer_Segment'] == cs]
    if cg and cg != 'All': dff = dff[dff['Country_Group'] == cg]
    return dff

def show_chart(title, subtitle, fig, badge=None):
    badge_html = f'<span class="chart-badge">{badge}</span>' if badge else ''
    st.markdown(f'<div class="chart-header"><div><div class="chart-title">{title}</div><div class="chart-subtitle">{subtitle}</div></div>{badge_html}</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

# === CSS ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
.stApp{font-family:'Inter',sans-serif}
section[data-testid="stSidebar"]{background:#141728;border-right:1px solid rgba(255,255,255,0.06)}
section[data-testid="stSidebar"] .stRadio>label{display:none}
section[data-testid="stSidebar"] .stRadio>div{gap:4px}
section[data-testid="stSidebar"] .stRadio>div>label{background:transparent;border:1px solid transparent;border-radius:10px;padding:10px 14px;color:#94a3b8;font-size:14px;font-weight:500;cursor:pointer;transition:all .25s ease;margin:0}
section[data-testid="stSidebar"] .stRadio>div>label:hover{background:rgba(255,255,255,0.04);border-color:rgba(255,255,255,0.06);color:#f1f5f9}
section[data-testid="stSidebar"] .stRadio>div>label[data-checked="true"],section[data-testid="stSidebar"] .stRadio>div>label[aria-checked="true"]{background:rgba(99,102,241,0.15);border-color:rgba(99,102,241,0.3);color:#f1f5f9}
.sidebar-logo{display:flex;align-items:center;gap:12px;padding-bottom:16px;margin-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.06)}
.sidebar-logo-icon{width:42px;height:42px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800;color:white;box-shadow:0 4px 15px rgba(99,102,241,0.3)}
.sidebar-logo-text{font-size:18px;font-weight:700;color:#f1f5f9}
.sidebar-logo-sub{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.5px}
.sidebar-stat{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:13px}
.sidebar-stat-label{color:#64748b}
.sidebar-stat-value{color:#f1f5f9;font-weight:600}
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
.kpi-card{background:#1e2235;border:1px solid rgba(255,255,255,0.05);border-radius:14px;padding:20px;position:relative;overflow:hidden;transition:all .25s ease;box-shadow:0 4px 20px rgba(0,0,0,0.2),0 0 0 1px rgba(255,255,255,0.05)}
.kpi-card:hover{transform:translateY(-3px);border-color:rgba(99,102,241,0.4);box-shadow:0 4px 20px rgba(0,0,0,0.2),0 0 20px rgba(99,102,241,0.15)}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:14px 14px 0 0}
.kpi-card.c1::before{background:linear-gradient(90deg,#6366f1,#8b5cf6)}
.kpi-card.c2::before{background:linear-gradient(90deg,#10b981,#34d399)}
.kpi-card.c3::before{background:linear-gradient(90deg,#0ea5e9,#38bdf8)}
.kpi-card.c4::before{background:linear-gradient(90deg,#f59e0b,#fbbf24)}
.kpi-icon{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;margin-bottom:12px}
.kpi-icon.c1{background:rgba(99,102,241,0.15)}.kpi-icon.c2{background:rgba(16,185,129,0.15)}.kpi-icon.c3{background:rgba(14,165,233,0.15)}.kpi-icon.c4{background:rgba(245,158,11,0.15)}
.kpi-label{font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px}
.kpi-value{font-size:26px;font-weight:800;color:#f1f5f9;letter-spacing:-.5px}
.chart-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.04)}
.chart-title{font-size:15px;font-weight:700;color:#f1f5f9}
.chart-subtitle{font-size:12px;color:#64748b;margin-top:2px}
.chart-badge{font-size:11px;font-weight:600;padding:4px 10px;border-radius:9999px;background:rgba(99,102,241,0.15);color:#818cf8}
.section-title{font-size:16px;font-weight:700;color:#f1f5f9;margin:24px 0 12px 0;display:flex;align-items:center;gap:8px}
.section-title::before{content:'';width:4px;height:20px;background:linear-gradient(to bottom,#6366f1,#8b5cf6);border-radius:9999px}
.styled-table{width:100%;border-collapse:collapse;font-family:'Inter',sans-serif;font-size:13px}
.styled-table th{background:#1a1d2e;color:#94a3b8;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.5px;padding:12px 16px;border-bottom:1px solid rgba(255,255,255,0.1);text-align:left}
.styled-table td{background:#1e2235;color:#f1f5f9;padding:10px 16px;border-bottom:1px solid rgba(255,255,255,0.04)}
.styled-table tr:nth-child(even) td{background:#222640}
.footer{text-align:center;padding:24px 0;margin-top:48px;border-top:1px solid rgba(255,255,255,0.05);font-size:12px;color:#64748b}
#MainMenu,header,footer{visibility:hidden}
.stDeployButton{display:none}
div[data-baseweb="select"]>div{background-color:#1e2235 !important}
@media(max-width:768px){.kpi-row{grid-template-columns:repeat(2,1fr)}}
</style>
""", unsafe_allow_html=True)

# === SIDEBAR ===
with st.sidebar:
    st.markdown('<div class="sidebar-logo"><div class="sidebar-logo-icon">📈</div><div><div class="sidebar-logo-text">ShopInsight</div><div class="sidebar-logo-sub">E-Commerce Analytics</div></div></div>', unsafe_allow_html=True)
    st.markdown("##### MENU")
    page = st.radio("nav", options=['overview','product','customer','geo'],
        format_func=lambda x: {'overview':'📊  Overview','product':'📦  Analisis Produk','customer':'👥  Analisis Pelanggan','geo':'🌍  Analisis Geografis'}[x],
        label_visibility="collapsed")
    st.markdown("---")
    st.markdown("##### DATASET")
    for label, value in {
        'Periode': f"{df['Date'].min().strftime('%b %Y')} — {df['Date'].max().strftime('%b %Y')}",
        'Transaksi': f"{df['TransactionNo'].nunique():,}",
        'Produk': f"{df['ProductName'].nunique():,}",
        'Pelanggan': f"{df['CustomerNo'].nunique():,}",
        'Negara': f"{df['Country'].nunique()}",
    }.items():
        st.markdown(f'<div class="sidebar-stat"><span class="sidebar-stat-label">{label}</span><span class="sidebar-stat-value">{value}</span></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="footer">Remedial UAS Business Intelligence<br>Universitas Islam Indonesia</div>', unsafe_allow_html=True)

# === HEADER & FILTERS (single-select) ===
st.markdown("## E-Commerce Business Intelligence Dashboard")
st.caption("Analisis strategis transaksi penjualan, segmentasi produk & pelanggan, dan distribusi geografis.")
fc1, fc2, fc3 = st.columns(3)
with fc1:
    sel_pg = st.selectbox("Kelompok Produk", ['All'] + [g for g in PRODUCT_GROUPS if g in df['Product_Group'].unique()], format_func=lambda x: 'Semua Kelompok' if x=='All' else x)
with fc2:
    sel_cs = st.selectbox("Segmen Pelanggan", ['All'] + [s for s in CUSTOMER_SEGMENTS if s in df['Customer_Segment'].unique()], format_func=lambda x: 'Semua Segmen' if x=='All' else x)
with fc3:
    sel_cg = st.selectbox("Kelompok Negara", ['All'] + [g for g in COUNTRY_GROUPS if g in df['Country_Group'].unique()], format_func=lambda x: 'Semua Negara' if x=='All' else x)

dff = fdf(df, sel_pg, sel_cs, sel_cg)

# === KPI ===
total_rev = dff['Revenue'].sum()
total_trx = dff['TransactionNo'].nunique()
total_cust = dff['CustomerNo'].nunique()
aov = total_rev / total_trx if total_trx > 0 else 0
st.markdown(f'''<div class="kpi-row">
<div class="kpi-card c1"><div class="kpi-icon c1">£</div><div class="kpi-label">Total Revenue</div><div class="kpi-value">{fmt(total_rev,"£",1)}</div></div>
<div class="kpi-card c2"><div class="kpi-icon c2">🛒</div><div class="kpi-label">Total Transaksi</div><div class="kpi-value">{fmt(total_trx)}</div></div>
<div class="kpi-card c3"><div class="kpi-icon c3">👥</div><div class="kpi-label">Total Pelanggan</div><div class="kpi-value">{fmt(total_cust)}</div></div>
<div class="kpi-card c4"><div class="kpi-icon c4">📈</div><div class="kpi-label">Avg Order Value</div><div class="kpi-value">£{aov:,.2f}</div></div>
</div>''', unsafe_allow_html=True)

# === PAGES ===
def page_overview():
    monthly = dff.groupby('YearMonth').agg(Revenue=('Revenue','sum'), Transaksi=('TransactionNo','nunique')).reset_index().sort_values('YearMonth')
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=monthly['YearMonth'], y=monthly['Revenue'], mode='lines+markers', line=dict(color='#6366f1', width=4, shape='spline'), marker=dict(size=3), fill='tozeroy', fillcolor='rgba(99,102,241,0.1)', hovertemplate='<b>%{x}</b><br>Revenue: £%{y:,.0f}<extra></extra>'))
    apply_layout(fig1, title='Tren Revenue Bulanan', xaxis_title='Bulan', yaxis_title='Revenue (£)', hovermode='x unified')
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=monthly['YearMonth'], y=monthly['Transaksi'], marker=dict(color='#0ea5e9', line=dict(width=2, color='rgba(255,255,255,0)'), cornerradius=8), opacity=0.9, hovertemplate='<b style="font-size:14px;color:#fff">%{x}</b><br><b>Volume Transaksi:</b> %{y:,} transaksi<extra></extra>'))
    apply_layout(fig2, title='Jumlah Transaksi per Bulan', xaxis_title='Bulan', yaxis_title='Jumlah Transaksi')
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    daily = dff.groupby('DayName')['TransactionNo'].nunique().reindex(day_order).reset_index(); daily.columns = ['Day','Count']
    peak = daily.loc[daily['Count'].idxmax(), 'Day']
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=daily['Day'], y=daily['Count'], marker=dict(color=['#6366f1' if d==peak else '#334155' for d in daily['Day']], line=dict(width=2, color='rgba(255,255,255,0)'), cornerradius=8), opacity=0.9, hovertemplate='<b style="font-size:14px;color:#fff">%{x}</b><br><b>Jumlah Transaksi:</b> %{y:,}<extra></extra>'))
    apply_layout(fig3, title='Distribusi Transaksi per Hari', xaxis_title='Hari', yaxis_title='Jumlah Transaksi')
    s_order = ['Spring','Summer','Autumn','Winter']; s_col = {'Spring':'#10b981','Summer':'#f59e0b','Autumn':'#fb923c','Winter':'#0ea5e9'}
    seasonal = dff.groupby('Season')['Revenue'].sum().reindex(s_order).reset_index()
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=seasonal['Season'], y=seasonal['Revenue'], marker=dict(color=[s_col.get(s,'#6366f1') for s in seasonal['Season']], line=dict(width=2, color='rgba(255,255,255,0)'), cornerradius=8), opacity=0.9, hovertemplate='<b style="font-size:14px;color:#fff">%{x}</b><br><b>Total Revenue:</b> £%{y:,.0f}<extra></extra>'))
    apply_layout(fig4, title='Revenue per Musim', xaxis_title='Musim', yaxis_title='Revenue (£)')
    st.markdown('<div class="section-title">Tren Penjualan</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1: show_chart('Tren Revenue Bulanan','Pendapatan total per bulan',fig1,'Time Series')
    with c2: show_chart('Jumlah Transaksi per Bulan','Volume transaksi bulanan',fig2,'Bar Chart')
    st.markdown('<div class="section-title">Pola Waktu</div>', unsafe_allow_html=True)
    c3,c4 = st.columns(2)
    with c3: show_chart('Distribusi Transaksi per Hari',f'Hari dengan transaksi tertinggi: {peak}',fig3)
    with c4: show_chart('Revenue per Musim','Perbandingan revenue antar musim',fig4)

def page_product():
    top10 = dff.groupby('ProductName')['Quantity'].sum().nlargest(10).reset_index().sort_values('Quantity')
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(y=top10['ProductName'].str[:35], x=top10['Quantity'], orientation='h', marker=dict(color='#6366f1', line=dict(width=2, color='rgba(255,255,255,0)'), cornerradius=8), opacity=0.9, hovertemplate='<b style="font-size:14px;color:#fff">%{y}</b><br><b>Total Quantity:</b> %{x:,} unit<extra></extra>'))
    apply_layout(fig1, title='Produk dengan Penjualan Tertinggi', xaxis_title='Total Quantity', yaxis_title='')
    fig2 = go.Figure()
    if 'Product_Group' in dff.columns:
        pg = dff.groupby('Product_Group')['Revenue'].sum().reindex(PRODUCT_GROUPS).dropna().reset_index()
        fig2.add_trace(go.Pie(labels=pg['Product_Group'], values=pg['Revenue'], marker=dict(colors=[COLOR_PRODUCT.get(g,'#6366f1') for g in pg['Product_Group']], line=dict(color='#1e2235', width=2)), hole=0.55, textinfo='percent+label', textposition='outside', textfont_size=11, hovertemplate='<b style="font-size:14px">%{label}</b><br><b>Revenue:</b> £%{value:,.0f}<br>%{percent}<extra></extra>'))
    apply_layout(fig2, title='Proporsi Revenue per Kelompok Produk', showlegend=False)
    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(x=dff['Price'], nbinsx=50, marker=dict(color='#6366f1', line=dict(width=1, color='rgba(255,255,255,0.2)'), cornerradius=4), opacity=0.85, hovertemplate='<b>Harga Range:</b> £%{x:.2f}<br><b>Frekuensi:</b> %{y:,} produk<extra></extra>'))
    apply_layout(fig3, title='Distribusi Harga Produk', xaxis_title='Harga (£)', yaxis_title='Frekuensi')
    qt = dff.groupby('TransactionNo')['Quantity'].sum().reset_index(); p99 = qt['Quantity'].quantile(0.99)
    fig4 = go.Figure()
    fig4.add_trace(go.Histogram(x=qt[qt['Quantity']<=p99]['Quantity'], nbinsx=50, marker=dict(color='#0ea5e9', line=dict(width=1, color='rgba(255,255,255,0.2)'), cornerradius=4), opacity=0.85, hovertemplate='<b>Quantity Range:</b> %{x:,.0f} unit<br><b>Frekuensi:</b> %{y:,} transaksi<extra></extra>'))
    apply_layout(fig4, title='Distribusi Quantity per Transaksi', xaxis_title='Total Quantity', yaxis_title='Frekuensi')
    st.markdown('<div class="section-title">Produk Terlaris</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1: show_chart('Produk dengan Penjualan Tertinggi','Berdasarkan total jumlah unit terjual',fig1,'Ranking')
    with c2: show_chart('Proporsi Revenue per Kelompok','Kategori: Very Freq → Very Rare',fig2,'Donut')
    st.markdown('<div class="section-title">Distribusi</div>', unsafe_allow_html=True)
    c3,c4 = st.columns(2)
    with c3: show_chart('Distribusi Harga Produk','Histogram harga per unit (£)',fig3)
    with c4: show_chart('Distribusi Quantity per Transaksi','Histogram jumlah item per transaksi',fig4)

def page_customer():
    fig1 = go.Figure()
    if 'Customer_Segment' in dff.columns:
        seg = dff.groupby('Customer_Segment')['CustomerNo'].nunique().reindex(CUSTOMER_SEGMENTS).dropna().reset_index(); seg.columns = ['Segment','Count']
        fig1.add_trace(go.Bar(x=seg['Segment'], y=seg['Count'], marker=dict(color=[COLOR_SEGMENT.get(s,'#6366f1') for s in seg['Segment']], line=dict(width=2, color='rgba(255,255,255,0)'), cornerradius=8), opacity=0.9, hovertemplate='<b style="font-size:14px;color:#fff">%{x}</b><br><b>Total Pelanggan:</b> %{y:,} orang<extra></extra>'))
    apply_layout(fig1, title='Jumlah Pelanggan per Segmen', xaxis_title='Segmen', yaxis_title='Jumlah Pelanggan')
    fig2 = go.Figure()
    if 'Customer_Segment' in dff.columns:
        sr = dff.groupby('Customer_Segment')['Revenue'].sum().reindex(CUSTOMER_SEGMENTS).dropna().reset_index()
        fig2.add_trace(go.Pie(labels=sr['Customer_Segment'], values=sr['Revenue'], marker=dict(colors=[COLOR_SEGMENT.get(s,'#6366f1') for s in sr['Customer_Segment']], line=dict(color='#1e2235', width=2)), hole=0.55, textinfo='percent+label', textposition='outside', textfont_size=11, hovertemplate='<b style="font-size:14px">%{label}</b><br><b>Revenue:</b> £%{value:,.0f}<br>%{percent}<extra></extra>'))
    apply_layout(fig2, title='Proporsi Revenue per Segmen', showlegend=False)
    fig3 = go.Figure()
    if 'Customer_Segment' in dff.columns:
        ca = dff.groupby(['CustomerNo','Customer_Segment']).agg(Frequency=('TransactionNo','nunique'), Monetary=('Revenue','sum')).reset_index()
        if len(ca) > 2000: ca = ca.sample(n=2000, random_state=42)
        for s in CUSTOMER_SEGMENTS:
            sub = ca[ca['Customer_Segment']==s]
            if len(sub)==0: continue
            fig3.add_trace(go.Scattergl(x=sub['Frequency'], y=sub['Monetary'], mode='markers', name=s, marker=dict(color=COLOR_SEGMENT.get(s), size=8, opacity=0.7, line=dict(width=1, color='white')), hovertemplate=f'<b style="font-size:14px;color:#fff">{s}</b><br><b>Frequency:</b> %{{x}} kali<br><b>Revenue:</b> £%{{y:,.0f}}<extra></extra>'))
    apply_layout(fig3, title='Segmentasi: Frequency vs Revenue', xaxis_title='Frequency (Jumlah Transaksi)', yaxis_title='Total Revenue (£)', height=480)
    tc = dff.groupby('CustomerNo').agg(Revenue=('Revenue','sum')).nlargest(10,'Revenue').reset_index().sort_values('Revenue')
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(y=tc['CustomerNo'], x=tc['Revenue'], orientation='h', marker=dict(color='#8b5cf6', line=dict(width=2, color='rgba(255,255,255,0)'), cornerradius=8), text=[f'£{r:,.0f}' for r in tc['Revenue']], textposition='outside', textfont_size=10, opacity=0.9, hovertemplate='<b style="font-size:14px;color:#fff">Customer ID: %{y}</b><br><b>Total Revenue:</b> £%{x:,.0f}<extra></extra>'))
    apply_layout(fig4, title='Pelanggan dengan Revenue Tertinggi', xaxis_title='Revenue (£)', yaxis_title='')
    st.markdown('<div class="section-title">Segmentasi Pelanggan</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1: show_chart('Jumlah Pelanggan per Segmen','Kategori: Loyal → Inactive',fig1,'Segmentasi')
    with c2: show_chart('Proporsi Revenue per Segmen','Kontribusi revenue tiap segmen',fig2,'Donut')
    st.markdown('<div class="section-title">Detail Pelanggan</div>', unsafe_allow_html=True)
    show_chart('Segmentasi: Frequency vs Revenue','Pemetaan kontribusi pelanggan berdasarkan intensitas transaksi',fig3)
    show_chart('Pelanggan dengan Revenue Tertinggi','Berdasarkan total revenue yang dihasilkan',fig4,'Ranking')

def page_geo():
    country_iso = {'United Kingdom':'GBR','Germany':'DEU','France':'FRA','Spain':'ESP','Belgium':'BEL','Switzerland':'CHE','Portugal':'PRT','Italy':'ITA','Finland':'FIN','Austria':'AUT','Norway':'NOR','Denmark':'DNK','Netherlands':'NLD','Australia':'AUS','Sweden':'SWE','Japan':'JPN','Channel Islands':'GBR','Poland':'POL','Ireland':'IRL','Iceland':'ISL','Singapore':'SGP','Czech Republic':'CZE','Greece':'GRC','Israel':'ISR','Lithuania':'LTU','United Arab Emirates':'ARE','Cyprus':'CYP','Canada':'CAN','USA':'USA','Brazil':'BRA','Malta':'MLT','Bahrain':'BHR','RSA':'ZAF','Saudi Arabia':'SAU','Lebanon':'LBN','EIRE':'IRL','European Community':'FRA','Unspecified':None}
    md = dff.groupby('Country').agg(Transaksi=('TransactionNo','nunique'), Revenue=('Revenue','sum')).reset_index()
    md['ISO'] = md['Country'].map(country_iso); md = md.dropna(subset=['ISO'])
    fig_map = go.Figure()
    fig_map.add_trace(go.Choropleth(locations=md['ISO'], z=md['Transaksi'], text=md['Country'], colorscale='YlOrRd', colorbar_title='Transaksi', hovertemplate='<b>%{text}</b><br>Transaksi: %{z:,}<extra></extra>'))
    apply_layout(fig_map, title='Peta Distribusi Transaksi per Negara', height=480, geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth', bgcolor='rgba(0,0,0,0)', landcolor='#1a1d2e', coastlinecolor='rgba(255,255,255,0.15)'))
    ct = dff.groupby(['Country','Country_Group'])['TransactionNo'].nunique().reset_index().rename(columns={'TransactionNo':'Transaksi'}).sort_values('Transaksi',ascending=False).head(15).sort_values('Transaksi')
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(y=ct['Country'], x=ct['Transaksi'], orientation='h', marker=dict(color=[COLOR_COUNTRY.get(g,'#6366f1') for g in ct['Country_Group']], line=dict(width=2, color='rgba(255,255,255,0)'), cornerradius=8), opacity=0.9, hovertemplate='<b style="font-size:14px;color:#fff">%{y}</b><br><b>Total Transaksi:</b> %{x:,} transaksi<extra></extra>'))
    apply_layout(fig_bar, title='Negara dengan Transaksi Tertinggi', xaxis_title='Jumlah Transaksi', yaxis_title='', height=480)
    fig_pie = go.Figure()
    if 'Country_Group' in dff.columns:
        cg = dff.groupby('Country_Group')['Revenue'].sum().reindex(COUNTRY_GROUPS).dropna().reset_index()
        fig_pie.add_trace(go.Pie(labels=cg['Country_Group'], values=cg['Revenue'], marker=dict(colors=[COLOR_COUNTRY.get(g,'#6366f1') for g in cg['Country_Group']], line=dict(color='#1e2235', width=2)), hole=0.55, textinfo='percent+label', textposition='outside', textfont_size=11, hovertemplate='<b style="font-size:14px">%{label}</b><br><b>Revenue:</b> £%{value:,.0f}<br>%{percent}<extra></extra>'))
    apply_layout(fig_pie, title='Proporsi Revenue per Kelompok Negara', showlegend=False)
    st.markdown('<div class="section-title">Peta Global</div>', unsafe_allow_html=True)
    show_chart('Peta Distribusi Transaksi Global','Sebaran transaksi berdasarkan lokasi pelanggan',fig_map,'Map')
    st.markdown('<div class="section-title">Perbandingan Negara</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1: show_chart('Negara dengan Transaksi Tertinggi','Negara dikelompokkan berdasarkan tingkat aktivitas transaksi',fig_bar)
    with c2: show_chart('Proporsi Revenue per Kelompok','Kategori: Tinggi → Rendah',fig_pie)
    if 'Country_Group' in dff.columns:
        st.markdown('<div class="section-title">Ringkasan Data</div>', unsafe_allow_html=True)
        gt = dff.groupby('Country_Group').agg(Negara=('Country','nunique'), Transaksi=('TransactionNo','nunique'), Revenue=('Revenue','sum'), Pelanggan=('CustomerNo','nunique')).reindex(COUNTRY_GROUPS).reset_index()
        gt['AOV'] = (gt['Revenue']/gt['Transaksi']).round(2)
        gt['Revenue'] = gt['Revenue'].apply(lambda x: f'£{x:,.0f}')
        gt['AOV'] = gt['AOV'].apply(lambda x: f'£{x:,.2f}')
        gt.columns = ['Kelompok','Negara','Transaksi','Revenue','Pelanggan','AOV']
        table_html = gt.to_html(index=False, classes='styled-table', border=0)
        st.markdown(f'<div class="chart-card"><div class="chart-header"><div><div class="chart-title">Ringkasan per Kelompok Negara</div><div class="chart-subtitle">Perbandingan indikator utama</div></div><span class="chart-badge">Table</span></div>{table_html}</div>', unsafe_allow_html=True)

# === ROUTING ===
{'overview':page_overview,'product':page_product,'customer':page_customer,'geo':page_geo}.get(page, page_overview)()
st.markdown('<div class="footer">Remedial UAS Business Intelligence — Universitas Islam Indonesia</div>', unsafe_allow_html=True)
