# src/analyze.py
import csv
import re
from collections import Counter
from typing import List, Dict, Set
import pandas as pd

# Curated skill dictionaries
PROGRAMMING_LANGUAGES = {
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'csharp', 'c', 
    'ruby', 'php', 'swift', 'kotlin', 'go', 'golang', 'rust', 'scala', 
    'r', 'matlab', 'perl', 'shell', 'bash', 'powershell', 'sql', 'html', 'css'
}

FRAMEWORKS_LIBRARIES = {
    'react', 'reactjs', 'react.js', 'angular', 'vue', 'vuejs', 'vue.js',
    'node', 'nodejs', 'node.js', 'express', 'django', 'flask', 'fastapi',
    'spring', 'spring boot', '.net', 'dotnet', 'asp.net',
    'jquery', 'bootstrap', 'tailwind', 'next.js', 'nextjs',
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
    'redux', 'graphql', 'rest', 'restful'
}

CLOUD_PLATFORMS = {
    'aws', 'azure', 'gcp', 'google cloud', 'cloud', 'docker', 'kubernetes',
    'jenkins', 'terraform', 'ansible', 'gitlab', 'github', 'bitbucket',
    'ci/cd', 'devops'
}

DATABASES = {
    'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'cassandra',
    'oracle', 'sql server', 'dynamodb', 'elasticsearch', 'sqlite',
    'nosql', 'database', 'db2', 'mariadb'
}

TOOLS_TECHNOLOGIES = {
    'git', 'jira', 'confluence', 'slack', 'agile', 'scrum', 'kanban',
    'linux', 'unix', 'windows', 'macos', 'api', 'microservices',
    'machine learning', 'ml', 'ai', 'artificial intelligence', 'data science',
    'big data', 'etl', 'data warehouse', 'business intelligence', 'bi',
    'power bi', 'tableau', 'excel', 'spark', 'hadoop', 'kafka'
}

METHODOLOGIES = {
    'agile', 'scrum', 'kanban', 'waterfall', 'lean', 'six sigma',
    'test driven development', 'tdd', 'behavior driven development', 'bdd'
}

SOFT_SKILLS = {
    'communication', 'teamwork', 'problem solving', 'analytical', 'leadership',
    'collaboration', 'critical thinking', 'time management', 'adaptability',
    'creativity', 'attention to detail', 'organizational', 'presentation'
}

# Combine all skills
ALL_SKILLS = (
    PROGRAMMING_LANGUAGES | 
    FRAMEWORKS_LIBRARIES | 
    CLOUD_PLATFORMS | 
    DATABASES | 
    TOOLS_TECHNOLOGIES | 
    METHODOLOGIES | 
    SOFT_SKILLS
)

