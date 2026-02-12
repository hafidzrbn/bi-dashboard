import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

# ============================================================
# 1. LOAD DATA & CONFIG
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DASHBOARD_CSV = os.path.join(BASE_DIR, 'df_dashboard.csv')
CLEAN_CSV = os.path.join(BASE_DIR, 'df_clean.csv')

if os.path.exists(DASHBOARD_CSV):
    df = pd.read_csv(DASHBOARD_CSV, encoding='utf-8-sig')
elif os.path.exists(CLEAN_CSV):
    df = pd.read_csv(CLEAN_CSV, encoding='utf-8-sig')
else:
    raise FileNotFoundError("File df_dashboard.csv atau df_clean.csv tidak ditemukan.")

df['Date'] = pd.to_datetime(df['Date'])
df['TransactionNo'] = df['TransactionNo'].astype(str)
df['CustomerNo'] = df['CustomerNo'].astype(str)
df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce').fillna(0)
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)

if 'YearMonth' not in df.columns:
    df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)

PRODUCT_GROUPS = [
    'Very Frequently Purchased', 'Frequently Purchased',
    'Moderately Purchased', 'Rarely Purchased', 'Very Rarely Purchased'
]
CUSTOMER_SEGMENTS = ['Loyal', 'Active', 'Occasional', 'Inactive']
COUNTRY_GROUPS = ['Transaksi Tinggi', 'Transaksi Sedang', 'Transaksi Rendah']

COLOR_PRODUCT = {
    'Very Frequently Purchased': '#10b981', 'Frequently Purchased': '#0ea5e9',
    'Moderately Purchased': '#f59e0b', 'Rarely Purchased': '#fb923c',
    'Very Rarely Purchased': '#f43f5e',
}
COLOR_SEGMENT = {
    'Loyal': '#10b981', 'Active': '#0ea5e9',
    'Occasional': '#f59e0b', 'Inactive': '#f43f5e',
}
COLOR_COUNTRY = {
    'Transaksi Tinggi': '#10b981', 'Transaksi Sedang': '#f59e0b',
    'Transaksi Rendah': '#f43f5e',
}

BASE_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter, sans-serif', color='#94a3b8', size=12),
    title_font=dict(family='Inter, sans-serif', color='#f1f5f9', size=15),
    xaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.06)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.06)'),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(font=dict(size=11, color='#94a3b8')),
    hoverlabel=dict(
        bgcolor='#1e2235',
        bordercolor='#6366f1',
        font=dict(family='Inter, sans-serif', size=13, color='#f1f5f9')
    ),
)

GRAPH_STYLE = {'height': '380px'}
GRAPH_STYLE_TALL = {'height': '440px'}
CHART_CFG = {'displayModeBar': True, 'displaylogo': False,
             'modeBarButtonsToRemove': ['lasso2d', 'select2d']}


def apply_layout(fig, **kw):
    fig.update_layout(**{**BASE_LAYOUT, **kw})
    return fig


# ============================================================
# 2. HELPERS
# ============================================================
def fmt(n, prefix='', decimals=0):
    if n >= 1_000_000:
        return f"{prefix}{n/1_000_000:,.{decimals}f}M"
    if n >= 1_000:
        return f"{prefix}{n/1_000:,.{decimals}f}K"
    return f"{prefix}{n:,.{decimals}f}"


def fdf(df_src, pg, cs, cg):
    dff = df_src.copy()
    if pg and pg != 'All':
        dff = dff[dff['Product_Group'] == pg]
    if cs and cs != 'All':
        dff = dff[dff['Customer_Segment'] == cs]
    if cg and cg != 'All':
        dff = dff[dff['Country_Group'] == cg]
    return dff


def G(fig, style=None):
    return dcc.Graph(figure=fig, config=CHART_CFG,
                     style=style or GRAPH_STYLE, responsive=True)


