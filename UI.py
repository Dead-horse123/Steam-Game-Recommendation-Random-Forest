import tkinter as tk
from tkinter import messagebox, font
import pandas as pd
import os
import re
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import threading

# Load the CSV file into a pandas DataFrame
dir_path = os.path.dirname(os.path.abspath(__file__))
file_path = r"\final_games_details.csv"
file_path = dir_path + file_path
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    messagebox.showerror('Error', f'File {file_path} not found.')
    exit()

# Create a dictionary to store game information with keys as game names
games_dict = {}

# Extract information from each row of the DataFrame and store it in the dictionary
for idx, row in df.iterrows():
    game_name = row['Name']
    game_info = f"ID: {row['gameID']} ¬ Name: {row['Name']} ¬ Year: {row['year']} ¬ Rating: {row['rating']}"
    games_dict[game_name] = game_info

# Function to update the games list based on search
def update_games_list(event=None):
    search_query = search_entry.get().strip().lower()
    games_listbox.delete(0, tk.END)
    if search_query == '':
        for game_info in games_dict.values():
            games_listbox.insert(tk.END, game_info)
    else:
        for game_name, game_info in games_dict.items():
            if search_query in game_name.lower():
                games_listbox.insert(tk.END, game_info)

# Function to add selected game to the played games list
def add_review(review):
    selected_game_info = games_listbox.get(tk.ACTIVE)
    if selected_game_info:
        # Extract game name using regex to handle special characters
        match = re.search(r'Name:\s*(.*?)\s*¬', selected_game_info)
        if match:
            selected_game_name = match.group(1).strip()
        else:
            messagebox.showwarning('Invalid Format', 'Failed to extract game name.')
            return
        
        # Check if the game is already in played games list
        for i in range(played_games_listbox.size()):
            item = played_games_listbox.get(i)
            split_item = item.split(' ¬ ')
            game_name_in_list = split_item[0].strip() if split_item else None
            if game_name_in_list and game_name_in_list == selected_game_name:
                # Update the review for the existing game entry
                played_games_listbox.delete(i)
                played_games_listbox.insert(i, f"{selected_game_name} ¬ {review}")
                return
        
        # If game is not already in played games list, add new entry
        played_games_listbox.insert(tk.END, f"{selected_game_name} ¬ {review}")

# Function to remove selected review from the played games list
def remove_review():
    selected_review = played_games_listbox.curselection()
    if selected_review:
        played_games_listbox.delete(selected_review)

# Function to write played games and reviews to a CSV file
def write_to_csv():
    data = []
    for i in range(played_games_listbox.size()):
        item = played_games_listbox.get(i)
        split_item = item.split(' ¬ ')
        if len(split_item) != 2:
            messagebox.showwarning('Invalid Format', f'Invalid format for item: {item}. Skipping.')
            continue
        
        game_name = split_item[0].strip()
        review_text = split_item[1].strip()
        
        # Map review text to numerical values
        if review_text == 'Like':
            review_value = 1
        elif review_text == 'Dislike':
            review_value = -1
        else:  # Neutral
            review_value = 0
        
        # Check if the game name exists in games_dict
        if game_name in games_dict:
            game_id = df[df['Name'] == game_name]['gameID'].values[0]
            data.append({'gameID': game_id, 'gameName': game_name, 'review': review_value})
        else:
            messagebox.showwarning('Game not found', f'Game "{game_name}" not found in the database.')

    if data:
        reviews_df = pd.DataFrame(data)
        reviews_df.to_csv(os.path.join(dir_path, r"your_games.csv"), index=False)
        messagebox.showinfo('CSV Saved', 'Played games reviews saved to your_games.csv')

# Function to load played games from your_games.csv
def load_played_games():
    try:
        if os.path.exists(os.path.join(dir_path, r"your_games.csv")):
            played_games_df = pd.read_csv(os.path.join(dir_path, r"your_games.csv"))
            for idx, row in played_games_df.iterrows():
                game_name = row['gameName']
                review = row['review']
                if review == 1:
                    review_text = 'Like'
                elif review == -1:
                    review_text = 'Dislike'
                else:
                    review_text = 'Neutral'
                played_games_listbox.insert(tk.END, f"{game_name} ¬ {review_text}")
    except Exception as e:
        messagebox.showerror('Error', f'Failed to load played games: {str(e)}')

