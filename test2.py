import pandas as pd
import matplotlib.pyplot as plt

# Lista nazw plików
filenames = [f'atp_matches_{i}.csv' for i in range(1968, 2025)]

# Inicjalizacja list do przechowywania lat, średnich wartości i procentu zwycięzców z prawą ręką
years = list(range(1968, 2025))
w_1stIn_mean = []
w_df = []
winner_hand_percent = []

# Iteracja po nazwach plików
for filename in filenames:
    data = pd.read_csv(filename)

    mean_w_1stIn = data['w_1stIn'].mean()
    mean_w_df = data['w_df'].mean()  # Załóżmy, że 'w_df' to interesująca nas zmienna

    # Obliczenie procentu zwycięzców używających prawej ręki ('R')
    winners_right_hand_percent = (data[data['winner_hand'] == 'R'].shape[0] / data.shape[0]) * 100

    w_1stIn_mean.append(mean_w_1stIn)
    w_df.append(mean_w_df)
    winner_hand_percent.append(winners_right_hand_percent)

# Tworzenie dataframe
stats_per_year = pd.DataFrame(
    {'years': years, 'w_1stIn_mean': w_1stIn_mean, 'w_df': w_df, 'winner_hand_percent': winner_hand_percent})

# Usuwanie wierszy zawierających NaN
stats_per_year.dropna(subset=['w_1stIn_mean', 'w_df', 'winner_hand_percent'], inplace=True)

# Znajdowanie pierwszego indeksu, od którego nie ma NaN
first_valid_index = stats_per_year.index[0]

# Rysowanie wykresu
plt.plot(stats_per_year['years'], stats_per_year['w_1stIn_mean'], label='Mean of Winning 1st Serve In per Year',
         color='blue')
plt.scatter(stats_per_year['years'], stats_per_year['w_1stIn_mean'], color='red')
plt.plot(stats_per_year['years'], stats_per_year['w_df'], label='Mean of W_DF per Year', color='green')
plt.scatter(stats_per_year['years'], stats_per_year['w_df'], color='orange')

# Dodanie procentu zwycięzców z prawą ręką do wykresu
plt.plot(stats_per_year['years'], stats_per_year['winner_hand_percent'], label='Percentage of Winners with Right Hand',
         color='purple')
plt.scatter(stats_per_year['years'], stats_per_year['winner_hand_percent'], color='yellow')

# Dodanie etykiet i tytułu
plt.xlabel('Year')
plt.ylabel('Values')
plt.title('Statistics per Year')
plt.legend()
plt.show()
