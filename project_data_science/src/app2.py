# Streamlit Dashboard for Adami Packaging Company

# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Set, Tuple, Optional
import datetime

# Set page configuration
st.set_page_config(
    page_title="Adami Packaging Analytics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #3B82F6;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    .insight-box {
        background-color: #EFF6FF;
        border-left: 5px solid #3B82F6;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 5px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #4B5563;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
@st.cache_data
def load_data():
    """Load and cache the data"""
    try:
        df_items = pd.read_parquet('../data/02 - trusted/parquet/tb_itens.parquet')
        df_orders = pd.read_parquet('../data/02 - trusted/parquet/tb_pedidos.parquet')
        return df_items, df_orders
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def clean_numeric_and_categorical(df: pd.DataFrame,
                                  numeric_threshold: float = 0.9,
                                  inplace: bool = False) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """Clean and categorize columns as numeric or categorical"""
    if not inplace:
        df = df.copy()

    df = df.replace(r'^\s*$', np.nan, regex=True)

    # Start with already numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    other_cols = [c for c in df.columns if c not in numeric_cols]

    categorical_cols = []

    # Try coercion for non-numeric columns
    for col in other_cols:
        coerced = pd.to_numeric(df[col], errors='coerce')
        prop_numeric = coerced.notna().sum() / len(df)
        if prop_numeric >= numeric_threshold:
            df[col] = coerced
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)

    # Fill values
    if numeric_cols:
        df[numeric_cols] = df[numeric_cols].fillna(0)
    if categorical_cols:
        df[categorical_cols] = df[categorical_cols].fillna('NA')

    return df, numeric_cols, categorical_cols

def get_common_numeric_cols(df_orders: pd.DataFrame, df_items: pd.DataFrame) -> List[str]:
    """Identify common columns that are numeric in both DataFrames"""
    common = set(df_orders.columns).intersection(df_items.columns)
    numeric_cols = []
    for col in common:
        s1 = pd.to_numeric(df_orders[col], errors='coerce')
        s2 = pd.to_numeric(df_items[col], errors='coerce')
        if s1.notna().any() and s2.notna().any():
            numeric_cols.append(col)
    # Remove text keys that might be inadvertently converted
    for k in ['ITEM', 'PEDIDO', 'IDCLIENTE']:
        if k in numeric_cols:
            numeric_cols.remove(k)
    return sorted(numeric_cols)

def build_diff_table(df_orders: pd.DataFrame, df_items: pd.DataFrame, 
                    id_cols: Optional[List[str]] = None, 
                    limit_items: Optional[int] = None) -> pd.DataFrame:
    """Build a table of differences between orders and items"""
    if id_cols is None:
        id_cols = [c for c in ['PEDIDO', 'ITEM', 'IDCLIENTE'] if c in df_orders.columns]

    # Ensure ITEM is comparable
    if 'ITEM' in df_orders.columns:
        df_orders = df_orders.copy()
        df_orders['ITEM'] = df_orders['ITEM'].astype(str)
    if 'ITEM' in df_items.columns:
        df_items = df_items.copy()
        df_items['ITEM'] = df_items['ITEM'].astype(str)

    # Select common numeric columns
    common_num_cols = get_common_numeric_cols(df_orders, df_items)
    if not common_num_cols:
        return pd.DataFrame()

    # Limit items (optional)
    if limit_items is not None and 'ITEM' in df_orders.columns:
        unique_items = df_orders['ITEM'].dropna().unique()
        selected_items = set(unique_items[:limit_items])
        df_orders = df_orders[df_orders['ITEM'].isin(selected_items)]

    # Subsets with necessary columns
    cols_orders = list(set(id_cols + common_num_cols))
    cols_items = list(set(['ITEM'] + common_num_cols))

    dfp = df_orders[cols_orders].copy()
    dfi = df_items[cols_items].copy().drop_duplicates('ITEM')

    # Coercion to numeric for common columns
    for col in common_num_cols:
        dfp[col] = pd.to_numeric(dfp[col], errors='coerce')
        dfi[col] = pd.to_numeric(dfi[col], errors='coerce')

    # Merge by ITEM
    if 'ITEM' not in dfp.columns:
        return pd.DataFrame()
    dfm = dfp.merge(dfi, on='ITEM', how='left', suffixes=('_order', '_item'))

    # Calculate differences
    out = dfm[id_cols].copy()
    for col in common_num_cols:
        order_col = f"{col}_order"
        item_col = f"{col}_item"

        # If names were not suffixed, adjust:
        if order_col not in dfm.columns and col in dfp.columns:
            order_col = col
        if item_col not in dfm.columns and col in dfi.columns:
            item_col = col

        # Absolute difference
        diff = dfm[order_col] - dfm[item_col]

        # Percentage difference with protection against division by zero
        base = dfm[item_col].replace(0, np.nan)
        diff_pct = (diff / base) * 100

        out[f"{col}_diff"] = diff
        out[f"{col}_diff_pct"] = diff_pct

    return out

