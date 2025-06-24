import os
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig, BrowserContext, BrowserContextConfig
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

class LinkedinBrowserAgent:
    """LinkedIn browser automation agent using browser_use."""
    
    def __init__(self, browser_url: str = None):
        """
        Initialize the LinkedIn browser agent.
        
        Args:
            browser_url: Browser connection URL from environment or default
        """
        self.browser_url = browser_url or os.getenv('BROWSER_DEBUG_URL', "http://127.0.0.1:9222")
        self.browser = None
        self.context = None
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        
    async def _initialize_browser(self):
        """Initialize browser and context if not already done."""
        if not self.browser:
            try:
                # Initialize browser with config
                browser_config = BrowserConfig(cdp_url=self.browser_url)
                self.browser = Browser(config=browser_config)
                
                # Initialize context with config
                context_config = BrowserContextConfig(
                    wait_for_network_idle_page_load_time=10.0,
                    highlight_elements=True
                )
                self.context = BrowserContext(self.browser, context_config)
                
                print("Browser session initialized successfully")
            except Exception as e:
                print(f"Error initializing browser session: {str(e)}")
                raise
        return self.browser, self.context
        
    async def get_profile_data(self, profile_url: str) -> Optional[Dict[str, Any]]:
        """
        Extract LinkedIn profile data using browser automation.
        
        Args:
            profile_url: LinkedIn profile URL
            
        Returns:
            Optional[Dict[str, Any]]: Extracted profile data or None if failed
        """
        try:
            # Only print on error or final result
            browser, context = await self._initialize_browser()
            extraction_task = f"""
            Navigate directly to {profile_url} and extract the profile information.
            Steps:
            1. Go directly to {profile_url}
            2. Extract the following information:
               - Name
               - Headline (job title and company)
               - Location
               - Current position details
               - Previous experience
               - Education
               - Skills
               - About/Summary
            Do not search Google or use any search engine. Go directly to the provided URL.
            Return the data as a JSON object with keys: Name, Headline, Location, Current Position, Previous Experience, Education, Skills, About.
            If any information is not available, mark it as \"Not available\".
            """
            agent = Agent(
                task=extraction_task,
                browser=browser,
                browser_context=context,
                llm=self.llm,
                max_failures=3,
                retry_delay=5,
                max_actions_per_step=3
            )
            result = await agent.run(max_steps=10)
            if result:
                profile_data = self._parse_result(result, profile_url)
                print("LinkedIn profile extraction completed successfully")
                return profile_data
            else:
                print("Failed to extract LinkedIn profile data")
                return None
        except Exception as e:
            print(f"Error extracting LinkedIn profile data: {str(e)}")
            return None
            
    def _parse_result(self, result, profile_url: str) -> Dict[str, Any]:
        """
        Parse the raw extraction result into structured data.
        
        Args:
            result: Raw extraction result from the agent
            profile_url: Original LinkedIn URL
            
        Returns:
            Dict[str, Any]: Structured profile data
        """
        try:
            # Try to find the last message with a JSON result
            if hasattr(result, 'history') and hasattr(result.history, '__iter__'):
                for step in reversed(result.history):
                    if hasattr(step, 'result') and isinstance(step.result, str) and step.result.strip().startswith('{'):
                        import json
                        try:
                            parsed = json.loads(step.result)
                            return {
                                'profile_url': profile_url,
                                'extraction_method': 'browser_automation',
                                'raw_result': step.result,
                                'parsed_data': parsed
                            }
                        except Exception as e:
                            print(f"Error parsing JSON: {str(e)}")
            # fallback: just return the last result as string
            return {
                'profile_url': profile_url,
                'extraction_method': 'browser_automation',
                'raw_result': str(result),
                'parsed_data': {}
            }
        except Exception as e:
            print(f"Error parsing LinkedIn result: {str(e)}")
            return {
                'profile_url': profile_url,
                'extraction_method': 'browser_automation',
                'raw_result': str(result),
                'parsed_data': {},
                'parse_error': str(e)
            }
            
    async def close_browser(self):
        """Close the browser."""
        if self.browser:
            try:
                await self.browser.close()
                print("Browser closed")
            except Exception as e:
                print(f"Error closing browser: {str(e)}")

# Async wrapper for easier integration
async def get_linkedin_profile_async(profile_url: str, browser_url: str = None) -> Optional[Dict[str, Any]]:
    """
    Async wrapper to get LinkedIn profile data.
    
    Args:
        profile_url: LinkedIn profile URL
        browser_url: Browser connection URL
        
    Returns:
        Optional[Dict[str, Any]]: Profile data or None
    """
    client = LinkedinBrowserAgent(browser_url)
    try:
        return await client.get_profile_data(profile_url)
    finally:
        await client.close_browser()

# Synchronous wrapper for compatibility
def get_linkedin_profile_data(profile_url: str, browser_url: str = None) -> Optional[Dict[str, Any]]:
    """
    Synchronous wrapper to get LinkedIn profile data.
    
    Args:
        profile_url: LinkedIn profile URL
        browser_url: Browser connection URL
        
    Returns:
        Optional[Dict[str, Any]]: Profile data or None
    """
    try:
        return asyncio.run(get_linkedin_profile_async(profile_url, browser_url))
    except Exception as e:
        print(f"Error in synchronous LinkedIn profile extraction: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the LinkedIn browser agent
    test_url = "https://www.linkedin.com/in/alosan"
    
    print("Testing LinkedIn Browser Agent")
    print("=" * 50)
    print(f"Testing URL: {test_url}")
    
    result = get_linkedin_profile_data(test_url)
    
    if result:
        print("✅ Success!")
        print("Extracted data:")
        print(result['parsed_data'])
    else:
        print("❌ Failed to extract LinkedIn profile data")