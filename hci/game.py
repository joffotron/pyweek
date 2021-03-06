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

debug = True

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

def CG(l):
    sz = len(l)
    i = 0
    while True:
        yield l[i]
        i += 1
        i %= sz

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
    ('player_d1',  'data/sprites/alien/alien-d1.png', (5, 6, 22, 55)),
    ('player_d2',  'data/sprites/alien/alien-d2.png', (5, 6, 22, 55)),
    ('player_d3',  'data/sprites/alien/alien-d3.png', (5, 6, 22, 55)),
    ('player_d4',  'data/sprites/alien/alien-d4.png', (5, 6, 22, 55)),
    ('player_u1',  'data/sprites/alien/alien-u1.png', (5, 6, 22, 55)),
    ('player_u2',  'data/sprites/alien/alien-u2.png', (5, 6, 22, 55)),
    ('player_u3',  'data/sprites/alien/alien-u3.png', (5, 6, 22, 55)),
    ('player_u4',  'data/sprites/alien/alien-u4.png', (5, 6, 22, 55)),
    ('player_l1',  'data/sprites/alien/alien-l1.png', (5, 6, 22, 55)),
    ('player_l2',  'data/sprites/alien/alien-l2.png', (5, 6, 22, 55)),
    ('player_l3',  'data/sprites/alien/alien-l3.png', (5, 6, 22, 55)),
    ('player_l4',  'data/sprites/alien/alien-l4.png', (5, 6, 22, 55)),
    ('player_r1',  'data/sprites/alien/alien-r1.png', (5, 6, 22, 55)),
    ('player_r2',  'data/sprites/alien/alien-r2.png', (5, 6, 22, 55)),
    ('player_r3',  'data/sprites/alien/alien-r3.png', (5, 6, 22, 55)),
    ('player_r4',  'data/sprites/alien/alien-r4.png', (5, 6, 22, 55)),
    ('fbi_d1',     'data/sprites/fbi_S1.png', (5, 6, 22, 55)),
    ('fbi_d2',     'data/sprites/fbi_S2.png', (5, 6, 22, 55)),
    ('fbi_dl1',    'data/sprites/fbi_SW1.png', (5, 6, 22, 55)),
    ('fbi_dl2',    'data/sprites/fbi_SW2.png', (5, 6, 22, 55)),
    ('fbi_dr1',    'data/sprites/fbi_SE1.png', (5, 6, 22, 55)),
    ('fbi_dr2',    'data/sprites/fbi_SE2.png', (5, 6, 22, 55)),
    ('fbi_l1',     'data/sprites/fbi_W1.png', (5, 6, 22, 55)),
    ('fbi_l2',     'data/sprites/fbi_W2.png', (5, 6, 22, 55)),
    ('fbi_r1',     'data/sprites/fbi_E1.png', (5, 6, 22, 55)),
    ('fbi_r2',     'data/sprites/fbi_E2.png', (5, 6, 22, 55)),
    ('fbi_u1',     'data/sprites/fbi_N1.png', (5, 6, 22, 55)),
    ('fbi_u2',     'data/sprites/fbi_N2.png', (5, 6, 22, 55)),
    ('fbi_ul1',    'data/sprites/fbi_NW1.png', (5, 6, 22, 55)),
    ('fbi_ul2',    'data/sprites/fbi_NW2.png', (5, 6, 22, 55)),
    ('fbi_ur1',    'data/sprites/fbi_NE1.png', (5, 6, 22, 55)),
    ('fbi_ur2',    'data/sprites/fbi_NE2.png', (5, 6, 22, 55)),
    ('saucer0', 'data/sprites/Saucer0.png', (20, 20, 140, 70)),
    ('saucer1', 'data/sprites/Saucer1.png', (20, 20, 140, 70)),
    ('saucer2', 'data/sprites/Saucer2.png', (20, 20, 140, 70)),
    ('farmer_u1', 'data/sprites/characters/farmer-u1.png', (1, 1, 30, 53)),
    ('farmer_u2', 'data/sprites/characters/farmer-u2.png', (1, 1, 30, 53)),
    ('farmer_u3', 'data/sprites/characters/farmer-u3.png', (1, 1, 30, 53)),
    ('farmer_u4', 'data/sprites/characters/farmer-u4.png', (1, 1, 30, 53)),
    ('farmer_d1', 'data/sprites/characters/farmer-d1.png', (1, 1, 30, 53)),
    ('farmer_d2', 'data/sprites/characters/farmer-d2.png', (1, 1, 30, 53)),
    ('farmer_d3', 'data/sprites/characters/farmer-d3.png', (1, 1, 30, 53)),
    ('farmer_d4', 'data/sprites/characters/farmer-d4.png', (1, 1, 30, 53)),
    ('farmer_r1', 'data/sprites/characters/farmer-r1.png', (1, 1, 30, 53)),
    ('farmer_r2', 'data/sprites/characters/farmer-r2.png', (1, 1, 30, 53)),
    ('farmer_r3', 'data/sprites/characters/farmer-r3.png', (1, 1, 30, 53)),
    ('farmer_r4', 'data/sprites/characters/farmer-r4.png', (1, 1, 30, 53)),
    ('farmer_l1', 'data/sprites/characters/farmer-l1.png', (1, 1, 30, 53)),
    ('farmer_l2', 'data/sprites/characters/farmer-l2.png', (1, 1, 30, 53)),
    ('farmer_l3', 'data/sprites/characters/farmer-l3.png', (1, 1, 30, 53)),
    ('farmer_l4', 'data/sprites/characters/farmer-l4.png', (1, 1, 30, 53)),
    ('cow_l0',  'data/sprites/cow000.png', (10, 10, 90, 50)),
    ('cow_l1',  'data/sprites/cow001.png', (10, 10, 90, 50)),
    ('cow_ul0',  'data/sprites/cow070.png', (10, 10, 90, 50)),
    ('cow_ul1',  'data/sprites/cow071.png', (10, 10, 90, 50)),
    ('cow_ur0',  'data/sprites/cow050.png', (10, 10, 90, 50)),
    ('cow_ur1',  'data/sprites/cow051.png', (10, 10, 90, 50)),
    ('cow_dl0',  'data/sprites/cow040.png', (10, 10, 90, 50)),
    ('cow_dl1',  'data/sprites/cow041.png', (10, 10, 90, 50)),
    ('cow_dr0',  'data/sprites/cow030.png', (10, 10, 90, 50)),
    ('cow_dr1',  'data/sprites/cow031.png', (10, 10, 90, 50)),
    ('cow_u0',  'data/sprites/cow010.png', (10, 10, 50, 90)),
    ('cow_u1',  'data/sprites/cow011.png', (10, 10, 50, 90)),
    ('cow_d0',  'data/sprites/cow020.png', (10, 10, 50, 90)),
    ('cow_d1',  'data/sprites/cow021.png', (10, 10, 50, 90)),
    ('cow_r0',  'data/sprites/cow060.png', (10, 10, 90, 50)),
    ('cow_r1',  'data/sprites/cow061.png', (10, 10, 90, 50)),
    ('warn',   'data/sprites/Warning.png', (0, 0, 16, 16)),
    ('player_warn',   'data/sprites/player_warn.png', (0, 0, 4, 8)),
    ('tree', 'data/sprites/treebiggersize.png', (8, 8, 72, 78)),
    ('bush', 'data/sprites/treepinkflower.png', (0, 0, 30, 37)),
    ('laser', 'data/sprites/laser.png', (0, 0, 8, 8)),
    ('trophy',  'data/sprites/CollectMe.png', (0, 0, 0, 0)),
    ('none',  'data/sprites/EmptyImage.png', (-10, -10, 20, 20)),
    ('chick1', 'data/sprites/chicksmall01.png', (0, 0, 64, 37)),
    ('chick2', 'data/sprites/chicksmall02.png', (0, 0, 64, 37)),
    ('square', 'data/sprites/square.png', (0, 0, 40, 40)),
    ('suv', 'data/sprites/Car.png', (0, 0, 160, 122)),
    ('hay1', 'data/sprites/hay02.png', (0, 0, 58, 45)),
    ]