# Main app structure
def main():
    # Load data
    df_items, df_orders = load_data()
    
    if df_items is None or df_orders is None:
        st.warning("Please check data paths and try again.")
        return
    
    # Clean and prepare data
    df_items_clean, items_num_cols, items_cat_cols = clean_numeric_and_categorical(df_items)
    df_orders_clean, orders_num_cols, orders_cat_cols = clean_numeric_and_categorical(df_orders)
    
    # Convert ID columns to string
    id_cols = [c for c in df_orders_clean.columns if c.upper().startswith('ID') or c.upper() in ['ITEM', 'PEDIDO', 'NROPEDIDO']]
    for col in id_cols:
        if col in df_orders_clean.columns:
            df_orders_clean[col] = df_orders_clean[col].astype(str)
    
    # Convert date columns to datetime
    date_cols = [c for c in df_orders_clean.columns if 'DATA' in c.upper()]
    for col in date_cols:
        if col in df_orders_clean.columns:
            df_orders_clean[col] = pd.to_datetime(df_orders_clean[col], errors='coerce')
    
    # Header
    st.markdown('<div class="main-header">Adami Packaging Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.image("https://via.placeholder.com/150x80?text=Adami+Logo", use_column_width=True)
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio(
        "Select Page",
        ["Overview", "Product Analysis", "Order Analysis", "Customer Analysis", "Comparison Analysis"]
    )
    
    # Filter section in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    
    # Date filter if we have date columns
    date_filter = None
    if date_cols:
        main_date_col = next((col for col in date_cols if 'PEDIDO' in col.upper()), date_cols[0])
        min_date = df_orders_clean[main_date_col].min().date()
        max_date = df_orders_clean[main_date_col].max().date()
        
        date_filter = st.sidebar.date_input(
            f"Filter by {main_date_col}",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    # Customer filter
    if 'IDCLIENTE' in df_orders_clean.columns:
        top_customers = df_orders_clean['IDCLIENTE'].value_counts().head(20).index.tolist()
        selected_customers = st.sidebar.multiselect(
            "Filter by Customer",
            options=["All"] + top_customers,
            default="All"
        )
    
    # Apply filters to data
    filtered_orders = df_orders_clean.copy()
    
    if date_filter and len(date_filter) == 2 and main_date_col in filtered_orders.columns:
        start_date, end_date = date_filter
        filtered_orders = filtered_orders[
            (filtered_orders[main_date_col].dt.date >= start_date) & 
            (filtered_orders[main_date_col].dt.date <= end_date)
        ]
    
    if 'IDCLIENTE' in filtered_orders.columns and selected_customers and "All" not in selected_customers:
        filtered_orders = filtered_orders[filtered_orders['IDCLIENTE'].isin(selected_customers)]
    
    # Page content based on selection
    if page == "Overview":
        display_overview(df_items_clean, filtered_orders)
    elif page == "Product Analysis":
        display_product_analysis(df_items_clean)
    elif page == "Order Analysis":
        display_order_analysis(filtered_orders)
    elif page == "Customer Analysis":
        display_customer_analysis(filtered_orders)
    else:  # Comparison Analysis
        display_comparison_analysis(df_items_clean, filtered_orders)
    
    # Footer
    st.markdown("---")
    st.markdown("© 2023 Adami Packaging Analytics | Data last updated: " + 
                datetime.datetime.now().strftime("%Y-%m-%d"))

def display_overview(df_items, df_orders):
    """Display overview dashboard with key metrics"""
    st.markdown('<div class="sub-header">Business Overview</div>', unsafe_allow_html=True)
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(df_items):,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Products</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(df_orders):,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Orders</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        if 'IDCLIENTE' in df_orders.columns:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{df_orders["IDCLIENTE"].nunique():,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Unique Customers</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Unique Customers</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        if 'QUANTIDADEPEDIDA' in df_orders.columns:
            total_qty = df_orders['QUANTIDADEPEDIDA'].sum()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{total_qty:,.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Quantity Ordered</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Quantity</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Time series chart if we have date columns
    date_cols = [c for c in df_orders.columns if 'DATA' in c.upper()]
    if date_cols:
        st.markdown('<div class="section-header">Order Trends</div>', unsafe_allow_html=True)
        
        main_date_col = next((col for col in date_cols if 'PEDIDO' in col.upper()), date_cols[0])
        
        # Create time series
        df_orders['year_month'] = df_orders[main_date_col].dt.to_period('M')
        orders_by_month = df_orders.groupby('year_month').size().reset_index(name='count')
        orders_by_month['year_month_str'] = orders_by_month['year_month'].astype(str)
        
        fig = px.line(
            orders_by_month, 
            x='year_month_str', 
            y='count',
            markers=True,
            title=f'Monthly Order Volume',
            labels={'year_month_str': 'Month', 'count': 'Number of Orders'}
        )
        fig.update_layout(xaxis_tickangle=45, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Product and customer distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">Product Distribution</div>', unsafe_allow_html=True)
        
        # Check if we have dimension data
        if all(col in df_items.columns for col in ['LARGURAINTERNA', 'COMPRIMENTOINTERNO', 'ALTURAINTERNA']):
            # Calculate volume and create size categories
            df_items['VOLUME'] = df_items['LARGURAINTERNA'] * df_items['COMPRIMENTOINTERNO'] * df_items['ALTURAINTERNA']
            df_items['SIZE_CATEGORY'] = pd.qcut(df_items['VOLUME'], 3, labels=['Small', 'Medium', 'Large'])
            
            size_counts = df_items['SIZE_CATEGORY'].value_counts()
            
            fig = px.pie(
                values=size_counts.values,
                names=size_counts.index,
                title='Product Distribution by Size',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dimension data not available for product distribution analysis.")
    
    with col2:
        st.markdown('<div class="section-header">Customer Concentration</div>', unsafe_allow_html=True)
        
        if 'IDCLIENTE' in df_orders.columns:
            # Customer concentration (Pareto)
            orders_by_customer = df_orders.groupby('IDCLIENTE').size().sort_values(ascending=False)
            cumulative_pct = (orders_by_customer.cumsum() / orders_by_customer.sum() * 100)
            
            # Create a DataFrame for the top 20 customers
            top_customers = orders_by_customer.head(20).reset_index()
            top_customers.columns = ['IDCLIENTE', 'Orders']
            top_customers['Cumulative %'] = cumulative_pct.loc[top_customers['IDCLIENTE']].values
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Bar(
                    x=top_customers['IDCLIENTE'],
                    y=top_customers['Orders'],
                    name='Orders'
                ),
                secondary_y=False
            )
            
            fig.add_trace(
                go.Scatter(
                    x=top_customers['IDCLIENTE'],
                    y=top_customers['Cumulative %'],
                    name='Cumulative %',
                    mode='lines+markers'
                ),
                secondary_y=True
            )
            
            fig.update_layout(
                title='Top 20 Customers by Order Volume',
                xaxis_title='Customer ID',
                height=400
            )
            
            fig.update_yaxes(title_text='Number of Orders', secondary_y=False)
            fig.update_yaxes(title_text='Cumulative %', secondary_y=True)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Customer data not available for concentration analysis.")
    
    # Key insights
    st.markdown('<div class="section-header">Key Business Insights</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("**Product Efficiency**")
        
        if 'AREALIQUIDAPECA' in df_items.columns and 'AREABRUTAPECA' in df_items.columns:
            df_items['APROVEITAMENTO_perc'] = (df_items['AREALIQUIDAPECA'] / df_items['AREABRUTAPECA'] * 100).clip(0, 100)
            avg_efficiency = df_items['APROVEITAMENTO_perc'].mean()
            low_efficiency = (df_items['APROVEITAMENTO_perc'] < 85).mean() * 100
            
            st.markdown(f"Average material utilization: **{avg_efficiency:.1f}%**")
            st.markdown(f"Products with low efficiency (<85%): **{low_efficiency:.1f}%**")
            
            if low_efficiency > 20:
                st.markdown("⚠️ **Action needed**: High percentage of products with low material efficiency.")
            else:
                st.markdown("✅ Good material utilization across product portfolio.")
        else:
            st.markdown("Material utilization data not available.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("**Customer Concentration Risk**")
        
        if 'IDCLIENTE' in df_orders.columns:
            orders_by_customer = df_orders.groupby('IDCLIENTE').size()
            top_customer_pct = orders_by_customer.max() / orders_by_customer.sum() * 100
            top5_pct = orders_by_customer.nlargest(5).sum() / orders_by_customer.sum() * 100
            
            st.markdown(f"Top customer concentration: **{top_customer_pct:.1f}%**")
            st.markdown(f"Top 5 customers concentration: **{top5_pct:.1f}%**")
            
            if top_customer_pct > 30:
                st.markdown("⚠️ **High risk**: Significant dependence on top customer.")
            elif top5_pct > 60:
                st.markdown("⚠️ **Moderate risk**: High concentration in top 5 customers.")
            else:
                st.markdown("✅ Well-diversified customer base.")
        else:
            st.markdown("Customer concentration data not available.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_product_analysis(df_items):
    """Display product analysis dashboard"""
    st.markdown('<div class="sub-header">Product Analysis</div>', unsafe_allow_html=True)
    
    # Product dimensions analysis
    st.markdown('<div class="section-header">Product Dimensions</div>', unsafe_allow_html=True)
    
    dims = ['LARGURAINTERNA', 'COMPRIMENTOINTERNO', 'ALTURAINTERNA']
    if all(dim in df_items.columns for dim in dims):
        # Calculate volume
        df_items['VOLUME'] = df_items['LARGURAINTERNA'] * df_items['COMPRIMENTOINTERNO'] * df_items['ALTURAINTERNA']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Dimension statistics
            st.markdown("**Dimension Statistics**")
            
            stats_df = pd.DataFrame({
                'Dimension': ['Width', 'Length', 'Height', 'Volume'],
                'Min': [
                    df_items['LARGURAINTERNA'].min(),
                    df_items['COMPRIMENTOINTERNO'].min(),
                    df_items['ALTURAINTERNA'].min(),
                    df_items['VOLUME'].min()
                ],
                'Max': [
                    df_items['LARGURAINTERNA'].max(),
                    df_items['COMPRIMENTOINTERNO'].max(),
                    df_items['ALTURAINTERNA'].max(),
                    df_items['VOLUME'].max()
                ],
                'Mean': [
                    df_items['LARGURAINTERNA'].mean(),
                    df_items['COMPRIMENTOINTERNO'].mean(),
                    df_items['ALTURAINTERNA'].mean(),
                    df_items['VOLUME'].mean()
                ],
                'Median': [
                    df_items['LARGURAINTERNA'].median(),
                    df_items['COMPRIMENTOINTERNO'].median(),
                    df_items['ALTURAINTERNA'].median(),
                    df_items['VOLUME'].median()
                ]
            })
            
            st.dataframe(stats_df.round(2), hide_index=True)
        
        with col2:
            # Size distribution
            df_items['SIZE_CATEGORY'] = pd.qcut(df_items['VOLUME'], 3, labels=['Small', 'Medium', 'Large'])
            size_counts = df_items['SIZE_CATEGORY'].value_counts()
            
            fig = px.pie(
                values=size_counts.values,
                names=size_counts.index,
                title='Product Distribution by Size',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Dimension relationships
        st.markdown("**Dimension Relationships**")
        
        fig = px.scatter_3d(
            df_items.sample(min(1000, len(df_items))),
            x='LARGURAINTERNA',
            y='COMPRIMENTOINTERNO',
            z='ALTURAINTERNA',
            color='SIZE_CATEGORY',
            title='3D Visualization of Product Dimensions',
            labels={
                'LARGURAINTERNA': 'Width',
                'COMPRIMENTOINTERNO': 'Length',
                'ALTURAINTERNA': 'Height'
            }
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Product dimension data not available.")
    
    # Material utilization analysis
    st.markdown('<div class="section-header">Material Utilization</div>', unsafe_allow_html=True)
    
    if 'AREALIQUIDAPECA' in df_items.columns and 'AREABRUTAPECA' in df_items.columns:
        df_items['APROVEITAMENTO_perc'] = (df_items['AREALIQUIDAPECA'] / df_items['AREABRUTAPECA'] * 100).clip(0, 100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Utilization statistics
            st.markdown("**Material Utilization Statistics**")
            
            util_stats = df_items['APROVEITAMENTO_perc'].describe()
            st.dataframe(pd.DataFrame({
                'Statistic': ['Mean', 'Median', 'Min', 'Max', 'Std Dev'],
                'Value': [
                    f"{util_stats['mean']:.2f}%",
                    f"{util_stats['50%']:.2f}%",
                    f"{util_stats['min']:.2f}%",
                    f"{util_stats['max']:.2f}%",
                    f"{util_stats['std']:.2f}%"
                ]
            }), hide_index=True)
        
        with col2:
            # Utilization distribution
            fig = px.histogram(
                df_items,
                x='APROVEITAMENTO_perc',
                nbins=20,
                title='Distribution of Material Utilization',
                labels={'APROVEITAMENTO_perc': 'Material Utilization (%)'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Utilization by size category
        if 'SIZE_CATEGORY' in df_items.columns:
            st.markdown("**Material Utilization by Product Size**")
            
            util_by_size = df_items.groupby('SIZE_CATEGORY')['APROVEITAMENTO_perc'].mean().reset_index()
            
            fig = px.bar(
                util_by_size,
                x='SIZE_CATEGORY',
                y='APROVEITAMENTO_perc',
                title='Average Material Utilization by Product Size',
                labels={
                    'SIZE_CATEGORY': 'Product Size',
                    'APROVEITAMENTO_perc': 'Avg. Material Utilization (%)'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Material utilization data not available.")
    
    # Process flags analysis
    st.markdown('<div class="section-header">Production Process Analysis</div>', unsafe_allow_html=True)
    
    flags = ['FLAG_REFILADO', 'FLAG_AMARRADO', 'FLAG_PALETIZADO', 'FLAG_ESPELHO', 'FLAG_FILME']
    available_flags = [flag for flag in flags if flag in df_items.columns]
    
    if available_flags:
        # Process flags distribution
        flag_data = []
        for flag in available_flags:
            yes_count = (df_items[flag] == 1).sum()
            no_count = (df_items[flag] == 0).sum()
            flag_data.append({
                'Process': flag.replace('FLAG_', ''),
                'Yes': yes_count,
                'No': no_count,
                'Yes_pct': yes_count / len(df_items) * 100
            })
        
        flag_df = pd.DataFrame(flag_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Process flags table
            st.markdown("**Process Flags Distribution**")
            
            display_df = flag_df[['Process', 'Yes', 'No', 'Yes_pct']].copy()
            display_df['Yes_pct'] = display_df['Yes_pct'].round(2).astype(str) + '%'
            display_df.columns = ['Process', 'Yes Count', 'No Count', 'Yes Percentage']
            
            st.dataframe(display_df, hide_index=True)
        
        with col2:
            # Process flags chart
            fig = px.bar(
                flag_df,
                x='Process',
                y='Yes_pct',
                title='Percentage of Products with Process Flags',
                labels={'Process': 'Process', 'Yes_pct': 'Percentage (%)'}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Process flag data not available.")
    
    # Palletization analysis
    st.markdown('<div class="section-header">Palletization Analysis</div>', unsafe_allow_html=True)
    
    palet_cols = ['PECASPORPACOTE', 'PACOTESPORPALETE', 'PECASPORPALETE']
    available_palet_cols = [col for col in palet_cols if col in df_items.columns]
    
    if available_palet_cols:
        col1, col2 = st.columns(2)
        
        with col1:
            # Palletization statistics
            st.markdown("**Palletization Statistics**")
            
            palet_stats = []
            for col in available_palet_cols:
                stats = df_items[col].describe()
                palet_stats.append({
                    'Metric': col.replace('PECAS', 'Pieces').replace('PACOTES', 'Packages').replace('POR', ' per '),
                    'Mean': stats['mean'],
                    'Median': stats['50%'],
                    'Min': stats['min'],
                    'Max': stats['max']
                })
            
            palet_stats_df = pd.DataFrame(palet_stats)
            st.dataframe(palet_stats_df.round(2), hide_index=True)
        
        with col2:
            # Pieces per pallet distribution
            if 'PECASPORPALETE' in available_palet_cols:
                fig = px.histogram(
                    df_items,
                    x='PECASPORPALETE',
                    nbins=20,
                    title='Distribution of Pieces per Pallet',
                    labels={'PECASPORPALETE': 'Pieces per Pallet'}
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Palletization data not available.")

def display_order_analysis(df_orders):
    """Display order analysis dashboard"""
    st.markdown('<div class="sub-header">Order Analysis</div>', unsafe_allow_html=True)
    
    # Order volume metrics
    st.markdown('<div class="section-header">Order Volume</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(df_orders):,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Orders</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if 'ITEM' in df_orders.columns:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{df_orders["ITEM"].nunique():,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Unique Products Ordered</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Unique Products</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        if 'QUANTIDADEPEDIDA' in df_orders.columns:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{df_orders["QUANTIDADEPEDIDA"].sum():,.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Quantity Ordered</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Quantity</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Time series analysis
    date_cols = [c for c in df_orders.columns if 'DATA' in c.upper()]
    if date_cols:
        st.markdown('<div class="section-header">Order Trends</div>', unsafe_allow_html=True)
        
        # Select date column for analysis
        date_col = st.selectbox(
            "Select date field for trend analysis:",
            date_cols
        )
        
        # Create time series by month
        df_orders['year_month'] = df_orders[date_col].dt.to_period('M')
        orders_by_month = df_orders.groupby('year_month').size().reset_index(name='count')
        orders_by_month['year_month_str'] = orders_by_month['year_month'].astype(str)
        
        # Create time series by day of week
        df_orders['day_of_week'] = df_orders[date_col].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        orders_by_dow = df_orders.groupby('day_of_week').size().reindex(day_order).reset_index(name='count')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly trend
            fig = px.line(
                orders_by_month, 
                x='year_month_str', 
                y='count',
                markers=True,
                title=f'Monthly Order Volume',
                labels={'year_month_str': 'Month', 'count': 'Number of Orders'}
            )
            fig.update_layout(xaxis_tickangle=45, height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Day of week distribution
            fig = px.bar(
                orders_by_dow,
                x='day_of_week',
                y='count',
                title='Order Distribution by Day of Week',
                labels={'day_of_week': 'Day of Week', 'count': 'Number of Orders'}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Seasonality analysis
        st.markdown("**Seasonality Analysis**")
        
        # Create month-only aggregation for seasonality
        df_orders['month'] = df_orders[date_col].dt.month
        orders_by_month_only = df_orders.groupby('month').size().reset_index(name='count')
        orders_by_month_only['month_name'] = orders_by_month_only['month'].apply(lambda x: datetime.date(2000, x, 1).strftime('%B'))
        
        fig = px.bar(
            orders_by_month_only.sort_values('month'),
            x='month_name',
            y='count',
            title='Seasonal Pattern: Orders by Month',
            labels={'month_name': 'Month', 'count': 'Number of Orders'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Date information not available for trend analysis.")
    
# app.py (continued)
    # Order status analysis
    st.markdown('<div class="section-header">Order Status Analysis</div>', unsafe_allow_html=True)
    
    status_cols = [col for col in df_orders.columns if 'STATUS' in col.upper()]
    if status_cols:
        # Select status column for analysis
        status_col = st.selectbox(
            "Select status field for analysis:",
            status_cols
        )
        
        status_counts = df_orders[status_col].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution table
            st.markdown("**Order Status Distribution**")
            
            status_df = pd.DataFrame({
                'Status': status_counts.index,
                'Count': status_counts.values,
                'Percentage': (status_counts.values / status_counts.sum() * 100).round(2)
            })
            
            st.dataframe(status_df, hide_index=True)
        
        with col2:
            # Status distribution chart
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title='Order Status Distribution',
                hole=0.4
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Status over time if we have date data
        if date_cols:
            st.markdown("**Status Evolution Over Time**")
            
            main_date_col = next((col for col in date_cols if 'PEDIDO' in col.upper()), date_cols[0])
            df_orders['year_month'] = df_orders[main_date_col].dt.to_period('M')
            df_orders['year_month_str'] = df_orders['year_month'].astype(str)
            
            status_by_month = df_orders.groupby(['year_month_str', status_col]).size().reset_index(name='count')
            
            fig = px.bar(
                status_by_month,
                x='year_month_str',
                y='count',
                color=status_col,
                title='Order Status Evolution Over Time',
                labels={'year_month_str': 'Month', 'count': 'Number of Orders'}
            )
            fig.update_layout(xaxis_tickangle=45, height=500)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Status information not available for analysis.")
    
    # Order quantity analysis
    st.markdown('<div class="section-header">Order Quantity Analysis</div>', unsafe_allow_html=True)
    
    if 'QUANTIDADEPEDIDA' in df_orders.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Quantity statistics
            st.markdown("**Order Quantity Statistics**")
            
            qty_stats = df_orders['QUANTIDADEPEDIDA'].describe()
            st.dataframe(pd.DataFrame({
                'Statistic': ['Mean', 'Median', 'Min', 'Max', 'Std Dev'],
                'Value': [
                    f"{qty_stats['mean']:.2f}",
                    f"{qty_stats['50%']:.2f}",
                    f"{qty_stats['min']:.2f}",
                    f"{qty_stats['max']:.2f}",
                    f"{qty_stats['std']:.2f}"
                ]
            }), hide_index=True)
        
        with col2:
            # Quantity distribution
            fig = px.histogram(
                df_orders,
                x='QUANTIDADEPEDIDA',
                nbins=20,
                title='Distribution of Order Quantities',
                labels={'QUANTIDADEPEDIDA': 'Quantity Ordered'}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Top products by quantity
        if 'ITEM' in df_orders.columns:
            st.markdown("**Top Products by Ordered Quantity**")
            
            qty_by_product = df_orders.groupby('ITEM')['QUANTIDADEPEDIDA'].sum().sort_values(ascending=False)
            
            fig = px.bar(
                x=qty_by_product.index[:15],
                y=qty_by_product.values[:15],
                title='Top 15 Products by Total Ordered Quantity',
                labels={'x': 'Product ID', 'y': 'Total Quantity'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Order quantity data not available for analysis.")

def display_customer_analysis(df_orders):
    """Display customer analysis dashboard"""
    st.markdown('<div class="sub-header">Customer Analysis</div>', unsafe_allow_html=True)
    
    if 'IDCLIENTE' not in df_orders.columns:
        st.warning("Customer ID information not available in the dataset.")
        return
    
    # Customer metrics
    st.markdown('<div class="section-header">Customer Overview</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{df_orders["IDCLIENTE"].nunique():,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Customers</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        avg_orders = len(df_orders) / df_orders["IDCLIENTE"].nunique()
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{avg_orders:.1f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Avg Orders per Customer</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        if 'QUANTIDADEPEDIDA' in df_orders.columns:
            avg_qty = df_orders['QUANTIDADEPEDIDA'].sum() / df_orders["IDCLIENTE"].nunique()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{avg_qty:.1f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Avg Quantity per Customer</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Avg Quantity per Customer</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Customer concentration analysis
    st.markdown('<div class="section-header">Customer Concentration</div>', unsafe_allow_html=True)
    
    # Orders by customer
    orders_by_customer = df_orders.groupby('IDCLIENTE').size().sort_values(ascending=False)
    
    # Calculate cumulative percentages
    total_orders = orders_by_customer.sum()
    orders_by_customer_pct = orders_by_customer / total_orders * 100
    cumulative_pct = orders_by_customer_pct.cumsum()
    
    # Create ABC classification
    customer_class = pd.DataFrame({
        'orders': orders_by_customer,
        'percentage': orders_by_customer_pct,
        'cumulative': cumulative_pct
    })
    
    customer_class['class'] = 'C'
    customer_class.loc[customer_class['cumulative'] <= 80, 'class'] = 'A'
    customer_class.loc[(customer_class['cumulative'] > 80) & (customer_class['cumulative'] <= 95), 'class'] = 'B'
    
    # Count customers by class
    customers_by_class = customer_class['class'].value_counts().reindex(['A', 'B', 'C'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ABC analysis table
        st.markdown("**Customer ABC Analysis**")
        
        abc_df = pd.DataFrame({
            'Class': ['A', 'B', 'C'],
            'Customers': [
                customers_by_class['A'],
                customers_by_class['B'],
                customers_by_class['C']
            ],
            'Percentage': [
                customers_by_class['A'] / len(customer_class) * 100,
                customers_by_class['B'] / len(customer_class) * 100,
                customers_by_class['C'] / len(customer_class) * 100
            ],
            'Orders %': [80, 15, 5]
        })
        
        abc_df['Percentage'] = abc_df['Percentage'].round(2).astype(str) + '%'
        abc_df['Orders %'] = abc_df['Orders %'].astype(str) + '%'
        
        st.dataframe(abc_df, hide_index=True)
    
    with col2:
        # ABC analysis chart
        fig = px.pie(
            values=[customers_by_class['A'], customers_by_class['B'], customers_by_class['C']],
            names=['A', 'B', 'C'],
            title='Customer Distribution by ABC Class',
            hole=0.4
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Pareto chart
    st.markdown("**Customer Pareto Analysis**")
    
    # Create a DataFrame for the top 50 customers
    top_customers = customer_class.head(50).reset_index()
    top_customers.columns = ['IDCLIENTE', 'Orders', 'Percentage', 'Cumulative', 'Class']
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(
            x=top_customers['IDCLIENTE'],
            y=top_customers['Orders'],
            name='Orders',
            marker_color=top_customers['Class'].map({'A': '#1E40AF', 'B': '#60A5FA', 'C': '#BFDBFE'})
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=top_customers['IDCLIENTE'],
            y=top_customers['Cumulative'],
            name='Cumulative %',
            mode='lines+markers',
            line=dict(color='red', width=2)
        ),
        secondary_y=True
    )
    
    # Add reference lines for 80% and 95%
    fig.add_shape(
        type="line",
        x0=top_customers['IDCLIENTE'].iloc[0],
        y0=80,
        x1=top_customers['IDCLIENTE'].iloc[-1],
        y1=80,
        line=dict(color="green", width=2, dash="dash"),
        yref='y2'
    )
    
    fig.add_shape(
        type="line",
        x0=top_customers['IDCLIENTE'].iloc[0],
        y0=95,
        x1=top_customers['IDCLIENTE'].iloc[-1],
        y1=95,
        line=dict(color="orange", width=2, dash="dash"),
        yref='y2'
    )
    
    fig.update_layout(
        title='Top 50 Customers - Pareto Analysis',
        xaxis_title='Customer ID',
        height=500,
        legend=dict(x=0.01, y=0.99)
    )
    
    fig.update_yaxes(title_text='Number of Orders', secondary_y=False)
    fig.update_yaxes(title_text='Cumulative %', secondary_y=True, range=[0, 100])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Customer order patterns
    st.markdown('<div class="section-header">Customer Order Patterns</div>', unsafe_allow_html=True)
    
    # Select top customers for detailed analysis
    top_n_customers = min(20, df_orders['IDCLIENTE'].nunique())
    top_customers_list = orders_by_customer.head(top_n_customers).index.tolist()
    
    selected_customer = st.selectbox(
        "Select a customer for detailed analysis:",
        ["All"] + top_customers_list
    )
    
    if selected_customer != "All":
        customer_orders = df_orders[df_orders['IDCLIENTE'] == selected_customer]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(customer_orders):,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Orders</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if 'ITEM' in customer_orders.columns:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{customer_orders["ITEM"].nunique():,}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Unique Products</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Unique Products</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            if 'QUANTIDADEPEDIDA' in customer_orders.columns:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{customer_orders["QUANTIDADEPEDIDA"].sum():,.0f}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Total Quantity</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Total Quantity</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Time series for customer if we have date data
        date_cols = [c for c in customer_orders.columns if 'DATA' in c.upper()]
        if date_cols:
            main_date_col = next((col for col in date_cols if 'PEDIDO' in col.upper()), date_cols[0])
            
            customer_orders['year_month'] = customer_orders[main_date_col].dt.to_period('M')
            orders_by_month = customer_orders.groupby('year_month').size().reset_index(name='count')
            orders_by_month['year_month_str'] = orders_by_month['year_month'].astype(str)
            
            fig = px.line(
                orders_by_month, 
                x='year_month_str', 
                y='count',
                markers=True,
                title=f'Monthly Order Volume for Customer {selected_customer}',
                labels={'year_month_str': 'Month', 'count': 'Number of Orders'}
            )
            fig.update_layout(xaxis_tickangle=45, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Top products for this customer
        if 'ITEM' in customer_orders.columns:
            st.markdown("**Top Products for Selected Customer**")
            
            product_counts = customer_orders['ITEM'].value_counts().head(10)
            
            fig = px.bar(
                x=product_counts.index,
                y=product_counts.values,
                title=f'Top 10 Products for Customer {selected_customer}',
                labels={'x': 'Product ID', 'y': 'Number of Orders'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Customer order frequency distribution
        st.markdown("**Customer Order Frequency Distribution**")
        
        # Create frequency bins
        order_freq = orders_by_customer.reset_index()
        order_freq.columns = ['IDCLIENTE', 'OrderCount']
        
        # Create frequency categories
        bins = [0, 1, 5, 10, 20, 50, 100, 1000, float('inf')]
        labels = ['1', '2-5', '6-10', '11-20', '21-50', '51-100', '101-1000', '1000+']
        order_freq['FrequencyBin'] = pd.cut(order_freq['OrderCount'], bins=bins, labels=labels)
        
        freq_counts = order_freq['FrequencyBin'].value_counts().sort_index()
        
        fig = px.bar(
            x=freq_counts.index,
            y=freq_counts.values,
            title='Customer Distribution by Order Frequency',
            labels={'x': 'Number of Orders', 'y': 'Number of Customers'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Customer recency analysis if we have date data
        date_cols = [c for c in df_orders.columns if 'DATA' in c.upper()]
        if date_cols:
            st.markdown("**Customer Recency Analysis**")
            
            main_date_col = next((col for col in date_cols if 'PEDIDO' in col.upper()), date_cols[0])
            
            # Get the most recent order date for each customer
            customer_last_order = df_orders.groupby('IDCLIENTE')[main_date_col].max().reset_index()
            
            # Calculate days since last order
            max_date = customer_last_order[main_date_col].max()
            customer_last_order['DaysSinceLastOrder'] = (max_date - customer_last_order[main_date_col]).dt.days
            
            # Create recency bins
            bins = [0, 30, 90, 180, 365, float('inf')]
            labels = ['< 30 days', '30-90 days', '90-180 days', '180-365 days', '> 365 days']
            customer_last_order['RecencyBin'] = pd.cut(customer_last_order['DaysSinceLastOrder'], bins=bins, labels=labels)
            
            recency_counts = customer_last_order['RecencyBin'].value_counts().sort_index()
            
            fig = px.bar(
                x=recency_counts.index,
                y=recency_counts.values,
                title='Customer Distribution by Recency',
                labels={'x': 'Time Since Last Order', 'y': 'Number of Customers'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def display_comparison_analysis(df_items, df_orders):
    """Display comparison analysis between items and orders"""
    st.markdown('<div class="sub-header">Comparison Analysis: Items vs Orders</div>', unsafe_allow_html=True)
    
    # Structure comparison
    st.markdown('<div class="section-header">Data Structure Comparison</div>', unsafe_allow_html=True)
    
    # Compare columns
    cols_items = set(df_items.columns)
    cols_orders = set(df_orders.columns)
    
    common_cols = cols_items.intersection(cols_orders)
    exclusive_items = cols_items - cols_orders
    exclusive_orders = cols_orders - cols_items
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(common_cols)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Common Columns</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(exclusive_items)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Item-Only Columns</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(exclusive_orders)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Order-Only Columns</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Visualize column distribution
    fig = px.pie(
        values=[len(common_cols), len(exclusive_items), len(exclusive_orders)],
        names=['Common', 'Item-Only', 'Order-Only'],
        title='Column Distribution Between Items and Orders',
        hole=0.4
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Show column lists
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Item-Only Columns**")
        st.write(sorted(exclusive_items))
    
    with col2:
        st.markdown("**Order-Only Columns**")
        st.write(sorted(exclusive_orders))
    
    # Item coverage analysis
    st.markdown('<div class="section-header">Item Coverage Analysis</div>', unsafe_allow_html=True)
    
    if 'ITEM' in df_items.columns and 'ITEM' in df_orders.columns:
        # Convert ITEM to string in both dataframes
        df_items_item = df_items['ITEM'].astype(str)
        df_orders_item = df_orders['ITEM'].astype(str)
        
        # Get unique items in each dataset
        items_in_items = set(df_items_item.unique())
        items_in_orders = set(df_orders_item.unique())
        
        # Calculate intersections
        items_common = items_in_items.intersection(items_in_orders)
        items_only_in_items = items_in_items - items_in_orders
        items_only_in_orders = items_in_orders - items_in_items
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(items_common):,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Items in Both</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(items_only_in_items):,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Items without Orders</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(items_only_in_orders):,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Orders without Item Record</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Visualize item coverage
        fig = px.bar(
            x=['Items in Both', 'Items without Orders', 'Orders without Item Record'],
            y=[len(items_common), len(items_only_in_items), len(items_only_in_orders)],
            title='Item Coverage Analysis',
            labels={'x': 'Category', 'y': 'Count'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ITEM column not found in both datasets for coverage analysis.")
    
    # Value comparison for common columns
    st.markdown('<div class="section-header">Value Comparison for Common Attributes</div>', unsafe_allow_html=True)
    
    # Get common numeric columns
    common_numeric_cols = get_common_numeric_cols(df_orders, df_items)
    
    if common_numeric_cols:
        st.markdown("**Common Numeric Columns**")
        st.write(common_numeric_cols)
        
        # Calculate differences between orders and items
        diff_table = build_diff_table(df_orders, df_items, limit_items=1000)
        
        if not diff_table.empty:
            # Calculate statistics on differences
            diff_stats = {}
            for col in common_numeric_cols:
                diff_col = f"{col}_diff"
                diff_pct_col = f"{col}_diff_pct"
                
                if diff_col in diff_table.columns and diff_pct_col in diff_table.columns:
                    diff_stats[col] = {
                        'mean_diff': diff_table[diff_col].mean(),
                        'mean_diff_pct': diff_table[diff_pct_col].mean(),
                        'items_with_diff': (diff_table[diff_col].abs() > 0.01).sum(),
                        'pct_items_with_diff': (diff_table[diff_col].abs() > 0.01).mean() * 100
                    }
            
            if diff_stats:
                diff_stats_df = pd.DataFrame.from_dict(diff_stats, orient='index')
                
                # Display statistics
                st.markdown("**Difference Statistics**")
                
                display_df = diff_stats_df.copy()
                display_df['mean_diff_pct'] = display_df['mean_diff_pct'].round(2).astype(str) + '%'
                display_df['pct_items_with_diff'] = display_df['pct_items_with_diff'].round(2).astype(str) + '%'
                display_df.columns = ['Mean Difference', 'Mean Difference %', 'Items with Difference', 'Items with Difference %']
                
                st.dataframe(display_df, use_container_width=True)
                
                # Visualize differences
                st.markdown("**Percentage of Items with Differences**")
                
                fig = px.bar(
                    x=diff_stats_df.index,
                    y=diff_stats_df['pct_items_with_diff'],
                    title='Percentage of Items with Differences Between Orders and Catalog',
                    labels={'x': 'Attribute', 'y': 'Items with Difference (%)'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show examples of differences
                st.markdown("**Examples of Items with Significant Differences**")
                
                # Find items with large differences
                significant_diffs = diff_table[diff_table[f"{common_numeric_cols[0]}_diff_pct"].abs() > 5]
                if not significant_diffs.empty:
                    st.dataframe(significant_diffs.head(10), use_container_width=True)
                else:
                    st.info("No items with significant differences found.")
            else:
                st.info("No difference statistics could be calculated.")
        else:
            st.info("No difference data could be generated.")
    else:
        st.info("No common numeric columns found for value comparison.")
    
    # Conceptual model explanation
    st.markdown('<div class="section-header">Conceptual Data Model</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Relationship Between Items and Orders
    
    Based on the analysis, we can infer the following conceptual model:
    
    1. **Items Table (tb_itens)**
       - Contains the master catalog of all products
       - Each record represents a unique product identified by ITEM
       - Stores the current/most recent characteristics of each product
       - Functions as a reference/catalog table
    
    2. **Orders Table (tb_pedidos)**
       - Contains orders placed by customers
       - Each record represents a specific order for an item
       - Stores the characteristics of the item at the time the order was placed
       - Includes additional information such as order status, delivery dates, quantities
    
    3. **Relationship**
       - An item can have zero, one, or multiple orders
       - Each order is associated with exactly one item
       - Item characteristics may change over time, but the order maintains the characteristics from when it was placed
    
    ### Key Differences
    
    1. **Temporality**: 
       - Items: represents the current state of the product
       - Orders: represents the state of the product at the time of order (historical)
    
    2. **Exclusive Information**:
       - Orders: contains transaction information (status, dates, quantities)
       - Items: contains updated technical and production information
    
    3. **Purpose**:
       - Items: reference for available products
       - Orders: record of commercial transactions and history
    """)

if __name__ == "__main__":
    main()