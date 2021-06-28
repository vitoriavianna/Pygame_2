import pygame
from pygame.locals import (KEYDOWN,
                           KEYUP,
                           K_LEFT,
                           K_RIGHT,
                           QUIT,
                           K_ESCAPE, K_UP, K_DOWN, K_RCTRL, K_LCTRL
                           )
import random
import os
from os import path
from math import ceil


#cores
branco = (255, 255, 255)
preto = (0, 0, 0)
vermelho = (255, 0, 0)
verde = (0, 255, 0)
azul = (0, 0, 255)
amarelo = (255, 255, 0)

#diretórios
img_dir = path.join(path.dirname(__file__), 'imagens')
sons_dir = path.join(path.dirname(__file__), 'sons')

LARGURA = 480
ALTURA = 600
DT = 45
POWERUP_TIME = 5000
BARRA_LARGURA = 100
BARRA_ALTURA = 10


pygame.init()
pygame.mixer.init()  
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("THE CORONA SHOOTER")
clock = pygame.time.Clock()    

font_name = pygame.font.match_font('arial')

def desenha_texto(surf, text, size, x, y):

    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, branco)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def desenha_vidas(surf, x, y, lives, img):
    for i in range(lives):
        img_rect= img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)
        
def desenha_shield_bar(surf, x, y, pct):
    pct = max(pct, 0) 
    fill = (pct / 100) * BARRA_LARGURA
    outline_rect = pygame.Rect(x, y, BARRA_LARGURA, BARRA_ALTURA)
    fill_rect = pygame.Rect(x, y, fill, BARRA_ALTURA)
    pygame.draw.rect(surf, verde, fill_rect)
    pygame.draw.rect(surf, branco, outline_rect, 2)

def menu_principal():
    global screen

    menu_song = pygame.mixer.music.load(path.join(sons_dir, "1.wav"))
    pygame.mixer.music.play(-1)

    title = pygame.image.load(path.join(img_dir, "main.png")).convert()
    title = pygame.transform.scale(title, (LARGURA, ALTURA), screen)

    screen.blit(title, (0,0))
    pygame.display.update()

    while True:
        e = pygame.event.poll()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN:
                break
            elif e.key == pygame.K_q:
                pygame.quit()
                quit()
        elif e.type == pygame.QUIT:
                pygame.quit()
                quit() 
        else:
            desenha_texto(screen, "Aperte [ENTER] para começar", 30, LARGURA/2, ALTURA/2)
            desenha_texto(screen, "ou [Q] para sair", 30, LARGURA/2, (ALTURA/2)+40)
            pygame.display.update()

    ready = pygame.mixer.Sound(path.join(sons_dir,'se_prepare.wav'))
    ready.play()
    screen.fill(preto)
    desenha_texto(screen, "SE PREPARE!", 40, LARGURA/2, ALTURA/2)
    pygame.display.update()


def novo_inimigo():
    mob_element = Inimigo()
    all_sprites.add(mob_element)
    mobs.add(mob_element)

class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (40, 100))
        self.image.set_colorkey(preto)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = LARGURA / 2
        self.rect.bottom = ALTURA - 10
        self.speedx = 0 
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()

    def update(self):
        if self.power >=2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = LARGURA / 2
            self.rect.bottom = ALTURA - 30

        self.speedx = 0    

        keystate = pygame.key.get_pressed()     
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT]:
            self.speedx = 5

        if keystate[pygame.K_SPACE]:
            self.shoot()

        if self.rect.right > LARGURA:
            self.rect.right = LARGURA
        if self.rect.left < 0:
            self.rect.left = 0

        self.rect.x += self.speedx

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shooting_sound.play()
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shooting_sound.play()

            if self.power >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                missile1 = Missile(self.rect.centerx, self.rect.top) 
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(missile1)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(missile1)
                shooting_sound.play()
                missile_sound.play()

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (LARGURA / 2, ALTURA + 200)