def chart_card(title, subtitle, graph, badge=None):
    header_children = [
        html.Div([
            html.Div(title, className='chart-title'),
            html.Div(subtitle, className='chart-subtitle'),
        ])
    ]
    if badge:
        header_children.append(html.Span(badge, className='chart-badge'))
    return html.Div(className='chart-card', children=[
        html.Div(className='chart-card-header', children=header_children),
        graph,
    ])


# ============================================================
# 3. INIT APP
# ============================================================
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title='ShopInsight - E-Commerce Analytics',
    update_title='Loading...',
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}],
)
server = app.server


# ============================================================
# 4. SIDEBAR — NAVIGASI
# ============================================================
NAV_ITEMS = [
    {'value': 'overview',  'icon': '📊', 'label': 'Overview'},
    {'value': 'product',   'icon': '📦', 'label': 'Analisis Produk'},
    {'value': 'customer',  'icon': '👥', 'label': 'Analisis Pelanggan'},
    {'value': 'geo',       'icon': '🌍', 'label': 'Analisis Geografis'},
]


def create_sidebar():
    return html.Div(className='sidebar', children=[
        # Logo
        html.Div(className='sidebar-logo', children=[
            html.Div(className='sidebar-logo-icon', children='📈'),
            html.Div([
                html.Div('ShopInsight', className='sidebar-logo-text'),
                html.Div('E-Commerce Analytics', className='sidebar-logo-sub'),
            ]),
        ]),

        html.Div(className='filter-divider'),

        # Navigasi
        html.Div(className='nav-section', children=[
            html.Div('MENU', className='nav-section-title'),
            dcc.RadioItems(
                id='nav-menu',
                options=[
                    {'label': html.Span([
                        html.Span(item['icon'], className='nav-icon'),
                        html.Span(item['label'], className='nav-label'),
                    ], className='nav-item-inner'),
                     'value': item['value']}
                    for item in NAV_ITEMS
                ],
                value='overview',
                className='nav-radio-group',
                inputClassName='nav-radio-input',
                labelClassName='nav-radio-label',
            ),
        ]),

        html.Div(className='filter-divider'),

        # Ringkasan
        html.Div(className='sidebar-stats', children=[
            html.Div('DATASET', className='nav-section-title'),
            html.Div(className='stat-row', children=[
                html.Span('Periode', className='stat-label'),
                html.Span(f"{df['Date'].min().strftime('%b %Y')} — {df['Date'].max().strftime('%b %Y')}",
                           className='stat-value'),
            ]),
            html.Div(className='stat-row', children=[
                html.Span('Transaksi', className='stat-label'),
                html.Span(f"{df['TransactionNo'].nunique():,}", className='stat-value'),
            ]),
            html.Div(className='stat-row', children=[
                html.Span('Produk', className='stat-label'),
                html.Span(f"{df['ProductName'].nunique():,}", className='stat-value'),
            ]),
            html.Div(className='stat-row', children=[
                html.Span('Pelanggan', className='stat-label'),
                html.Span(f"{df['CustomerNo'].nunique():,}", className='stat-value'),
            ]),
            html.Div(className='stat-row', children=[
                html.Span('Negara', className='stat-label'),
                html.Span(f"{df['Country'].nunique()}", className='stat-value'),
            ]),
        ]),

        html.Div(style={'flex': '1'}),

        html.Div(className='dashboard-footer', children=[
            html.Div('Remedial UAS Business Intelligence'),
            html.Div('Universitas Islam Indonesia'),
        ]),
    ])


