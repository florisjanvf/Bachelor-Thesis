import requests
import os
import time
import datetime
import random
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


def get_player_characteristics_for(season, fake_headers):
    filename_to_check = f'player_characteristics_{season}_{season+1}.csv'
    filepath_to_check = os.path.join('..', 'data', 'player-characteristics', 'scraped', filename_to_check)
    if os.path.exists(filepath_to_check):
        player_characteristics = pd.read_csv(filepath_or_buffer=filepath_to_check)
    else:
        column_names = ['season', 'player_name', 'team', 'player_rating', 'position', 'nation',
                        'league', 'skill_moves', 'weak_foot_quality', 'work_rate_a',
                        'work_rate_d', 'player_height', 'player_weight', 'age']
        player_characteristics = pd.DataFrame(columns=column_names)

        # get the number of pages to scrape from
        initial_url = f'https://www.futbin.com/{season+1-2000}/players?page=1&league=13&showStats=Weight,Age&version=all_nif'
        initial_request = requests.get(url=initial_url, headers=fake_headers)
        soup = BeautifulSoup(initial_request.text, 'html.parser')
        page_items = soup.find_all('li', class_='page-item')
        last_page_item = page_items[-2]
        soup = BeautifulSoup(str(last_page_item), 'html.parser')
        last_page_link = soup.find('a', class_='page-link')
        last_page_number = int(last_page_link.text)
        sleep_time = random.choice([5, 6, 7, 8, 9, 10])
        time.sleep(sleep_time)

        # create list of page numbers to check
        pages_to_scrape = list(range(1, last_page_number + 1))

        # scrape every page for the player id
        for page in pages_to_scrape:
            player_stats_on_page = get_player_characteristics_on(page, season, fake_headers)
            player_characteristics = pd.concat([player_characteristics, player_stats_on_page], ignore_index=True)

        player_characteristics.to_csv(path_or_buf=filepath_to_check, index=False)

    return player_characteristics


def get_player_characteristics_on(page, season, fake_headers):
    url = f'https://www.futbin.com/{season+1-2000}/players?page={page}&league=13&showStats=Weight,Age&version=all_nif'
    request = requests.get(url=url, headers=fake_headers)
    soup = BeautifulSoup(request.text, 'html.parser')
    sleep_duration = random.choice([5, 6, 7, 8, 9, 10])
    time.sleep(sleep_duration)

    column_names = ['season', 'player_name', 'team', 'player_rating', 'position', 'nation',
                    'league', 'skill_moves', 'weak_foot_quality', 'work_rate_a',
                    'work_rate_d', 'player_height', 'player_weight', 'age']
    player_characteristics = pd.DataFrame(columns=column_names)

    # Find all table rows (tr) with class 'player_tr_1' or 'player_tr_2'
    player_rows = soup.find_all('tr', class_=['player_tr_1', 'player_tr_2'])

    for row in player_rows:
        results = dict()
        results['season'] = f'{season}/{season+1}'
        results['league'] = 'EPL'

        # Find the player name
        player_name = row.find('a', class_='player_name_players_table').text
        results['player_name'] = player_name

        # Find the team and nation
        titles = []
        tags = row.find_all('a', {'data-original-title': True, 'data-placement': 'top'})
        for tag in tags:
            title = tag['data-original-title']
            titles.append(title)
        player_team = titles[0]
        player_nation = titles[1]
        results['team'] = player_team
        results['nation'] = player_nation

        # Find the player rating
        span_tag = row.select_one('span[class^="form rating"]')
        rating = int(span_tag.text)
        results['player_rating'] = rating

        # Find the player position
        position_element = row.find(class_='font-weight-bold')
        position = position_element.text.strip()
        results['position'] = position

        # Find out the version of the card
        versions_to_keep = ['', 'normal', 'rare', 'non-rare']
        td_element = row.find('td', class_='mobile-hide-table-col')
        version = td_element.div.text.strip().lower()
        if version not in versions_to_keep:
            continue

        # Get Skills Moves and Weak Foot Quality
        skill_moves = np.nan
        weak_foot_quality = np.nan
        td_elements = row.find_all('td')
        for td in td_elements:
            skill_moves_element = td.find('i', class_='icon-star-full stars-')
            weak_foot_quality_element = td.find('i', class_='icon-star-full stars')
            if skill_moves_element:
                skill_moves = td.text.strip()
                if skill_moves == '':
                    pass
                else:
                    skill_moves = int(skill_moves)
            if weak_foot_quality_element:
                weak_foot_quality = int(td.text.strip()[0])
        results['skill_moves'] = skill_moves
        results['weak_foot_quality'] = weak_foot_quality

        # Get Attacking Work Rate and Defensive Work Rate
        attacking_work_rate = np.nan
        defensive_work_rate = np.nan
        work_rates_elements_v1 = row.find_all('td')[7].find_all(style='font-weight: bold;')
        work_rates_elements_v2 = row.find_all('td')[8].find_all(style='font-weight: bold;')
        if work_rates_elements_v1:
            attacking_work_rate = work_rates_elements_v1[0].text.strip()
            defensive_work_rate = work_rates_elements_v1[1].text.strip()
        if work_rates_elements_v2:
            attacking_work_rate = work_rates_elements_v2[0].text.strip()
            defensive_work_rate = work_rates_elements_v2[1].text.strip()
        results['work_rate_a'] = attacking_work_rate
        results['work_rate_d'] = defensive_work_rate

        # Get Height, Age and Weight
        td_elements_v2 = row.find_all('td')
        # Weight
        weight = td_elements_v2[-1].text.strip()
        results['player_weight'] = weight
        # Age
        current_age_player = td_elements_v2[-2].text.strip()
        current_year = datetime.date.today().year
        year_difference = current_year - season
        age_at_the_time = int(current_age_player) - year_difference + 1
        results['age'] = age_at_the_time
        # Height
        height = td_elements_v2[-6].text.strip().split(' ')[0]
        results['player_height'] = height

        results_df = pd.DataFrame(results, index=[0])
        player_characteristics = pd.concat([player_characteristics, results_df], ignore_index=True)

    return player_characteristics


