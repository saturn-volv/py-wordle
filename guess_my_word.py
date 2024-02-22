"""
    py-wordle
    A Python 3.1x recreation of the New York Times sensation "Wordle"

    Author: Saturn Harrison
    Company: ""
    Copyright: 2024
"""
import random
import time

## Utility functions:
# Gets a list of strings for each line in a text file.
def get_list_from_txt(path):
    return open(path, 'rt').read().splitlines()

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
    print("\033c", end='')
    print(GUI.WELCOME_MESSAGE)
    print(GUI.ERROR_MESSAGE)
    GUI.ERROR_MESSAGE = ""

MAX_ATTEMPTS = 6
WORD_LENGTH = 5

VALID_WORD_PATH = 'word_bank/all_words.txt'
ANSWER_WORD_PATH = 'word_bank/target_words.txt'
CONFIG_PATH = 'config.txt'

DATE_TODAY = time.strftime("%d/%m/%Y")

# All valid input words. Not every word you can use can be an answer.
valid_words = get_list_from_txt(VALID_WORD_PATH)
# All the words the answer for the game could possibly be.
target_words = get_list_from_txt(ANSWER_WORD_PATH)
class Config:
    # For interal use to make sure everything is working.
    debug_mode = False
    # Whether to print using emojis, or with numerical values.
    display_symbols = False
    # For full customization of what characters can be displayed.
    game_characters = list()
    # Whether to use a seed from todays date, or psuedo-random
    seed_from_date = False

    # Setting the previous values does nothing.
    def generate_config(self):
        settings = get_list_from_txt(CONFIG_PATH)
        for line in settings:
            if line.startswith("#") or len(line) < 1:
                continue
            setting = line.split("=")[0]
            value = line.split("#")[0].strip().split("=")[1]
            if setting == "debug_mode":
                self.debug_mode = value == "true"
            elif setting == "display_symbols":
                self.display_symbols = value == "true"
            elif setting == "game_characters":
                self.game_characters = value.split(",")
            elif setting == "seed_from_date":
                self.seed_from_date = value == "true"
    def __init__(self):
        self.generate_config()

CONFIG = Config()

# A front end class to handle how text may be displayed. This could be used to provide localization in the future.
class GUI:
    # Used so that i can ouput why the answer the user has inputed may not be a valid word.
    ERROR_MESSAGE = ""
    # The welcome message, better practice than using a simple `print("str")` function call.
    WELCOME_MESSAGE = f"Welcome to Wordle! The date today is {DATE_TODAY}."
    # The intro word prompt.
    WORD_PROMPT = "You have {attempts_left} attempts left.\nPlease enter a word: "
    # The format for how an attempt is printed to the console.
    ATTEMPT_FORMAT = "{attempt}\n{footnote} ({score}/5.0)"
    # The ouput format for sharing your results of the game.
    MOMENTO_FORMAT = "Wordle {final_word} {score}/6\n\n{attempts}"

    def send_error(msg):
        GUI.ERROR_MESSAGE = msg
        return False

    # Simple structure to clarify the ascii tokens based on a score value of each character.
    class Footnote:
        MISSED = (CONFIG.game_characters[0], 0)
        CONTAINS = (CONFIG.game_characters[1], 1)
        CORRECT = (CONFIG.game_characters[2], 2)

        def from_score(value):
            for t in [  GUI.Footnote.MISSED,  
                        GUI.Footnote.CONTAINS,
                        GUI.Footnote.CORRECT ]:
                if t[1] == value:
                    return t[0]
            return GUI.Footnote.MISSED
        
        def generate_footnote(game):
            attempts = game.attempts
            final_list = list()
            for _, score_tuple in attempts.items():
                final_list.append(''.join(score_tuple[0]))
            attempt_footnote = "\n".join(final_list)
            score = str(len(attempts))
            if not won_the_game:
                score = "X"
            return GUI.MOMENTO_FORMAT.format(final_word=game.target_word.upper(), score=score, attempts=attempt_footnote)