# ============================================================
# 5. FILTER BAR
# ============================================================
def create_filter_bar():
    def dd(id_, label, options):
        return html.Div(className='filter-bar-item', children=[
            html.Label(label, className='filter-bar-label'),
            dcc.Dropdown(id=id_, options=options, value='All', multi=False,
                         placeholder=f'Pilih {label.lower()}...', className='dash-dropdown'),
        ])

    pg = [{'label': 'Semua Kelompok', 'value': 'All'}] + \
         [{'label': g, 'value': g} for g in PRODUCT_GROUPS if g in df['Product_Group'].unique()]
    cs = [{'label': 'Semua Segmen', 'value': 'All'}] + \
         [{'label': s, 'value': s} for s in CUSTOMER_SEGMENTS if s in df['Customer_Segment'].unique()]
    cg = [{'label': 'Semua Negara', 'value': 'All'}] + \
         [{'label': g, 'value': g} for g in COUNTRY_GROUPS if g in df['Country_Group'].unique()]

    return html.Div(className='filter-bar', children=[
        dd('filter-product-group', 'Kelompok Produk', pg),
        dd('filter-customer-segment', 'Segmen Pelanggan', cs),
        dd('filter-country-group', 'Kelompok Negara', cg),
    ])


# ============================================================
# 6. MAIN CONTENT
# ============================================================
def create_main_content():
    return html.Div(className='main-content', children=[
        html.Div(className='page-header', children=[
            html.H1('E-Commerce Business Intelligence Dashboard', className='page-title'),
            html.P('Analisis strategis transaksi penjualan, segmentasi produk & pelanggan, dan distribusi geografis.',
                    className='page-description'),
        ]),
        create_filter_bar(),
        html.Div(className='kpi-container', children=[
            html.Div(className='kpi-card kpi-revenue', children=[
                html.Div(className='kpi-icon icon-revenue', children='£'),
                html.Div('TOTAL REVENUE', className='kpi-label'),
                html.Div('—', className='kpi-value', id='kpi-revenue'),
            ]),
            html.Div(className='kpi-card kpi-transactions', children=[
                html.Div(className='kpi-icon icon-transactions', children='🛒'),
                html.Div('TOTAL TRANSAKSI', className='kpi-label'),
                html.Div('—', className='kpi-value', id='kpi-transactions'),
            ]),
            html.Div(className='kpi-card kpi-customers', children=[
                html.Div(className='kpi-icon icon-customers', children='👥'),
                html.Div('TOTAL PELANGGAN', className='kpi-label'),
                html.Div('—', className='kpi-value', id='kpi-customers'),
            ]),
            html.Div(className='kpi-card kpi-aov', children=[
                html.Div(className='kpi-icon icon-aov', children='📈'),
                html.Div('AVG ORDER VALUE', className='kpi-label'),
                html.Div('—', className='kpi-value', id='kpi-aov'),
            ]),
        ]),
        dcc.Loading(
            id='page-loading',
            type='default',
            children=[html.Div(id='page-content')]
        ),
    ])


