import os
from typing import Dict, Any, List, Optional
from github import Github
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re

# Load environment variables
load_dotenv()

class GitHubClient:
    def __init__(self):
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GitHub token not found")
        self.client = Github(github_token)

    def get_candidate_github_data(self, username: str) -> Dict[str, Any]:
        try:
            user = self.client.get_user(username)
            # Minimal profile fields
            profile = {
                'login': user.login,
                'name': user.name,
                'location': user.location,
                'bio': user.bio,
                'blog': user.blog,
                'company': user.company,
                'email': user.email,
                'public_repos': user.public_repos,
                'followers': user.followers,
                'following': user.following,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat(),
                'html_url': user.html_url,
                'linkedin_url': self.get_linkedin_from_github(user.login)
            }
            # Minimal repo fields
            repos = []
            for repo in user.get_repos(sort='updated', direction='desc'):
                if not repo.fork:
                    repos.append({
                        'name': repo.name,
                        'description': repo.description,
                        'language': repo.language,
                        'stars': repo.stargazers_count,
                        'html_url': repo.html_url,
                        'created_at': repo.created_at.isoformat(),
                        'updated_at': repo.updated_at.isoformat()
                    })
            # Contribution stats (minimal)
            stats = {
                'total_contributions': 0,  # Not available via API without scraping
                'languages_used': {},
                'collaboration_indicators': {
                    'contributed_to_others_repos': 0,  # Not available via API
                    'has_organizations': bool(user.get_orgs().totalCount > 0),
                    'organization_count': user.get_orgs().totalCount
                },
                'community_engagement': {
                    'public_gists': user.public_gists,
                    'followers': user.followers,
                    'following': user.following
                }
            }
            # Count languages used
            for repo in repos:
                lang = repo['language']
                if lang:
                    stats['languages_used'][lang] = stats['languages_used'].get(lang, 0) + 1
            return {
                'profile': profile,
                'repositories': repos,
                'contribution_stats': stats
            }
        except Exception as e:
            print(f"Error fetching GitHub data: {str(e)}")
            return {}

    def get_linkedin_from_github(self, username: str) -> Optional[str]:
        url = f"https://github.com/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        text_to_search = ""
        bio_section = soup.select_one('[data-bio-text]')
        if bio_section:
            text_to_search += bio_section.get_text(" ", strip=True) + " "
        social_links_container = soup.select_one('.js-profile-editable-area')
        if social_links_container:
            social_links = social_links_container.select("a[href]")
            for link in social_links:
                href = link.get("href", "")
                if (href.startswith('http') and 
                    not href.startswith('https://github.com') and 
                    not href.startswith('https://docs.github.com') and
                    not href.startswith('https://support.github.com')):
                    text_to_search += href + " "
        readme_content = soup.select_one('[data-target="readme-toc.content"]')
        if readme_content:
            text_to_search += readme_content.get_text(" ", strip=True) + " "
        linkedin_patterns = [
            r"(https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+/?)",
            r"(linkedin\.com/in/[a-zA-Z0-9\-_%]+/?)",
            r"(in/[a-zA-Z0-9\-_%]+/?)",
            r"(@[a-zA-Z0-9\-_%]+)"
        ]
        for pattern in linkedin_patterns:
            linkedin_match = re.search(pattern, text_to_search, re.IGNORECASE)
            if linkedin_match:
                url = linkedin_match.group(1)
                if not url.startswith('http'):
                    if url.startswith('@'):
                        url = f"https://linkedin.com/in/{url[1:]}"
                    elif url.startswith('in/'):
                        url = f"https://linkedin.com/{url}"
                    else:
                        url = f"https://{url}"
                return url.rstrip('/')
        return None