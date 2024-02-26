"""
    py-wordle
    A Python 3.1x recreation of the New York Times sensation "Wordle"

    [Still in the process of documenting everything.]

    Author: Saturn Harrison
    Company: ""
    Copyright: 2024
"""
import random
import time

WORD_LENGTH = 5
VALID_WORD_PATH = 'word_bank/all_words.txt'
ANSWER_WORD_PATH = 'word_bank/target_words.txt'
CONFIG_PATH = 'config.txt'
DATE_TODAY = time.strftime("%d/%m/%Y")

# Used so that i can ouput why the answer the user has inputed may not be a valid word.
ERROR_MESSAGE = " "
# The welcome message, better practice than using a simple `print("str")` function call.
WELCOME_MESSAGE = f"Welcome to Wordle! The date today is {DATE_TODAY}."
# The intro word prompt.
WORD_PROMPT = "You have {attempts_left} attempts left.\nPlease enter a word: "
# The format for how an attempt is printed to the console.
ATTEMPT_FORMAT = "{attempt}\n{footnote} ({score}/5.0)"
# The ouput format for sharing your results of the game.
MOMENTO_FORMAT = "Wordle {final_word} {score}/6\n\n{attempts}"

## Utility functions:
# Gets a list of strings for each line in a text file.
def get_list_from_txt(path):
    return open(path, 'rt', encoding="utf8").read().splitlines()

# Generates a dictionary for the amount of each unique character in a word.
def generate_char_frequency(word):
    char_freq = {}
    splitted_word = list(word)
    for char in splitted_word:
        char_freq[char] = char_freq.setdefault(char, 0) + 1
    
    return char_freq
def get_index_of_character_excluding_others(index, word):
    char = word[index]
    count = 0
    for i, c in enumerate(word):
        if c == char:
            count += 1
        if i == index:
            return count
    return -1
# Clears the console for a clean view.
def clear_console():
    global ERROR_MESSAGE
    global WELCOME_MESSAGE
    print("\033c", end='')
    print(WELCOME_MESSAGE)
    print(ERROR_MESSAGE)
    ERROR_MESSAGE = ""

# All valid input words. Not every word you can use can be an answer.
valid_words = get_list_from_txt(VALID_WORD_PATH)
# All the words the answer for the game could possibly be.
target_words = get_list_from_txt(ANSWER_WORD_PATH)

CONFIG = dict()

def generate_config():
    settings = get_list_from_txt(CONFIG_PATH)
    for line in settings:
        if line.startswith("#") or len(line) < 1 or "=" not in line:
            continue

        global CONFIG
        setting = line.split("=")[0]
        value = line.split("#")[0].strip().split("=")[1]

        if setting == "game_characters":
            try:
                CONFIG[setting] = value.split(",")
            except:
                CONFIG[setting] = ["⬛", "🟨", "🟩"]
        elif setting == "max_attempts":
            try:
                CONFIG[setting] = int(value)
            except:
                CONFIG[setting] = 6
        else:
            CONFIG[setting] = value == "true"
generate_config()

def send_error(msg):
    global ERROR_MESSAGE
    ERROR_MESSAGE = msg
    return False

FOOTNOTES = {
    "MISSED": 0,
    "CONTAINS": 1,
    "CORRECT": 2
}
def game_char_from_value(value):
    return CONFIG["game_characters"][value]

# Will be a dictionary of tuples, with the attempted word as a key, and a tuple containing the score, and the displayed footnote.
attempts = dict()
# The word of the "day".
target_word = ""

def init_game():
    clear_console()
    if CONFIG["debug_mode"]:
        print(f"[DEBUG]: A valid word has been chosen. ({target_word})") # Making sure an answer is actually provided.

# generates the contained letters seperately, as this handles whether a character has been guessed previously and is correct.
def generate_contained_scores(user_guess):
    score_list = list()
    target_freq = generate_char_frequency(target_word)
    for i, char in enumerate(user_guess):
        if target_word.find(char) > -1:
            if get_index_of_character_excluding_others(i, user_guess) <= target_freq[char]:
                score_list.append(1)
                continue
        score_list.append(0)
    return score_list
    
