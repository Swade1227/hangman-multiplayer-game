# Competitive Multiplayer Hangman Game

This is a simple competitive multiplayer hangman game implemented using Python and sockets.

**How to play:**
1. **Start the server:** Run the `server.py` script to initiate the game server.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals to join the game.
3. **Player input:** any single character input will count as a guess, "pass" wills skip your turn, and "exit" will close the connection.

NOTE: As of now there is no win condition

**Technologies used:**
* Python
* Sockets
* Threading

**Additional resources:**
* [Python documentation](https://docs.python.org/3/)
* [Python sockets tutorial](https://realpython.com/python-sockets/)

# Game Message Protocol Specification

## Overview

This document specifies the message types exchanged between the server and clients in the word guessing game, including their structure and expected responses.

## Message Types

### Join
- **Purpose**: Automatically sent when a client runs the client program to join the game.
- **Format**: Happens automatically upon running `client.py`.
- **Expected Server Response**: 
  - `Welcome! Type 'pass' to pass your turn or 'exit' to leave.`

### Guess
- **Purpose**: Sent by a client to make a letter guess.
- **Format**: `<single_character>`
  - *Example*: A single alphabetic character (e.g., "a")
- **Expected Server Response**:
  - **Correct Guess**: 
    - `Correct! Your word: <updated_word>`
    - *Example*: `Correct! Your word: n_______n_`
  - **Incorrect Guess**: 
    - `Incorrect guess.`

### Pass
- **Purpose**: Sent by a client to skip their turn.
- **Format**: `"PASS"`
- **Expected Server Response**: 
  - *(empty response or confirmation, optional)*

### Exit
- **Purpose**: Sent by a client to exit the game.
- **Format**: `"EXIT"`
- **Expected Server Response**: 
  - `Disconnected from server.`

### Game Update
- **Purpose**: Sent by the server to provide updates regarding the game state, such as the current state of the word, or game reset if necessary.
- **Expected Response**: 
  - `<updated client word>`

### Turn Notification
- **Purpose**: Sent by the server to inform a client that it is their turn.
- **Expected Response**: 
  - `It's your turn!`