# ============================================================
# 7. PAGE BUILDERS
# ============================================================
def build_overview(dff):
    monthly = (dff.groupby('YearMonth')
               .agg(Revenue=('Revenue', 'sum'), Transaksi=('TransactionNo', 'nunique'))
               .reset_index().sort_values('YearMonth'))

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=monthly['YearMonth'], y=monthly['Revenue'],
        mode='lines+markers', line=dict(color='#6366f1', width=4, shape='spline'),
        marker=dict(size=3), fill='tozeroy', fillcolor='rgba(99,102,241,0.1)',
        hovertemplate='<b>%{x}</b><br>Revenue: £%{y:,.0f}<extra></extra>'))
    apply_layout(fig1, title='Tren Revenue Bulanan', xaxis_title='Bulan',
                 yaxis_title='Revenue (£)', hovermode='x unified')

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=monthly['YearMonth'], y=monthly['Transaksi'],
        marker=dict(color='#0ea5e9', line=dict(width=2, color='rgba(255,255,255,0)'), cornerradius=8),
        opacity=0.9,
        hovertemplate='<b style="font-size: 14px; color: #ffffff;">%{x}</b><br><b>Volume Transaksi:</b> %{y:,} transaksi<extra></extra>'))
    apply_layout(fig2, title='Jumlah Transaksi per Bulan', xaxis_title='Bulan',
                 yaxis_title='Jumlah Transaksi')
    fig2.update_traces(
        hovertemplate='<b style="font-size: 14px; color: #ffffff;">%{x}</b><br><b>Volume Transaksi:</b> %{y:,} transaksi<extra></extra>',
        selector=dict(type='bar')
    )

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily = dff.groupby('DayName')['TransactionNo'].nunique().reindex(day_order).reset_index()
    daily.columns = ['Day', 'Count']
    peak = daily.loc[daily['Count'].idxmax(), 'Day']

    fig3 = go.Figure()
    colors = ['#6366f1' if d == peak else '#334155' for d in daily['Day']]
    fig3.add_trace(go.Bar(
        x=daily['Day'], y=daily['Count'],
        marker=dict(color=colors, line=dict(width=2, color='rgba(255,255,255,0)'), cornerradius=8),
        opacity=0.9,
        hovertemplate='<b style="font-size: 14px; color: #ffffff;">%{x}</b><br><b>Jumlah Transaksi:</b> %{y:,}<extra></extra>'))
    apply_layout(fig3, title='Distribusi Transaksi per Hari', xaxis_title='Hari',
                 yaxis_title='Jumlah Transaksi')

    s_order = ['Spring', 'Summer', 'Autumn', 'Winter']
    s_col = {'Spring': '#10b981', 'Summer': '#f59e0b', 'Autumn': '#fb923c', 'Winter': '#0ea5e9'}
    seasonal = dff.groupby('Season')['Revenue'].sum().reindex(s_order).reset_index()

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=seasonal['Season'], y=seasonal['Revenue'],
        marker=dict(
            color=[s_col.get(s, '#6366f1') for s in seasonal['Season']],
            line=dict(width=2, color='rgba(255,255,255,0)'),
            cornerradius=8
        ),
        opacity=0.9,
        hovertemplate='<b style="font-size: 14px; color: #ffffff;">%{x}</b><br><b>Total Revenue:</b> £%{y:,.0f}<extra></extra>'))
    apply_layout(fig4, title='Revenue per Musim', xaxis_title='Musim', yaxis_title='Revenue (£)')

    return html.Div([
        html.Div(className='section-title', children='Tren Penjualan'),
        html.Div(className='grid-2', children=[
            chart_card('Tren Revenue Bulanan', 'Pendapatan total per bulan', G(fig1), 'Time Series'),
            chart_card('Jumlah Transaksi per Bulan', 'Volume transaksi bulanan', G(fig2), 'Bar Chart'),
        ]),
        html.Div(className='section-title', children='Pola Waktu'),
        html.Div(className='grid-2', children=[
            chart_card('Distribusi Transaksi per Hari', f'Hari dengan transaksi tertinggi: {peak}', G(fig3)),
            chart_card('Revenue per Musim', 'Perbandingan revenue antar musim', G(fig4)),
        ]),
    ])


