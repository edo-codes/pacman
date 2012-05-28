# README

## Pacman

This is an implementation of the classic game "Pac-man", using Python 3.2. It uses the console library for its UI.


### Gameplay

Right now, the enemy logic hasn't been coded yet, only directly chasing the player. You control the player with the arrow keys, you eat the pellets and avoid the enemies.

### Implementation

I have attempted to abstract the 'framework' bits from the game to a certain degree so that I might add a sprite-based ui later.

It is all written in a single file, so I don't have to switch buffers in vim.

First the game objects are created, such as the player, the ghosts, the pellets etc., all inheriting from a `gameobject` base class. They contain their position, size and color, and game logic for that object.

The `steptowards()` method implements a simple pathfinding algorithm that stores a cache -- `pathfindingqueue` -- inside each object that another object routes to. This is so that multiple enemies can chase the player without repeating the calculations in a single step.

The `init()`, `gameloop()`, `keypress()` and `draw()` are all methods that are called by the 'framework'. `draw()` uses curses directly and contains the 'drawings' for the objects, which might not be very clean.

Many methods accept an objects list in a (probably misguided) attempt to make the whole thing a bit more functional (as in functional programming functional).

The framework uses the `curses` library. 
