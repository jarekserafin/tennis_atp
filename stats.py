import pandas as pd
import matplotlib.pyplot as plt


filenames = [f'data/atp_matches_{i}.csv' for i in range(1991, 2025)]

years = list(range(1991, 2025))
w_1stIn_mean = []
w_df = []
winner_hand_percent = []
winner_ht = []
winner_age = []
loser_age = []
difference = []

for filename in filenames:
    data = pd.read_csv(filename)

    mean_w_1stIn = data['w_1stIn'].mean()
    mean_w_df = data['w_df'].mean()
    mean_winner_ht = data['winner_ht'].mean()
    mean_winner_age = data['winner_age'].mean()
    mean_loser_age = data['loser_age'].mean()

    winners_right_or_left_hand_percent = (data[(data['winner_hand'] == 'R') | (data['winner_hand'] == 'U')].shape[0] / data.shape[0]) * 100

    w_1stIn_mean.append(mean_w_1stIn)
    w_df.append(mean_w_df)
    winner_hand_percent.append(winners_right_or_left_hand_percent)
    winner_ht.append(mean_winner_ht)
    winner_age.append(mean_winner_age)
    loser_age.append(mean_loser_age)
    difference.append(mean_winner_age - mean_loser_age)

# Tworzenie dataframe
stats_per_year = pd.DataFrame(
    {'years': years,
     'w_1stIn_mean': w_1stIn_mean,
     'w_df': w_df,
     'winner_hand_percent': winner_hand_percent,
     'winner_height': winner_ht,
     'winner_age': winner_age,
     'loser_age': loser_age,
     'diff of age': difference
     })

print(stats_per_year.head())

# Wykresy
# plt.plot(stats_per_year['years'], stats_per_year['winner_age'], label='Winner')
# plt.plot(stats_per_year['years'], stats_per_year['loser_age'], label='Loser')
plt.plot(stats_per_year['years'], stats_per_year['diff of age'], label='Diff')
plt.axhline(y=0, color='gray', linestyle='--')


plt.legend()
plt.show()
