# py-wordle
 A python recreation of the New York Times game "Wordle".<br>
 <sub> 
    Project (PRJ) Assessment - ICT40120 - Certificate IV in Information Technology (Games and Intelligent Systems).
 </sub>
 
## How to play
 As the console will prompt, input a 5 letter word. You can find a list of valid words here: [word_bank/all_words.txt](https://github.com/saturn-volv/py-wordle/blob/main/word_bank/all_words.txt).

 You cannot enter any words greater or less than 5 characters in length nor can they contain any characters that are not valid english characters. You can also not reuse any previous attempts. 
 
 Inputting any of these will not penalise you or use an attempt, and the program will tell you if you do use an invalid entry.
 
 The program will spit out if the word you chose has letters is either: 
 - In the correct placement for the final answer - "🟩"
 - Is contained in the final answer  - "🟨"
 - Or isn't in the final answer at all  - "⬛"

 You will have 6 attempts to guess the word. If you are unsuccessful you will be prompted that you are out of attempts, and will have to restart the game. 

 Once the game has ended, you will be prompted for if you want to recieve a "momento". This will give you a little text object you can share with others, containing a little info-graphic of your attempts at guessing the final answer.