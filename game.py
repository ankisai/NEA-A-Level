import random
import pygame
from .platforms import Platform
from .player import PlayerArrow, PlayerAI
from .obstacle import Spike
from .jewel import Jewel
from .fireball import Fireball


class Game():
    screenWidth = 1000
    screenHeight = 700

    # zones for platform generation
    topZone = (80, 200)
    middleZone = (300, 400)
    bottomZone = (400, 520)

    minPlatformGapX = 220
    maxPlatformGapX = 380

    def __init__(self):
        self.player1 = PlayerArrow(100, self.screenHeight // 2)
        self.player2 = PlayerAI(150, self.screenHeight // 2)
        # list storing all objects/elements in game
        self.platforms = []
        self.spikes = []
        self.jewels = []
        self.levelTimes = []
        self.fireballs = []
        self.damageTexts = []

        self.distance = 0
        self.totalDistance = 0
        self.startX = 100
        self.finishX = 2500
        self.finishLineWorldX = self.finishX
        self.gameOver = False
        self.winner = None
        self.startTime = pygame.time.get_ticks()
        self.endTime = self.startTime
        self.level = 0
        # score tracking (times & jewel counts)
        self.player1Score = 0
        self.player2Score = 0
        self.totalJewelsP1 = 0
        self.totalJewelsP2 = 0
        self.safeFrames = 0
        # adjusts different difficulty settings for levels
        self.levelList = [
            {'minGap': 180, 'maxGap': 260, 'aiSpeed': 5},
            {'minGap': 200, 'maxGap': 280, 'aiSpeed': 5},
            {'minGap': 202, 'maxGap': 283, 'aiSpeed': 5}
        ]

        self.finishImage = pygame.transform.scale(
            pygame.image.load('assets/Tiles/tile_0112.png').convert_alpha(),
            (70, 70)
        )
        self.startImage = pygame.transform.scale(
            pygame.image.load('assets/Tiles/tile_0111.png').convert_alpha(),
            (40, 40)
        )

        self.loadLevel(self.level)
        self.createInitialPlatforms()
        self.placeJewels()
        self.placeSpikes()
    
    def createInitialPlatforms(self):
        self.platforms = [] # clear all existing platforms
        # start platform
        self.startPlatform = Platform(50, self.screenHeight // 2, 150, 20)
        self.platforms.append(self.startPlatform)

        # first top & bottom path platform
        topStart = Platform(200, 200, 150, 20)
        bottomStart = Platform(200, 500, 150, 20)
        self.platforms.extend([topStart, bottomStart]) # add both starting platforms

        topPath = self.generatePathRecursive(topStart, self.topZone, depth=8)
        bottomPath = self.generatePathRecursive(bottomStart, self.bottomZone, depth=10)
        self.platforms.extend(topPath)
        self.platforms.extend(bottomPath)

        self.generateBridges(topPath, bottomPath)
        self.fillBottomPath(bottomPath)
        self.addBaseSafetyPlatforms()

    def fillBottomPath(self, bottomPath):
        if bottomPath:
            last = bottomPath[-1]
        else:
            last = None

        if last:
            lastY = last.rect.y

            while last.rect.x < self.finishX - 200:

                newX = last.rect.x + random.randint(self.minPlatformGapX, self.maxPlatformGapX)

                # smooth stepping instead of random vertical jumps
                step = random.randint(-25, 25)
                newY = lastY + step

                # clamp to bottom zone
                if newY < self.bottomZone[0]:
                    newY = self.bottomZone[0]
                if newY > self.bottomZone[1]:
                    newY = self.bottomZone[1]

                plat = self.safePlatform(newX, newY)

                if plat:
                    self.platforms.append(plat)
                    last = plat
                    lastY = newY
                else:
                    break
    
    # middle platform generation to connect bottom & top path
    def generateBridges(self, topPath, bottomPath):
        for t in topPath:
            closest = None
            bestdx = 9999
            for b in bottomPath:
                dx = abs(b.rect.centerx - t.rect.centerx)
                if dx < bestdx:
                    bestdx = dx
                    closest = b
            if closest and bestdx < 240:
                verticalGap = abs(t.rect.y - closest.rect.y)
                if verticalGap < 140:
                    continue
                midX = (t.rect.centerx + closest.rect.centerx) // 2
                midY = random.randint(self.middleZone[0], self.middleZone[1])
                bridge = self.safePlatform(midX, midY)

                if bridge:
                    self.platforms.append(bridge)

    # same logic as in dual_player version
    def generatePathRecursive(self, startPlatform, zone, depth):
        if depth == 0: # base case
            return []

        state = [[float(startPlatform.rect.y)], [0.0]]
        transitionMatrix = [[1.0, 1.0], [0.0, 1.0]]

        if zone == self.bottomZone:
            verticalRange = 60
            bias = random.choice([-1, 1]) * random.randint(15, 30)
        else:
            verticalRange = 40
            bias = random.choice([-1, 1]) * random.randint(10, 25)

        inputVec = [[random.randint(-verticalRange, verticalRange) + bias], [0.0]]

        result = [
            transitionMatrix[0][0]*state[0][0] +
            transitionMatrix[0][1]*state[1][0] +
            inputVec[0][0],
            transitionMatrix[1][0]*state[0][0] +
            transitionMatrix[1][1]*state[1][0] +
            inputVec[1][0]
        ]

        newY = int(max(zone[0], min(zone[1], result[0])))

        if zone == self.bottomZone:
            gap = random.randint(self.minPlatformGapX + 50, self.maxPlatformGapX + 90)
        else:
            gap = random.randint(self.minPlatformGapX, self.maxPlatformGapX)

        newX = startPlatform.rect.x + gap

        plat = self.safePlatform(newX, newY)
        if not plat:
            return []

        return [plat] + self.generatePathRecursive(plat, zone, depth - 1)

    # stops trying after several failed attempts
    def safePlatform(self, x, y, attempts=6):
        if attempts == 0:
            return None
    
        # rectangle to test platform placement
        newRect = pygame.Rect(x, y, 150, 20)

        for p in self.platforms:
            if newRect.colliderect(p.rect.inflate(40, 30)):
                return self.safePlatform(
                    x + random.randint(40, 80),
                    y + random.randint(-30, 30),
                    attempts - 1
                )
            minXGap = 190
            minYGap = 120

            if y >= self.bottomZone[0]:
                minXGap = 170
                minYGap = 230

            if abs(p.rect.x - x) < minXGap and abs(p.rect.y - y) < minYGap:
                return self.safePlatform(
                    x + random.randint(40, 80),
                    y + random.randint(-30, 30),
                    attempts - 1
                )

        if x >= self.finishLineWorldX - 150:
            return None
        for p in self.platforms:
            if abs(p.rect.x - x) < 100:
                if abs(p.rect.y - y) < 100:
                    return self.safePlatform(
                        x + random.randint(40, 80), 
                        y + random.randint(-30, 30),
                        attempts-1
                    )
        return Platform(x, y, 150, 20)
    
    def addBaseSafetyPlatforms(self):
        width = 150
        height = 20
        baseY = self.screenHeight - 28

        # periodic spacing
        spacing = 260

        # start after start platform
        x = self.startPlatform.rect.right + 200

        # find the furthest existing safety platform
        existing = [
            p for p in self.platforms
            if abs(p.rect.y - baseY) < 20
        ]

        if existing:
            last = max(existing, key=lambda p: p.rect.x)
            x = last.rect.x + spacing

        while x < self.finishLineWorldX - 200:

            newRect = pygame.Rect(x, baseY, width, height)

            # only prevent exact duplicates
            duplicate = False
            for p in self.platforms:
                if abs(p.rect.x - x) < 40 and abs(p.rect.y - baseY) < 20:
                    duplicate = True
                    break
            # prevent platforms too close above (head hit issue)
            tooCloseAbove = False
            for p in self.platforms:
                if abs(p.rect.x - x) < 120:  # horizontal overlap zone
                    if 0 < (baseY - p.rect.y) < 140:  # platform above too close
                        tooCloseAbove = True
                        break

            if not duplicate and not tooCloseAbove:
                self.platforms.append(Platform(x, baseY, width, height))

            x += spacing

    def loadLevel(self, levelIndex):
        level = self.levelList[levelIndex]
        self.minPlatformGapX = level['minGap']
        self.maxPlatformGapX = level['maxGap']
        self.player2.speedx = level['aiSpeed']

    def nextLevel(self):
        if self.level < len(self.levelList) - 1:
            self.level += 1
        self.reset()

    def reset(self, fullReset = False):
        self.distance = 0
        self.totalDistance = 0
        self.finishLineWorldX = self.finishX

        self.platforms = []
        self.spikes = []
        self.jewels = []
        self.fireballs = []
        self.damageTexts = []

        self.gameOver = False
        self.winner = None
        self.fireballHitCooldown = 0


        # Load level settings
        self.loadLevel(self.level)

        # Recreate platforms FIRST
        self.createInitialPlatforms()

        # Now safely compute spawn Y
        startY = self.startPlatform.rect.top - self.player1.size

        # Reset players AFTER platforms exist
        self.player1.rect.x = 100
        self.player2.rect.x = 150

        self.player1.reset(startY)
        self.player2.reset(startY)

        self.player1.touchGround = True
        self.player2.touchGround = True

        # Reset timers and scores
        # Only reset round state
        if fullReset:
            self.player1Score = 0
            self.player2Score = 0
            self.totalJewelsP1 = 0
            self.totalJewelsP2 = 0
            self.levelTimes = []
            self.level = 0
        self.startTime = pygame.time.get_ticks()

        # Place objects after platforms exist
        self.placeJewels()
        self.placeSpikes()
        self.placeFireballs()
        self.safeFrames = 15

    def scrollingGame(self):
        if self.player1.rect.x > self.screenWidth // 2:
            scrollAmount = self.player1.rect.x - self.screenWidth // 2
            self.player1.rect.x = self.screenWidth // 2
            self.player2.rect.x -= scrollAmount # moves platform left to simulate world moving

            for p in self.platforms:
                p.rect.x -= scrollAmount
                p.baseX -= scrollAmount
                # move spikes along with oscillation and scroll

            for s in self.spikes:
                s.rect.x -= scrollAmount
            for j in self.jewels:
                j.rect.x -= scrollAmount
            for f in self.fireballs:
                f.x -= scrollAmount
                f.updateRect()


            self.finishLineWorldX -= scrollAmount
            self.distance += scrollAmount
            self.totalDistance += scrollAmount

        while self.distance > 250 and not self.gameOver:
            if self.finishLineWorldX <= self.screenWidth:
                break

            lastTop = None
            lastTopMaxX = None

            for p in self.platforms:

                if p.rect.y < self.screenHeight // 2:

                    if lastTop is None:
                        lastTop = p
                        lastTopMaxX = p.rect.x
                    else:
                        if p.rect.x > lastTopMaxX:
                            lastTop = p
                            lastTopMaxX = p.rect.x
            lastBottom = None
            lastBottomMaxX = None

            for p in self.platforms:

                if p.rect.y >= self.screenHeight // 2:

                    if lastBottom is None:
                        lastBottom = p
                        lastBottomMaxX = p.rect.x
                    else:
                        if p.rect.x > lastBottomMaxX:
                            lastBottom = p
                            lastBottomMaxX = p.rect.x


            if lastTop:
                newTop = self.generatePathRecursive(lastTop, self.topZone, depth=2)
                self.platforms.extend(newTop)
            if lastBottom:
                newBottom = self.generatePathRecursive(lastBottom, self.bottomZone, depth=2)
                self.platforms.extend(newBottom)

            self.distance -= 250
        self.addBaseSafetyPlatforms()

        updatedPlatforms = []
        for p in self.platforms:
            rightEdge = p.rect.x + p.rect.width

            if rightEdge > 0:
                updatedPlatforms.append(p)

        self.platforms = updatedPlatforms

        if len(self.platforms) == 0:
            return

    def checkFinish(self):
        if self.gameOver or self.safeFrames > 0:
            return

        finishX = self.finishLineWorldX

        p1Hit = self.player1.rect.right >= finishX
        p2Hit = self.player2.rect.right >= finishX

        if p1Hit and p2Hit:
            # whoever is further right wins
            if self.player1.rect.right > self.player2.rect.right:
                self.winner = 'Player 1'
            else:
                self.winner = 'Player 2'

            self.gameOver = True
            self.endTime = pygame.time.get_ticks()

        elif p1Hit:
            self.gameOver = True
            self.winner = 'Player 1'
            self.endTime = pygame.time.get_ticks()

        elif p2Hit:
            self.gameOver = True
            self.winner = 'Player 2'
            self.endTime = pygame.time.get_ticks()

    def placeJewels(self):
        self.jewels = []

        if not self.platforms:
            return

        if self.level == 0:
            numJewels = 6
        elif self.level == 1:
            numJewels = 9
        else:
            numJewels = 14

        validPlatforms = [
            p for p in self.platforms
            if p.rect.top < 450 and p != self.startPlatform  # hard vertical safety cap
        ]

        if not validPlatforms:
            return

        usedX = []

        for i in range(numJewels):
            platform = random.choice(validPlatforms)

            jewelX = platform.rect.centerx
            jewelY = platform.rect.top - 35
            spawnX = 100
            if abs(jewelX - spawnX) < 150:
                continue

            # prevent clustering
            if any(abs(jewelX - x) < 80 for x in usedX):
                continue

            self.jewels.append(Jewel(jewelX, jewelY))
            usedX.append(jewelX)

    def checkJewels(self):

        if self.gameOver:
            return

        for jewel in self.jewels[:]:
            # check if player 1 touched jewel
            if self.player1.rect.colliderect(jewel.rect):
                self.totalJewelsP1 += 1
                self.jewels.remove(jewel)
                continue

            if self.player2.rect.colliderect(jewel.rect):
                self.totalJewelsP2 += 1
                self.jewels.remove(jewel)
                continue
            if self.player1.state[1][0] > 0:  # falling velocity
                continue
    
    # chance of spawn increases as level increases
    def placeSpikes(self):
        self.spikes = []
        for p in self.platforms:
            chance = 0.06
            if self.level == 1:
                chance = 0.09 
            elif self.level == 2:
                chance = 0.11

            if random.random() < chance:
                if self.level == 1:
                    spikeX = random.randint(
                        p.rect.centerx + 20,
                        p.rect.right - 30
                    )
                else:
                    spikeX = random.randint(
                        p.rect.left + 10,
                        p.rect.right - 30
                    )

                spikeY = p.rect.top - 20
                self.spikes.append(Spike(spikeX, spikeY))
    # level ends when either player hits a spike
    def checkSpikes(self):
        for spike in self.spikes:
            if self.player1.rect.colliderect(spike.rect):
                self.gameOver = True
                self.winner = 'Player 2'
                self.endTime = pygame.time.get_ticks()
                return
            if self.player2.rect.colliderect(spike.rect):
                self.gameOver = True
                self.winner = 'Player 1'
                self.endTime = pygame.time.get_ticks()
                return
    
    def placeFireballs(self):
        self.fireballs = []

        if self.level != 2: 
            return

        for i in range(3): 
            x = random.randint(500, self.finishX - 300)
            y = random.randint(150, self.screenHeight - 200)
            self.fireballs.append(Fireball(x, y))

    # only spawns in level 3
    def checkFireballs(self):
        if self.safeFrames > 0:
            return
        if self.fireballHitCooldown > 0:
            return
        currentTime = pygame.time.get_ticks()

        for f in self.fireballs[:]: 

            if self.player1.rect.colliderect(f.rect):
                if self.totalJewelsP1 > 0:
                    self.totalJewelsP1 -= 1

                self.damageTexts.append({
                    "text": "-1",
                    "x": f.x,
                    "y": f.y,
                    "time": currentTime
                })

                self.fireballs.remove(f) 
                self.fireballHitCooldown = 20
                return

            if self.player2.rect.colliderect(f.rect):
                if self.totalJewelsP2 > 0:
                    self.totalJewelsP2 -= 1

                self.damageTexts.append({
                    "text": "-1",
                    "x": f.x,
                    "y": f.y,
                    "time": currentTime
                })

                self.fireballs.remove(f)
                self.fireballHitCooldown = 20
                return