cdata = [
    {
    1: (lambda g, t, v: sprite.Player(g, t, v),  None),
    2: (lambda g, t, v: sprite.Bush(g, t, v),    None),
    3: (lambda g, t, v: sprite.Tree(g, t, v),    None),
    4: (lambda g, t, v: sprite.Farmer(g, t, v),  None),
    5: (lambda g, t, v: sprite.FBISpawn(g, t, v),None),
    6: (lambda g, t, v: sprite.Cow(g, t, v),     None),
    7: (lambda g, t, v: sprite.CollectableCow(g, t, v), CG(['lvl1_cow'])),
    8: (lambda g, t, v: sprite.Chicken(g, t, v), None),
    9: (lambda g, t, v: sprite.SUV(g, t, v), None),
    10: (lambda g, t, v: sprite.HayBale(g, t, v), None),
    },

    {
    1: (lambda g, t, v: sprite.Player(g, t, v),  None),
    2: (lambda g, t, v: sprite.Bush(g, t, v),    None),
    3: (lambda g, t, v: sprite.Tree(g, t, v),    None),
    4: (lambda g, t, v: sprite.Farmer(g, t, v),  CG(['lvl2_farmer'])),
    5: (lambda g, t, v: sprite.FBISpawn(g, t, v),None),
    6: (lambda g, t, v: sprite.StationaryCow(g, t, v),  None),
    7: (lambda g, t, v: sprite.CollectableCow(g, t, v), None),
    8: (lambda g, t, v: sprite.Chicken(g, t, v), None),
    9: (lambda g, t, v: sprite.SUV(g, t, v), None),
    10: (lambda g, t, v: sprite.HayBale(g, t, v), None),
    },

    {
    1: (lambda g, t, v: sprite.Player(g, t, v),  None),
    2: (lambda g, t, v: sprite.Bush(g, t, v),    None),
    3: (lambda g, t, v: sprite.Tree(g, t, v),    None),
    4: (lambda g, t, v: sprite.Farmer(g, t, v),  CG(['lvl3_farmer', 'lvl3_farmer01', 'lvl3_farmer02', 'lvl3_farmer03'])),
    5: (lambda g, t, v: sprite.FBISpawn(g, t, v),None),
    6: (lambda g, t, v: sprite.StationaryCow(g, t, v),  None),
    7: (lambda g, t, v: sprite.CollectableCow(g, t, v), CG(['lvl3_cow01', 'lvl3_cow02', 'lvl3_cow03', 'lvl3_cow04', 'lvl3_cow05', 'lvl3_cow06', 'lvl3_cow07', 'lvl3_cow08', 'lvl3_cow01'])),
    8: (lambda g, t, v: sprite.Chicken(g, t, v), None),
    9: (lambda g, t, v: sprite.SUV(g, t, v), None),
    10: (lambda g, t, v: sprite.HayBale(g, t, v), None),
    },

    {
    1: (lambda g, t, v: sprite.Player(g, t, v),  None),
    2: (lambda g, t, v: sprite.Bush(g, t, v),    None),
    3: (lambda g, t, v: sprite.Tree(g, t, v),    None),
    4: (lambda g, t, v: sprite.Farmer(g, t, v),  CG(['lvl4_farmer1','lvl4_farmer2','lvl4_farmer3'])),
    5: (lambda g, t, v: sprite.FBISpawn(g, t, v),None),
    6: (lambda g, t, v: sprite.StationaryCow(g, t, v),  None),
    7: (lambda g, t, v: sprite.CollectableCow(g, t, v), CG(['lvl4_cow_path1','lvl4_cow_path2','lvl4_cow_path3'])),
    8: (lambda g, t, v: sprite.Chicken(g, t, v), None),
    9: (lambda g, t, v: sprite.SUV(g, t, v), None),
    10: (lambda g, t, v: sprite.HayBale(g, t, v), None),
    }
    ]

