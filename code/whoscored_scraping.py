import numpy as np
import pandas as pd
import soccerdata as sd
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_epl_schedule(season_number):
    """Get EPL schedule for season that starts with season_number and ends with season_number+1"""
    filename_to_check = f'epl_schedule_{season_number}_{season_number + 1}.csv'
    filepath_to_check = os.path.join('..', 'data', 'player-ratings', 'scraped', 'match-schedules', filename_to_check)

    if os.path.exists(filepath_to_check):
        match_schedule = pd.read_csv(filepath_or_buffer=filepath_to_check)
    else:
        season_string = f'{season_number}-{season_number + 1}'
        ws = sd.WhoScored(leagues="ENG-Premier League", seasons=season_string, proxy='tor')
        match_schedule = ws.read_schedule()
        match_schedule.to_csv(path_or_buf=filepath_to_check, index=False)

    return match_schedule


def get_player_ratings(season_number, epl_schedule):
    """Get EPL player ratings for every match for season that starts with season_number and ends with season_number+1"""
    filename_to_check = f'player_ratings_{season_number}_{season_number + 1}.csv'
    filepath_to_check = os.path.join('..', 'data', 'player-ratings', 'scraped', filename_to_check)

    if os.path.exists(filepath_to_check):
        player_ratings = pd.read_csv(filepath_or_buffer=filepath_to_check)
    else:
        # initialize new dataframe where data will be stored
        failed_to_scrape = []
        failed_to_scrape_twice = []
        failed_to_scrape_thrice = []
        game_dataframes = []
        column_names = ['season', 'home_team', 'away_team', 'player_name', 'player_rating', 'starter',
                        'home_game', 'match_id']
        # get a list of all match_ids for the given season
        match_ids = epl_schedule.loc[:, 'game_id']

        # Configure driver with Tor proxy using soccerdata API
        ws = sd.WhoScored(proxy='tor')
        driver = ws._driver

        # # Configure Tor proxy
        # tor_proxy = "socks5://localhost:9050"  # Assuming Tor is running on the default port
        #
        # # Configure Selenium Chrome webdriver options
        # chrome_options = Options()
        # chrome_options.add_argument(f'--proxy-server={tor_proxy}')
        #
        # # Create the Chrome webdriver
        # driver = webdriver.Chrome(options=chrome_options)
        # # Now the driver is configured to use Tor as a proxy

        # get player ratings for each match in the season
        for match_id in match_ids:
            print(f'Starting match: {match_id}')
            match_filter = (epl_schedule['game_id'] == match_id)
            match_information = epl_schedule.loc[match_filter]
            home_team = match_information['home_team'].iloc[0]
            away_team = match_information['away_team'].iloc[0]
            match_df = pd.DataFrame(columns=column_names)

            url = f'https://www.whoscored.com/Matches/{match_id}/LiveStatistics'
            # web driver goes to page
            driver.get(url)

            WebDriverWait(driver, timeout=60).until(
                EC.presence_of_element_located((By.ID, 'player-table-statistics-body')))

            player_names_list = []
            player_ratings_list = []
            for name in driver.find_elements(By.CSS_SELECTOR, 'a.player-link span.iconize.iconize-icon-left'):
                player_names_list.append(name.text)
            for rating in driver.find_elements(By.CSS_SELECTOR, 'td.rating'):
                player_ratings_list.append(rating.text)
            # TODO: add extra selenium and BS code to scrape the age, position, nationality and minutes played

            len_player_names_list = len(player_names_list)
            if len_player_names_list == 36 or len_player_names_list == 40:
                half_len_player_names = int(len_player_names_list / 2)
                home_list = [True] * half_len_player_names
                away_list = [False] * half_len_player_names
                home_away_list = home_list + away_list

                starter_home_list = [True] * 11 + [False] * (half_len_player_names - 11)
                starter_away_list = [True] * 11 + [False] * (half_len_player_names - 11)
                starter_list = starter_home_list + starter_away_list
            else:
                home_away_list = [np.nan] * len_player_names_list
                starter_list = [np.nan] * len_player_names_list

            len_player_ratings_list = len(player_ratings_list)
            if (len_player_names_list != len_player_ratings_list) or (len_player_names_list not in [36, 40]):
                failed_to_scrape.append(match_id)
                continue

            print(len(player_names_list))
            print(len(player_ratings_list))
            match_df['player_name'] = player_names_list
            match_df['player_rating'] = player_ratings_list
            match_df['starter'] = starter_list
            match_df['home_game'] = home_away_list
            match_df['season'] = f'{season_number}/{season_number + 1}'
            match_df['home_team'] = home_team
            match_df['away_team'] = away_team
            match_df['match_id'] = match_id

            print(f'Finished match: {match_id}')
            print('-' * 100)
            file_name = f'match_{match_id}.csv'
            subfolder = f'{season_number}-{season_number + 1}'
            path_to_save = os.path.join('..', 'data', 'player-ratings', 'scraped', 'scraped-matches',
                                        subfolder, file_name)
            match_df.to_csv(path_or_buf=path_to_save)
            game_dataframes.append(match_df)

        for match_id in failed_to_scrape:
            print(f'Starting match: {match_id}')
            match_filter = (epl_schedule['game_id'] == match_id)
            match_information = epl_schedule.loc[match_filter]
            home_team = match_information['home_team'].iloc[0]
            away_team = match_information['away_team'].iloc[0]
            match_df = pd.DataFrame(columns=column_names)

            url = f'https://www.whoscored.com/Matches/{match_id}/LiveStatistics'
            # web driver goes to page
            driver.get(url)

            WebDriverWait(driver, timeout=60).until(
                EC.presence_of_element_located((By.ID, 'player-table-statistics-body')))

            player_names_list = []
            player_ratings_list = []
            time.sleep(5)
            for name in driver.find_elements(By.CSS_SELECTOR, 'a.player-link span.iconize.iconize-icon-left'):
                player_names_list.append(name.text)
            for rating in driver.find_elements(By.CSS_SELECTOR, 'td.rating'):
                player_ratings_list.append(rating.text)
            # TODO: add extra selenium and BS code to scrape the age, position, nationality and minutes played

            len_player_names_list = len(player_names_list)
            if len_player_names_list == 36 or len_player_names_list == 40:
                half_len_player_names = int(len_player_names_list / 2)
                home_list = [True] * half_len_player_names
                away_list = [False] * half_len_player_names
                home_away_list = home_list + away_list

                starter_home_list = [True] * 11 + [False] * (half_len_player_names - 11)
                starter_away_list = [True] * 11 + [False] * (half_len_player_names - 11)
                starter_list = starter_home_list + starter_away_list
            else:
                home_away_list = [np.nan] * len_player_names_list
                starter_list = [np.nan] * len_player_names_list

            len_player_ratings_list = len(player_ratings_list)
            if (len_player_names_list != len_player_ratings_list) or (len_player_names_list not in [36, 40]):
                failed_to_scrape_twice.append(match_id)
                continue

            print(len(player_names_list))
            print(len(player_ratings_list))
            match_df['player_name'] = player_names_list
            match_df['player_rating'] = player_ratings_list
            match_df['starter'] = starter_list
            match_df['home_game'] = home_away_list
            match_df['season'] = f'{season_number}/{season_number + 1}'
            match_df['home_team'] = home_team
            match_df['away_team'] = away_team
            match_df['match_id'] = match_id

            print(f'Finished match: {match_id}')
            print('-' * 100)
            file_name = f'match_{match_id}.csv'
            subfolder = f'{season_number}-{season_number + 1}'
            path_to_save = os.path.join('..', 'data', 'player-ratings', 'scraped', 'scraped-matches',
                                        subfolder, file_name)
            match_df.to_csv(path_or_buf=path_to_save)
            game_dataframes.append(match_df)

        for match_id in failed_to_scrape_twice:
            print(f'Starting match: {match_id}')
            match_filter = (epl_schedule['game_id'] == match_id)
            match_information = epl_schedule.loc[match_filter]
            home_team = match_information['home_team'].iloc[0]
            away_team = match_information['away_team'].iloc[0]
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
                failed_to_scrape_thrice.append(match_id)
                continue

            print(len(player_names_list))
            print(len(player_ratings_list))
            match_df['player_name'] = player_names_list
            match_df['player_rating'] = player_ratings_list
            match_df['starter'] = starter_list
            match_df['home_game'] = home_away_list
            match_df['season'] = f'{season_number}/{season_number + 1}'
            match_df['home_team'] = home_team
            match_df['away_team'] = away_team
            match_df['match_id'] = match_id

            print(f'Finished match: {match_id}')
            print('-' * 100)
            file_name = f'match_{match_id}.csv'
            subfolder = f'{season_number}-{season_number + 1}'
            path_to_save = os.path.join('..', 'data', 'player-ratings', 'scraped', 'scraped-matches',
                                        subfolder, file_name)
            match_df.to_csv(path_or_buf=path_to_save)
            game_dataframes.append(match_df)

        if len(failed_to_scrape_thrice) == 0:
            print('Successfully scraped all matches')
        else:
            print(f'The scraper was unable to scrape matches with the following ids: {failed_to_scrape_thrice}')
            df_failures = pd.Series(data=failed_to_scrape_thrice, name='match_id')
            file_name = f'{season_number}_{season_number + 1}_failed_to_scrape.csv'
            path_to_save = os.path.join('..', 'data', 'player-ratings', 'scraped', 'scraped-matches',
                                        'failed-to-scrape', file_name)
            df_failures.to_csv(path_or_buf=path_to_save, index=False)
        player_ratings = pd.concat(game_dataframes, axis=0)
        player_ratings.to_csv(path_or_buf=filepath_to_check, index=False)
        driver.quit()
    return player_ratings