def build_product(dff):
    top10 = dff.groupby('ProductName')['Quantity'].sum().nlargest(10).reset_index().sort_values('Quantity')
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        y=top10['ProductName'].str[:35], x=top10['Quantity'],
        orientation='h',
        marker=dict(color='#6366f1', line=dict(width=2, color='rgba(255,255,255,0)'), cornerradius=8),
        opacity=0.9,
        hovertemplate='<b style="font-size: 14px; color: #ffffff;">%{y}</b><br><b>Total Quantity:</b> %{x:,} unit<extra></extra>'))
    apply_layout(fig1, title='Produk dengan Penjualan Tertinggi', xaxis_title='Total Quantity', yaxis_title='')

    fig2 = go.Figure()
    if 'Product_Group' in dff.columns:
        pg = dff.groupby('Product_Group')['Revenue'].sum().reindex(PRODUCT_GROUPS).dropna().reset_index()
        fig2.add_trace(go.Pie(
            labels=pg['Product_Group'], values=pg['Revenue'],
            marker=dict(
                colors=[COLOR_PRODUCT.get(g, '#6366f1') for g in pg['Product_Group']],
                line=dict(color='#1e2235', width=2)
            ),
            hole=0.55, textinfo='percent+label', textposition='outside', textfont_size=11,
            hovertemplate='<b style="font-size: 14px;">%{label}</b><br><b>Revenue:</b> £%{value:,.0f}<br>%{percent}<extra></extra>'))
    apply_layout(fig2, title='Proporsi Revenue per Kelompok Produk', showlegend=False)

    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(
        x=dff['Price'], nbinsx=50,
        marker=dict(color='#6366f1', line=dict(width=1, color='rgba(255,255,255,0.2)'), cornerradius=4),
        opacity=0.85,
        hovertemplate='<b>Harga Range:</b> £%{x:.2f}<br><b>Frekuensi:</b> %{y:,} produk<extra></extra>'))
    apply_layout(fig3, title='Distribusi Harga Produk', xaxis_title='Harga (£)', yaxis_title='Frekuensi')

    qt = dff.groupby('TransactionNo')['Quantity'].sum().reset_index()
    p99 = qt['Quantity'].quantile(0.99)
    fig4 = go.Figure()
    fig4.add_trace(go.Histogram(
        x=qt[qt['Quantity'] <= p99]['Quantity'], nbinsx=50,
        marker=dict(color='#0ea5e9', line=dict(width=1, color='rgba(255,255,255,0.2)'), cornerradius=4),
        opacity=0.85,
        hovertemplate='<b>Quantity Range:</b> %{x:,.0f} unit<br><b>Frekuensi:</b> %{y:,} transaksi<extra></extra>'))
    apply_layout(fig4, title=f'Distribusi Quantity per Transaksi',
                 xaxis_title='Total Quantity', yaxis_title='Frekuensi')

    return html.Div([
        html.Div(className='section-title', children='Produk Terlaris'),
        html.Div(className='grid-2', children=[
            chart_card('Produk dengan Penjualan Tertinggi', 'Berdasarkan total jumlah unit terjual', G(fig1), 'Ranking'),
            chart_card('Proporsi Revenue per Kelompok', 'Kategori: Very Freq → Very Rare', G(fig2), 'Donut'),
        ]),
        html.Div(className='section-title', children='Distribusi'),
        html.Div(className='grid-2', children=[
            chart_card('Distribusi Harga Produk', 'Histogram harga per unit (£)', G(fig3)),
            chart_card('Distribusi Quantity per Transaksi', 'Histogram jumlah item per transaksi', G(fig4)),
        ]),
    ])


