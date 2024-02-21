from enum import Enum
import random
import time
import re

# For interal use to make sure everything is working.
DEBUGGING = False

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
# Clears the console for a clean view.
def clear_console():
    print("\033c", end='')
    print(GUI.WELCOME_MESSAGE)
    print(GUI.ERROR_MESSAGE)
    GUI.ERROR_MESSAGE = ""

def only_letters(text):
    match = re.match("^[a-hj-m]*$", text)
    return match is not None

MAX_ATTEMPTS = 6
WORD_LENGTH = 5

VALID_WORD_PATH = 'word_bank/all_words.txt'
ANSWER_WORD_PATH = 'word_bank/target_words.txt'

# All valid input words. Not every word you can use can be an answer.
valid_words = get_list_from_txt(VALID_WORD_PATH)
# All the words the answer for the game could possibly be.
target_words = get_list_from_txt(ANSWER_WORD_PATH)

# A front end class to handle how text may be displayed. This could be used to provide localization in the future.
class GUI:
    # Used so that i can ouput why the answer the user has inputed may not be a valid word.
    ERROR_MESSAGE = ""
    # The welcome message, better practice than using a simple `print("str")` function call.
    WELCOME_MESSAGE = f"Welcome to Wordle! The date today is {time.strftime("%d/%m/%Y")}."
    # The intro word prompt.
    WORD_PROMPT = "You have {attempts_left} attempts left.\nPlease enter a word: "
    # The format for how an attempt is printed to the console.
    ATTEMPT_FORMAT = "{attempt}\n{0}{1}{2}{3}{4} ({score}/5)"

# Handles the back-end gameplay, such as checking characters are correct.
class Game:
    # A list of all the attempts, to be printed after each attempt.
    attempts = []
    attempted_words = []
    # Generates the answer word in the main function, so there is still backend.
    answer_word = ""

    # Starts a new game instance
    def __init__(self, answer):
        self.answer_word = answer
        clear_console()
        if DEBUGGING: 
            print(f"[DEBUG]: A valid word has been chosen. ({self.answer_word})") # Making sure an answer is actually provided.

    # Simple enum structure to clarify the ascii tokens.
    class LetterCheck(Enum):
        MISSED = "⬛"  # Letter is not in the word.
        CONTAINS = "🟨"  # The letter is in the word but the wrong place.
        CORRECT = "🟩"  # The letter is in the word AND in the correct place.
    
    # Outputs the Enum based on the score of the letter at a chosen point.
    def check_char(self, char, input_word):
        index_of_input = input_word.find(char)
        if index_of_input == -1:
            return self.LetterCheck.MISSED
        index_of_answer = self.answer_word.find(char)
        if index_of_input == index_of_answer:
            return self.LetterCheck.CORRECT
        elif self.answer_word.find(char) >= 0:
            for i in range(5):
                if self.answer_word[i] == input_word[i] == char:
                    return self.LetterCheck.MISSED
            return self.LetterCheck.CONTAINS
        else:
            return self.LetterCheck.MISSED

    # Adds an attempt to the game list. Used for ouputting to console.
    def add_attempt(self, chosen_word):
        chars = []
        answer_dict = generate_char_frequency(self.answer_word)
        attempt_dict = {}
        for i, char in enumerate(list(chosen_word)):
            attempt_dict[char] = attempt_dict.setdefault(char, 0) + 1
            if DEBUGGING: # To make sure the ordering is correct.
                print(char)
            if attempt_dict.get(char) > answer_dict.get(char, 0):
                chars.append(self.LetterCheck.MISSED.value)
                continue
            else:
                o_char = self.check_char(char, chosen_word)
                chars.append(o_char.value)
        
        for i, char in enumerate(chars):
            # Overrides to make sure that every correct letter is, infact, correct
            if chosen_word[i] == self.answer_word[i]:
                chars[i] = self.LetterCheck.CORRECT.value
        correct_chars = 0
        for char in chars:
            if char == "🟩": 
                correct_chars += 2
            if char == "🟨":
                correct_chars += 1
    
        word_score = correct_chars / 2
        if word_score.is_integer():
            word_score = int(word_score)
        attempt = GUI.ATTEMPT_FORMAT.format(*chars, attempt=chosen_word.upper(), score=word_score)
        self.attempted_words.append(chosen_word)
        self.attempts.append(attempt)
        return word_score >= 5

# Prints out the 
def print_attempts(game):
    clear_console()
    for attempt in game.attempts:
        print(attempt)

# Gets the word from the target list.
def get_wordle_word():
    return random.choice(target_words)

# Checks to make sure the word is of correct length, a valid word, and hasn't been used before.
def check_word(attempt, game):
    if not attempt.isalpha():
        GUI.ERROR_MESSAGE = "Please only use alphabetical characters. Try Again."
        return False
    if len(attempt) < WORD_LENGTH:
        GUI.ERROR_MESSAGE = "Not enough characters. Try Again."
        return False
    if len(attempt) > WORD_LENGTH:
        GUI.ERROR_MESSAGE = "Too many characters. Try Again."
        return False
    if attempt not in valid_words:
        GUI.ERROR_MESSAGE = "Invalid word. Try Again."
        return False
    if attempt in game.attempted_words:
        GUI.ERROR_MESSAGE = "You have tried this word before. Try Again."
        return False
    return True

# Prompts the user to enter a word, while also providing if the answer given is valid or not.
def attempt_word(game):
    chosen_word = input(f"{GUI.WORD_PROMPT.format(attempts_left = MAX_ATTEMPTS - len(game.attempts))}\n> ").lower()
    if not check_word(chosen_word, game):
        return False
    return game.add_attempt(chosen_word)

def main():
    # Simple boolean to reveal outside scope if the game was won or not.
    won_the_game = False
    # The winning word, selected from the .txt file
    word_of_the_day = get_wordle_word()
    game = Game(word_of_the_day)

    # Game loop.
    while len(game.attempts) < MAX_ATTEMPTS:
        if attempt_word(game):
            won_the_game = True
            print_attempts(game)
            break
        print_attempts(game)
    if won_the_game:
        print(f"You won! You got it in {len(game.attempts)} tries!")
    else:
        print("You ran out of attempts :(")
        print(f"The word was {word_of_the_day}.")

if __name__ == "__main__":
    main()
    # Just stops the game from ending *right* away.
    input("Press any ENTER to contine...")
    print("\033c", end='')

    # Was gonna have the results be copyable, 
    # but you cannot copy to clipboard without installing new libraries...

