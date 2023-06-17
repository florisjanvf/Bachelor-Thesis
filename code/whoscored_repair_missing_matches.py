import pandas as pd
import soccerdata as sd
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# initialize new dataframe where data will be stored
failed_to_scrape = []
game_dataframes = dict()
column_names = ['player_name', 'player_rating', 'starter',
                'home_game', 'match_id']

match_ids_to_scrape = [505335, 614056, 719865, 829520, 958430]
missing_seasons = ['2011/2012', '2012/2013', '2013/2014', '2014/2015', '2015/2016']
match_season_dic = dict(zip(match_ids_to_scrape, missing_seasons))

# Configure driver with Tor proxy using soccerdata API
ws = sd.WhoScored(proxy='tor')
driver = ws._driver

# get player ratings for each match in the season
for match_id in match_ids_to_scrape:
    print(f'Starting match: {match_id}')
    match_df = pd.DataFrame(columns=column_names)

    url = f'https://www.whoscored.com/Matches/{match_id}/LiveStatistics'
    # web driver goes to page
    driver.get(url)

    WebDriverWait(driver, timeout=60).until(
        EC.presence_of_element_located((By.ID, 'player-table-statistics-body')))

    player_names_list = []
    player_ratings_list = []
    starter_list = []
    home_away_list = []
    time.sleep(5)

    i = 1
    j = 1
    not_seen_first_dash = True
    for name in driver.find_elements(By.CSS_SELECTOR, 'a.player-link span.iconize.iconize-icon-left'):
        player_names_list.append(name.text)
    for rating in driver.find_elements(By.CSS_SELECTOR, 'td.rating'):
        rating_text = rating.text
        player_ratings_list.append(rating_text)
        if 1 <= i <= 11:
            starter_list.append(True)
            home_away_list.append(True)
        elif i >= 12:
            if rating_text != '-' and not_seen_first_dash:
                starter_list.append(False)
                home_away_list.append(True)
            elif rating_text != '-' and not not_seen_first_dash:
                if 1 <= j <= 11:
                    starter_list.append(True)
                else:
                    starter_list.append(False)
                home_away_list.append(False)
                j += 1
            else:
                if j < 7:
                    starter_list.append(False)
                    home_away_list.append(True)
                    not_seen_first_dash = False
                else:
                    starter_list.append(False)
                    home_away_list.append(False)
        i += 1
    # TODO: add extra selenium and BS code to scrape the age, position, nationality and minutes played

    len_player_names_list = len(player_names_list)
    len_player_ratings_list = len(player_ratings_list)
    if (len_player_names_list != len_player_ratings_list) or (len_player_names_list < 22):
        failed_to_scrape.append(match_id)
        continue

    print(len(player_names_list))
    print(len(player_ratings_list))
    match_df['player_name'] = player_names_list
    match_df['player_rating'] = player_ratings_list
    match_df['starter'] = starter_list
    match_df['home_game'] = home_away_list
    match_df['match_id'] = match_id

    print(f'Finished match: {match_id}')
    print('-' * 100)
    game_dataframes[match_id] = match_df

if len(failed_to_scrape) == 0:
    print('Successfully scraped all matches')
else:
    print(f'The scraper was unable to scrape matches with the following ids: {failed_to_scrape}')
    df_failures = pd.Series(data=failed_to_scrape, name='match_id')
    file_name = f'failed_to_scrape.csv'
    path_to_save = os.path.join('..', 'data', 'player-ratings', 'scraped', 'scraped-matches',
                                'failed-to-scrape', file_name)
    df_failures.to_csv(path_or_buf=path_to_save, index=False)

player_ratings = pd.concat(game_dataframes, axis=0)
driver.quit()

for match_id, season in match_season_dic.items():
    filename_to_check = f'player_ratings_{season.replace("/", "_")}.csv'
    filepath_to_check = os.path.join('..', 'data', 'player-ratings', 'scraped', filename_to_check)
    original_player_ratings = pd.read_csv(filepath_or_buffer=filepath_to_check)

    match_id_filter = original_player_ratings['match_id']==match_id
    new_ratings_df = game_dataframes[match_id]
    original_player_ratings.loc[match_id_filter,['player_name', 'player_rating', 'starter', 'home_game']] = \
        new_ratings_df.loc[:,['player_name', 'player_rating', 'starter', 'home_game']].values

    original_player_ratings.to_csv(path_or_buf=filepath_to_check, index=False)
