# Sprite classes for platform Game
import pygame as pg
from random import choice, randrange
from settings import *
vec = pg.math.Vector2

class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        #grab an image out of a larger spritesheet
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
        self.dead = False
        self.walking = False
        self.jumping = False
        self.shield = False
        self.jetpack = False
        self.hidden = False
        self.lives = 0
        self.current_frame = 0
        self.last_update = 0
        self.load_bunny_img()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = vec(40, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_bunny_img(self):
        self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
                                self.game.spritesheet.get_image(690, 406, 120, 201)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
        self.walk_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201),
                                self.game.spritesheet.get_image(692, 1458, 120, 207)]
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)
        self.walk_frames_l = [pg.transform.flip(frame, True, False) for frame in self.walk_frames_r]
        for frame in self.walk_frames_l:
            frame.set_colorkey(BLACK)
        self.jump_frame = self.game.spritesheet.get_image(382, 763, 150, 181)
        self.jump_frame.set_colorkey(BLACK)
        self.hurt_frame = self.game.spritesheet.get_image(382, 946, 150, 174)
        self.hurt_frame.set_colorkey(BLACK)

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -5:
                self.vel.y = -5

    def jump(self):
        # jump only if standing on a platform
        self.rect.y += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 2
        if hits and not self.jumping:
            self.game.jump_sound.play()
            self.jumping = True
            self.vel.y = -PLAYER_JUMP

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAVITY)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] and not self.dead:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT] and not self.dead:
            self.acc.x = PLAYER_ACC
        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # equation of motion
        self.vel += self.acc
        if abs(self.vel.x) < .1:
            self.vel.x = 0
        self.pos += self.vel + .5 * self.acc
        # wrap around the sides of the screen
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2
        self.rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x !=0:
            self.walking = True
        else:
            self.walking = False
        # show walk animation
        if self.walking and not self.dead:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # show jump animation
        if self.jumping and self.vel.y < 0 and not self.dead:
            bottom = self.rect.bottom
            self.image = self.jump_frame
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
        # show idle animation
        if not self.jumping and not self.walking and not self.dead:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        self.mask = pg.mask.from_surface(self.image)

    def hide(self):
        # protect the player temporarily
        self.hidden = True
        self.hide_timer = pg.time.get_ticks()
        self.game.mob.killed_me = True

class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.load_plat_img()
        images = [self.game.spritesheet.get_image(0, 288, 380, 94),
                  self.game.spritesheet.get_image(213, 1662, 201, 100)]
        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        p = Pow(self.game, self)
        if p.spawn < randrange(100):
            p.kill()

    def load_plat_img(self):
        pass

    def pct_spawn(self):
        pass

class Pow(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.load_pow_img()
        self.all_images = [item for item in self.items]
        self.type = choice(self.all_images)
        self.pct_spawn()
        self.image = self.items[self.type]
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([self.plat.rect.left + 30,
                                    self.plat.rect.centerx,
                                    self.plat.rect.right - 30])
        self.rect.bottom = self.plat.rect.top

    def update(self):
        self.rect.bottom = self.plat.rect.top
        if not self.game.platforms.has(self.plat):
            self.kill()

    def load_pow_img(self):
        self.spring_img = self.game.spritesheet.get_image(0, 1988, 145, 57)
        self.spring_img.set_colorkey(BLACK)
        self.jetpack_img = self.game.spritesheet.get_image(852, 1089, 65, 77)
        self.jetpack_img.set_colorkey(BLACK)
        self.shield_img = self.game.spritesheet.get_image(826, 134, 71, 70)
        self.shield_img.set_colorkey(BLACK)
        self.health_img = self.game.spritesheet.get_image(814, 1661, 78, 70)
        self.health_img.set_colorkey(BLACK)
        self.items = {'spring': self.spring_img, 'jetpack': self.jetpack_img,
                      'shield': self.shield_img, 'health': self.health_img}

    def pct_spawn(self):
        if self.game.score < 500:
            if self.type == 'spring':
                self.spawn = 2
            if self.type == 'health':
                self.spawn = 2
            if self.type == 'jetpack':
                self. spawn = 2
            if self.type == 'shield':
                self.spawn = 2
        elif self.game.score < 1000:
            if self.type == 'spring':
                self.spawn = 8
            if self.type == 'health':
                self.spawn = 2
            if self.type == 'jetpack':
                self. spawn = 3
            if self.type == 'shield':
                self.spawn = 4
        else:
            if self.type == 'spring':
                self.spawn = 4
            if self.type == 'health':
                self.spawn = 4
            if self.type == 'jetpack':
                self. spawn = 2
            if self.type == 'shield':
                self.spawn = 5

class Pow_Player(pg.sprite.Sprite):
    def __init__(self, game, type):
        self._layer = ACTIVATED_POW_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = type
        self.load()
        self.image = self.all_pow[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = self.game.player.rect.center
        self.last_update = pg.time.get_ticks()

    def update(self):
        self.rect = self.image.get_rect()
        self.rect.center = self.game.player.rect.center
        now = pg.time.get_ticks()
        if not self.game.player.dead:
            if now - self.last_update > SHIELD_DURABILITY and self.image == self.shield_img:
                self.last_update = now
                self.game.player.shield = False
                self.kill()
            if self.image == self.jetpack_img:
                self.game.player.vel.y = -JETPACK_BOOST
                if now - self. last_update > JETPACK_DURABILITY:
                    self.last_update = now
                    if self.game.player.vel.y <= 0:
                        self.kill()
                        self.game.player.jetpack = False

    def load(self):
        self.shield_img = self.game.spritesheet.get_image(0, 1662, 211, 215)
        self.shield_img.set_colorkey(BLACK)
        self.jetpack_img = self.game.spritesheet.get_image(563, 1843, 133, 160)
        self.jetpack_img.set_colorkey(BLACK)
        self.all_pow = {'shield': self.shield_img, 'jetpack': self.jetpack_img}

class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey(BLACK)
        self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey(BLACK)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([-100, WIDTH + 100])
        self.vx, self.vy = vec(randrange(1, 4), 0)
        if self.rect.centerx > WIDTH :
            self.vx *= -1
        self.rect.y = randrange(-300,0)
        self.dy = .5
        self.killed_me = False

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if abs(self.vy) >= 3:
            self.dy *= -1
        center = self.rect.center
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()

class Cloud(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = CLOUD_LAYER
        self.groups = game.all_sprites, game.clouds
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = choice(self.game.cloud_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        scale = randrange(50, 101) / 100
        self.image = pg.transform.scale(self.image, (int(self.rect.width * scale),
                                                     int(self.rect.height * scale)))
        self.rect.x, self.rect.y = vec(randrange(WIDTH - self.rect.width), randrange(-500, -50))

    def update(self):
        if self.rect.top > HEIGHT * 2:
            self.kill()