def generate_confirmed_scores(user_guess, contained_list):
    target_freq = generate_char_frequency(target_word)
    score_list = contained_list[:]
    for i, char in enumerate(user_guess):
        if char == target_word[i]:
            score_list[i] = 2        
            target_freq[char] -= 1   
            # Iterates back on itself to clear any excess "yellow" letters
            for index, c in enumerate(user_guess[::-1]):
                if c == char and score_list[4 - index] < 2 and 4-index != i:
                    if target_freq[c] > 0:
                        score_list[index] = 1
                        target_freq[char] -= 1   
                    else:
                        score_list[index] = 0     
                        target_freq[char] -= 1   
    return score_list
    
def generate_score(user_guess):
    score_list = generate_confirmed_scores(user_guess, generate_contained_scores(user_guess))
    return score_list
def reveal_attempt(score_list):
    emoji_list = list()
    for score in score_list:
        emoji_list.append(game_char_from_value(score))
    return emoji_list

def generate_attempt(user_guess):
    score_list = generate_score(user_guess)
    attempt = (reveal_attempt(score_list), score_list)
    attempts[user_guess] = attempt

def get_score(user_guess):
    if user_guess not in attempts:
        return 0
    total_score = 0
    for val in attempts[user_guess][1]:
        total_score += val
    return total_score
    
def print_attempts():
    clear_console()
    output = list()
    for key, score_tuple in attempts.items():
        output.append(ATTEMPT_FORMAT.format(attempt=key.upper(),footnote=''.join(map(str, score_tuple[0 if CONFIG["display_symbols"] else 1])), score=(get_score(key) / 2)))        
    for footnote in output:
        print(footnote)
    
def check_win_con(user_guess):
    return get_score(user_guess) >= 10
    
    
def generate_footnote():
    final_list = list()
    for _, score_tuple in attempts.items():
        final_list.append(''.join(score_tuple[0]))
    attempt_footnote = "\n".join(final_list)
    score = str(len(attempts))
    if not won_the_game:
        score = "X"
    return MOMENTO_FORMAT.format(final_word=(target_word.upper() if not CONFIG["seed_from_date"] else DATE_TODAY), score=score, attempts=attempt_footnote)

def check_attempt(user_guess):
    passed = False
    if user_guess in attempts:
        passed = send_error("You have already tried this word. Try again.")
    elif len(user_guess) != 5:
        passed = send_error("Your guess must be 5 characters in length. Try again.")
    elif not user_guess.isalpha():
        passed = send_error("Please only use alphabetical characters. Try again.")
    elif user_guess not in valid_words:
        passed = send_error("Invalid word. Try again.")
    else:
        passed = True
        generate_attempt(user_guess)
    return passed
        
# Gets the word from the target list.
def get_wordle_word():
    if CONFIG["seed_from_date"]:
        random.seed(a=DATE_TODAY,version=2)
    return random.choice(target_words)

# Sends the user a prompt to recieve a momento of their game.
def prompt_footnote():
    input("Press ENTER for momento.")
    print("\033c", end='')
    print(generate_footnote())

won_the_game = False
def play():
    while len(attempts) < CONFIG["max_attempts"]:
        user_guess = input(WORD_PROMPT.format(attempts_left=(CONFIG["max_attempts"] - len(attempts))))
        if check_attempt(user_guess):
            global won_the_game; won_the_game = check_win_con(user_guess)
            print_attempts()

            if won_the_game:
                print("You won!")
                prompt_footnote()
                return
        else:
            print_attempts()
    print("You ran out of attempts :(")
    print(f"The correct word was {target_word}.")
    prompt_footnote()

def init():
    global target_word
    target_word = get_wordle_word()
    init_game()
    play()

init()
input("")
print("\033c", end='')
