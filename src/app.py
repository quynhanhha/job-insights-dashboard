# src/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import os
from datetime import datetime

# Import skill extraction from analyze module
try:
    # Try relative import first (when running as module)
    from .analyze import (
        normalize_text, 
        extract_skills, 
        ALL_SKILLS,
        PROGRAMMING_LANGUAGES,
        FRAMEWORKS_LIBRARIES,
        CLOUD_PLATFORMS,
        DATABASES,
        TOOLS_TECHNOLOGIES
    )
except ImportError:
    # Fall back to absolute import (when running directly)
    from analyze import (
        normalize_text, 
        extract_skills, 
        ALL_SKILLS,
        PROGRAMMING_LANGUAGES,
        FRAMEWORKS_LIBRARIES,
        CLOUD_PLATFORMS,
        DATABASES,
        TOOLS_TECHNOLOGIES
    )

# Page config
st.set_page_config(
    page_title="Job Insights Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load job data from CSV."""
    try:
        df = pd.read_csv("data/jobs_merged.csv")
        return df
    except FileNotFoundError:
        st.error("❌ data/jobs_merged.csv not found. Please run `python3 -m src.fetch_jobs` first.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return pd.DataFrame()

def get_file_timestamp():
    """Get last modified time of data file."""
    try:
        if os.path.exists("data/jobs_merged.csv"):
            timestamp = os.path.getmtime("data/jobs_merged.csv")
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return "Unknown"
    except:
        return "Unknown"

@st.cache_data
def prepare_data(df):
    """Prepare data with derived columns (cached for performance)."""
    if df.empty:
        return df
    df = df.copy()
    df['title_normalized'] = df['title'].apply(normalize_text)
    df['role_category'] = df['title'].apply(categorize_role)
    return df

@st.cache_data
def extract_skills_from_df(df):
    """Extract all skills from dataframe (cached for performance)."""
    all_skills = []
    prog_langs = []
    frameworks = []
    cloud = []
    databases = []
    
    for text in df['title_normalized']:
        all_skills.extend(extract_skills(text, ALL_SKILLS))
        prog_langs.extend(extract_skills(text, PROGRAMMING_LANGUAGES))
        frameworks.extend(extract_skills(text, FRAMEWORKS_LIBRARIES))
        cloud.extend(extract_skills(text, CLOUD_PLATFORMS))
        databases.extend(extract_skills(text, DATABASES))
    
    return {
        'all': Counter(all_skills),
        'programming': Counter(prog_langs),
        'frameworks': Counter(frameworks),
        'cloud': Counter(cloud),
        'databases': Counter(databases)
    }

def categorize_role(title: str) -> str:
    """Categorize job title into role buckets."""
    if not title or not isinstance(title, str):
        return "Other"
    
    title_lower = title.lower()
    
    # Check in order of specificity
    if any(word in title_lower for word in ['data scientist', 'machine learning', 'ml engineer', 'ai ']):
        return "Data Science & ML"
    elif any(word in title_lower for word in ['data analyst', 'business intelligence', 'analytics']):
        return "Data Analytics"
    elif any(word in title_lower for word in ['data engineer', 'data architect', 'etl']):
        return "Data Engineering"
    elif any(word in title_lower for word in ['business analyst', 'systems analyst', 'functional analyst']):
        return "Business Analysis"
    elif any(word in title_lower for word in ['software engineer', 'software developer', 'developer', 'engineer', 'programmer']):
        return "Software Engineering"
    elif any(word in title_lower for word in ['devops', 'sre', 'infrastructure', 'cloud']):
        return "DevOps & Infrastructure"
    elif any(word in title_lower for word in ['qa', 'test', 'quality assurance']):
        return "QA & Testing"
    elif any(word in title_lower for word in ['support', 'help desk', 'service desk', 'technical support']):
        return "IT Support"
    elif any(word in title_lower for word in ['security', 'cybersecurity', 'infosec']):
        return "Cybersecurity"
    elif any(word in title_lower for word in ['product manager', 'product owner']):
        return "Product Management"
    elif any(word in title_lower for word in ['project manager', 'program manager', 'scrum master']):
        return "Project Management"
    else:
        return "Other"

def extract_all_skills_from_text(text: str) -> list:
    """Extract all skills from text."""
    return extract_skills(text, ALL_SKILLS)

# Main app
def main():
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="main-header">💼 Job Insights Dashboard</div>', unsafe_allow_html=True)
        st.markdown("Explore tech job opportunities and skill trends across Australia")
    with col2:
        last_updated = get_file_timestamp()
        st.markdown(f"**Last Updated:**  \n{last_updated}")
    
    # Load data
    with st.spinner('Loading data...'):
        df = load_data()
    
    if df.empty:
        st.stop()
    
    # Prepare data (cached)
    df = prepare_data(df)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Data summary
    st.sidebar.info(f"**Total Dataset:** {len(df)} jobs")
    
    # Reset filters button
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Source filter
    sources = sorted(df['source'].unique())
    selected_sources = st.sidebar.multiselect(
        "Job Sources",
        options=sources,
        default=sources,
        help="Select one or more job sources"
    )
    
    # Role bucket filter
    roles = sorted(df['role_category'].unique())
    selected_roles = st.sidebar.multiselect(
        "Role Categories",
        options=roles,
        default=roles,
        help="Select job categories to analyze"
    )
    
    # Min count slider for skill frequency
    min_skill_count = st.sidebar.slider(
        "Min Skill Mentions",
        min_value=1,
        max_value=20,
        value=1,
        help="Show skills mentioned at least this many times"
    )
    
    # Location filter
    locations = ['All'] + sorted([loc for loc in df['location'].unique() if pd.notna(loc)])
    selected_location = st.sidebar.selectbox(
        "Location",
        options=locations,
        help="Filter by location"
    )
    
    st.sidebar.markdown("---")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_sources:
        filtered_df = filtered_df[filtered_df['source'].isin(selected_sources)]
    
    if selected_roles:
        filtered_df = filtered_df[filtered_df['role_category'].isin(selected_roles)]
    
    if selected_location != 'All':
        filtered_df = filtered_df[filtered_df['location'] == selected_location]
    
    # Filter summary in sidebar
    st.sidebar.success(f"**Filtered Results:** {len(filtered_df)} jobs")
    
    # Check if filtered data is empty
    if filtered_df.empty:
        st.warning("⚠️ No jobs match the selected filters. Please adjust your filters.")
        st.stop()
    
    # KPI Row
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{len(filtered_df)}</div>
            <div class="kpi-label">Total Jobs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        distinct_companies = filtered_df['company'].nunique()
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{distinct_companies}</div>
            <div class="kpi-label">Companies</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        distinct_locations = filtered_df['location'].nunique()
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{distinct_locations}</div>
            <div class="kpi-label">Locations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        distinct_roles = filtered_df['role_category'].nunique()
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{distinct_roles}</div>
            <div class="kpi-label">Role Types</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Extract skills from filtered data (use cached function for performance)
    with st.spinner('Analyzing skills...'):
        skill_data = extract_skills_from_df(filtered_df)
        skill_counts = skill_data['all']
    
    # Filter by min count
    filtered_skills = {skill: count for skill, count in skill_counts.items() if count >= min_skill_count}
    
    # Charts Row 1
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💻 Top Skills")
        
        if filtered_skills:
            # Get top 15 skills
            top_skills = sorted(filtered_skills.items(), key=lambda x: x[1], reverse=True)[:15]
            skills_df = pd.DataFrame(top_skills, columns=['Skill', 'Count'])
            
            fig = px.bar(
                skills_df,
                x='Count',
                y='Skill',
                orientation='h',
                color='Count',
                color_continuous_scale='Blues',
                title=f"Top 15 Skills (min {min_skill_count} mentions)"
            )
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False,
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No skills found with at least {min_skill_count} mentions. Try lowering the minimum count.")
    
    with col2:
        st.markdown("### 📈 Jobs by Source")
        
        source_counts = filtered_df['source'].value_counts()
        
        fig = px.pie(
            values=source_counts.values,
            names=source_counts.index,
            title="Distribution by Source",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Role Distribution")
        
        role_counts = filtered_df['role_category'].value_counts().head(10)
        
        fig = px.bar(
            x=role_counts.values,
            y=role_counts.index,
            orientation='h',
            labels={'x': 'Number of Jobs', 'y': 'Role Category'},
            title="Top 10 Role Categories",
            color=role_counts.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🏢 Top Companies")
        
        company_counts = filtered_df['company'].value_counts().head(10)
        
        fig = px.bar(
            x=company_counts.values,
            y=company_counts.index,
            orientation='h',
            labels={'x': 'Number of Jobs', 'y': 'Company'},
            title="Top 10 Hiring Companies",
            color=company_counts.values,
            color_continuous_scale='Teal'
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Skill Category Breakdown
    st.markdown("### 🔧 Skills by Category")
    
    # Use cached skill data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**Programming Languages**")
        prog_lang_counts = skill_data['programming'].most_common(5)
        if prog_lang_counts:
            for skill, count in prog_lang_counts:
                st.write(f"• {skill.title()}: {count}")
        else:
            st.write("None detected")
    
    with col2:
        st.markdown("**Frameworks**")
        framework_counts = skill_data['frameworks'].most_common(5)
        if framework_counts:
            for skill, count in framework_counts:
                st.write(f"• {skill.title()}: {count}")
        else:
            st.write("None detected")
    
    with col3:
        st.markdown("**Cloud & DevOps**")
        cloud_counts = skill_data['cloud'].most_common(5)
        if cloud_counts:
            for skill, count in cloud_counts:
                st.write(f"• {skill.upper()}: {count}")
        else:
            st.write("None detected")
    
    with col4:
        st.markdown("**Databases**")
        db_counts = skill_data['databases'].most_common(5)
        if db_counts:
            for skill, count in db_counts:
                st.write(f"• {skill.upper()}: {count}")
        else:
            st.write("None detected")
    
    st.markdown("---")
    
    # Jobs Table
    st.markdown("### 📋 Job Listings")
    
    # Display options
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_query = st.text_input("🔎 Search jobs", placeholder="Enter keywords...")
    with col2:
        n_jobs = st.selectbox("Show", options=[10, 25, 50, 100], index=0)
    with col3:
        # Export button
        csv_export = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export",
            data=csv_export,
            file_name=f"jobs_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            help="Download filtered data as CSV"
        )
    
    # Apply search filter
    display_df = filtered_df.copy()
    if search_query:
        mask = (
            display_df['title'].str.contains(search_query, case=False, na=False) |
            display_df['company'].str.contains(search_query, case=False, na=False) |
            display_df['location'].str.contains(search_query, case=False, na=False)
        )
        display_df = display_df[mask]
    
    # Prepare display columns
    display_cols = ['title', 'company', 'location', 'source', 'role_category', 'url']
    display_df = display_df[display_cols].head(n_jobs)
    
    # Format the dataframe for display
    display_df = display_df.rename(columns={
        'title': 'Job Title',
        'company': 'Company',
        'location': 'Location',
        'source': 'Source',
        'role_category': 'Category',
        'url': 'URL'
    })
    
    # Convert URLs to clickable links
    display_df['URL'] = display_df['URL'].apply(
        lambda x: f'<a href="{x}" target="_blank">View Job</a>' if pd.notna(x) else ''
    )
    
    # Display table
    st.markdown(
        display_df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )
    
    st.markdown(f"*Showing {len(display_df)} of {len(filtered_df)} jobs*")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>💼 Job Insights Dashboard | Data sources: Prosple, Workforce AU</p>
        <p>Built with Streamlit | Last updated: Check data/jobs_merged.csv timestamp</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

