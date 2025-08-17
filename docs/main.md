# `main.py` - Client Entry Point

The `main.py` script is the entry point for the client-side application.

## Functionality

1.  **Initialization**:
    *   Initializes the `pygame` library.
    *   Suppresses the `pygame` welcome message for a cleaner console output.

2.  **User Input**:
    *   Prompts the user to enter their name.
    *   Validates the length of the name based on the `min_name_length` and `max_name_length` settings in `config/game.yaml`.
    *   Continues to prompt for a name until a valid one is entered.

3.  **Game Execution**:
    *   Creates an instance of the `Game` class from `game.py`.
    *   Calls the `run()` method of the `Game` object, passing the player's name to start the game.
    *   Wraps the game execution in a `try...finally` block to ensure that `pygame.quit()` is called, even if an error occurs.

## Dependencies

*   `pygame`: For graphics and window management.
*   `game.py`: Contains the main `Game` class.
*   `utils.config_loader.py`: To load game configuration settings.
