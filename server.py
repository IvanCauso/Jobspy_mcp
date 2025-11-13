import os
from fastmcp import FastMCP
from jobspy import scrape_jobs
import json

# Server instance
app = FastMCP("JobSpy MCP")

@app.tool()
def search_jobs(
    search_term: str,
    location: str = "",
    site_name: list[str] = None,
    results_wanted: int = 20,
    hours_old: int = 72,
    country_indeed: str = "USA",
    job_type: str = None,
    is_remote: bool = None,
    distance: int = 50,
    linkedin_fetch_description: bool = False,
    offset: int = 0
):
    """Search for jobs across multiple job boards (LinkedIn, Indeed, ZipRecruiter, Glassdoor, Google).
    
    Args:
        search_term: Job title or keywords to search for (e.g., "software engineer", "data analyst")
        location: Location for job search (e.g., "San Francisco, CA", "New York, NY", "Remote")
        site_name: List of job boards to search. Options: ["linkedin", "indeed", "zip_recruiter", "glassdoor", "google"]
                   Default: ["indeed", "linkedin", "zip_recruiter"]
        results_wanted: Number of job results to retrieve (default: 20, max: 50 per site)
        hours_old: Maximum age of job postings in hours (default: 72 = 3 days)
        country_indeed: Country code for Indeed search (default: "USA")
        job_type: Filter by job type. Options: "fulltime", "parttime", "internship", "contract"
        is_remote: Filter for remote jobs only (True/False)
        distance: Search radius in miles from location (default: 50)
        linkedin_fetch_description: Fetch full job descriptions from LinkedIn (slower but more detailed)
        offset: Number of jobs to skip (for pagination)
    
    Returns:
        Dictionary containing list of jobs with details: title, company, location, date_posted, job_url, 
        description, salary info, and more
    """
    try:
        print(f"[DEBUG] search_jobs called: search_term='{search_term}', location='{location}', sites={site_name}")
        
        # Default site names if not provided
        if site_name is None:
            site_name = ["indeed", "linkedin", "zip_recruiter"]
        
        # Validate site names
        valid_sites = ["linkedin", "indeed", "zip_recruiter", "glassdoor", "google"]
        site_name = [site for site in site_name if site.lower() in valid_sites]
        
        if not site_name:
            return {"error": "No valid job sites provided", "jobs": []}
        
        print(f"[DEBUG] Scraping from sites: {site_name}")
        
        # Build kwargs for scrape_jobs
        kwargs = {
            "site_name": site_name,
            "search_term": search_term,
            "results_wanted": results_wanted,
            "hours_old": hours_old,
            "country_indeed": country_indeed,
            "linkedin_fetch_description": linkedin_fetch_description,
            "offset": offset,
        }
        
        # Add optional parameters only if provided
        if location:
            kwargs["location"] = location
        if job_type:
            kwargs["job_type"] = job_type
        if is_remote is not None:
            kwargs["is_remote"] = is_remote
        if distance:
            kwargs["distance"] = distance
        
        # Scrape jobs
        jobs_df = scrape_jobs(**kwargs)
        
        print(f"[DEBUG] Found {len(jobs_df)} jobs")
        
        # Convert DataFrame to list of dictionaries
        jobs_list = jobs_df.to_dict('records')
        
        # Clean up the data - convert any NaN to None
        for job in jobs_list:
            for key, value in job.items():
                if isinstance(value, float) and str(value) == 'nan':
                    job[key] = None
        
        print(f"[DEBUG] Returning {len(jobs_list)} jobs")
        
        return {
            "jobs": jobs_list,
            "count": len(jobs_list),
            "search_params": {
                "search_term": search_term,
                "location": location,
                "sites": site_name,
                "results_wanted": results_wanted,
                "hours_old": hours_old
            }
        }
        
    except Exception as e:
        print(f"[ERROR] Exception in search_jobs: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "jobs": []}


@app.tool()
def get_job_sites():
    """Get list of available job board sites that can be searched.
    
    Returns:
        Dictionary with available job sites and their descriptions
    """
    return {
        "sites": [
            {
                "name": "linkedin",
                "description": "LinkedIn Jobs - Professional networking platform with extensive job listings"
            },
            {
                "name": "indeed",
                "description": "Indeed - One of the largest job search engines worldwide"
            },
            {
                "name": "zip_recruiter",
                "description": "ZipRecruiter - Job search platform with smart matching technology"
            },
            {
                "name": "glassdoor",
                "description": "Glassdoor - Job listings with company reviews and salary information"
            },
            {
                "name": "google",
                "description": "Google Jobs - Aggregated job listings from across the web"
            }
        ],
        "note": "You can search multiple sites simultaneously by passing a list of site names"
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    print(f"[INFO] Starting JobSpy MCP server on port {port}")
    # Run with HTTP transport for MCP
    app.run("http", host="0.0.0.0", port=port)