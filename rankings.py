import pandas as pd
import matplotlib.pyplot as plt
import time
import matplotlib.dates as mdates


start_time = time.time()

files = [
    'data/atp_rankings_70s.csv',
    'data/atp_rankings_80s.csv',
    'data/atp_rankings_90s.csv',
    'data/atp_rankings_00s.csv',
    'data/atp_rankings_10s.csv',
    'data/atp_rankings_20s.csv'
]

rankings_df_list = [pd.read_csv(file) for file in files]
rankings_df = pd.concat(rankings_df_list, ignore_index=True)

players_df = pd.read_csv('data/atp_players.csv')

players_df['dob'] = pd.to_datetime(players_df['dob'], format='%Y%m%d', errors='coerce')
rankings_df['ranking_date'] = pd.to_datetime(rankings_df['ranking_date'], format='%Y%m%d', errors='coerce')

print(rankings_df.columns)

rankings_top1000 = rankings_df.groupby('ranking_date').head(100)

merged_df = pd.merge(rankings_top1000, players_df, left_on='player', right_on='player_id', how='left')

merged_df['ranking_date'] = pd.to_datetime(merged_df['ranking_date'], errors='coerce')

merged_df['age'] = (merged_df['ranking_date'] - merged_df['dob']).dt.days // 365.25

average_age_per_date = merged_df.groupby('ranking_date')['age'].mean()

end_time = time.time()

execution_time = end_time - start_time

print(f"Czas wykonywania programu: {execution_time:.2f} sekundy")


# plots
plt.figure(figsize=(10, 6))
plt.plot(average_age_per_date.index, average_age_per_date.values, marker='o', linestyle='-')
plt.xlabel('Date')
plt.ylabel('Average Age')
plt.title('Average Age of Players in Ranking Over Time')
plt.grid(True)

date_format = mdates.DateFormatter('%Y-%m-%d')
plt.gca().xaxis.set_major_formatter(date_format)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

