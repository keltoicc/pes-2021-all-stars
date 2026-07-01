import re

from bs4 import BeautifulSoup


def extract_club_id(href):

    if not href:
        return None

    match = re.search(r"/verein/(\d+)", href)

    if match:
        return int(match.group(1))

    return None

def extract_season_id(href):

    if not href:
        return None

    match = re.search(r"/saison_id/(\d+)", href)

    if match:
        return int(match.group(1))

    return None

def parse_achievements(html_path):

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    achievements = []

    current_title = None

    rows = soup.select("table tbody tr")

    for row in rows:

        classes = row.get("class", [])

        #
        # HEADER
        #

        if "bg_Sturm" in classes:

            title_cell = row.find("td", class_="hauptlink")

            if title_cell:
                raw_title = title_cell.get_text(strip=True)

                current_title = re.sub(
                    r"^\d+x\s?+",
                    "",
                    raw_title
                )

            continue

        #
        # ACHIEVEMENT ROW
        #

        season_cell = row.find(
            "td",
            class_="erfolg_table_saison"
        )

        if not season_cell:
            continue

        season = season_cell.get_text(strip=True)

        club_cell = row.find("td", class_="no-border-links")

        club_name = None
        club_id = None
        season_id = None

        if club_cell:

            links = club_cell.find_all("a", href=True)

            valid_links = [
                link for link in links
                if link.get("href")
            ]

            if valid_links:

                club_link = valid_links[-1]

                href = club_link["href"]

                club_name = club_link.get("title")

                club_id = extract_club_id(href)

                season_id = extract_season_id(href)

        achievements.append({
            "title": current_title,
            "season": season,
            "season_id": season_id,
            "club_name": club_name,
            "club_id": club_id
        })

    return achievements