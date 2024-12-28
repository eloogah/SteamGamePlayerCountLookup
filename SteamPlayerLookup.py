import sys
import requests
from bs4 import BeautifulSoup
import pytz
import humanize
from datetime import datetime

def convert_timestamp_to_readable(timestamp_str):
    """
    Converts a timestamp string to a human readable "X time ago" format
    Example: "2024-10-31T04:07:25Z" -> "an hour ago"
    """
    try:
        # Parse the timestamp
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
        # Convert to UTC
        timestamp = pytz.UTC.localize(timestamp)
        # Get current time in UTC
        now = datetime.now(pytz.UTC)
        # Return human readable difference
        return humanize.naturaltime(now - timestamp)
    except Exception as e:
        return "time ago"

if len(sys.argv) < 2:  # Check if we have at least the steamid argument
    print("Usage: python SteamPlayerLookup.py <steamid> [-w]")
    sys.exit(1)

if len(sys.argv) > 2 and sys.argv[1] == "-w":  # Check if -w flag is provided
    with open('SteamIDs.txt', 'w') as file:
        file.write(sys.argv[2])  # Write the steamid (now the third argument)

    with open('SteamIDs.txt', 'r') as file:
        steamID = file.read()
else:
    steamID = sys.argv[1]

def get_game_stats(game_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(game_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        title_element = soup.select_one('h1')#title

        stats_div = soup.find('div', id='app-heading')
        if stats_div:
            stats = stats_div.find_all('div', class_='app-stat')
            current_players_div = stats[0] if stats else None

            # Get the time element
            time_element = soup.find('abbr', class_='timeago')

        if title_element and current_players_div and time_element:
            # Extract the text and clean it up
            title = title_element.text.strip()

            # Get the player count from the first span with class "num"
            player_count = int(current_players_div.find('span', class_='num').text.replace(',', ''))

            # Get the "playing X min ago" text
            timestamp = time_element.get('title', '')
            time_ago = convert_timestamp_to_readable(timestamp)

            last_updated = time_ago

            return title, player_count, last_updated
        else:
            return None, None , None

    except Exception as e:
        print(f"Error extracting game stats: {e}")
        return None, None


if __name__ == "__main__":
    url = ("https://steamcharts.com/app/" + steamID)
    title, player_count, last_updated = get_game_stats(url)

    if title and player_count and last_updated is not None:
        print(f"Game: {title}")
        print(f"Current players: {player_count}")
        print(f"Last updated: {last_updated}")
    else:
        print("Failed to get game stats")