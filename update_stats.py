import os
import re
import requests

# GitHub username to query
USERNAME = "Aggarwal-Raghav"

# Fetch token from environment variables (provided by GitHub Actions)
TOKEN = os.getenv("GH_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}


def get_pr_count(query):
    """Fetches the total count of pull requests matching the query."""
    url = f"https://api.github.com/search/issues?q={query}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json().get("total_count", 0)


if __name__ == "__main__":
    print("Fetching PR stats from GitHub API...")

    # 1. Fetch exact PR counts dynamically
    total_merged = get_pr_count(f"is:pr is:merged author:{USERNAME} org:apache")
    hive_merged = get_pr_count(f"is:pr is:merged author:{USERNAME} repo:apache/hive")
    tez_merged = get_pr_count(f"is:pr is:merged author:{USERNAME} repo:apache/tez")
    hive_site_merged = get_pr_count(
        f"is:pr is:merged author:{USERNAME} repo:apache/hive-site"
    )

    print(
        f"Stats fetched - Total: {total_merged}, Hive: {hive_merged}, Tez: {tez_merged}, Hive-Site: {hive_site_merged}"
    )

    # 2. Build the updated HTML table string
    new_table = f"""  <table>
    <thead>
      <tr>
        <th colspan="4" align="center"><h3>Pull Requests Merged</h3></th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td align="center" width="25%"><img src="https://www.apache.org/img/asf_logo.png" height="28" alt="Apache" /></td>
        <td align="center" width="25%"><img src="https://hive.apache.org/images/hive.svg" height="28" alt="Apache Hive" /></td>
        <td align="center" width="25%"><img src="https://tez.apache.org/images/ApacheTezLogo_lowres.png" height="28" alt="Apache Tez" /></td>
        <td align="center" width="25%"><img src="https://www.apache.org/img/asf_logo.png" height="28" alt="Apache" /></td>
      </tr>
      <tr>
        <td align="center"><b>Total Merged</b></td>
        <td align="center"><b>Apache Hive</b></td>
        <td align="center"><b>Apache Tez</b></td>
        <td align="center"><b>Hive-Site</b></td>
      </tr>
      <tr>
        <td align="center"><h2>{total_merged}</h2></td>
        <td align="center"><h2>{hive_merged}</h2></td>
        <td align="center"><h2>{tez_merged}</h2></td>
        <td align="center"><h2>{hive_site_merged}</h2></td>
      </tr>
    </tbody>
  </table>"""

    # 3. Read the current README.md
    with open("README.md", "r", encoding="utf-8") as file:
        readme = file.read()

    # 4. Use Regex to replace the content strictly between the HTML comments
    start_tag = r"<!-- PR_STATS_START -->"
    end_tag = r"<!-- PR_STATS_END -->"

    # re.DOTALL ensures '.' matches newlines as well
    pattern = re.compile(rf"({start_tag}).*?({end_tag})", re.DOTALL)

    # Replace the matched section with the new table, preserving the tags
    new_readme = re.sub(pattern, rf"\1\n{new_table}\n\2", readme)

    # 5. Write the updated content back to README.md
    with open("README.md", "w", encoding="utf-8") as file:
        file.write(new_readme)

    print("README.md successfully updated!")
