"""
    py-wordle
    A Python 3.1x recreation of the New York Times sensation "Wordle"

    Author: Saturn Harrison
    Company: ""
    Copyright: 2024
"""
import random
import time

# For interal use to make sure everything is working.
DEBUGGING = True

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

DATE_TODAY = time.strftime("%d/%m/%Y")

# All valid input words. Not every word you can use can be an answer.
valid_words = get_list_from_txt(VALID_WORD_PATH)
# All the words the answer for the game could possibly be.
target_words = get_list_from_txt(ANSWER_WORD_PATH)

# A front end class to handle how text may be displayed. This could be used to provide localization in the future.
class GUI:
    # Used so that i can ouput why the answer the user has inputed may not be a valid word.
    ERROR_MESSAGE = ""
    # The welcome message, better practice than using a simple `print("str")` function call.
    WELCOME_MESSAGE = f"Welcome to Wordle! The date today is {DATE_TODAY}."
    # The intro word prompt.
    WORD_PROMPT = "You have {attempts_left} attempts left.\nPlease enter a word: "
    # The format for how an attempt is printed to the console.
    ATTEMPT_FORMAT = "{0}{1}{2}{3}{4} ({score}/5)"
    # The ouput format for sharing your results of the game.
    MOMENTO_FORMAT = "Wordle {final_word} {score}/6\n\n{attempts}"

    # Simple structure to clarify the ascii tokens based on a score value of each character.
    class Footnote:
        MISSED = ("⬛", 0)
        CONTAINS = ("🟨", 1)
        CORRECT = ("🟩", 2)

        def from_score(value):
            for t in [  GUI.Footnote.MISSED,  
                        GUI.Footnote.CONTAINS,
                        GUI.Footnote.CORRECT ]:
                if t[1] == value:
                    return t[0]
            return GUI.Footnote.MISSED

class Game:
    # Will be a dictionary of tuples, with the attempted word as a key, and a tuple containing the score, and the displayed footnote.
    attempts = dict()
    # The word of the "day".
    target_word = ""

    def __init__(self, target_word):
        self.target_word = target_word
        clear_console()
        if DEBUGGING:
            print(f"[DEBUG]: A valid word has been chosen. ({self.target_word})") # Making sure an answer is actually provided.

    def generate_contained_scores(self, user_guess):
        score_list = list()
        target_freq = generate_char_frequency(self.target_word)
        for i, char in enumerate(user_guess):
            if self.target_word.find(char) > -1:
                if get_index_of_character_excluding_others(i, user_guess) <= target_freq[char]:
                    score_list.append(1)
                    continue
            score_list.append(0)
        return score_list
    
    def generate_confirmed_scores(self, user_guess, contained_list):
        guess_freq = generate_char_frequency(user_guess)
        target_freq = generate_char_frequency(self.target_word)
        score_list = contained_list[:]
        for i, char in enumerate(user_guess):
            if char == self.target_word[i]:
                score_list[i] = 2
                guess_freq[char] -= 1
                if guess_freq[char] <= 1:
                    for i in range(len(user_guess)):
                        if score_list[i] != 2:
                            score_list[i] = 0
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


# Gets the word from the target list.
def get_wordle_word():
    return random.choice(target_words)
        
def play():
    target_word = get_wordle_word()
    game = Game(target_word)

    while len(game.attempts) < MAX_ATTEMPTS:
        user_guess = input("Enter ur guess: ")
        game.generate_attempt(user_guess)
        print(game.attempts)


play()
