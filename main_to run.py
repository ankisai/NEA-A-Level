import pygame
import sys

pygame.init()

# clock to control the frame rate
clock = pygame.time.Clock() 

# all the fonts for the menu UI
font = pygame.font.SysFont('arial', 60, bold=True)
smallFont = pygame.font.SysFont('arial', 28)
tinyFont = pygame.font.SysFont('arial', 22)


def drawGradient(screen):
    for y in range(600):
        colour = (
            180 - y // 8,
            230 - y // 6,
            180 - y // 10
        )
        pygame.draw.line(screen, colour, (0, y), (800, y))


def drawButton(screen, rect, text, baseColour, hoverColour):
    mousePos = pygame.mouse.get_pos()

    # change colour when mouse hovers
    if rect.collidepoint(mousePos):
        colour = hoverColour
    else:
        colour = baseColour
    
    # shadow effect below the buttons
    shadowRect = rect.copy()
    shadowRect.y += 5

    pygame.draw.rect(screen, (60, 60, 60), shadowRect, border_radius=15)
    pygame.draw.rect(screen, colour, rect, border_radius=15)
    pygame.draw.rect(screen, (40, 80, 40), rect, 3, border_radius=15)

    textSurface = smallFont.render(text, True, (255, 255, 255))
    screen.blit(textSurface, textSurface.get_rect(center=rect.center))


