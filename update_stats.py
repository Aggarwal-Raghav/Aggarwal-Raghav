"""
update_stats.py

A script to fetch GitHub PR statistics and update README.md.
Uses only built-in Python modules for maximum compatibility and minimal dependencies.
"""

import json
import logging
import os
import re
import urllib.parse
import urllib.request
from typing import Dict, Optional

# --- Configuration ---
USERNAME = "Aggarwal-Raghav"
README_PATH = "README.md"
START_TAG = "<!-- PR_STATS_START -->"
END_TAG = "<!-- PR_STATS_END -->"

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def get_pr_count(query: str, headers: Dict[str, str]) -> int:
    """
    Fetches the total count of pull requests matching the query using urllib.

    Args:
        query: The GitHub search query string.
        headers: HTTP headers including authorization.

    Returns:
        The total count of matching items, or 0 on failure.
    """
    params = {"q": query}
    url = f"https://api.github.com/search/issues?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url)
    for key, value in headers.items():
        req.add_header(key, value)

    try:
        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("total_count", 0)

            logger.error(f"GitHub API returned status code {response.getcode()}")
    except Exception as e:
        logger.exception(f"Exception occurred while fetching PR count for query '{query}': {e}")

    return 0


def generate_table_html(stats: Dict[str, int]) -> str:
    """
    Generates the HTML table string based on the provided statistics.
    """
    return f"""  <table>
    <thead>
      <tr>
        <th colspan="4" align="center"><h3>Pull Requests Merged</h3></th>
        <th colspan="1" align="center"><h3>PR Reviewed</h3></th>
        <th colspan="1" align="center"><h3>PRs in Progress</h3></th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td align="center" width="16%"><img src="https://www.apache.org/img/asf_logo.png" height="28" alt="Apache" /></td>
        <td align="center" width="16%"><img src="https://hive.apache.org/images/hive.svg" height="28" alt="Apache Hive" /></td>
        <td align="center" width="16%"><img src="https://tez.apache.org/images/ApacheTezLogo_lowres.png" height="28" alt="Apache Tez" /></td>
        <td align="center" width="16%"><img src="https://www.apache.org/img/asf_logo.png" height="28" alt="Apache" /></td>
        <td align="center" width="16%"><img src="https://www.apache.org/img/asf_logo.png" height="28" alt="Apache" /></td>
        <td align="center" width="16%"><img src="https://www.apache.org/img/asf_logo.png" height="28" alt="Apache" /></td>
      </tr>
      <tr>
        <td align="center"><b>Total Merged</b></td>
        <td align="center"><b>Apache Hive</b></td>
        <td align="center"><b>Apache Tez</b></td>
        <td align="center"><b>Hive-Site</b></td>
        <td align="center"><b>Total Reviewed</b></td>
        <td align="center"><b>Total Open</b></td>
      </tr>
      <tr>
        <td align="center"><h2>{stats['total_merged']}</h2></td>
        <td align="center"><h2>{stats['hive_merged']}</h2></td>
        <td align="center"><h2>{stats['tez_merged']}</h2></td>
        <td align="center"><h2>{stats['hive_site_merged']}</h2></td>
        <td align="center"><h2>{stats['total_reviewed']}</h2></td>
        <td align="center"><h2>{stats['total_open']}</h2></td>
      </tr>
    </tbody>
  </table>"""


def update_readme(new_content: str) -> bool:
    """
    Updates the README.md file by replacing the content between the defined tags.
    """
    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            readme = f.read()

        # Regex to replace content between tags, preserving the tags themselves
        pattern = re.compile(
            rf"({re.escape(START_TAG)}).*?({re.escape(END_TAG)})", 
            re.DOTALL
        )

        if not pattern.search(readme):
            logger.error(f"Tags {START_TAG} or {END_TAG} not found in {README_PATH}")
            return False

        updated_readme = pattern.sub(rf"\1\n{new_content}\n\2", readme)

        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(updated_readme)

        return True
    except IOError as e:
        logger.error(f"IO Error updating {README_PATH}: {e}")
        return False


def main() -> None:
    """
    Main execution flow.
    """
    logger.info("Fetching PR stats from GitHub API...")

    token = os.getenv("GH_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    if not token:
        logger.warning("GH_TOKEN not found. API rate limits may apply.")

    # 1. Fetch statistics
    queries = {
        "total_merged": f"is:pr is:merged author:{USERNAME} org:apache",
        "hive_merged": f"is:pr is:merged author:{USERNAME} repo:apache/hive",
        "tez_merged": f"is:pr is:merged author:{USERNAME} repo:apache/tez",
        "hive_site_merged": f"is:pr is:merged author:{USERNAME} repo:apache/hive-site",
        "total_reviewed": f"type:pr reviewed-by:{USERNAME} -author:{USERNAME} org:apache",
        "total_open": f"is:pr author:{USERNAME} is:open org:apache"
    }

    stats = {key: get_pr_count(query, headers) for key, query in queries.items()}

    logger.info(f"Stats fetched: {stats}")

    # 2. Build the updated HTML table string
    table_html = generate_table_html(stats)

    # 3. Update the README
    if update_readme(table_html):
        logger.info(f"{README_PATH} successfully updated!")
    else:
        logger.error(f"Failed to update {README_PATH}")


if __name__ == "__main__":
    main()
