import pygame
import random
import numpy as np

class Player():
    def __init__(self, x, y, colour=None):
        self.spawnY = y
        self.prevY = y
        self.size = 35
        self.rect = pygame.Rect(x, y, self.size, self.size)
        spritePath = 'assets/Tiles/Characters/tile_0002.png'
        self.image = pygame.image.load(spritePath).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.speedx = 5
        self.touchGround = False
        self.state = np.array([[float(y)], [0.0]])
        self.stateMatrix = np.array([[1.0, 1.0], [0.0, 1.0]])
        self.accelerationInput = np.array([[0.0], [0.0]])

    def gravityEffect(self, gravity):
        self.prevY = self.rect.y
        if not self.touchGround:
            self.accelerationInput[1][0] = gravity
        else:
            self.accelerationInput[1][0] = 0
        self.state = self.stateMatrix @ self.state + self.accelerationInput
        self.rect.y = int(self.state[0][0])

    def jump(self, jumpStrength):
        if self.touchGround:
            self.state[1][0] = jumpStrength
            self.touchGround = False

    def applyHorizontalControl(self, controlSignal):
        self.rect.x += controlSignal

    def checkCollision(self, platforms):
        self.touchGround = False
        if isinstance(self, PlayerAI) and self.lastJumpFeatures is not None:
            reward = 1.0 # + reinforcement for successful action
            target = np.array([reward])
            self.mlTrain(self.lastJumpFeatures, target)
            self.lastJumpFeatures = None

        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.prevY + self.rect.height <= p.rect.top and self.state[1][0] >= 0:
                    self.rect.bottom = p.rect.top
                    self.state[0][0] = self.rect.y
                    self.state[1][0] = 0
                    self.touchGround = True
                elif self.prevY >= p.rect.bottom:
                    self.rect.top = p.rect.bottom
                    self.state[0][0] = self.rect.y
                    self.state[1][0] = 1.5

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def reset(self, startY=None):
        if startY is None:
            startY = self.spawnY
        self.state[0][0] = startY
        self.state[1][0] = 0
        self.rect.y = startY
        self.prevY = startY
        self.touchGround = False