def merge_player_ratings(player_ratings_per_season):
    filename_to_check = f'player_ratings.csv'
    filepath_to_check = os.path.join('..', 'data', 'player-ratings', filename_to_check)
    if os.path.exists(filepath_to_check):
        return
    else:
        if not isinstance(player_ratings_per_season, dict):
            raise TypeError('please pass a dictionary as the function argument')
        else:
            player_ratings_per_season_list = player_ratings_per_season.values()
            merged_player_ratings_df = pd.concat(player_ratings_per_season_list, ignore_index=True)
            merged_player_ratings_df.to_csv(path_or_buf=filepath_to_check, index=False)


def main():
    print('Starting program')
    print('-' * 100)
    start_time = time.time()

    # TODO: uncomment line below and delete line below that once all the data for the 2022/2023 season is available
    possible_seasons = [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]

    season_input = input('Please enter the season for which you would'
                         ' like to scrape the EPL match ratings (e.g., 2015)\nOR enter "Order 66" if'
                         ' you want to scrape everything from the 2009/2010\nseason to the 2022/2023 season: ').lower()
    if season_input == 'order 66':
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

    player_ratings_per_season = dict()
    for season in seasons:
        print(f'Scraping has started for season {season}/{season + 1}')

        print(f'Gathering EPL schedule for season {season}/{season + 1}')
        # compute the epl schedule for that season
        epl_schedule = get_epl_schedule(season)

        print(f'Gathering player ratings for season {season}/{season + 1}')
        # compute player ratings for all matches in the season
        player_ratings = get_player_ratings(season, epl_schedule)

        print(f'Scraping has finished for season {season}/{season + 1}')
        player_ratings_per_season[season] = player_ratings

    if season_input == 'order 66':
        merge_player_ratings(player_ratings_per_season)

    print('-' * 100)
    print('Finished program')
    end_time = time.time()
    print(f'Execution time: {end_time - start_time}')


if __name__ == '__main__':
    main()
