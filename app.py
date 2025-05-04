import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
from pandas.api.types import CategoricalDtype

# Configuration
st.set_page_config(
    page_title="Sri Lanka Agricultural Exports",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Caches the data after first load
@st.cache_data(show_spinner=False) 
def load_export_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df

# Load the cleaned exports CSV data
df = load_export_data("./cleaned_exports.csv")

# Global CSS
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;600&display=swap');
        html, body, .stApp {
            font-family: 'Inter Tight', sans-serif;
            background-color: #043927;  /* Dark green background */
        }
        .stApp::before{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url("/app/static/images/bg.jpg");
            background-size: cover;
            background-position: center;
            opacity: 0.2; /* Adjust the opacity as needed */
            z-index: 0;
        }
            
        /* White text for headings & body */
        h1, h2, h3, h4, h5, h6, p, div, span, label, .stMetric {
            color: white !important;
        }
        /* Sidebar background image and transparency */
        [data-testid="stSidebar"] {
            background-color: rgba(0,0,0,0.0) !important;
            background-image: url("app/static/images/sidebar_bg.png");
            background-size: cover;
            background-position: center;
        }
        /* Header color match */
        header[data-testid="stHeader"] {
            background-color: #043927;
        }
        /* Make all select boxes black */
        .stSelectbox > div[data-baseweb] {
            background-color: #000000 !important;
            color: #ffffff !important;
            border-radius: 8px;
        }
        /* Change red tags to plain grey */
        span[data-baseweb="tag"] {
            background-color: #010101 !important;
            color: #333333 !important;
        }

        div[data-baseweb="tab-panel"] {
            background-color: #01010190;
            padding: 10px;
            border-radius: 8px;
            margin-top: 20px;
            margin-bottom: 20px;
        } 
          
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/11/Flag_of_Sri_Lanka.svg", width=70)
    st.title("🌾 Sri Lanka Exports")

    # Create the radio navigation
    page = st.radio("Navigate", ["Overview", "Trends", "About"])


# Overview
if page == "Overview":
    st.markdown("<h1 style='text-align: center;'>🌾 Sri Lanka Agricultural Exports</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Overview</h2>", unsafe_allow_html=True)
    st.write("### Snippet of the Dataset")
    st.dataframe(df.head(20))
    st.write("### Descriptive Statistics")
    st.dataframe(df.describe())

    st.markdown("<h3 style='text-align: center;'>Export Distribution by Product</h3>", unsafe_allow_html=True)
    fig = px.pie(
        df, 
        names='Product', 
        values='Exports (US Mn)', 
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        title=dict(
            text="<b>Export Distribution Pie Chart</b>",
            x=0.5,
            xanchor='center',
            font=dict(size=22, color="dark grey", family="Arial")
        ),
        font=dict(size=18),
        paper_bgcolor='rgba(0, 0, 0, 0.75)',
        legend=dict(
            orientation="h",
            y=0.5,
            x=0.85,
            xanchor="center",
            yanchor="middle",
            font=dict(size=18),
            bordercolor="Black",
            borderwidth=1
        )
    )
    fig.update_traces(
        textinfo='label+percent',  
        hoverinfo='label+percent+value', 
        marker=dict(line=dict(color='#000000', width=1)) 
    )
    st.plotly_chart(fig, use_container_width=True)

# Trends Page
elif page == "Trends":
    st.markdown("<h2 style='text-align: center;'>📈 Production and Export Trends</h2>", unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center;'>Performance Metrics</h3>", unsafe_allow_html=True)
    total_production = df['Production (Mn.Kg/Nuts)'].sum()
    total_exports = df['Exports (US Mn)'].sum()
    top_product = df.groupby('Product')['Exports (US Mn)'].sum().idxmax()
    top_product_value = df.groupby('Product')['Exports (US Mn)'].sum().max()

    kpi_cols = st.columns(3, gap="large")
    with kpi_cols[0]:
        st.metric("Total Production", f"{int(total_production):,} Mn.Kg/Nuts")
    with kpi_cols[1]:
        st.metric("Total Exports", f"${int(total_exports):,}M")
    with kpi_cols[2]:
        st.metric("Top Export", f"{top_product} (${int(top_product_value):,}M)")

    st.markdown("<hr style='margin: 2rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

    st.markdown("### Filter Data")
    with st.form(key='trends_form'):
        filter_col1, filter_col2 = st.columns([2, 1])
        with filter_col1:
            product_filter = st.multiselect(
                "Select Product(s):", 
                options=df['Product'].unique().tolist(), 
                default=df['Product'].unique().tolist(),
                help="Choose one or more products to filter the data."
            )
        with filter_col2:
            year_filter = st.multiselect(
                "Select Year(s):", 
                options=sorted(df['Year'].unique()), 
                default=sorted(df['Year'].unique()),
                help="Choose one or more years to filter the data."
            )
        apply_button = st.form_submit_button(label='Apply Filters') 

    # Only show charts after clicking apply
    if apply_button:
        filtered_df = df[(df['Product'].isin(product_filter)) & (df['Year'].isin(year_filter))]

        if filtered_df.empty:
            st.warning("No data available for the selected filters. Please adjust your selection.")
        else:
            tab1, tab2, tab3, tab4 = st.tabs(["Annual Production and Exports", "Average Monthly Production", "Production Vs Exports", "Cumulative exports"])

        with tab1:
            yearly_data = filtered_df.groupby(['Year', 'Product'])[['Production (Mn.Kg/Nuts)', 'Exports (US Mn)']].sum().reset_index()

            # Line chart for Production
            st.subheader("Line Chart: Annual Production")
            fig1_prod = px.line(
                yearly_data, 
                x='Year', 
                y='Production (Mn.Kg/Nuts)', 
                color='Product',
                markers=True,
                title="Yearly Trends of Production by Product",
                labels={'Production (Mn.Kg/Nuts)': 'Production (Mn.Kg/Nuts)'},
                color_discrete_sequence=px.colors.qualitative.Dark24  # Darker shades for lines
            )
            fig1_prod.update_layout(
                title=dict(
                    text="<b>Yearly Trends of Production by Product</b>",
                    x=0.5,
                    xanchor='center',
                    font=dict(size=24, color="dark grey", family="Arial")  # Bigger font and dark gray color
                ),
                xaxis_title="Year",
                yaxis_title="Production (Mn.Kg/Nuts)",
                paper_bgcolor='rgba(0, 0, 0, 0.75)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                legend=dict(
                    font=dict(size=16) 
                )
            )
            st.plotly_chart(fig1_prod, use_container_width=True)

            # Line chart for Exports
            st.subheader("Line Chart: Annual Exports")
            fig1_exp = px.line(
                yearly_data, 
                x='Year', 
                y='Exports (US Mn)', 
                color='Product',
                markers=True,
                title="Yearly Trends of Exports by Product",
                labels={'Exports (US Mn)': 'Exports (US Mn)'},
                color_discrete_sequence=px.colors.qualitative.Dark24
            )
            fig1_exp.update_layout(
                title=dict(
                    text="<b>Yearly Trends of Exports by Product</b>",
                    x=0.5,
                    xanchor='center',
                    font=dict(size=24, color="dark grey", family="Arial")
                ),
                xaxis_title="Year",
                yaxis_title="Exports (US Mn)",
                paper_bgcolor='rgba(0, 0, 0, 0.75)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                legend=dict(
                    font=dict(size=16) 
                )
            )
            st.plotly_chart(fig1_exp, use_container_width=True)
            
        with tab2:
            # Calculate average production for each month across all years and products
            avg_monthly_production = filtered_df.groupby(['Month'])['Production (Mn.Kg/Nuts)'].mean().reset_index()
            month_order = list(calendar.month_name[1:])  # Define month_order as a list of month names
            avg_monthly_production['Month'] = pd.Categorical(avg_monthly_production['Month'], categories=month_order, ordered=True)
            avg_monthly_production = avg_monthly_production.sort_values('Month')  # Sort by calendar order

            # Create bar chart for average monthly production
            st.subheader("Bar Chart: Average Monthly Production")
            fig3 = px.bar(
                avg_monthly_production,
                x='Month',
                y='Production (Mn.Kg/Nuts)',
                title="Bar Chart of Average Monthly Production",
                labels={'Production (Mn.Kg/Nuts)': 'Average Production (Mn.Kg/Nuts)', 'Month': 'Month'},
                color_discrete_sequence=['#3B444B']  # Set a consistent color
            )
            fig3.update_layout(
                title=dict(
                    text="<b>Bar Chart of Average Monthly Production</b>",
                    x=0.5,
                    xanchor='center',
                    font=dict(size=24, color="black", family="Arial")  # Bigger font and black color
                ),
                xaxis_title="Month",
                yaxis_title="Average Production (Mn.Kg/Nuts)",
                paper_bgcolor='rgba(0, 0, 0, 0.75)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                xaxis=dict(
                    title_font=dict(color="black"),
                    tickfont=dict(color="black")
                ),
                yaxis=dict(
                    title_font=dict(color="black"),
                    tickfont=dict(color="black")
                ),
                legend=dict(
                    font=dict(size=14, color="black")
                )
            )
            st.plotly_chart(fig3, use_container_width=True)

            # Create bar chart for average monthly exports
            avg_monthly_exports = filtered_df.groupby(['Month'])['Exports (US Mn)'].mean().reset_index()
            avg_monthly_exports['Month'] = pd.Categorical(avg_monthly_exports['Month'], categories=month_order, ordered=True)
            avg_monthly_exports = avg_monthly_exports.sort_values('Month')

            st.subheader("Bar Chart: Average Monthly Exports")
            fig4 = px.bar(
                avg_monthly_exports,
                x='Month',
                y='Exports (US Mn)',
                title="Bar Chart of Average Monthly Exports",
                labels={'Exports (US Mn)': 'Average Exports (US Mn)', 'Month': 'Month'},
                color_discrete_sequence=['#3B444B']  # Set a consistent color
            )
            fig4.update_layout(
                title=dict(
                    text="<b>Bar Chart of Average Monthly Exports</b>",
                    x=0.5,
                    xanchor='center',
                    font=dict(size=24, color="black", family="Arial")  # Bigger font and black color
                ),
                xaxis_title="Month",
                yaxis_title="Average Exports (US Mn)",
                paper_bgcolor='rgba(0, 0, 0, 0.75)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                xaxis=dict(
                    title_font=dict(color="black"),
                    tickfont=dict(color="black")
                ),
                yaxis=dict(
                    title_font=dict(color="black"),
                    tickfont=dict(color="black")
                ),
                legend=dict(
                    font=dict(size=14, color="black")
                )
            )
            st.plotly_chart(fig4, use_container_width=True)


        with tab3:
            st.markdown("<h3 style='text-align: center; color: black;'>Bubble Chart: Production vs Exports</h3>", unsafe_allow_html=True)
            fig4 = px.scatter(
            filtered_df,
            x='Production (Mn.Kg/Nuts)',
            y='Exports (US Mn)',
            size='Year',  # Bubble size representing year
            color='Product',  # Color representing different products
            hover_name='Product',
            title="Production vs Exports Bubble Chart",
            labels={'Production (Mn.Kg/Nuts)': 'Production (Mn.Kg/Nuts)', 'Exports (US Mn)': 'Exports (US Mn)'},
            size_max=60
            )
            fig4.update_layout(
            xaxis_title="Production (Mn.Kg/Nuts)",
            yaxis_title="Exports (US Mn)",
            title=dict(
                text="<b>Production vs Exports Bubble Chart</b>",
                x=0.5,
                xanchor='center',
                font=dict(size=24, color="black", family="Arial")
            ),
            xaxis=dict(
                title_font=dict(color="black"),
                tickfont=dict(color="black")
            ),
            yaxis=dict(
                title_font=dict(color="black"),
                tickfont=dict(color="black")
            ),
            paper_bgcolor='rgba(0, 0, 0, 0.75)',
            plot_bgcolor='rgba(0, 0, 0, 0)'
            )
            st.plotly_chart(fig4, use_container_width=True)

        with tab4:
            # Ensure months are in calendar order
            filtered_df['Month_Parsed'] = pd.Categorical(
                filtered_df['Month'], categories=month_order, ordered=True
            )

            # Group data by Month and Product for cumulative exports
            cumulative_exports = filtered_df.groupby(['Month_Parsed', 'Product'])['Exports (US Mn)'].sum().reset_index()

            # Create stacked area chart
            st.markdown("<h3 style='text-align: center; color: black;'>Stacked Area Chart: Cumulative Monthly Exports</h3>", unsafe_allow_html=True)
            fig5 = px.area(
                cumulative_exports,
                x='Month_Parsed',
                y='Exports (US Mn)',
                color='Product',
                title="Cumulative Monthly Exports by Product",
                labels={'Month_Parsed': 'Month', 'Exports (US Mn)': 'Exports (US Mn)'},
                color_discrete_sequence=px.colors.qualitative.Set2
            )

            fig5.update_layout(
                title=dict(
                    text="<b>Cumulative Monthly Exports by Product</b>",
                    x=0.5,
                    xanchor='center',
                    font=dict(size=24, color="black", family="Arial")
                ),
                xaxis_title="Month",
                yaxis_title="Cumulative Exports (US Mn)",
                xaxis=dict(
                    title_font=dict(color="black"),
                    tickfont=dict(color="black")
                ),
                yaxis=dict(
                    title_font=dict(color="black"),
                    tickfont=dict(color="black")
                ),
                legend=dict(
                    font=dict(size=14, color="black")
                ),
                paper_bgcolor='rgba(0, 0, 0, 0.75)',
                plot_bgcolor='rgba(0, 0, 0, 0)'
            )

            st.plotly_chart(fig5, use_container_width=True)
   

