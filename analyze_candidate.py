import os
import json
from typing import Optional
from utils.github_browse_agent import GitHubBrowseAgent
from utils.llm_client import LLMClient
from utils.linkedin_browser_agent import get_linkedin_profile_data

def read_job_requirements(job_profile: str) -> str:
    path = f"job_requirements/{job_profile}.txt"
    if not os.path.exists(path):
        return ""
    with open(path) as f:
        return f.read()

def analyze_candidate(github_url: str, job_profile: str = "product_engineer") -> Optional[str]:
    # Gather job requirements
    job_requirements = read_job_requirements(job_profile)
    # Gather GitHub data using the new minimal client method
    github_data = {}
    if github_url:
        username = github_url.rstrip('/').split('/')[-1]
        gh_client = GitHubBrowseAgent()
        github_data = gh_client.get_candidate_github_data(username)
        linkedin_url = github_data.get('profile').get('linkedin_url')
    # Gather LinkedIn data if available
    linkedin_data = None
    if linkedin_url:
        print(f"LinkedIn URL: {linkedin_url}")
        linkedin_result = get_linkedin_profile_data(linkedin_url)
        if linkedin_result and linkedin_result.get('parsed_data'):
            linkedin_data = linkedin_result['parsed_data']
    # Compose system prompt for LLM
    system_prompt = f"""
You are an expert technical recruiter. Your task is to evaluate a candidate for the following job:

[JOB REQUIREMENTS]
{job_requirements}

[CANDIDATE DATA]
GitHub: {json.dumps(github_data, indent=2)}
LinkedIn: {json.dumps(linkedin_data, indent=2) if linkedin_data else 'Not provided'}

For each requirement, provide a brief, evidence-based data point from the candidate's profile (GitHub, LinkedIn, Twitter, etc.).

- For years of experience and location, prefer LinkedIn if available, as it is more frequently updated and reliable for these fields. Only use GitHub or other sources if they provide explicit, verifiable information (such as a public resume or clear employment history), and cite the source link. If no reliable source is available, explicitly state that the information is not verifiable and do not guess or infer.
- For technical skills, project work, and open-source contributions, prefer GitHub as the primary source, but also include LinkedIn evidence if it adds value or context. Cite all sources used.
- For professional background, education, and job titles, prefer LinkedIn if available, but supplement with GitHub or other sources if relevant.
- For all requirements, always use the source that is most likely to be accurate and up-to-date for that specific requirement. If both sources provide relevant evidence, include both and cite their respective links.
- If no reliable source is available for a requirement, explicitly state that the information is not verifiable and do not guess or infer.

Whenever you reference LinkedIn, GitHub, Twitter, blog, or any other source, always provide the source link (e.g., repo URL, LinkedIn profile, tweet, blog post) in the analysis table or justification.

Produce a single, clear, structured analysis table mapping each requirement to the candidate's evidence, source(s), and verifiability/notes. Do not include a second summary table.

Finally, give a clear recommendation using one of these 5 levels: Strongly Shortlist, Shortlist, Neutral, Reject, Strongly Reject. Add a one-sentence justification for your recommendation.
"""
    llm = LLMClient()
    analysis = llm.get_completion(system_prompt, "Evaluate this candidate for the job above.")
    if analysis:
        print(analysis)
    return analysis

def main():
    candidates = [
        {
            'github': 'https://github.com/sroecker',
            'job_profile': 'product_engineer'
        },
        # This candidate has a LinkedIn URL in their GitHub profile (for testing LinkedIn extraction)
        {
            'github': 'https://github.com/aosan',
            'job_profile': 'product_engineer'
        }
    ]
    print("Starting candidate analysis...")
    for i, candidate in enumerate(candidates, 1):
        print(f"\n{'#'*60}\nANALYZING CANDIDATE {i}/{len(candidates)}\n{'#'*60}: {candidate['github']}")
        analyze_candidate(
            github_url=candidate['github'],
            job_profile=candidate.get('job_profile', 'product_engineer')
        )
    print("\nAnalysis complete.")

if __name__ == "__main__":
    main() 