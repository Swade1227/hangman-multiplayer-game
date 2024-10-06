# Competitive Multiplayer Hangman Game

This is a simple competitive multiplayer hangman game implemented using Python and sockets.

**How to play:**
1. **Start the server:** Run the `server.py` script to initiate the game server.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals to join the game.
3. **Player input:** "exit" will close the connection, and as of now anything other input will be broadcasted to the other player

_Not Implemented Yet:_

**Play the game:** 
1. clients connect to server and get intro text from server
2. clients always have an input line, and to start both plays must input "ready" to ready up and start the game
3. once game starts players have input line and specified commands like "guess" (folowed by a letter for their guess), "check" (displays both players hangmen states), and "quit" (exits game without issue).
4. The server would handle each clients gamestates but must be linked temporally so that the players have to guess a letter in turns. 5. Players take turns guessing letters in rounds. The first player to guess the word or outlast the opponent (without completing their hangman) wins!

**Technologies used:**
* Python
* Sockets
* Threading

**Additional resources:**
* [Python documentation](https://docs.python.org/3/)
* [Python sockets tutorial](https://realpython.com/python-sockets/)