class Explosão(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center



class Inimigo(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(preto)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width *.90 / 2)
        self.rect.x = random.randrange(0, LARGURA - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(5, 20)     

 
        self.speedx = random.randrange(-3, 3)

        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks() 
        
    def rotate(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_update > 50: 
            self.last_update = time_now
            self.rotation = (self.rotation + self.rotation_speed) % 360 
            new_image = pygame.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if (self.rect.top > ALTURA + 10) or (self.rect.left < -25) or (self.rect.right > LARGURA + 20):
            self.rect.x = random.randrange(0, LARGURA - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

#define poderes
class Powers(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(preto)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > ALTURA:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(preto)
        self.rect = self.image.get_rect()
        self.rect.bottom = y 
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = missile_img
        self.image.set_colorkey(preto)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


background = pygame.image.load(path.join(img_dir, 'space2.png')).convert()
background_rect = background.get_rect()

player_img = pygame.image.load(path.join(img_dir, 'seringa.png')).convert()
player_mini_img = pygame.transform.scale(player_img, (20, 35))
player_mini_img.set_colorkey(preto)
bullet_img = pygame.image.load(path.join(img_dir, 'gota.png')).convert()
missile_img = pygame.image.load(path.join(img_dir, 'laser.png')).convert_alpha()
meteor_images = []
meteor_list = [
    'virus1.png',
    'virus2.png', 
    'virus3.png']

for image in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, image)).convert())

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(6):
    filename = 'explosão0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(preto)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)

    filename = 'explosão0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(preto)
    explosion_anim['player'].append(img)

powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'escudo.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'arma.png')).convert()


shooting_sound = pygame.mixer.Sound(path.join(sons_dir, 'Atirar.wav'))
missile_sound = pygame.mixer.Sound(path.join(sons_dir, 'Atirar.wav'))
expl_sounds = []
for sound in ['dano_nave.wav', 'se_prepare.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(sons_dir, sound)))
pygame.mixer.music.set_volume(0.2)

player_die_sound = pygame.mixer.Sound(path.join(sons_dir, 'dano_nave.wav'))

#loop do jogo
running = True
menu_display = True
while running:
    if menu_display:
        menu_principal()
        pygame.time.wait(3000)
        pygame.mixer.music.stop()
        #música do jogo
        pygame.mixer.music.load(path.join(sons_dir, '1.wav'))
        pygame.mixer.music.play(-1)
        
        menu_display = False
        
        all_sprites = pygame.sprite.Group()
        jogador = Jogador()
        all_sprites.add(jogador)

        mobs = pygame.sprite.Group()
        for i in range(5):     
            novo_inimigo()

        #grupo para os tiros
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()

        score = 0
        
    clock.tick(DT)     
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    all_sprites.update()

    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius         
        random.choice(expl_sounds).play()
        expl = Explosão(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Powers(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        novo_inimigo()        


    hits = pygame.sprite.spritecollide(jogador, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        jogador.shield -= hit.radius * 2
        expl = Explosão(hit.rect.center, 'sm')
        all_sprites.add(expl)
        novo_inimigo()
        if jogador.shield <= 0: 
            player_die_sound.play()
            death_explosion = Explosão(jogador.rect.center, 'player')
            all_sprites.add(death_explosion)
            jogador.hide()
            jogador.lives -= 1
            jogador.shield = 100

    #se o jogador pegar um poder
    hits = pygame.sprite.spritecollide(jogador, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            jogador.shield += random.randrange(10, 30)
            if jogador.shield >= 100:
                jogador.shield = 100
        if hit.type == 'gun':
            jogador.powerup()

    if jogador.lives == 0 and not death_explosion.alive():
        running = False

    screen.fill(preto)
    screen.blit(background, background_rect)

    all_sprites.draw(screen)
    desenha_texto(screen, str(score), 18, LARGURA / 2, 10)
    desenha_shield_bar(screen, 5, 5, jogador.shield)

    desenha_vidas(screen, LARGURA - 100, 5, jogador.lives, player_mini_img)

    pygame.display.flip()       

pygame.quit()
