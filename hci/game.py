# Copyright (c) 2006 Matthew Gregan <kinetik@flim.org>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import sys
import cPickle
import time
import random

from pygame.locals import *
import pygame
from pgu import tilevid

import splashscreen
import menu
import sprite

def initialize_modules():
    '''Initialize PyGame modules.  If any modules fail, report all failures
    and exit the program.'''
    modules = (pygame.display, pygame.mixer, pygame.font)
    errors = []

    for m in modules:
        try:
            m.init()
        except pygame.error, e:
            errors.append(e)

    for e in errors:
        print >> sys.stderr, 'initialization failure: %s' %e

    if errors: sys.exit(1)

def tile_block(g, t, a):
    c = t.config
    if c['top'] == 1 and a._rect.bottom <= t._rect.top \
           and a.rect.bottom > t.rect.top:
        a.rect.bottom = t.rect.top
    if c['left'] == 1 and a._rect.right <= t._rect.left \
           and a.rect.right > t.rect.left:
        a.rect.right = t.rect.left
    if c['right'] == 1 and a._rect.left >= t._rect.right \
           and a.rect.left < t.rect.right:
        a.rect.left = t.rect.right
    if c['bottom'] == 1 and a._rect.top >= t._rect.bottom \
           and a.rect.top < t.rect.bottom:
        a.rect.top = t.rect.bottom

    # craziness
    if hasattr(a.backref, 'tile_blocked'):
        a.backref.tile_blocked()

    a.backref.get_sprite_pos()
    a.backref.stop()