def build_customer(dff):
    fig1 = go.Figure()
    if 'Customer_Segment' in dff.columns:
        seg = dff.groupby('Customer_Segment')['CustomerNo'].nunique().reindex(CUSTOMER_SEGMENTS).dropna().reset_index()
        seg.columns = ['Segment', 'Count']
        fig1.add_trace(go.Bar(
            x=seg['Segment'], y=seg['Count'],
            marker=dict(
                color=[COLOR_SEGMENT.get(s, '#6366f1') for s in seg['Segment']],
                line=dict(width=2, color='rgba(255,255,255,0)'),
                cornerradius=8
            ),
            opacity=0.9,
            hovertemplate='<b style="font-size: 14px; color: #ffffff;">%{x}</b><br><b>Total Pelanggan:</b> %{y:,} orang<extra></extra>'))
    apply_layout(fig1, title='Jumlah Pelanggan per Segmen', xaxis_title='Segmen', yaxis_title='Jumlah Pelanggan')

    fig2 = go.Figure()
    if 'Customer_Segment' in dff.columns:
        sr = dff.groupby('Customer_Segment')['Revenue'].sum().reindex(CUSTOMER_SEGMENTS).dropna().reset_index()
        fig2.add_trace(go.Pie(
            labels=sr['Customer_Segment'], values=sr['Revenue'],
            marker=dict(
                colors=[COLOR_SEGMENT.get(s, '#6366f1') for s in sr['Customer_Segment']],
                line=dict(color='#1e2235', width=2)
            ),
            hole=0.55, textinfo='percent+label', textposition='outside', textfont_size=11,
            hovertemplate='<b style="font-size: 14px;">%{label}</b><br><b>Revenue:</b> £%{value:,.0f}<br>%{percent}<extra></extra>'))
    apply_layout(fig2, title='Proporsi Revenue per Segmen', showlegend=False)

    fig3 = go.Figure()
    if 'Customer_Segment' in dff.columns:
        ca = dff.groupby(['CustomerNo', 'Customer_Segment']).agg(
            Frequency=('TransactionNo', 'nunique'), Monetary=('Revenue', 'sum')).reset_index()
        # Optimize performance: sample data if > 2000 points to maintain smooth scrolling
        if len(ca) > 2000:
            ca = ca.sample(n=2000, random_state=42)
        for s in CUSTOMER_SEGMENTS:
            sub = ca[ca['Customer_Segment'] == s]
            if len(sub) == 0:
                continue
            fig3.add_trace(go.Scattergl(
                x=sub['Frequency'], y=sub['Monetary'], mode='markers', name=s,
                marker=dict(
                    color=COLOR_SEGMENT.get(s),
                    size=8,
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                hovertemplate=f'<b style="font-size: 14px; color: #ffffff;">{s}</b><br><b>Transaksi Frequency:</b> %{{x}} kali<br><b>Total Revenue:</b> £%{{y:,.0f}}<extra></extra>'))
    apply_layout(fig3, title='Segmentasi: Frequency vs Revenue',
                 xaxis_title='Frequency (Jumlah Transaksi)', yaxis_title='Total Revenue (£)')

    tc = dff.groupby('CustomerNo').agg(Revenue=('Revenue', 'sum')).nlargest(10, 'Revenue').reset_index()
    tc = tc.sort_values('Revenue')
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        y=tc['CustomerNo'], x=tc['Revenue'], orientation='h',
        marker=dict(color='#8b5cf6', line=dict(width=2, color='rgba(255,255,255,0)'), cornerradius=8),
        text=[f'£{r:,.0f}' for r in tc['Revenue']], textposition='outside', textfont_size=10,
        opacity=0.9,
        hovertemplate='<b style="font-size: 14px; color: #ffffff;">Customer ID: %{y}</b><br><b>Total Revenue:</b> £%{x:,.0f}<extra></extra>'))
    apply_layout(fig4, title='Pelanggan dengan Revenue Tertinggi', xaxis_title='Revenue (£)', yaxis_title='')

    return html.Div([
        html.Div(className='section-title', children='Segmentasi Pelanggan'),
        html.Div(className='grid-2', children=[
            chart_card('Jumlah Pelanggan per Segmen', 'Kategori: Loyal → Inactive', G(fig1), 'Segmentasi'),
            chart_card('Proporsi Revenue per Segmen', 'Kontribusi revenue tiap segmen', G(fig2), 'Donut'),
        ]),
        html.Div(className='section-title', children='Detail Pelanggan'),
        chart_card('Segmentasi: Frequency vs Revenue',
                   'Pemetaan kontribusi pelanggan berdasarkan intensitas transaksi', G(fig3, GRAPH_STYLE_TALL)),
        chart_card('Pelanggan dengan Revenue Tertinggi', 'Berdasarkan total revenue yang dihasilkan', G(fig4), 'Ranking'),
    ])