tdata = {
    0x02: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x04: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x05: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x06: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x07: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x08: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x09: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x0A: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x0B: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x0C: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x0D: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x0E: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x0F: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x10: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x11: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x12: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x13: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x14: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x15: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x16: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x17: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x18: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    0x19: ('fbi,farmer,player', tile_block, {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
    }

map_files  = ['level1.tga', 'level2.tga', 'level3.tga', 'level4.tga']
music_files = ['Track01.ogg', 'Track02.ogg', 'Track03.ogg']
fbi_limit   = [0,1,2,4]
def do_menu(screen, width, height, game_running=False):
    menu_image   = pygame.image.load('data/screens/menu.png')
    menu_font = pygame.font.Font('data/fonts/Another_.ttf', 36)

    options = ['Start Game', 'Instructions', 'Quit']
    if game_running:
        options[0] = 'Resume Game'
    selection = menu.show([width, height], screen, menu_image, menu_font, options)

    if selection == -1 or selection == 2:
        sys.exit()

    if selection == 1:
        instructions(screen, width, height)

    return selection

def instructions(screen, width, height):
    txt = (('Collect all the Earthly trophies on the level and return to your ship!'),
           ('If you are seen by the locals the FBI will appear on the scene.'),
           ('Unless you love to be probed, don\'t let them catch you!'),
           (''),
           ('W, A, S, D or cursor keys', 'Movement'),
           ('Left click', 'Move to selected location'),
           ('Right click', 'Abduct Earthly item'),
           ('Space', 'Morph into an Earthly item'),
           ('Enter', 'Pause game'),
           ('Escape', 'Main Menu'),
           (''), (''),
           ('[Hit any key to continue.]'))
    screen.fill([0, 0, 0])
    font = pygame.font.Font('data/fonts/Another_.ttf', 24)
    y = 32
    for i in txt:
        if len(i) == 2:
            l, r = i

            t = font.render(l, 1, [255, 255, 255])
            tr = t.get_rect()
            tr.x = 32
            tr.y = y
            screen.blit(t, tr)

            t = font.render(r, 1, [255, 255, 255])
            tr = t.get_rect()
            tr.x = width - tr.w - 32
            tr.y = y
            screen.blit(t, tr)
        else:
            t = font.render(i, 1, [255, 255, 255])
            tr = t.get_rect()
            tr.x = width / 2 - tr.w / 2
            tr.y = y
            screen.blit(t, tr)
        y += 32

    pygame.display.flip()

    while True:
        e = pygame.event.wait()
        if e.type is KEYDOWN:
            return

def load_level(lvl_num, screen, wide, high, load_image):
    if debug:
        try:
            version = open('_MTN/revision').read().strip()
            if version.startswith('format'):
                version = os.popen('mtn automate get_base_revision_id').read().strip()
        except IOError, e:
            version = '?'

    #Must stop all sounds before starting the level again
    #If resumed from "Game over" you get multiple sounds
    pygame.mixer.stop()

    #Reset the cops flag
    sprite.FBI.called_the_cops = False
    


    game = tilevid.Tilevid()
    game.view.w = wide
    game.view.h = high
    game.tile_w = 32
    game.tile_h = 32
    game.screen = screen
    game.screen.blit(load_image, [0,0])
    pygame.display.flip()
    if debug:
        pygame.display.set_caption("The Extraterrorestrial [rev %.6s...]" % version)
    else:
        pygame.display.set_caption("The Extraterrorestrial")
    game.frame = 0
    game.recording = False
    game.recorded_path = []

    game.tga_load_tiles('data/tilesets/LakeSet.png', [game.tile_w, game.tile_h], tdata)
    game.tga_load_level('data/maps/' + map_files[lvl_num], True)
    game.bounds = pygame.Rect(game.tile_w, game.tile_h,
                              (len(game.tlayer[0])-2)*game.tile_w,
                              (len(game.tlayer)-2)*game.tile_h)

    game.load_images(idata)
    game.deferred_effects = []
    game.fbi_spawns = []

    game.run_codes(cdata[lvl_num], (0, 0, len(game.tlayer[0]), len(game.tlayer)))

    game.music = pygame.mixer.music
    music_to_play = lvl_num % len(music_files)
    game.music.load('data/music/' + music_files[music_to_play])
    game.music.play(-1)

    game.agents = 0
    game.max_fbi_agents = fbi_limit[lvl_num]
    game.quit = 0
    game.pause = 0
    game.game_over = False
    game.debug = debug

    game.player.view_me(game)
    game.player.setup_required_trophies(game)

    return game

def run():
    initialize_modules()
    pygame.mixer.set_num_channels(16)

    splash_image = pygame.image.load('data/screens/splash.png')
    death_image  = pygame.image.load('data/screens/GameOverMan.png')
    load_image   = pygame.image.load('data/screens/Loading.png')

    width = 640
    height = 480

    screen    = pygame.display.set_mode([width, height], pygame.DOUBLEBUF)

    if not debug:
        splashscreen.fade_in(screen, splash_image)
        pygame.time.wait(500)
        splashscreen.fade_out(screen, splash_image)
    
        while do_menu(screen, width, height) != 0:
            pass
        
        level = 0
    else:
        level = 1
        
    game  = load_level(level, screen, width, height, load_image)

    t = pygame.time.Clock()

    game.quit = 0
    game.paint(game.screen)

    game.pause = 0

    text = pygame.font.Font('data/fonts/Another_.ttf', 36)
    text_sm = pygame.font.Font('data/fonts/Another_.ttf', 16)

    game.player.view_me(game)

    direction = 0
    while not game.quit:
        t.tick(60)
        for e in pygame.event.get():
            if e.type is QUIT: game.quit = 1
            if e.type is KEYDOWN:
                if e.key == K_ESCAPE:
                    while do_menu(screen, width, height, True) != 0:
                        pass
                if e.key == K_F10:
                    flags = pygame.DOUBLEBUF
                    if not game.fullscreen:
                        flags |= pygame.FULLSCREEN
                        game.fullscreen = True
                    game.screen = pygame.display.set_mode([game.view.w, game.view.h], flags)
                if e.key == K_SPACE: game.player.morph()
                if e.key == K_RETURN:
                     if not game.game_over:
                         game.pause = not game.pause
                     else:
                         game = load_level(level, screen, width, height, load_image)
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
            caption = 'Press enter to try again!'
            txt = text.render(caption, 1, [0, 0, 0])
            txtrect = txt.get_rect()
            txtrect.x = game.view.w / 2 - txtrect.w / 2
            txtrect.y = game.view.h / 2 - txtrect.h / 2
            game.screen.blit(txt, txtrect)
            txt = text.render(caption, 1, [255, 255, 255])
            txtrect.x += 2
            txtrect.y += 2
            game.screen.blit(txt, txtrect)
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

            if game.player.state == "done":
                level = (level + 1) % len(map_files)
                game.music.stop()
                game = load_level(level, screen, width, height, load_image)
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

            if debug:
                caption = "FPS %2.2f" % t.get_fps()
                txt = text.render(caption, 1, [0, 0, 0])
                game.screen.blit(txt, [1, game.view.w - txt.get_height() + 1])
                txt = text.render(caption, 1, [255, 255, 255])
                game.screen.blit(txt, [0, game.view.h - txt.get_height()])

            game.frame += 1
            pygame.display.flip()
