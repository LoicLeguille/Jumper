# Save Bertrand ! (a platform game)
# Art- from Kenney.nl
# Happy Tune by https://opengameart.org/users/syncopika
# Yippee by https://opengameart.org/users/snabisch

import pygame as pg
import random
from settings import *
from sprites import *
from os import path

class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        self.img_dir = path.join(self.dir, 'img')
        with open(path.join(self.dir, HS_FILE), 'r+') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        # load spritesheets image
        self.spritesheet = Spritesheet(path.join(self.img_dir, SPRITESHEET))
        # load health image
        self.health_img = self.spritesheet.get_image(868, 1936, 52, 71)
        self.health_img.set_colorkey(BLACK)
        # load clouds
        self.cloud_images = []
        for i in range(1, 3):
            self.cloud_images.append(pg.image.load(path.join(self.img_dir, ('cloud{}.png').format(i))).convert())
        # load sound
        self.snd_dir = path.join(self.dir, 'snd')
        self.shield_sound = pg.mixer.Sound(path.join(self.snd_dir, 'shield.wav'))
        self.jetpack_sound = pg.mixer.Sound(path.join(self.snd_dir, 'jetpack.wav'))
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Jump.wav'))
        self.spring_sound = pg.mixer.Sound(path.join(self.snd_dir, 'spring.wav'))

    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.player = Player(self)
        self.mob = Mob(self)
        self.mob.kill()
        self.plat_list = []
        for plat in PLATFORM_LIST:
            p = Platform(self, *plat)
            self.plat_list.append(p)
        for i in range(10):
            cloud = Cloud(self)
            cloud.rect.y += 500
        self.mob_timer = 0
        pg.mixer.music.load(path.join(self.snd_dir, 'HappyTune.ogg'))
        self.run()

    def run(self):
        # Game Loop
        pg.mixer.music.play(loops = -1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        # unhide if hidden
        if self.player.hidden and pg.time.get_ticks() - self.player.hide_timer > 1000:
            self.mob.killed_me = False
        # spawn a mob ?
        now = pg.time.get_ticks()
        if now - self.mob_timer > MOB_SPAWN + random.choice([-1000, 500, 0, 500, 1000]):
            self.mob_timer = now
            self.mob = Mob(self)
        # hit mobs ?
        if not self.mob.killed_me and self.player.shield == False:
            mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False)
            if mob_hits:
                mob_hits_mask = pg.sprite.spritecollide(self.player, self.mobs, False, pg.sprite.collide_mask)
                if mob_hits_mask:
                    self.player.lives -= 1
                    self.player.hide()
                if self.player.lives < 0:
                    self.player.dead = True
                    self.jumping = True
                    self.player.image = self.player.hurt_frame
                    self.player.vel.y = -15
                # show falling animation
                if self.player.rect.bottom > HEIGHT:
                    for sprite in self.all_sprites:
                        sprite.rect.y -= max(self.player.vel.y, 10)
                        if sprite.rect.bottom < 0:
                            sprite.kill()
                if len(self.platforms) == 0:
                    self.playing = False
        # check if player hits a platform - only if falling
        if self.player.vel.y > 0 and not self.player.dead:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = max(hits, key = lambda x: x.rect.bottom)
                if lowest.rect.left - 10 < self.player.pos.x < lowest.rect.right + 10:
                    if self.player.pos.y < lowest.rect.centery :
                        self.player.pos.y = lowest.rect.top
                        self.player.vel.y = 0
                        self.player.jumping = False
        # if player reaches top 1/3 of the screen
        if self.player.rect.top <= HEIGHT / 3:
            if random.randrange(100) < CLOUD_SPAWN :
                Cloud(self)
            self.player.pos.y += max(abs(self.player.vel.y), 3)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y / 2), 3)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 3)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 3)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.plat_list.remove(plat)
                    self.score += 10
        # spawn new platforms
        while len(self.platforms) < 10:
            width = random.randrange(50, 100)
            p = Platform(self,random.randrange(0, WIDTH - width - 50),
                         self.plat_list[-1].rect.y - randrange(150, 202))
            self.plat_list.append(p)
        # if player hits a powerup
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, False)
        for pow in pow_hits:
            if not self.player.dead:
                if pow.type == 'spring' and not self.player.jetpack:
                    self.spring_sound.play()
                    self.player.vel.y = -SPRING_BOOST
                    self.player.jumping = True
                if pow.type == 'health':
                    self.player.hide()
                    if self.player.lives < 3:
                        self.player.lives += 1
                    pow.kill()
                if pow.type == 'jetpack':
                    self.player.jetpack = True
                    self.player.jumping = False
                    self.jetpack_sound.play()
                    Pow_Player(self, pow.type)
                    pow.kill()
                if pow.type == 'shield' and not self.player.jetpack:
                    self.shield_sound.play()
                    self.player.shield = True
                    Pow_Player(self, pow.type)
                    pow.kill()
        # Fall ?!
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

    def events(self):
        # Game Loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def draw(self):
        # Game Loop - draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        for i in range(self.player.lives):
            self.rect = self.health_img.get_rect()
            self.rect.x = 30 * i +4
            self.rect.y = 4
            self.screen.blit(self.health_img, self.rect)
        pg.display.set_caption('{:.2f}'.format(self.clock.get_fps()))
        # *after* drawing everything, flip the display
        pg.display.flip()

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def show_start_screen(self):
        # game splash/start screen
        pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
        pg.mixer.music.play(loops = -1)
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text('Arrows to move, Space to jump', 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text('Press a key to play', 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text('High score: ' + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(700)

    def show_go_screen(self):
        # game over/continue
        if not self.running:
            return
        pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
        pg.mixer.music.play(loops = -1)
        self.screen.fill(BGCOLOR)
        self.draw_text('GAME OVER', 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text('Score: ' + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text('Press a key to play again', 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text('NEW HIGH SCORE!', 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text('High Score: ' + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