def merge_player_characteristics(player_characteristics_per_season):
    filename_to_check = f'player_characteristics.csv'
    filepath_to_check = os.path.join('..', 'data', 'player-characteristics', filename_to_check)
    if os.path.exists(filepath_to_check):
        return
    else:
        if not isinstance(player_characteristics_per_season, dict):
            raise TypeError('please pass a dictionary as the function argument')
        else:
            player_characteristics_per_season_list = player_characteristics_per_season.values()
            merged_player_characteristics_df = pd.concat(player_characteristics_per_season_list, ignore_index=True)
            merged_player_characteristics_df.to_csv(path_or_buf=filepath_to_check, index=False)


def main():
    print('Starting program')
    print('-' * 100)
    start_time = time.time()

    possible_seasons = [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
    fake_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    season_input = input('Please enter the season for which you would like to scrape player'
                         ' characteristics (e.g., "2014" for the 2014/2015 season)\nOR'
                         ' enter "all" if you want to scrape player'
                         ' characteristics from the 2009/2010 season to the 2022/2023 season: ').lower()
    if season_input == 'all':
        seasons = possible_seasons
    else:
        try:
            int_season = int(season_input)
            if int_season < 2009 or int_season > 2022:
                raise ValueError
            else:
                seasons = [int_season]
        except ValueError:
            print('Invalid input for season, please try again')
            return

    player_characteristics_per_season = dict()
    for season in seasons:
        print(f'Scraping has started for season {season}/{season + 1}')

        print(f'Gathering player characteristics for season {season}/{season + 1}')
        player_characteristics = get_player_characteristics_for(season, fake_headers)

        print(f'Scraping has finished for season {season}/{season + 1}')
        player_characteristics_per_season[season] = player_characteristics

    if season_input == 'all':
        merge_player_characteristics(player_characteristics_per_season)

    print('-' * 100)
    print('Finished program')
    end_time = time.time()
    print(f'Execution time: {end_time - start_time}')


if __name__ == '__main__':
    main()
