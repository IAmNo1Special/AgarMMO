if __name__ == "__main__":
    import contextlib
    import pygame
    from client.game import Game
    from shared.config_loader import game_cfg

    # Initialize pygame and suppress welcome message
    with contextlib.redirect_stdout(None):
        pygame.init()

    # Load validation settings from config
    min_name_len = game_cfg['validation']['min_name_length']
    max_name_len = game_cfg['validation']['max_name_length']
    
    # Get user's name with validation
    while True:
        name = input(f"Please enter your name (between {min_name_len} and {max_name_len} characters): ")
        if min_name_len <= len(name) <= max_name_len:
            break
        print(f"Error: Name must be between {min_name_len} and {max_name_len} characters")
    
    # Start the game
    try:
        game = Game()
        game.run(name)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()

