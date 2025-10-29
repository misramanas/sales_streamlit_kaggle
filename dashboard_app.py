"""
E-Commerce Sales Dashboard
Interactive dashboard built with Streamlit
Author: Manas Misra
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Cache the data loading
@st.cache_data
def load_data():
    df = pd.read_csv('sales_data.csv')
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df['Month'] = df['Order_Date'].dt.month
    df['Month_Name'] = df['Order_Date'].dt.strftime('%B')
    df['Year'] = df['Order_Date'].dt.year
    return df

# Load data
df = load_data()

# Sidebar - Filters
st.sidebar.header("📌 Filters")

# Date range filter
min_date = df['Order_Date'].min()
max_date = df['Order_Date'].max()

start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

# Category filter
categories = st.sidebar.multiselect(
    "Select Categories",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Region filter
regions = st.sidebar.multiselect(
    "Select Regions",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

# Customer Segment filter
segments = st.sidebar.multiselect(
    "Select Customer Segments",
    options=df['Customer_Segment'].unique(),
    default=df['Customer_Segment'].unique()
)

# Apply filters
df_filtered = df[
    (df['Order_Date'] >= pd.to_datetime(start_date)) &
    (df['Order_Date'] <= pd.to_datetime(end_date)) &
    (df['Category'].isin(categories)) &
    (df['Region'].isin(regions)) &
    (df['Customer_Segment'].isin(segments))
]

# Main Dashboard
st.title("📊 E-Commerce Sales Dashboard")
st.markdown("### Real-time Sales Analytics & Insights")
st.markdown("---")

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = df_filtered['Final_Price'].sum()
    st.metric(
        label="💰 Total Revenue",
        value=f"${total_revenue:,.0f}",
        delta=f"{len(df_filtered)} orders"
    )

with col2:
    avg_order_value = df_filtered['Final_Price'].mean()
    st.metric(
        label="📈 Avg Order Value",
        value=f"${avg_order_value:,.2f}",
        delta=f"{df_filtered['Quantity'].sum()} items"
    )

with col3:
    total_customers = len(df_filtered)
    st.metric(
        label="👥 Total Orders",
        value=f"{total_customers:,}",
        delta=f"{len(df_filtered['Customer_Segment'].unique())} segments"
    )

with col4:
    discount_amount = df_filtered['Discount_Amount'].sum()
    st.metric(
        label="🎁 Total Discounts",
        value=f"${discount_amount:,.0f}",
        delta=f"{(df_filtered['Discount_Percent'] > 0).sum()} orders"
    )

st.markdown("---")

# Row 1: Sales by Category and Monthly Trend
col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Revenue by Category")
    category_data = df_filtered.groupby('Category')['Final_Price'].sum().sort_values(ascending=True)

    fig_category = px.bar(
        x=category_data.values,
        y=category_data.index,
        orientation='h',
        labels={'x': 'Revenue ($)', 'y': 'Category'},
        color=category_data.values,
        color_continuous_scale='Blues'
    )
    fig_category.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Revenue ($)",
        yaxis_title="Category"
    )
    st.plotly_chart(fig_category, use_container_width=True)

with col2:
    st.subheader("📅 Monthly Sales Trend")
    monthly_data = df_filtered.groupby('Month')['Final_Price'].sum().reset_index()

    fig_monthly = px.line(
        monthly_data,
        x='Month',
        y='Final_Price',
        markers=True,
        labels={'Final_Price': 'Revenue ($)', 'Month': 'Month'}
    )
    fig_monthly.update_traces(line_color='#00CC96', line_width=3, marker=dict(size=10))
    fig_monthly.update_layout(height=400)
    st.plotly_chart(fig_monthly, use_container_width=True)

# Row 2: Regional Performance and Customer Segments
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌍 Regional Distribution")
    region_data = df_filtered.groupby('Region')['Final_Price'].sum()

    fig_region = px.pie(
        values=region_data.values,
        names=region_data.index,
        hole=0.4
    )
    fig_region.update_traces(textposition='inside', textinfo='percent+label')
    fig_region.update_layout(height=400)
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    st.subheader("👤 Customer Segments")
    segment_data = df_filtered.groupby('Customer_Segment')['Final_Price'].sum().sort_values(ascending=False)

    fig_segment = px.bar(
        x=segment_data.index,
        y=segment_data.values,
        labels={'x': 'Customer Segment', 'y': 'Revenue ($)'},
        color=segment_data.index,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_segment.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Customer Segment",
        yaxis_title="Revenue ($)"
    )
    st.plotly_chart(fig_segment, use_container_width=True)

# Row 3: Payment Methods and Top Products
col1, col2 = st.columns(2)

with col1:
    st.subheader("💳 Payment Methods")
    payment_data = df_filtered['Payment_Method'].value_counts()

    fig_payment = go.Figure(data=[go.Bar(
        x=payment_data.values,
        y=payment_data.index,
        orientation='h',
        marker=dict(
            color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
        )
    )])
    fig_payment.update_layout(
        height=400,
        xaxis_title="Number of Orders",
        yaxis_title="Payment Method",
        showlegend=False
    )
    st.plotly_chart(fig_payment, use_container_width=True)

with col2:
    st.subheader("🏆 Top 10 Products")
    top_products = df_filtered.groupby('Product')['Final_Price'].sum().sort_values(ascending=False).head(10)

    fig_products = px.bar(
        x=top_products.values,
        y=top_products.index,
        orientation='h',
        labels={'x': 'Revenue ($)', 'y': 'Product'},
        color=top_products.values,
        color_continuous_scale='Viridis'
    )
    fig_products.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Revenue ($)",
        yaxis_title="Product"
    )
    st.plotly_chart(fig_products, use_container_width=True)

# Row 4: Detailed Data Table
st.markdown("---")
st.subheader("📋 Detailed Sales Data")

# Show dataframe with formatting
st.dataframe(
    df_filtered[['Order_Date', 'Category', 'Product', 'Final_Price', 'Quantity', 
                 'Customer_Segment', 'Region', 'Payment_Method']].head(100),
    use_container_width=True,
    height=400
)

# Download button
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=df_filtered.to_csv(index=False).encode('utf-8'),
    file_name='filtered_sales_data.csv',
    mime='text/csv',
)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>📊 Sales Dashboard | Built with Streamlit & Plotly | Data updates in real-time</p>
    </div>
    """, unsafe_allow_html=True)