def normalize_text(text: str) -> str:
    """
    Normalize text: lowercase, strip punctuation (except necessary ones).
    Preserve dots in abbreviations like 'node.js', 'asp.net'
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_skills(text: str, skill_dict: Set[str]) -> List[str]:
    """
    Extract skills from text using regex word boundaries.
    """
    if not text:
        return []
    
    normalized = normalize_text(text)
    found_skills = []
    
    for skill in skill_dict:
        # Create pattern with word boundaries
        # For multi-word skills, use \b at start and end
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, normalized):
            found_skills.append(skill)
    
    return found_skills

def load_jobs(csv_path: str = "data/jobs_merged.csv") -> pd.DataFrame:
    """
    Load jobs from CSV file.
    """
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} jobs from {csv_path}")
        return df
    except FileNotFoundError:
        print(f"Error: {csv_path} not found. Run fetch_jobs.py first.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return pd.DataFrame()

def analyze_jobs(df: pd.DataFrame) -> Dict:
    """
    Analyze jobs and extract insights.
    Returns a dictionary with various statistics and skill frequencies.
    """
    if df.empty:
        return {}
    
    # Normalize text fields
    df['title_normalized'] = df['title'].apply(normalize_text)
    df['company_normalized'] = df['company'].apply(normalize_text)
    df['location_normalized'] = df['location'].apply(normalize_text)
    df['description_normalized'] = df['description'].apply(normalize_text)
    
    # Combine title and description for skill extraction
    df['searchable_text'] = df['title_normalized'] + ' ' + df['description_normalized'].fillna('')
    
    # Extract skills
    all_programming_langs = []
    all_frameworks = []
    all_cloud = []
    all_databases = []
    all_tools = []
    
    for text in df['searchable_text']:
        all_programming_langs.extend(extract_skills(text, PROGRAMMING_LANGUAGES))
        all_frameworks.extend(extract_skills(text, FRAMEWORKS_LIBRARIES))
        all_cloud.extend(extract_skills(text, CLOUD_PLATFORMS))
        all_databases.extend(extract_skills(text, DATABASES))
        all_tools.extend(extract_skills(text, TOOLS_TECHNOLOGIES))
    
    # Create frequency counters
    results = {
        'total_jobs': len(df),
        'sources': df['source'].value_counts().to_dict(),
        'top_companies': df['company'].value_counts().head(20).to_dict(),
        'top_locations': df['location'].value_counts().head(20).to_dict(),
        'programming_languages': Counter(all_programming_langs).most_common(20),
        'frameworks': Counter(all_frameworks).most_common(20),
        'cloud_platforms': Counter(all_cloud).most_common(15),
        'databases': Counter(all_databases).most_common(15),
        'tools_technologies': Counter(all_tools).most_common(20),
    }
    
    return results

def print_analysis(results: Dict):
    """
    Pretty print analysis results.
    """
    if not results:
        print("No results to display.")
        return
    
    print("\n" + "=" * 70)
    print("JOB INSIGHTS ANALYSIS")
    print("=" * 70)
    
    print(f"\n📊 TOTAL JOBS: {results['total_jobs']}")
    
    print("\n📍 JOBS BY SOURCE:")
    for source, count in results['sources'].items():
        print(f"  {source:15s}: {count:4d} jobs")
    
    print("\n🏢 TOP 10 COMPANIES:")
    for i, (company, count) in enumerate(list(results['top_companies'].items())[:10], 1):
        if company:
            print(f"  {i:2d}. {company:40s}: {count:3d} jobs")
    
    print("\n📍 TOP 10 LOCATIONS:")
    for i, (location, count) in enumerate(list(results['top_locations'].items())[:10], 1):
        if location:
            print(f"  {i:2d}. {location:40s}: {count:3d} jobs")
    
    print("\n💻 TOP 15 PROGRAMMING LANGUAGES:")
    for i, (skill, count) in enumerate(results['programming_languages'][:15], 1):
        print(f"  {i:2d}. {skill:20s}: {count:4d} mentions")
    
    print("\n🔧 TOP 15 FRAMEWORKS & LIBRARIES:")
    for i, (skill, count) in enumerate(results['frameworks'][:15], 1):
        print(f"  {i:2d}. {skill:20s}: {count:4d} mentions")
    
    print("\n☁️  TOP 10 CLOUD & DEVOPS:")
    for i, (skill, count) in enumerate(results['cloud_platforms'][:10], 1):
        print(f"  {i:2d}. {skill:20s}: {count:4d} mentions")
    
    print("\n🗄️  TOP 10 DATABASES:")
    for i, (skill, count) in enumerate(results['databases'][:10], 1):
        print(f"  {i:2d}. {skill:20s}: {count:4d} mentions")
    
    print("\n🛠️  TOP 15 TOOLS & TECHNOLOGIES:")
    for i, (skill, count) in enumerate(results['tools_technologies'][:15], 1):
        print(f"  {i:2d}. {skill:20s}: {count:4d} mentions")
    
    print("\n" + "=" * 70)

def save_analysis_csv(results: Dict, output_path: str = "data/skills_analysis.csv"):
    """
    Save analysis results to CSV files.
    """
    if not results:
        print("No results to save.")
        return
    
    # Save programming languages
    with open("data/programming_languages.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["skill", "count"])
        writer.writerows(results['programming_languages'])
    
    # Save frameworks
    with open("data/frameworks.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["skill", "count"])
        writer.writerows(results['frameworks'])
    
    # Save cloud platforms
    with open("data/cloud_platforms.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["skill", "count"])
        writer.writerows(results['cloud_platforms'])
    
    # Save databases
    with open("data/databases.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["skill", "count"])
        writer.writerows(results['databases'])
    
    # Save tools
    with open("data/tools_technologies.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["skill", "count"])
        writer.writerows(results['tools_technologies'])
    
    print(f"\n✓ Analysis results saved to data/*.csv")

def run_analysis():
    """
    Main analysis function.
    """
    print("Loading jobs data...")
    df = load_jobs()
    
    if df.empty:
        print("No data to analyze. Please run fetch_jobs.py first.")
        return
    
    print("Analyzing jobs and extracting skills...")
    results = analyze_jobs(df)
    
    print_analysis(results)
    save_analysis_csv(results)
    
    print("\nAnalysis complete! ✨")

if __name__ == "__main__":
    run_analysis()

