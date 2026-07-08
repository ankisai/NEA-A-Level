def run():
    import pygame
    import sys
    from .game import Game

    # initialise pygame modules & create game window
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((1000, 700))

    # load & resize all images
    introPlayerImg = pygame.image.load('assets/Tiles/Characters/tile_0002.png').convert_alpha()
    introAIImg = pygame.image.load('assets/Tiles/Characters/tile_0006.png').convert_alpha()
    introPlayerImg = pygame.transform.scale(introPlayerImg, (80, 80))
    introAIImg = pygame.transform.scale(introAIImg, (80, 80))
    jewelIcon = pygame.image.load('assets/Tiles/tile_0067.png').convert_alpha()
    jewelIcon = pygame.transform.scale(jewelIcon, (24, 24))

    # Backgrounds
    gameBackground = pygame.image.load('assets/Tiles/Backgrounds/tile_0014.png').convert()
    gameBackground = pygame.transform.scale(gameBackground, (1000, 700))
    nameBackground = pygame.image.load('assets/Tiles/Backgrounds/tile_0005.png').convert()
    nameBackground = pygame.transform.scale(nameBackground, (1000, 700))

    # Fonts used for UI text and score display
    font = pygame.font.SysFont('comicsansms', 36)
    smallFont = pygame.font.SysFont('comicsansms', 28)

    # Player enters name before game begins
    # Screen dispays both player & AI characters
    def askPlayerName(screen):
        name = ''
        clock = pygame.time.Clock()
        bgColour = (210, 235, 210)
        inputBox = pygame.Rect(300, 420, 400, 55)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name.strip():
                        return name
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        if len(name) < 12:
                            name = name + event.unicode

            screen.fill(bgColour)

            title = font.render('Enter your name', True, (20, 60, 20))
            screen.blit(title, title.get_rect(center=(500, 150)))

            playerX = 260
            playerY = 260
            screen.blit(introPlayerImg, (playerX, playerY))

            playerLabel = smallFont.render('You', True, (20, 60, 20))
            screen.blit(playerLabel, playerLabel.get_rect(center=(playerX + 40, playerY + 95)))

            inputBox = pygame.Rect(playerX - 57, playerY + 125, 200, 45)
            drawRoundedRect(
                screen,
                inputBox,
                (255, 255, 255),
                radius=12,
                border=3,
                borderColour=(60, 100, 60)
            )

            txtSurface = smallFont.render(name, True, (0, 80, 0))
            screen.blit(txtSurface, (inputBox.x + 10, inputBox.y + 8))

            aiX = 660
            aiY = 260
            screen.blit(introAIImg, (aiX, aiY))

            aiLabel = smallFont.render('AI', True, (20, 60, 20))
            screen.blit(aiLabel, aiLabel.get_rect(center=(aiX + 40, aiY + 115)))

            hint = smallFont.render('Press ENTER to start', True, (40, 90, 40))
            screen.blit(hint, hint.get_rect(center=(500, 520)))

            pygame.display.flip()
            clock.tick(60)

    # used to draw round UI box 
    def drawRoundedRect(surface, rect, colour, radius=12, border=0, borderColour=(0,0,0)):
        pygame.draw.rect(surface, colour, rect, border_radius=radius)
        if border > 0:
            pygame.draw.rect(surface, borderColour, rect, border, border_radius=radius)

    # 3 sec countdown before level starts
    def countdown(screen):
        for i in range(3, 0, -1):
            screen.blit(gameBackground, (0,0))
            text = font.render(str(i), True, (255, 0, 0))
            rect = text.get_rect(center=(500, 350))
            screen.blit(text, rect)
            pygame.display.flip()
            pygame.time.delay(1000)

    # displays game stats & winner of the level
    def winnerPopup(screen, playerName, actualWinner, level, game):
        while True:
            for event in pygame.event.get(): # check for window events
                if event.type == pygame.QUIT: # window closed safely
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN: # handles keyboard input
                    if event.key == pygame.K_n and level < 2:
                        return 'next'
                    if event.key == pygame.K_r:
                        return 'restart'
                    if event.key == pygame.K_m:
                        return 'menu'
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
            # draw background
            screen.blit(gameBackground, (0,0))
            # dark transparent overlay (highlight pop up box)
            overlay = pygame.Surface((1000, 700))
            overlay.set_alpha(180)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))

            lines = [] # list holding all text lines to show in popup

            if actualWinner == 'Player 1':
                winnerName = playerName
            else:
                winnerName = 'AI'

            lines.append(f'Winner of Level {level + 1}: {winnerName}')

            if level == 2: # if final level - display overall match stats
                # overall match winner
                if game.player1Score > game.player2Score:
                    overallWinner = playerName
                elif game.player2Score > game.player1Score:
                    overallWinner = 'AI'
                else:
                    overallWinner = winnerName

                # determine who collected most jewels
                if game.totalJewelsP1 > game.totalJewelsP2:
                    jewelWinner = playerName
                elif game.totalJewelsP2 > game.totalJewelsP1:
                    jewelWinner = 'AI'
                else:
                    jewelWinner = 'Tie'

                # find fastest level completed
                fastestTime = min(game.levelTimes)
                fastestLevel = game.levelTimes.index(fastestTime) + 1
                # stats to pop up text using f-strings
                lines += [
                    '',
                    f'Overall Winner (Best of 3): {overallWinner}',
                    f'Most Jewels Collected: {jewelWinner}',
                    '',
                    'Total Jewels:',
                    f'{playerName}: {game.totalJewelsP1}',
                    f'AI: {game.totalJewelsP2}',
                    '',
                    f'Fastest Level: Level {fastestLevel}',
                    f'Time: {fastestTime} seconds'
                ]

            if level < 2: # option to next level only shown in last level
                lines += ['', 'N = Next Level']

            lines += ['R = Restart Level', 'M = Main Menu', 'Q = Quit']

            # calculate popup box size dynamically (based on no. of text lines)
            lineHeight = 36
            boxPadding = 30
            boxHeight = lineHeight * len(lines) + boxPadding * 2
            boxTop = (700 - boxHeight) // 2

            drawRoundedRect(
                screen,
                (180, boxTop, 640, boxHeight),
                (245, 255, 245),
                radius=20,
                border=3,
                borderColour=(60, 100, 60)
            )

            y = boxTop + boxPadding
            for text in lines:
                if text == '':
                    y += lineHeight // 2
                    continue
                if text.startswith('Winner of'):
                    renderFont = font
                else:
                    renderFont = smallFont

                if text.startswith('Winner of'):
                    colour = (0, 100, 0)
                else:
                    colour = (0, 80, 0)

                txt = renderFont.render(text, True, colour)
                rect = txt.get_rect(center=(500, y))
                screen.blit(txt, rect)

                if level == 2:
                    if text.startswith(playerName + ':') or text.startswith('AI:'):
                        screen.blit(jewelIcon, (rect.right + 10, rect.centery - 12))

                y += lineHeight

            pygame.display.flip()
            clock.tick(60)

    playerName = askPlayerName(screen)
    screen.fill((0,0,0))
    pygame.display.flip()
    pygame.time.delay(100)

    game = Game()
    game.reset()
    countdown(screen)
    game.startTime = pygame.time.get_ticks()

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            

        keys = pygame.key.get_pressed()

        if not game.gameOver and game.safeFrames <= 0:
            game.player1.move(keys)
            game.player2.move(game.platforms, game.spikes)
            game.player1.gravityEffect(0.5)
            game.player2.gravityEffect(0.5)
            game.scrollingGame()

            if game.safeFrames <= 0 and game.player1.rect.top > 700:
                game.gameOver = True
                game.winner = 'Player 2'
                game.endTime = pygame.time.get_ticks()

            elif game.safeFrames <= 0 and game.player2.rect.top > 700:
                game.gameOver = True
                game.winner = 'Player 1'
                game.endTime = pygame.time.get_ticks()
        game.player1.checkCollision(game.platforms)
        game.player2.checkCollision(game.platforms)
        game.checkFinish()
        if not game.gameOver:
            game.checkJewels()
            game.checkSpikes()
            game.checkFireballs()
        if game.safeFrames > 0:
            game.safeFrames -= 1
        if game.fireballHitCooldown > 0:
            game.fireballHitCooldown -= 1
        screen.blit(gameBackground, (0,0))

        for p in game.platforms:
            p.update()
            p.draw(screen)

        for s in game.spikes:
            s.draw(screen)

        for j in game.jewels:
            j.draw(screen)

        for f in game.fireballs:
            f.update()
            f.draw(screen)
        currentTime = pygame.time.get_ticks()
        for dmg in game.damageTexts[:]:
            if currentTime - dmg['time'] > 1000:
                game.damageTexts.remove(dmg)
                continue
            textSurface = smallFont.render(dmg['text'], True, (255, 0, 0))
            screen.blit(textSurface, (dmg['x'], dmg['y'] - 30))

        screen.blit(
            game.startImage,
            (game.startPlatform.rect.centerx - 20, game.startPlatform.rect.top - 45)
        )

        game.player1.draw(screen)
        game.player2.draw(screen)

        if not game.gameOver:
            elapsedTime = (pygame.time.get_ticks() - game.startTime) // 1000
        else:
            elapsedTime = (game.endTime - game.startTime) // 1000

        timerText = font.render('Time: ' + str(elapsedTime) + 's', True, (0,0,0))
        levelText = font.render('Level: ' + str(game.level + 1), True, (0,0,0))

        screen.blit(levelText, (20, 50))
        screen.blit(timerText, (20, 20))

        scoreText = smallFont.render(
            playerName + ': ' + str(game.player1Score) +
            '   AI: ' + str(game.player2Score),
            True,
            (0,0,0)
        )
        screen.blit(scoreText, (20, 80))
        dashHeight = 15
        gap = 10
        currentY = 10
        colourFlag = True

        while currentY < 700:
            if colourFlag:
                colour = (0, 0, 0)
            else:
                colour = (255, 255, 255)

            pygame.draw.rect(
                screen,
                colour,
                (game.finishLineWorldX - 2, currentY, 4, dashHeight)
            )

            currentY += dashHeight + gap
            colourFlag = not colourFlag
        flagWidth = game.finishImage.get_width()
        flagHeight = game.finishImage.get_height()
        flagX = game.finishLineWorldX - flagWidth // 2
        flagY = 10
        screen.blit(game.finishImage, (flagX, flagY))
        pygame.display.flip()
        clock.tick(60)

        if game.gameOver:
            choice = winnerPopup(screen, playerName, game.winner, game.level, game)

            if choice == 'next' and game.level < 2:
                if game.winner == 'Player 1':
                    game.player1Score += 1
                elif game.winner == 'Player 2':
                    game.player2Score += 1

                levelTime = (game.endTime - game.startTime) // 1000
                game.levelTimes.append(levelTime)


                game.nextLevel()
                countdown(screen)
                game.startTime = pygame.time.get_ticks()

            elif choice == 'restart':
                game.reset()
                countdown(screen)
                game.startTime = pygame.time.get_ticks()

            elif choice == 'menu':
                game.reset(fullReset=True)
                screen.fill((0,0,0))
                pygame.display.flip()
                return

                
