# Job Insights Dashboard

A comprehensive data pipeline and interactive dashboard that fetches, analyzes, and visualizes tech job opportunities across Australia.

---

## Overview

Job Insights Dashboard is an end-to-end solution that:
- **Fetches** real job postings from multiple Australian job boards
- **Analyzes** technical skills and job market trends
- **Visualizes** insights through an interactive Streamlit dashboard

Perfect for job seekers, recruiters, and market researchers looking to understand the Australian tech job landscape.

---

## Features

### Job Fetching
- Multi-source scraping from Australian job boards (Prosple, Workforce AU)
- Advanced anti-bot handling using Playwright
- Comprehensive coverage across:
  - Software Engineering
  - Data Analytics & Science
  - Business Analysis
  - IT Support & Infrastructure
  - DevOps & Cloud
  - Cybersecurity
  - And more...

### Data Analysis
- Automated skill extraction from job titles
- Categorization by:
  - Programming languages (Python, Java, JavaScript, etc.)
  - Frameworks & libraries (React, Django, Spring, etc.)
  - Cloud platforms (AWS, Azure, GCP)
  - Databases (PostgreSQL, MongoDB, MySQL, etc.)
  - Tools & technologies
- Role classification and frequency analysis

### Interactive Dashboard
- **Key Metrics**: Total jobs, companies, locations, role types
- **Skill Analysis**: Top 15 skills with customizable filtering
- **Distribution Charts**: Jobs by source, role categories, top companies
- **Searchable Table**: Filterable job listings with direct links
- **Export Functionality**: Download filtered data as CSV
- **Real-time Filters**: Source, role, location, and skill frequency

---

## Tech Stack

### Core
- **Python 3.13+**
- **pandas** - Data manipulation and analysis
- **Streamlit** - Interactive dashboard frontend
- **Plotly** - Advanced charting and visualizations

### Web Scraping
- **requests** - HTTP client
- **BeautifulSoup4** - HTML parsing
- **Playwright** - Headless browser automation for anti-bot bypass

### Data Processing
- CSV-based storage and deduplication
- Regex-based skill extraction
- MD5 hashing for duplicate detection

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/job-insights-dashboard.git
cd job-insights-dashboard
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers
```bash
python -m playwright install chromium
```

---

## Usage

### Fetch Job Data
Run the job fetcher to scrape latest listings:
```bash
python3 -m src.fetch_jobs
```

This will:
- Query multiple job boards with comprehensive search terms
- Fetch and normalize job listings
- Deduplicate entries
- Save results to `data/jobs_merged.csv`

**Note**: This process may take 10-20 minutes depending on network speed and number of queries.

### Run Analysis (Optional)
Generate skill frequency reports:
```bash
python3 -m src.analyze
```

Outputs CSV files to `data/` with skill breakdowns by category.

### Launch Dashboard
Start the interactive Streamlit app:
```bash
streamlit run src/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## Project Structure

```
job-insights-dashboard/
├── src/
│   ├── fetch_jobs.py          # Main job fetching orchestrator
│   ├── analyze.py              # Skill extraction and analysis
│   ├── app.py                  # Streamlit dashboard application
│   ├── fetchers/               # Source-specific scrapers
│   │   ├── prosple.py
│   │   ├── workforce_au.py
│   │   ├── seek.py            # (Currently blocked)
│   │   ├── indeed.py          # (Currently blocked)
│   │   ├── jora.py            # (Currently blocked)
│   │   └── careerone.py       # (Currently blocked)
│   └── utils/                  # Helper functions
│       ├── normalize.py
│       └── dedupe.py
├── data/
│   └── jobs_merged.csv        # Deduplicated job listings
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Data Sources

### Currently Active
- **Prosple** (Graduate & early career jobs)
- **Workforce Australia** (Government job board)

### Blocked (Anti-scraping protection)
- Seek
- Indeed
- Jora
- CareerOne

**Note**: Some major job boards have advanced bot detection. We've implemented Playwright-based scraping, but some sources remain inaccessible. The active sources provide good coverage of graduate and government-listed opportunities.

---

## Dashboard Features

### Filters
- **Job Sources**: Select specific job boards
- **Role Categories**: Filter by job type (Software Engineering, Data Analytics, etc.)
- **Location**: Filter by city or remote
- **Min Skill Mentions**: Show only skills above a threshold

### Visualizations
1. **Top Skills** - Horizontal bar chart of most in-demand technologies
2. **Jobs by Source** - Pie chart showing distribution across job boards
3. **Role Distribution** - Top 10 job categories
4. **Top Companies** - Leading employers by number of listings
5. **Skills by Category** - Breakdown of programming languages, frameworks, cloud platforms, and databases

### Job Listings Table
- Searchable by title, company, or location
- Clickable URLs to view original job postings
- Adjustable results count (10/25/50/100)
- CSV export functionality

---

## Roadmap

- [x] Setup repository
- [x] Fetch job listings from multiple sources
- [x] Implement Playwright for anti-bot bypass
- [x] Analyze skill frequencies
- [x] Build Streamlit dashboard
- [x] Add filters and search
- [x] Implement caching for performance
- [x] Add CSV export functionality
- [ ] Deploy to Streamlit Cloud
- [ ] Add scheduling for automatic data refresh
- [ ] Implement job description scraping
- [ ] Add salary analysis (if data available)
- [ ] Email alerts for matching jobs

---

## Performance

- **Caching**: Data preparation and skill extraction are cached for instant filter updates
- **Load Time**: Initial load ~1-2s, filter changes <0.1s
- **Scalability**: Handles 1000+ job listings efficiently

---

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

---

## License

MIT License - see LICENSE file for details

---

## Acknowledgments

- Job data sourced from Prosple and Workforce Australia
- Built with Streamlit and Plotly
- Web scraping powered by Playwright

---

## Contact

For questions or feedback, please open an issue on GitHub.