# Function to run another Python script for recommendations
def get_recommendations():
    try:
        # Replace 'path_to_script.py' with the actual path to your Jupyter notebook
        notebook_path = os.path.join(dir_path, r'random_forest_model.ipynb')

        # Load the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        # Execute the notebook
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.preprocess(nb, {'metadata': {'path': dir_path}})

        # Show success message
        messagebox.showinfo('Notebook Executed', 'Recommendations generated successfully.')

    except Exception as e:
        messagebox.showerror('Error', f'Failed to run recommendations notebook: {str(e)}')

# Create the main window
root = tk.Tk()
root.title('Game Tracker')

# Set default font size for the application
default_font = font.nametofont("TkDefaultFont")
default_font.configure(size=12)
root.option_add("*Font", default_font)

# Search Frame
search_frame = tk.Frame(root)
search_frame.pack(pady=10)

search_label = tk.Label(search_frame, text='Search by Name:')
search_label.grid(row=0, column=0)

search_entry = tk.Entry(search_frame, width=50, font=('Arial', 14))
search_entry.grid(row=0, column=1)
search_entry.bind('<Return>', update_games_list)  # Bind Enter key to update_games_list function

search_button = tk.Button(search_frame, text='Search', command=update_games_list, font=('Arial', 12))
search_button.grid(row=0, column=2, padx=10)

# Games List Frame
games_frame = tk.Frame(root)
games_frame.pack(pady=10)

games_label = tk.Label(games_frame, text='Games:', font=('Arial', 16, 'bold'))
games_label.grid(row=0, column=0)

games_listbox = tk.Listbox(games_frame, width=100, height=15, font=('Arial', 12))
games_listbox.grid(row=1, column=0, padx=20)

scrollbar = tk.Scrollbar(games_frame, orient=tk.VERTICAL, command=games_listbox.yview)
scrollbar.grid(row=1, column=1, sticky=tk.NS)
games_listbox.config(yscrollcommand=scrollbar.set)

# Populate games_listbox with all games from the CSV upon application start
for game_info in games_dict.values():
    games_listbox.insert(tk.END, game_info)

# Played Games Frame
played_games_frame = tk.Frame(root)
played_games_frame.pack(pady=10)

played_games_label = tk.Label(played_games_frame, text='Played Games:', font=('Arial', 16, 'bold'))
played_games_label.grid(row=0, column=0)

played_games_listbox = tk.Listbox(played_games_frame, width=100, height=5, font=('Arial', 12))
played_games_listbox.grid(row=1, column=0, padx=20)

# Create scrollbar for played_games_listbox
scrollbar_played = tk.Scrollbar(played_games_frame, orient=tk.VERTICAL, command=played_games_listbox.yview)
scrollbar_played.grid(row=1, column=1, sticky=tk.NS)
played_games_listbox.config(yscrollcommand=scrollbar_played.set)

remove_button = tk.Button(played_games_frame, text='Remove Review', command=remove_review, font=('Arial', 12))
remove_button.grid(row=2, column=0, pady=10)

confirm_button = tk.Button(played_games_frame, text='Confirm', command=write_to_csv, font=('Arial', 12))
confirm_button.grid(row=3, column=0, pady=10)

# Rating Frame
rating_frame = tk.Frame(root)
rating_frame.pack(pady=10)

rating_label = tk.Label(rating_frame, text='Add Your Review:', font=('Arial', 16, 'bold'))
rating_label.grid(row=0, column=0, padx=10)

like_button = tk.Button(rating_frame, text='Like', command=lambda: add_review('Like'), font=('Arial', 12))
like_button.grid(row=0, column=1, padx=10)

dislike_button = tk.Button(rating_frame, text='Dislike', command=lambda: add_review('Dislike'), font=('Arial', 12))
dislike_button.grid(row=0, column = 2, padx=10)

neutral_button = tk.Button(rating_frame, text='Neutral', command=lambda: add_review('Neutral'), font=('Arial', 12))
neutral_button.grid(row=0, column=3, padx=10)

# Get Recommendations Frame
recommendations_frame = tk.Frame(root)
recommendations_frame.pack(pady=10)

recommendations_button = tk.Button(recommendations_frame, text='Get Recommendations', command=get_recommendations, font=('Arial', 14))
recommendations_button.pack()

# Function to run the tkinter application
def run_application():
    # Load played games from the CSV file if it exists
    load_played_games()
    # Run the tkinter main loop
    root.mainloop()

run_application()

