# NEA-A-Level
Single & Dual-player Platformer game (using basic ML for single-player version)
Run 'main_to run' file to play game
The players of the game will move across some randomly generated platforms arranged at 
multiple heights on a screen. Gravity will pull the players down, so they must jump and navigate 
around the platforms cautiously.  
The ultimate aim for the players is to either stay on the platforms longer than their opponent 
without falling, or if both manage to stay on, they are both racing towards a goal/finish line.  
There will be many combinations of platforms that the players can choose to follow to reach the 
same goal, some may be faster but riskier, or longer but safer.  

There will be obstacles along the way, including spikes & fireballs
Once a level is fully complete, the next generation of map will be more 
challenging, with either harder platform routes, more obstacles, more time crunch etc. This will 
prevent players from getting bored after multiple plays, thus keeping them engaged with the 
game and ensures a dynamic interface.  

For the single-player version, it now uses a single-layer neural network with linear regression for the AI component, aswell as using a reward-based system to optimise as it progresses through levels. 

FUTURE IMPROVEMENTS : Use a Q-Learning system, more obstacle options
