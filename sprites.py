# Sprite classes for platform game
import pygame as pg
from settings import *
import random
import os

# gyroscope ADD
# import time
# import board
# import digitalio
# import adafruit_lis3dh
# END

# gyroscope ADD
#start = time.time()
# END

vec = pg.math.Vector2
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")

class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2, height // 2))
        return image

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load(os.path.join(img_folder, "player.png")).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (40, HEIGHT - 100)
        self.pos = vec(40, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, PLAYER_GRAV)

    # gyroscope ADD      
    def gyroscope(self):
        #if((time.time() - start) % 5.0 <= 1.0):
                i2c = board.I2C()
                int1 = digitalio.DigitalInOut(board.D6)  # Set this to the correct pin for the interrupt!
                lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
                self.x, self.y, self.z = lis3dh.acceleration
         
    def jump(self):
        # jump only if standing on a platform
        hits = pg.sprite.spritecollide(self, self.game.normal_platforms, False)
        if hits and self.vel.y > 0:
            self.game.jump_sound.play()
            self.vel.y = -PLAYER_JUMP
            self.acc.y = PLAYER_GRAV
    
    def update(self):
        
        
        #self.animate()
        self.acc.x = 0
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC
        
        
        
        # # gyroscope ADD
        # #self.animate()
        # self.gyroscope()
        # self.acc.x = 0
        # keys = pg.key.get_pressed()
        # if self.x < -3.0:
        #     self.acc.x = -PLAYER_ACC
        # if self.x >  3.0:
        #     self.acc.x = PLAYER_ACC
        # # END
        

        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        # wrap around the sides of the screen
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = self.pos

class NormalPlatform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.normal_platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        normal_images = [self.game.spritesheet.get_image(0, 576, 380, 94),
                         self.game.spritesheet.get_image(218, 1456, 201, 100)]
        self.image = random.choice(normal_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if random.randrange(100) < POW_SPAWN_PCT:
            Pow(self.game, self)

class BrokenPlatform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.broken_platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        broken_images = [self.game.spritesheet.get_image(0, 480, 380, 94),
                         self.game.spritesheet.get_image(382, 306, 200, 100)]
        self.image = random.choice(broken_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if random.randrange(100) < POW_SPAWN_PCT:
            Pow(self.game, self)

class Pow(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.pows
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = random.choice(['life','boost'])
        if self.type == 'life':
            self.image = self.game.spritesheet.get_image(820, 1733, 78, 70)
        if self.type == 'boost':
            self.image = self.game.spritesheet.get_image(852, 1089, 65, 77)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.normal_platforms.has(self.plat) and not self.game.broken_platforms.has(self.plat):
            self.kill()

class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load(os.path.join(img_folder, "monster.png")).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice([-100, WIDTH + 100])
        self.vx = -random.randrange(1, 4)
        self.rect.y = random.randrange(HEIGHT / 2)
        self.vy = 0
        self.dy = 0.5

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < -3:
            self.dy *= -1
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()