class PlayerArrow(Player):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load('assets/Tiles/Characters/tile_0002.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.imageAlt = pygame.image.load('assets/Tiles/Characters/tile_0003.png').convert_alpha()
        self.imageAlt = pygame.transform.scale(self.imageAlt, (self.size, self.size))
        self.currentImage = self.image
        self.legTimer = 0
        self.legInterval = 10

    def move(self, keys):
        moving = False
        if keys[pygame.K_LEFT]:
            self.applyHorizontalControl(-self.speedx)
            moving = True
        if keys[pygame.K_RIGHT]:
            self.applyHorizontalControl(self.speedx)
            moving = True
        if keys[pygame.K_UP]:
            self.jump(-13)

        if moving:
            self.legTimer += 1

            if self.legTimer >= self.legInterval:
                if self.currentImage == self.image:
                    self.currentImage = self.imageAlt
                else:
                    self.currentImage = self.image

                self.legTimer = 0
        else:
            self.currentImage = self.image
            self.legTimer = 0

    def draw(self, screen):
        screen.blit(self.currentImage, self.rect)


class PlayerAI(Player):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load('assets/Tiles/Characters/tile_0006.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.imageAlt = pygame.image.load('assets/Tiles/Characters/tile_0007.png').convert_alpha()
        self.imageAlt = pygame.transform.scale(self.imageAlt, (self.size, self.size))
        self.currentImage = self.image
        self.legTimer = 0
        self.legInterval = 10
        self.speedx = 4
        self.baseSpeed = self.speedx
        self.speedNoise = 0.3
        self.skill = 0.85
        self.reactionCoolDown = 0
        self.commitTimer = 0
        self.panicChance = 0.008
        self.targetPlatform = None
        self.mlLr = 0.0005
        self.mlWeights = np.random.randn(6, 1) * 0.1
        self.mlBias = np.zeros((1, 1))
        self.lastJumpFeatures = None


    def canReach(self, platform):
        horizontalDistance = platform.rect.centerx - self.rect.centerx
        if horizontalDistance <= 0:
            return False

        simX = float(self.rect.centerx)
        simY = float(self.rect.bottom)
        simVy = -12
        gravity = 0.5

        horizontalSpeed = self.speedx * 0.85

        for i in range(75): 
            simX += horizontalSpeed
            simY += simVy
            simVy += gravity
            if (
                abs(simX - platform.rect.centerx) < 14 and
                abs(simY - platform.rect.top) < 14 and
                simVy > 0
            ):
                return True
            if simY > platform.rect.top + 120:
                return False

        return False

    def extractFeatures(self, platform):
        horizontalDistance = platform.rect.centerx - self.rect.centerx
        verticalDifference = platform.rect.top - self.rect.bottom
        vy = self.state[1][0]

        if self.speedx > 0:
            time = horizontalDistance / self.speedx
        else:
            time = horizontalDistance / 0.1

        if self.canReach(platform):
            reachable = 1.0
        else:
            reachable = 0.0

        verticalPreference = -abs(verticalDifference) / 250
        forwardBias = horizontalDistance / 300

        return np.array([
            time,
            verticalDifference,
            vy,
            reachable,
            verticalPreference,
            forwardBias
        ])
    def evaluateUtility(self, features):
        weights = np.array([-0.6, -0.04, -0.2, 2.5, 1.2, 1.8])
        utility = np.dot(weights, features)
        utility *= self.skill
        utility += random.uniform(-0.2, 0.2)
        return utility
    
    def mlPredict(self, x): # ensure input shape is valid
        try:
            if x.shape[1] != 6:
                raise ValueError('Input array should have 6 features.')
            return np.dot(x, self.mlWeights) + self.mlBias
        except Exception as e:
            print(f'Error in mlPredict: {e}')
            return np.zeros((x.shape[0], 1))

    def mlTrain(self, x, target): # ensure shapes of x and target match for the training
        try:
            if x is None:
                return
            if x.shape[0] != target.shape[0]:
                raise ValueError('Input and target arrays must have the same number of rows.')
            prediction = self.mlPredict(x)
            error = prediction - target
            self.mlWeights -= self.mlLr * (x.T @ error)
            self.mlBias -= self.mlLr * error
        except Exception as e:
            print(f'Error in mlTrain: {e}')
        
    def isLandingSafe(self, platform, spikes):
        landingRect = pygame.Rect(
            platform.rect.centerx - 15,
            platform.rect.top - 5,
            30,
            10
        )

        for s in spikes:
            if landingRect.colliderect(s.rect.inflate(20, 10)):
                return False
        return True

    def move(self, platforms, spikes=None):
        if spikes is None:
            spikes = []

        self.speedx = max(2.5, self.baseSpeed + random.uniform(-self.speedNoise, self.speedNoise))
        self.applyHorizontalControl(self.speedx)

        #new reinforcement learning for penalty - failed jump
        if not self.touchGround and self.rect.y > 640:
            if self.lastJumpFeatures is not None:
                target = np.array([[-1.0]])
                self.mlTrain(self.lastJumpFeatures, target)
                self.lastJumpFeatures = None

        # Animate legs
        self.legTimer += 1
        if self.legTimer >= self.legInterval:
            if self.currentImage == self.image:
                self.currentImage = self.imageAlt
            else:
                self.currentImage = self.image

            self.legTimer = 0
        if self.reactionCoolDown > 0:
            self.reactionCoolDown -= 1
            # still allows spike reaction despite cooldown
            for s in spikes:
                if self.rect.right < s.rect.centerx < self.rect.right + 80:
                    if abs(s.rect.bottom - self.rect.bottom) < 30:
                        self.jump(-13)
                        return
            return
        
        candidates = []

        for p in platforms:
            horizontalDistance = p.rect.left - self.rect.right
            if horizontalDistance <= 0 or horizontalDistance > 400:
                continue

            if not self.isLandingSafe(p, spikes):
                continue

            if p.rect.width < 40:
                continue

            if self.canReach(p):
                candidates.append(p)
        bestScore = -float('inf')
        bestPlatform = None

        for p in candidates:
            features = self.extractFeatures(p)

            # Depth-2 to look for future options
            futureOptions = 0
            for future in platforms:
                if future.rect.centerx > p.rect.centerx:
                    if self.canReach(future):
                        futureOptions += 1

            lookaheadBonus = min(futureOptions, 3) * 1.0

            score = self.evaluateUtility(features)
            score += lookaheadBonus

            if score > bestScore:
                bestScore = score
                bestPlatform = p

        self.targetPlatform = bestPlatform
        jumpRequired = False

        for s in spikes:
            if self.rect.right < s.rect.centerx < self.rect.right + max(90, self.speedx * 25):
                if abs(s.rect.bottom - self.rect.bottom) < 30:
                    jumpRequired = True
                    break
            
        if self.touchGround:
            jumpRequired = False
            lookAhead = max(100, int(self.speedx*35))
            groundAhead = False
            for p in platforms:
                if (
                    p.rect.left <= self.rect.centerx + 60 <= p.rect.right and
                    abs(p.rect.top - self.rect.bottom) < 6
                ):
                    groundAhead = True
                    break
            # Extra detects large gaps (no platforms)
            gapDanger = True
            for p in platforms:
                if (
                    self.rect.centerx < p.rect.centerx < self.rect.centerx + lookAhead and
                    abs(p.rect.top - self.rect.bottom) < 80
                ):
                    gapDanger = False
                    break

            if gapDanger:
                jumpRequired = True
            if not groundAhead:
                jumpRequired = True

            
            for s in spikes:
                horizontalDist = s.rect.left - self.rect.right
                verticalAlign = abs(s.rect.bottom - self.rect.bottom)
                if 0 < horizontalDist < 90 and verticalAlign < 25:
                    jumpRequired = True
                    break

            if self.targetPlatform:
                horizontalDistance  = self.targetPlatform.rect.centerx - self.rect.centerx
                verticalDifference = self.targetPlatform.rect.top - self.rect.bottom


                if verticalDifference < -15:
                    jumpRequired = True

    
                edgeDistance = self.targetPlatform.rect.left - self.rect.right
                if 10 < edgeDistance < 45:
                    jumpRequired = True
##########################################
        for s in spikes:
            if 0 < (s.rect.left - self.rect.right) < 50:
                if abs(s.rect.bottom - self.rect.bottom) < 25:
                    self.jump(-13)
                    return
        
        if jumpRequired:
            headBlocked = False
            headCheck = pygame.Rect(self.rect.x, self.rect.y - 28, self.rect.width, 28)
            for p in platforms:
                if headCheck.colliderect(p.rect):
                    headBlocked = True
                    break
            if headBlocked:
                jumpRequired = False
   #################################################         
            # positive reinforcement learning
            if jumpRequired:
                if self.targetPlatform is not None:
                    features = self.extractFeatures(self.targetPlatform)
                    x = features.reshape(1, -1)
                    adjustment = self.mlPredict(x)[0][0]
                    adjustment = np.clip(adjustment, -0.8, 0.8)
                else:
                    adjustment = 0  

                jumpStrength = -12 + adjustment

                if self.targetPlatform is not None:
                    self.lastJumpFeatures = x
                else:
                    self.lastJumpFeatures = None
                self.mlTrain(self.lastJumpFeatures, np.array([[1.0]]))
                self.jump(jumpStrength)
                self.reactionCoolDown = 8


        # Personality randomness
        if self.touchGround and random.random() < self.panicChance and self.targetPlatform is not None:
            features = self.extractFeatures(self.targetPlatform)
            x = features.reshape(1, -1)

            adjustment = self.mlPredict(x)[0][0]

            adjustment = np.clip(adjustment, -0.8, 0.8)

            jumpStrength = -12 + adjustment

            self.lastJumpFeatures = x
            self.jump(jumpStrength)

    def draw(self, screen):
        screen.blit(self.currentImage, self.rect)

    def reset(self, startY=None):
        super().reset(startY)
        self.targetPlatform = None
        self.commitTimer = 0
        self.reactionCoolDown = 0
        self.lastJumpFeatures = None