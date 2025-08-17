# AgarMMO

A multiplayer game inspired by Agar.io, built with Python, Pygame, and sockets.

## Overview

This project is a client-server based multiplayer game where players control blobs and try to eat smaller blobs to grow larger, while avoiding being eaten by larger players.

### Core Technologies

* **Client**: `pygame-ce` for rendering and user input.
* **Server**: Python's built-in `socket` and `threading` modules for handling multiple clients.
* **Configuration**: YAML files for easy customization of game parameters.

## How to Run

1. **Start the server**: `uv run server/main.py`
2. **Start the client**: `uv run client/main.py`
