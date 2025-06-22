from django.shortcuts import render
from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup
from django.conf import settings

SERP_API_KEY = settings.SERP_API_KEY

def home(request):
    return render(request, 'chatbot/index.html')

def chat(request):
    if request.method == "POST":
        user_msg = request.POST.get('message')

        # Step 1: Prepare the search query
        search_query = f"In python {user_msg} site:geeksforgeeks.org OR site:w3schools.com OR site:tutorialspoint.com"
        params = {
            "engine": "google",
            "q": search_query,
            "api_key": SERP_API_KEY
        }

        try:
            res = requests.get("https://serpapi.com/search", params=params)
            data = res.json()
            organic_results = data.get("organic_results", [])
            if not organic_results:
                return JsonResponse({"reply": "❌ No relevant results found."})

            # Step 2: Merge top 5 snippets
            clean_texts = []
            for result in organic_results[:5]:
                snippet = result.get("snippet")
                if snippet:
                    clean_texts.append(snippet.strip())
            merged_summary = " ".join(clean_texts)

            # Step 3: Fallback scrape (if needed)
            if not merged_summary:
                first_link = organic_results[0].get("link")
                headers = {"User-Agent": "Mozilla/5.0"}
                page = requests.get(first_link, headers=headers)
                soup = BeautifulSoup(page.text, 'html.parser')
                paragraphs = soup.find_all('p')
                for para in paragraphs:
                    text = para.get_text(strip=True)
                    if any(x in text.lower() for x in ["offers a wide range", "privacy policy", "advertise", "newsletter"]):
                        continue
                    if len(text) > 50:
                        merged_summary = text
                        break

            if not merged_summary:
                merged_summary = "I found the page, but couldn't extract a clear explanation."

            # Step 4: Return response without quiz
            first_link = organic_results[0].get("link")
            return JsonResponse({
                "reply": merged_summary,
                "source": first_link
            })

        except Exception as e:
            return JsonResponse({
                "reply": f"❌ Sorry, something went wrong.\nError: {str(e)}"
            })