idata = [
    ('player_d1',  'data/test/alien/alien-d1.png', (5, 6, 22, 55)),
    ('player_d2',  'data/test/alien/alien-d2.png', (5, 6, 22, 55)),
    ('player_d3',  'data/test/alien/alien-d3.png', (5, 6, 22, 55)),
    ('player_d4',  'data/test/alien/alien-d4.png', (5, 6, 22, 55)),
    ('player_u1',  'data/test/alien/alien-u1.png', (5, 6, 22, 55)),
    ('player_u2',  'data/test/alien/alien-u2.png', (5, 6, 22, 55)),
    ('player_u3',  'data/test/alien/alien-u3.png', (5, 6, 22, 55)),
    ('player_u4',  'data/test/alien/alien-u4.png', (5, 6, 22, 55)),
    ('player_l1',  'data/test/alien/alien-l1.png', (5, 6, 22, 55)),
    ('player_l2',  'data/test/alien/alien-l2.png', (5, 6, 22, 55)),
    ('player_l3',  'data/test/alien/alien-l3.png', (5, 6, 22, 55)),
    ('player_l4',  'data/test/alien/alien-l4.png', (5, 6, 22, 55)),
    ('player_r1',  'data/test/alien/alien-r1.png', (5, 6, 22, 55)),
    ('player_r2',  'data/test/alien/alien-r2.png', (5, 6, 22, 55)),
    ('player_r3',  'data/test/alien/alien-r3.png', (5, 6, 22, 55)),
    ('player_r4',  'data/test/alien/alien-r4.png', (5, 6, 22, 55)),
    ('fbi_d1',     'data/test/fbi_S1.png', (5, 6, 22, 55)),
    ('fbi_d2',     'data/test/fbi_S2.png', (5, 6, 22, 55)),
    ('fbi_dl1',    'data/test/fbi_SW1.png', (5, 6, 22, 55)),
    ('fbi_dl2',    'data/test/fbi_SW2.png', (5, 6, 22, 55)),
    ('fbi_dr1',    'data/test/fbi_SE1.png', (5, 6, 22, 55)),
    ('fbi_dr2',    'data/test/fbi_SE2.png', (5, 6, 22, 55)),
    ('fbi_l1',     'data/test/fbi_W1.png', (5, 6, 22, 55)),
    ('fbi_l2',     'data/test/fbi_W2.png', (5, 6, 22, 55)),
    ('fbi_r1',     'data/test/fbi_E1.png', (5, 6, 22, 55)),
    ('fbi_r2',     'data/test/fbi_E2.png', (5, 6, 22, 55)),
    ('fbi_u1',     'data/test/fbi_N1.png', (5, 6, 22, 55)),
    ('fbi_u2',     'data/test/fbi_N2.png', (5, 6, 22, 55)),
    ('fbi_ul1',    'data/test/fbi_NW1.png', (5, 6, 22, 55)),
    ('fbi_ul2',    'data/test/fbi_NW2.png', (5, 6, 22, 55)),
    ('fbi_ur1',    'data/test/fbi_NE1.png', (5, 6, 22, 55)),
    ('fbi_ur2',    'data/test/fbi_NE2.png', (5, 6, 22, 55)),
    ('saucer0', 'data/test/Saucer0.png', (20, 20, 140, 70)),
    ('saucer1', 'data/test/Saucer1.png', (20, 20, 140, 70)),
    ('saucer2', 'data/test/Saucer2.png', (20, 20, 140, 70)),
    ('farmer_u0', 'data/test/characters/farmer-up0.png', (1, 1, 30, 53)),
    ('farmer_d0', 'data/test/characters/farmer-dw0.png', (1, 1, 30, 53)),
    ('farmer_r0', 'data/test/characters/farmer-rg0.png', (1, 1, 30, 53)),
    ('farmer_l0', 'data/test/characters/farmer-lf0.png', (1, 1, 30, 53)),
    ('cow_l0',  'data/test/cow000.png', (10, 10, 90, 50)),
    ('cow_l1',  'data/test/cow001.png', (10, 10, 90, 50)),
    ('cow_ul0',  'data/test/cow070.png', (10, 10, 90, 50)),
    ('cow_ul1',  'data/test/cow071.png', (10, 10, 90, 50)),
    ('cow_ur0',  'data/test/cow050.png', (10, 10, 90, 50)),
    ('cow_ur1',  'data/test/cow051.png', (10, 10, 90, 50)),
    ('cow_dl0',  'data/test/cow040.png', (10, 10, 90, 50)),
    ('cow_dl1',  'data/test/cow041.png', (10, 10, 90, 50)),
    ('cow_dr0',  'data/test/cow030.png', (10, 10, 90, 50)),
    ('cow_dr1',  'data/test/cow031.png', (10, 10, 90, 50)),
    ('cow_u0',  'data/test/cow010.png', (10, 10, 50, 90)),
    ('cow_u1',  'data/test/cow011.png', (10, 10, 50, 90)),
    ('cow_d0',  'data/test/cow020.png', (10, 10, 50, 90)),
    ('cow_d1',  'data/test/cow021.png', (10, 10, 50, 90)),
    ('cow_r0',  'data/test/cow060.png', (10, 10, 90, 50)),
    ('cow_r1',  'data/test/cow061.png', (10, 10, 90, 50)),
    ('warn',   'data/test/Warning.png', (0, 0, 16, 16)),
    ('tree', 'data/test/treebiggersize.png', (10, 15, 95, 95)),
    ('bush', 'data/test/treepinkflower.png', (0, 0, 30, 37)),
    ('laser', 'data/test/laser.png', (0, 0, 8, 8)),
    ('trophy',  'data/test/CollectMe.png', (0, 0, 0, 0)),
    ('none',  'data/test/EmptyImage.png', (0, 0, 0, 0)),
    ('chick1', 'data/test/chicksmall01.png', (0, 0, 64, 37)),
    ('chick2', 'data/test/chicksmall02.png', (0, 0, 64, 37)),
    ]