class Game:
    # Will be a dictionary of tuples, with the attempted word as a key, and a tuple containing the score, and the displayed footnote.
    attempts = dict()
    # The word of the "day".
    target_word = ""

    def __init__(self, target_word):
        self.target_word = target_word
        clear_console()
        if CONFIG.debug_mode:
            print(f"[DEBUG]: A valid word has been chosen. ({self.target_word})") # Making sure an answer is actually provided.

    # generates the contained letters seperately, as this handles whether a character has been guessed previously and is correct.
    def generate_contained_scores(self, user_guess):
        score_list = list()
        target_freq = generate_char_frequency(self.target_word)
        for i, char in enumerate(user_guess):
            if self.target_word.find(char) > -1:
                if get_index_of_character_excluding_others(i, user_guess) <= target_freq[char]:
                    print(char)
                    score_list.append(1)
                    continue
            score_list.append(0)
        return score_list
    
    def generate_confirmed_scores(self, user_guess, contained_list):
        guess_freq = generate_char_frequency(user_guess)
        score_list = contained_list[:]
        for i, char in enumerate(user_guess):
            if char == self.target_word[i]:
                score_list[i] = 2
                if guess_freq[char] <= 1:
                    for i in range(len(user_guess)):
                        if user_guess[i] == char and score_list[i] != 2:
                            score_list[i] = 0
                guess_freq[char] -= 1
        return score_list
    
    def generate_score(self, user_guess):
        score_list = self.generate_confirmed_scores(user_guess, self.generate_contained_scores(user_guess))
        return score_list
    def generate_footnote(self, score_list):
        emoji_list = list()
        for score in score_list:
            emoji_list.append(GUI.Footnote.from_score(score))
        return emoji_list

    def generate_attempt(self, user_guess):
        score_list = self.generate_score(user_guess)
        attempt = (self.generate_footnote(score_list), score_list)
        self.attempts[user_guess] = attempt

    def get_score(self, user_guess):
        if user_guess not in self.attempts:
            return 0
        total_score = 0
        for val in self.attempts[user_guess][1]:
            total_score += val
        return total_score
    
    def print_attempts(self):
        clear_console()
        output = list()
        for key, score_tuple in self.attempts.items():
            output.append(GUI.ATTEMPT_FORMAT.format(attempt=key.upper(),footnote=''.join(map(str, score_tuple[0 if CONFIG.display_symbols else 1])), score=(self.get_score(key) / 2)))
        
        for footnote in output:
            print(footnote)
    
    def check_win_con(self, user_guess):
        return self.get_score(user_guess) >= 10

def check_attempt(game, user_guess):
    passed = False
    if user_guess in game.attempts:
        passed = GUI.send_error("You have already tried this word. Try again.")
    elif len(user_guess) != 5:
        passed = GUI.send_error("Your guess must be 5 characters in length. Try again.")
    elif not user_guess.isalpha():
        passed = GUI.send_error("Please only use alphabetical characters. Try again.")
    elif user_guess not in valid_words:
        passed = GUI.send_error("Invalid word. Try again.")
    else:
        passed = True
        game.generate_attempt(user_guess)
    game.print_attempts()
    return passed
        
# Gets the word from the target list.
def get_wordle_word():
    if CONFIG.seed_from_date:
        random.seed(a=DATE_TODAY,version=2)
    return random.choice(target_words)

"""Sends the user a prompt to recieve a momento of their game.
"""
def prompt_footnote(game):
    input("Press ENTER for momento.")
    print("\033c", end='')
    print(GUI.Footnote.generate_footnote(game))

won_the_game = False
def play(game):
    while len(game.attempts) < MAX_ATTEMPTS:
        user_guess = input(GUI.WORD_PROMPT.format(attempts_left=(MAX_ATTEMPTS - len(game.attempts))))
        if check_attempt(game, user_guess):
            global won_the_game; won_the_game = game.check_win_con(user_guess)
            game.print_attempts()

            if won_the_game:
                print("You won!")
                prompt_footnote(game)
                return
    print("You ran out of attempts :(")
    print(f"The correct word was {game.target_word}.")
    prompt_footnote(game)

def init():
    target_word = get_wordle_word()
    game = Game(target_word)
    play(game)


init()
input("")
print("\033c", end='')
