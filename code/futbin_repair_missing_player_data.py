import numpy as np
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import time
import random
import datetime


def get_player_characteristics_for(url, season, fake_headers):
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


########################################################################

# load in the data
data_path = os.path.join('..', 'data')
fake_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
df_2011_2012 = pd.read_csv(os.path.join(data_path, 'player-characteristics', 'scraped', 'player_characteristics_2011_2012.csv'))
df_2012_2013 = pd.read_csv(os.path.join(data_path, 'player-characteristics', 'scraped', 'player_characteristics_2012_2013.csv'))
df_2013_2014 = pd.read_csv(os.path.join(data_path, 'player-characteristics', 'scraped', 'player_characteristics_2013_2014.csv'))
df_2014_2015 = pd.read_csv(os.path.join(data_path, 'player-characteristics', 'scraped', 'player_characteristics_2014_2015.csv'))

########################################################################

# remove the 6 teams that should not be there
teams_to_remove = ['Burnley', 'Crystal Palace', 'Hull City', 'West Ham United', 'Southampton', 'Leicester City']
wrong_teams_obs = df_2011_2012.loc[df_2011_2012['team'].isin(teams_to_remove)]
wrong_teams_obs_ix = wrong_teams_obs.index
df_2011_2012.drop(index=wrong_teams_obs_ix, inplace=True)
print(df_2011_2012['team'].nunique())  # check to see it went according to plan
# scrape results for new teams
urls = ['https://www.futbin.com/12/players?page=1&club=3&showStats=Weight,Age&version=all_nif',
        'https://www.futbin.com/12/players?page=1&showStats=Weight,Age&version=all_nif&club=1917',
        'https://www.futbin.com/12/players?page=1&showStats=Weight,Age&version=all_nif&club=144',
        'https://www.futbin.com/12/players?club=144&page=1&showStats=Weight,Age&version=all_nif&club=4',
        'https://www.futbin.com/12/players?page=1&showStats=Weight,Age&version=all_nif&club=1792',
        'https://www.futbin.com/12/players?page=1&showStats=Weight,Age&version=all_nif&club=110']

result = list()

for url in urls:
    res = get_player_characteristics_for(url, 2011, fake_headers)
    result.append(res)

df_to_add = pd.concat(result, ignore_index=True)
df_2011_2012 = pd.concat([df_2011_2012, df_to_add], ignore_index=True)
df_2011_2012.to_csv(path_or_buf=os.path.join(data_path, 'player-characteristics', 'scraped', 'player_characteristics_2011_2012.csv'), index=False)

########################################################################

# remove the 6 teams that should not be there
teams_to_remove = ['Burnley', 'Crystal Palace', 'Hull City', 'Leicester City']
wrong_teams_obs = df_2012_2013.loc[df_2012_2013['team'].isin(teams_to_remove)]
wrong_teams_obs_ix = wrong_teams_obs.index
df_2012_2013.drop(index=wrong_teams_obs_ix, inplace=True)
print(df_2012_2013['team'].nunique())  # check to see it went according to plan
# scrape results for new teams
urls = ['https://www.futbin.com/13/players?page=1&showStats=Weight,Age&version=all_nif&club=1793',
        'https://www.futbin.com/13/players?page=2&showStats=Weight,Age&version=all_nif&club=1793',
        'https://www.futbin.com/13/players?page=1&showStats=Weight,Age&version=all_nif&club=1917',
        'https://www.futbin.com/13/players?page=2&showStats=Weight,Age&version=all_nif&club=1917',
        'https://www.futbin.com/13/players?page=1&showStats=Weight,Age&version=all_nif&club=144',
        'https://www.futbin.com/13/players?page=2&showStats=Weight,Age&version=all_nif&club=144',
        'https://www.futbin.com/13/players?page=1&showStats=Weight,Age&version=all_nif&club=1792',
        'https://www.futbin.com/13/players?page=2&showStats=Weight,Age&version=all_nif&club=1792']

result = list()

for url in urls:
    res = get_player_characteristics_for(url, 2012, fake_headers)
    result.append(res)

df_to_add = pd.concat(result, ignore_index=True)
df_2012_2013 = pd.concat([df_2012_2013, df_to_add], ignore_index=True)
df_2012_2013.to_csv(path_or_buf=os.path.join(data_path, 'player-characteristics', 'scraped', 'player_characteristics_2012_2013.csv'), index=False)

########################################################################

# remove the 6 teams that should not be there
teams_to_remove = ['Burnley', 'Queens Park Rangers', 'Leicester City']
wrong_teams_obs = df_2013_2014.loc[df_2013_2014['team'].isin(teams_to_remove)]
wrong_teams_obs_ix = wrong_teams_obs.index
df_2013_2014.drop(index=wrong_teams_obs_ix, inplace=True)
print(df_2013_2014['team'].nunique())  # check to see it went according to plan
# scrape results for new teams
urls = ['https://www.futbin.com/14/players?page=1&showStats=Weight,Age&version=all_nif&club=1792',
        'https://www.futbin.com/14/players?page=2&showStats=Weight,Age&version=all_nif&club=1792',
        'https://www.futbin.com/14/players?page=1&showStats=Weight,Age&version=all_nif&club=1961',
        'https://www.futbin.com/14/players?page=2&showStats=Weight,Age&version=all_nif&club=1961',
        'https://www.futbin.com/14/players?page=1&showStats=Weight,Age&version=all_nif&club=144',
        'https://www.futbin.com/14/players?page=2&showStats=Weight,Age&version=all_nif&club=144']

result = list()

for url in urls:
    res = get_player_characteristics_for(url, 2013, fake_headers)
    result.append(res)

df_to_add = pd.concat(result, ignore_index=True)
df_2013_2014 = pd.concat([df_2013_2014, df_to_add], ignore_index=True)
df_2013_2014.to_csv(path_or_buf=os.path.join(data_path, 'player-characteristics', 'scraped', 'player_characteristics_2013_2014.csv'), index=False)

########################################################################

# remove the 6 teams that should not be there
teams_to_remove = ['Norwich City', 'Bournemouth', 'Watford']
wrong_teams_obs = df_2014_2015.loc[df_2014_2015['team'].isin(teams_to_remove)]
wrong_teams_obs_ix = wrong_teams_obs.index
df_2014_2015.drop(index=wrong_teams_obs_ix, inplace=True)
print(df_2014_2015['team'].nunique())  # check to see it went according to plan
# scrape results for new teams
urls = ['https://www.futbin.com/15/players?page=1&showStats=Weight,Age&version=all_nif&club=15',
        'https://www.futbin.com/15/players?page=2&showStats=Weight,Age&version=all_nif&club=15',
        'https://www.futbin.com/15/players?page=1&showStats=Weight,Age&version=all_nif&club=1796',
        'https://www.futbin.com/15/players?page=2&showStats=Weight,Age&version=all_nif&club=1796',
        'https://www.futbin.com/15/players?page=1&showStats=Weight,Age&version=all_nif&club=1952',
        'https://www.futbin.com/15/players?page=2&showStats=Weight,Age&version=all_nif&club=1952']

result = list()

for url in urls:
    res = get_player_characteristics_for(url, 2014, fake_headers)
    result.append(res)

df_to_add = pd.concat(result, ignore_index=True)
df_2014_2015 = pd.concat([df_2014_2015, df_to_add], ignore_index=True)
df_2014_2015.to_csv(path_or_buf=os.path.join(data_path, 'player-characteristics', 'scraped', 'player_characteristics_2014_2015.csv'), index=False)