def build_geo(dff):
    country_iso = {
        'United Kingdom': 'GBR', 'Germany': 'DEU', 'France': 'FRA', 'Spain': 'ESP',
        'Belgium': 'BEL', 'Switzerland': 'CHE', 'Portugal': 'PRT', 'Italy': 'ITA',
        'Finland': 'FIN', 'Austria': 'AUT', 'Norway': 'NOR', 'Denmark': 'DNK',
        'Netherlands': 'NLD', 'Australia': 'AUS', 'Sweden': 'SWE', 'Japan': 'JPN',
        'Channel Islands': 'GBR', 'Poland': 'POL', 'Ireland': 'IRL', 'Iceland': 'ISL',
        'Singapore': 'SGP', 'Czech Republic': 'CZE', 'Greece': 'GRC', 'Israel': 'ISR',
        'Lithuania': 'LTU', 'United Arab Emirates': 'ARE', 'Cyprus': 'CYP',
        'Canada': 'CAN', 'USA': 'USA', 'Brazil': 'BRA', 'Malta': 'MLT',
        'Bahrain': 'BHR', 'RSA': 'ZAF', 'Saudi Arabia': 'SAU', 'Lebanon': 'LBN',
        'EIRE': 'IRL', 'European Community': 'FRA', 'Unspecified': None,
    }
    md = dff.groupby('Country').agg(Transaksi=('TransactionNo', 'nunique'),
                                     Revenue=('Revenue', 'sum')).reset_index()
    md['ISO'] = md['Country'].map(country_iso)
    md = md.dropna(subset=['ISO'])

    fig_map = go.Figure()
    fig_map.add_trace(go.Choropleth(
        locations=md['ISO'], z=md['Transaksi'], text=md['Country'],
        colorscale='YlOrRd', colorbar_title='Transaksi',
        hovertemplate='<b>%{text}</b><br>Transaksi: %{z:,}<extra></extra>'))
    apply_layout(fig_map, title='Peta Distribusi Transaksi per Negara',
                 geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth',
                          bgcolor='rgba(0,0,0,0)', landcolor='#1a1d2e',
                          coastlinecolor='rgba(255,255,255,0.15)'))

    ct = (dff.groupby(['Country', 'Country_Group'])['TransactionNo'].nunique()
          .reset_index().rename(columns={'TransactionNo': 'Transaksi'})
          .sort_values('Transaksi', ascending=False).head(15).sort_values('Transaksi'))
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        y=ct['Country'], x=ct['Transaksi'], orientation='h',
        marker=dict(
            color=[COLOR_COUNTRY.get(g, '#6366f1') for g in ct['Country_Group']],
            line=dict(width=2, color='rgba(255,255,255,0)'),
            cornerradius=8
        ),
        opacity=0.9,
        hovertemplate='<b style="font-size: 14px; color: #ffffff;">%{y}</b><br><b>Total Transaksi:</b> %{x:,} transaksi<extra></extra>'))
    apply_layout(fig_bar, title='Negara dengan Transaksi Tertinggi',
                 xaxis_title='Jumlah Transaksi', yaxis_title='')

    fig_pie = go.Figure()
    if 'Country_Group' in dff.columns:
        cg = dff.groupby('Country_Group')['Revenue'].sum().reindex(COUNTRY_GROUPS).dropna().reset_index()
        fig_pie.add_trace(go.Pie(
            labels=cg['Country_Group'], values=cg['Revenue'],
            marker=dict(
                colors=[COLOR_COUNTRY.get(g, '#6366f1') for g in cg['Country_Group']],
                line=dict(color='#1e2235', width=2)
            ),
            hole=0.55, textinfo='percent+label', textposition='outside', textfont_size=11,
            hovertemplate='<b style="font-size: 14px;">%{label}</b><br><b>Revenue:</b> £%{value:,.0f}<br>%{percent}<extra></extra>'))
    apply_layout(fig_pie, title='Proporsi Revenue per Kelompok Negara', showlegend=False)

    table_comp = html.Div()
    if 'Country_Group' in dff.columns:
        gt = (dff.groupby('Country_Group').agg(
            Negara=('Country', 'nunique'), Transaksi=('TransactionNo', 'nunique'),
            Revenue=('Revenue', 'sum'), Pelanggan=('CustomerNo', 'nunique'))
              .reindex(COUNTRY_GROUPS).reset_index())
        gt['AOV'] = (gt['Revenue'] / gt['Transaksi']).round(2)
        gt['Revenue'] = gt['Revenue'].apply(lambda x: f'£{x:,.0f}')
        gt['AOV'] = gt['AOV'].apply(lambda x: f'£{x:,.2f}')
        gt.columns = ['Kelompok', 'Negara', 'Transaksi', 'Revenue', 'Pelanggan', 'AOV']
        table_comp = dash_table.DataTable(
            data=gt.to_dict('records'),
            columns=[{'name': c, 'id': c} for c in gt.columns],
            style_header={
                'backgroundColor': '#1a1d2e', 'color': '#94a3b8', 'fontWeight': '600',
                'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '0.5px',
                'border': 'none', 'borderBottom': '1px solid rgba(255,255,255,0.1)'},
            style_cell={
                'backgroundColor': '#1e2235', 'color': '#f1f5f9', 'fontSize': '13px',
                'border': 'none', 'borderBottom': '1px solid rgba(255,255,255,0.05)',
                'padding': '12px 16px', 'fontFamily': 'Inter, sans-serif'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#222640'}])

    return html.Div([
        html.Div(className='section-title', children='Peta Global'),
        chart_card('Peta Distribusi Transaksi Global', 'Sebaran transaksi berdasarkan lokasi pelanggan',
                   G(fig_map, GRAPH_STYLE_TALL), 'Map'),
        html.Div(className='section-title', children='Perbandingan Negara'),
        html.Div(className='grid-2', children=[
            chart_card('Negara dengan Transaksi Tertinggi', 'Negara dikelompokkan berdasarkan tingkat aktivitas transaksi', G(fig_bar, GRAPH_STYLE_TALL)),
            chart_card('Proporsi Revenue per Kelompok', 'Kategori: Tinggi → Rendah', G(fig_pie)),
        ]),
        html.Div(className='section-title', children='Ringkasan Data'),
        html.Div(className='chart-card', children=[
            html.Div(className='chart-card-header', children=[
                html.Div([html.Div('Ringkasan per Kelompok Negara', className='chart-title'),
                           html.Div('Perbandingan indikator utama', className='chart-subtitle')]),
                html.Span('Table', className='chart-badge'),
            ]),
            table_comp,
        ]),
    ])


# ============================================================
# 8. APP LAYOUT
# ============================================================
app.layout = html.Div(className='grid-sidebar', children=[
    create_sidebar(),
    create_main_content(),
])


# ============================================================
# 9. CALLBACKS
# ============================================================
@app.callback(
    [Output('kpi-revenue', 'children'),
     Output('kpi-transactions', 'children'),
     Output('kpi-customers', 'children'),
     Output('kpi-aov', 'children'),
     Output('page-content', 'children')],
    [Input('nav-menu', 'value'),
     Input('filter-product-group', 'value'),
     Input('filter-customer-segment', 'value'),
     Input('filter-country-group', 'value')],
)
def update_dashboard(page, pg, cs, cg):
    dff = fdf(df, pg, cs, cg)
    total_rev = dff['Revenue'].sum()
    total_trx = dff['TransactionNo'].nunique()
    total_cust = dff['CustomerNo'].nunique()
    aov = total_rev / total_trx if total_trx > 0 else 0

    builders = {'overview': build_overview, 'product': build_product,
                'customer': build_customer, 'geo': build_geo}
    content = builders.get(page, build_overview)(dff)
    return fmt(total_rev, '£', 1), fmt(total_trx), fmt(total_cust), f'£{aov:,.2f}', content


# ============================================================
# 10. RUN
# ============================================================
if __name__ == '__main__':
    print(f"Dataset: {len(df):,} rows | Running at http://127.0.0.1:8050")
    app.run(debug=True, host='0.0.0.0', port=8050)