cdata = [
    {
    1: (lambda g, t, v: sprite.Player(g, t, v),  None),
    2: (lambda g, t, v: sprite.Bush(g, t, v),    None),
    3: (lambda g, t, v: sprite.Tree(g, t, v),    None),
    4: (lambda g, t, v: sprite.Farmer(g, t, v),  None),
    5: (lambda g, t, v: sprite.FBISpawn(g, t, v),None),
    6: (lambda g, t, v: sprite.Cow(g, t, v),     None),
    7: (lambda g, t, v: sprite.CollectableCow(g, t, v), ['lvl1_cow']),
    8: (lambda g, t, v: sprite.Chicken(g, t, v), None),
    },

    {
    1: (lambda g, t, v: sprite.Player(g, t, v),  None),
    2: (lambda g, t, v: sprite.Bush(g, t, v),    None),
    3: (lambda g, t, v: sprite.Tree(g, t, v),    None),
    4: (lambda g, t, v: sprite.Farmer(g, t, v),  ['lvl2_farmer']),
    5: (lambda g, t, v: sprite.FBISpawn(g, t, v),None),
    6: (lambda g, t, v: sprite.StationaryCow(g, t, v),     None),
    7: (lambda g, t, v: sprite.CollectableCow(g, t, v), None),
    8: (lambda g, t, v: sprite.Chicken(g, t, v), None),
    }
    ]

tdata = {
    0x02: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x05: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x06: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x07: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x08: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x09: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x0A: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x0B: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    }

map_files  = ['level1.tga', 'level2.tga']
music_files = ['Track01.ogg', 'Track02.ogg']

def load_level(lvl_num):
    try:
        version = open('_MTN/revision').read().strip()
        if version.startswith('format'):
            version = os.popen('mtn automate get_base_revision_id').read().strip()
    except IOError, e:
        version = '?'

    game = tilevid.Tilevid()
    game.view.w = 640
    game.view.h = 480
    game.tile_w = 32
    game.tile_h = 32
    game.screen = pygame.display.set_mode([game.view.w, game.view.h], pygame.DOUBLEBUF)
    pygame.display.set_caption("The Extraterrorestrial [rev %.6s...]" % version)
    game.frame = 0
    game.recording = False
    game.recorded_path = []

    game.tga_load_tiles('data/tilesets/testset.png', [game.tile_w, game.tile_h], tdata)
    game.tga_load_level('data/maps/' + map_files[lvl_num], True)
    game.bounds = pygame.Rect(game.tile_w, game.tile_h,
                              (len(game.tlayer[0])-2)*game.tile_w,
                              (len(game.tlayer)-2)*game.tile_h)

    game.load_images(idata)
    game.deferred_effects = []
    game.fbi_spawns = []

    game.menu_font = pygame.font.Font('data/fonts/Another_.ttf', 36)
    game.run_codes(cdata[lvl_num], (0, 0, len(game.tlayer[0]), len(game.tlayer)))
    game.music = pygame.mixer.music
    game.music.queue('data/music/' + music_files[lvl_num])
    game.music.set_endevent(USEREVENT)

    game.agents = 0
    game.max_fbi_agents = lvl_num * 2
    game.quit = 0
    game.pause = 0
    game.game_over = False

    game.player.view_me(game)

    return game

