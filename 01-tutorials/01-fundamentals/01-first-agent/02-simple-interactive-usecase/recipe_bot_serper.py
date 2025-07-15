# Import Agent and tools
from strands import Agent, tool
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException, DuckDuckGoSearchException
import logging
import http.client
import json

# Configure logging
logging.getLogger("strands").setLevel(logging.INFO) # Set to DEBUG for more detailed logs

# Define a websearch tool
@tool
def websearch(keywords: str, region: str = "us-en", max_results: int | None = None) -> str:
    """Search the web using serper.dev API to get updated information.
    Args:
        keywords (str): The search query keywords.
        region (str): The search region (unused for serper.dev).
        max_results (int | None): The maximum number of results to return.
    Returns:
        A formatted string with search results.
    """
    try:
        conn = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps({
            "q": keywords
        })
        headers = {
            'X-API-KEY': 'SERPER_API_KEY',
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        result_json = json.loads(data.decode("utf-8"))
        results = result_json.get("organic", [])
        if not results:
            return "No results found."
        # Limit results if max_results is set
        if max_results is not None:
            results = results[:max_results]
        # Print the indexes of the search results
        print(f"[websearch] Returning result indexes: {list(range(len(results)))}")
        # Print all links and snippets from the search results
        for i, r in enumerate(results):
            print(f"[websearch] Result {i}: link={r.get('link', '')}")
            print(f"[websearch] Result {i}: snippet={r.get('snippet', '')}")
        formatted = "\n".join(
            f"{i+1}. {r.get('title', 'No title')}\n{r.get('link', '')}\n{r.get('snippet', '')}\n"
            for i, r in enumerate(results)
        )
        return formatted
    except Exception as e:
        return f"Exception: {e}"
    

# Create a recipe assistant agent
recipe_agent = Agent(
    system_prompt="""You are RecipeBot, a helpful cooking assistant.
    Help users find recipes based on ingredients and answer cooking questions.
    Use the websearch tool to find recipes when users mention ingredients or to look up cooking information.""",
    tools=[websearch],
)


if __name__ == "__main__":
    print("\n👨‍🍳 RecipeBot: Ask me about recipes or cooking! Type 'exit' to quit.\n")
    
    # Run the agent in a loop for interactive conversation
    while True:
        user_input = input("\nYou > ")
        if user_input.lower() == "exit":
            print("Happy cooking! 🍽️")
            break
        response = recipe_agent(user_input)
        print(f"\nRecipeBot > {response}")