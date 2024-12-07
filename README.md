# Competitive Multiplayer Hangman Game

This is a simple competitive multiplayer hangman game implemented using Python and sockets.

**How to play:**
1. **Start the server:** Run the `server.py` script to initiate the game server (server -p PORT)
   ex: python server.py -p 12345
2. **Connect clients:** Run the `client.py` script on two different machines or terminals to join the game (client -i SERVER_IP/DNS -p PORT)
   ex: python client.py -i 127.0.0.1 -p 12345
3. **Game Objective:** The goal of the game is to guess the secret word letter by letter. 
4. **Player input:** any single character input will count as a guess and "exit" will close the connection.
5. **Win condition:** a player wins the game by correctly guessing each letter of word. Upon winning the game is reset and a new word is selected.

**Technologies used:**
* Python
* Sockets
* Threading

**Additional resources:**
* [Python documentation](https://docs.python.org/3/)
* [Python sockets tutorial](https://realpython.com/python-sockets/)

**Current bugs**
- Turn mismanagment when a player starts solo game and other client joins after.
- Reads repeated input as new input

**Security/Risk Evaluation**
- Lack of Input Validation: As of now there is not extensive input validation on the client's guessing inputs
  - Fix: Check the input and exclude anything other than A-Z and a-z.

- No Encryption: As of now there is no encryption on the communication between the server and clients
  - Fix: Implement TLS to encrypt data sent between the server and the clients

- No Logging Security: As of now there is not much consideration for security with the log files. If someone were to somehow access to them it would reveal the client and servers IP Addresses.
   - Fix: Remove the IP Address logging in both the serer and client logging system.

# Game Message Protocol Specification

## Overview

This document specifies the message types exchanged between the server and clients in the word guessing game, including their structure and expected responses.

## Message Types

### Join
- **Purpose**: Automatically sent when a client runs the client program to join the game. Assigns unique ID to each client.
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
