import json
import os
from typing import override
from scraper import fetch_website_links,fetch_website_content

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")



gemini = OpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=api_key)

def generate_sys_prompt_for_links() -> str :
    return """
You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
Return ONLY valid JSON.
Return ONLY a JSON array of strings.
Do not include markdown.
Do not include explanations.
Do not include text before or after the JSON.
You should return me an array of strings . Each string is the url for relevant page"""


def generate_user_prompt_for_links(url : str ,all_links : list[str])->str:
    prompt : str = f"""
Here is the list of links on the website {url} -
Please decide which of these are relevant web links for a brochure about the company, 
respond with the full https URL in JSON format.
Do not include Terms of Service, Privacy, email links.

Links (some might be relative links):

"""

    for link in all_links:
        prompt+= "\n"+link + "\n"
    return prompt

def brochure_system_prompt()->str:
    return """
You are an assistant that analyzes the contents of several relevant pages from a company website
and creates a short brochure about the company for prospective customers, investors and recruits.
Respond in markdown without code blocks.
Include details of company culture, customers and careers/jobs if you have the information.
your response should be json , where they should be an object , a key called "answer" and its value should be your response

"""


def brochure_user_prompt(website_content : str , relevant_links : list[str])->str:
    prompt = """You are looking at a company called: {company_name}
Here are the contents of its landing page and other relevant pages;
use this information to build a short brochure of the company in markdown without code blocks.\n\n"""
    prompt += website_content + "\n\n"
    for link in relevant_links:
        prompt += "\n"+link + "\n"
    return prompt








def brochure(url):
    all_the_links_from_page = fetch_website_links(url)
    response = gemini.chat.completions.create(model="gemini-3.5-flash",messages=[{"role" : "system", "content" : generate_sys_prompt_for_links() }, {"role" : "user", "content" : generate_user_prompt_for_links(url , all_the_links_from_page) }])
    relevant_links_from_page = json.loads(response.choices[0].message.content)
    content_of_page = fetch_website_content(url)
    response = gemini.chat.completions.create(model="gemini-3.5-flash",
                                          messages=[{"role": "system", "content": brochure_system_prompt()},
                                                    {"role": "user", "content": brochure_user_prompt(content_of_page,relevant_links_from_page)}])
    print(response.choices[0].message.content)








brochure("https://roadmap.sh/")