def showInstructions(screen):
    # variables for scrolling mechanism
    scrollOffset = 0
    dragging = False
    lineHeight = 28

    singleText = [
        'Take control of the BLUE sprite using the Arrow Keys!',
        'Enter your name and prepare for the challenge.',
        'Battle through 3 levels — each tougher than the last!',
        'Level 2 increases the danger with extra spikes.',
        'Level 3 unleashes spikes AND deadly fireballs!',
        'Avoid spikes at all costs.',
        'In Level 3, fireballs steal one of your jewels!',
        'Collect as many jewels as you can.',
        'Win 2 out of 3 rounds to claim victory.',
        'After all 3 levels, compare total jewels collected!'
    ]

    dualText = [
        'Play with a friend!',
        'BLUE player uses Arrow Keys.',
        'YELLOW player uses WASD keys.',
        'Race through 3 dangerous levels.',
        'Level 2 adds more spikes.',
        'Level 3 introduces spikes AND fireballs!',
        'Hit a fireball? You lose a jewel!',
        'Collect jewels while racing.',
        'First to finish wins the round.',
        'Win 2 out of 3 rounds to become champion!'
    ]

    popupWidth = 650
    popupHeight = 500
    popupX = (800 - popupWidth) // 2
    popupY = (600 - popupHeight) // 2

    popupRect = pygame.Rect(popupX, popupY, popupWidth, popupHeight)
    contentArea = pygame.Rect(popupX + 30, popupY + 80, popupWidth - 70, 330)

    scrollbarTrack = pygame.Rect(
        contentArea.right + 5,
        contentArea.y,
        10,
        contentArea.height
    )

    closeButton = pygame.Rect(
        popupX + popupWidth // 2 - 60,
        popupY + popupHeight - 60,
        120,
        40
    )

    # calculates the height of all content to set scroll limit
    totalLines = 4 + len(singleText) + len(dualText)
    contentHeight = totalLines * lineHeight + 100
    maxScroll = max(0, contentHeight - contentArea.height)

    while True:
        drawGradient(screen)

        # dims background behind pop-up
        dimSurface = pygame.Surface((800, 600))
        dimSurface.set_alpha(150)
        dimSurface.fill((0, 0, 0))
        screen.blit(dimSurface, (0, 0))

        pygame.draw.rect(screen, (250, 255, 250), popupRect, border_radius=18)
        pygame.draw.rect(screen, (30, 80, 30), popupRect, 3, border_radius=18)

        title = font.render('Instructions', True, (20, 70, 20))
        screen.blit(title, title.get_rect(center=(400, popupY + 40)))

        # calculates position & size of scrollbar thumb
        if contentHeight > contentArea.height:
            thumbHeight = max(40, contentArea.height * contentArea.height // contentHeight)
            thumbY = scrollbarTrack.y + (scrollOffset / maxScroll) * (contentArea.height - thumbHeight)
        else:
            thumbHeight = contentArea.height
            thumbY = scrollbarTrack.y

        scrollbarThumb = pygame.Rect(
            scrollbarTrack.x,
            thumbY,
            scrollbarTrack.width,
            thumbHeight
        )

        screen.set_clip(contentArea) #restricts draw area to content box

        yPos = contentArea.y + 10 - scrollOffset

        # draw single-player section
        singleTitle = smallFont.render('Single Player Mode', True, (0, 100, 0))
        screen.blit(singleTitle, (contentArea.x, yPos))
        yPos += 35
        for line in singleText:
            textSurface = tinyFont.render(line, True, (0, 0, 0))
            screen.blit(textSurface, (contentArea.x + 15, yPos))
            yPos += lineHeight
        yPos += 25

        # draw dual-player section
        dualTitle = smallFont.render('Dual Player Mode', True, (0, 100, 0))
        screen.blit(dualTitle, (contentArea.x, yPos))
        yPos += 35
        for line in dualText:
            textSurface = tinyFont.render(line, True, (0, 0, 0))
            screen.blit(textSurface, (contentArea.x + 15, yPos))
            yPos += lineHeight

        screen.set_clip(None)

        # will draw scrollbar if content exceeds visible area (met)
        if contentHeight > contentArea.height:
            pygame.draw.rect(screen, (210, 210, 210), scrollbarTrack, border_radius=5)
            pygame.draw.rect(screen, (160, 160, 160), scrollbarThumb, border_radius=5)

        drawButton(screen, closeButton, 'Close', (170, 80, 80), (200, 100, 100))

        pygame.display.flip()
        clock.tick(60)

        # handles all events inside popup
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if closeButton.collidepoint(event.pos):
                    return
                if scrollbarThumb.collidepoint(event.pos):
                    dragging = True

            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False

            # updates scroll position when scrollbar is dragged
            if event.type == pygame.MOUSEMOTION and dragging:
                mouseY = event.pos[1]
                relativeY = mouseY - scrollbarTrack.y
                relativeY = max(0, min(relativeY, contentArea.height - thumbHeight))
                scrollOffset = (relativeY / (contentArea.height - thumbHeight)) * maxScroll


def chooseMode(screen): # displays main menu & player choice
    singleButton = pygame.Rect(250, 240, 300, 65)
    dualButton = pygame.Rect(250, 320, 300, 65)
    instructionButton = pygame.Rect(250, 400, 300, 65)
    quitButton = pygame.Rect(250, 480, 300, 65)

    while True:
        drawGradient(screen)

        # menu titles & buttons are drawn
        title = font.render('PLATFORMER GAME', True, (20, 70, 20))
        screen.blit(title, title.get_rect(center=(400, 150)))
        drawButton(screen, singleButton, 'Single Player', (70, 160, 90), (90, 190, 110))
        drawButton(screen, dualButton, 'Dual Player', (70, 160, 90), (90, 190, 110))
        drawButton(screen, instructionButton, 'Instructions', (90, 140, 200), (110, 170, 230))
        drawButton(screen, quitButton, 'Quit', (170, 80, 80), (200, 100, 100))

        pygame.display.flip()

        # all menu inputs are handled
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if singleButton.collidepoint(event.pos):
                    return 'single'
                if dualButton.collidepoint(event.pos):
                    return 'dual'
                if instructionButton.collidepoint(event.pos):
                    showInstructions(screen)
                if quitButton.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

# launches chose game mode
def main():
    while True:
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Game Mode Selection')
        mode = chooseMode(screen)
        if mode == 'single':
            from single_player import main as singleMain
            singleMain.run()

        elif mode == 'dual':
            from dual_player import main as dualMain
            dualMain.run()

# entry point for the program
if __name__ == '__main__':
    main()


