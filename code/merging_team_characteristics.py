import os
import pandas as pd


teams_info_per_season = dict()
seasons = list(range(2009, 2023))
data_path = os.path.join('..', 'data', 'team-characteristics', 'scraped')

for season in seasons:
    filename = f'teams_{season}_{season + 1}.csv'
    filepath = os.path.join(data_path, filename)
    df = pd.read_csv(filepath_or_buffer=filepath)

    df['season'] = f'{season}/{season + 1}'
    df = df[['season'] + df.columns[:-1].tolist()]

    teams_info_per_season[season] = df

team_info_per_season_list = teams_info_per_season.values()
merged_team_info = pd.concat(team_info_per_season_list, ignore_index=True)
merged_team_info.to_csv(path_or_buf=os.path.join('..', 'data', 'team-characteristics', f'team_characteristics.csv'),
                        index=False)