def run():
    initialize_modules()

    level = 0
    game  = load_level(level)

    splash_image = pygame.image.load('data/screens/splash.png')
    menu_image   = pygame.image.load('data/screens/menu.png')
    death_image  = pygame.image.load('data/screens/GameOverMan.png')

    # splashscreen.fade_in(game.screen, splash_image)
    # pygame.time.wait(500)
    # splashscreen.fade_out(game.screen, splash_image)

    selection = menu.show([game.view.w, game.view.h], game.screen, menu_image, game.menu_font)

    t = pygame.time.Clock()

    game.quit = 0
    game.paint(game.screen)

    game.pause = 0

    if selection == -1: game.quit = 1

    text = pygame.font.Font(None, 36)
    text_sm = pygame.font.Font(None, 16)

    game.player.view_me(game)

    direction = 0
    while not game.quit:
        t.tick(60)
        for e in pygame.event.get():
            if e.type is QUIT: game.quit = 1
            if e.type is KEYDOWN:
                if e.key == K_ESCAPE: game.quit = 1
                if e.key == K_F10:
                    flags = pygame.DOUBLEBUF
                    if not game.fullscreen:
                        flags |= pygame.FULLSCREEN
                        game.fullscreen = True
                    game.screen = pygame.display.set_mode([game.view.w, game.view.h], flags)
                if e.key == K_r: game.player.morph()
                if e.key == K_RETURN:
                     if not game.game_over:
                         game.pause = not game.pause
                     else:
                         game = load_level(level)
                         game.music.play()
                if e.key == K_BACKQUOTE:
                    if game.recording:
                        file = open('data/paths/path' + str(time.time()), 'wb');
                        cPickle.dump(game.recorded_path, file, protocol=2)
                        file.close()
                        game.recording = False
                    else:
                        game.recording = True
                        game.recorded_path = []
            if e.type is MOUSEBUTTONDOWN:
                if e.button == 1:
                    if game.recording:
                        game.recorded_path.append((game.view.x + e.pos[0], game.view.y + e.pos[1]))
            if e.type is USEREVENT:
                game.music.play()

        if game.pause:
            caption = "GAME PAUSED"
            game.music.pause()
            txt = text.render(caption, 1, [0, 0, 0])
            dx = game.view.w/2 - txt.get_rect().w/2
            dy = game.view.h/2 - txt.get_rect().h/2
            game.screen.blit(txt, [dx + 1, dy + 1])
            txt = text.render(caption, 1, [255, 255, 255])
            game.screen.blit(txt, [dx, dy])
            pygame.display.flip()
        elif game.game_over:
            game.player.walking_sound.stop()
            game.music.stop()
            game.screen.fill([0, 0, 0])
            game.screen.blit(death_image, [0,0])
            pygame.display.flip()
        else:
            game.music.unpause()
            if game.view.x == game.bounds.w - game.view.w + game.tile_w \
                   and direction == 1:
                direction = -1
            elif game.view.x == game.tile_w and direction == -1:
                direction = 1
            game.view.x += direction

            game.run_codes(cdata, (game.view.right/game.tile_w, 0, 1, 17))
            game.loop()

            game.paint(game.screen)

            for e in game.deferred_effects[:]:
                e()
                game.deferred_effects.remove(e)

            if game.player.lvl_complete:
                level = (level + 1) % 2
                game.music.stop()
                game = load_level(level)
                game.music.play()

            if game.recording:
                # draw recorded path
                def sub_gv(pt):
                    return (pt[0]-game.view.x, pt[1]-game.view.y)

                for pt in xrange(len(game.recorded_path)):
                    start = sub_gv(game.recorded_path[pt-1])
                    end   = sub_gv(game.recorded_path[pt])
                    pygame.draw.line(game.screen, [random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)], start, end, 2)

                if (game.frame / 30) % 2 == 0:
                    caption = "RECORDING PATH"
                    txt = text.render(caption, 1, [0, 0, 0])
                    dx = game.view.w/2 - txt.get_rect().w/2
                    game.screen.blit(txt, [dx+1,2])
                    txt = text.render(caption, 1, [255, 0, 0])
                    game.screen.blit(txt, [dx, 1])

            caption = "FPS %2.2f" % t.get_fps()
            txt = text.render(caption, 1, [0, 0, 0])
            game.screen.blit(txt, [1, game.view.w - txt.get_height() + 1])
            txt = text.render(caption, 1, [255, 255, 255])
            game.screen.blit(txt, [0, game.view.h - txt.get_height()])

            #caption = "SCORE %05d" % game.player.sprite.score
            #txt = text.render(caption, 1, [0, 0, 0])
            #game.screen.blit(txt, [0, 0])
            #txt = text.render(caption, 1, [255, 255, 255])
            #game.screen.blit(txt, [1, 1])

            game.frame += 1
            pygame.display.flip()