# About Page
elif page == "About":
    st.markdown("<h1 style='text-align: center;'>📖 About</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div style='color: white; font-size: 16px; line-height: 1.7;'>

    ### Objectives of the Dashboard  
    The primary objectives of this dashboard are to:

    -  **Visualize agricultural production and export trends** across Sri Lanka.  
    -  **Identify top-performing products** by export revenue.  
    -  **Compare monthly and annual trends** for Tea, Coconut, and Rubber.  
    -  **Support decision-makers** with clear, data-driven insights.  
    -  **Provide students and researchers** with an interactive view of trade data.  

    These objectives align with the broader goal of supporting **economic analysis, export planning**, and **data transparency** for Sri Lanka’s agriculture sector.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: left; color: white;'>About This Project</h3>", unsafe_allow_html=True)

    st.markdown("""
    <div style='color: white; font-size: 16px; line-height: 1.7;    background-color: #01010190;
            padding: 10px;
            border-radius: 8px;
            margin-top: 20px;
            margin-bottom: 20px;'>


    Built using **Streamlit**, it includes visualizations like:
    - Pie charts for export distribution
    - Line charts for production and export trends
    - Bar charts for average monthly production and exports
    - Bubble charts for production vs. exports
    - Stacked area charts for cumulative monthly exports
    - Interactive filters for product and year selection
    - Responsive design for various devices
    The dashboard is designed to be user-friendly, allowing users to explore the data interactively. It provides a comprehensive overview of Sri Lanka's agricultural exports, focusing on Tea, Coconut, and Rubber.
  
    ### Technologies Used
    - **Streamlit**: For building the web application.
    - **Plotly**: For creating interactive visualizations.
    - **Pandas**: For data manipulation and analysis.
    - **Python**: The programming language used for development.
    - **HTML/CSS**: For custom styling and layout.
    - **GitHub**: For version control and collaboration.
    - **Google Colab**: For initial data analysis and cleaning.

    ### Data Source  
    - Custom dataset compiled from the Sri Lanka Central Bank Monthly Economic Indicators 
    - Background image in sidebar: https://www.travelmole.com/wp-content/uploads/2022/08/SriLanka.jpg  
    - Background image: https://www.pexels.com/photo/scenic-view-of-wheat-field-against-sky-321542            

    #### Created By  
    **Ranudi Perera**  
    BSc (Hons) Business Data Analytics  
    University of Westminster | IIT Sri Lanka  
    GitHub: https://github.com/ranudiperera
    </div>
    """, unsafe_allow_html=True)