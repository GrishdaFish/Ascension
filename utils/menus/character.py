__author__ = 'Grishnak'
from button import *
from check_box import *
from color_text import *
from dialog_box import *
import libtcodpy as libtcod


def get_centered_text(text, width):
    head = text
    s = len(head)
    pos = width - s/2
    return head, pos

def character_info(con, width, height, game, x=0, y=0):
    skill_window = game.gEngine.console_new(width/2, height)
    skill_window_y_pos = width/2
    s_header, s_pos = get_centered_text("Skills", width/4)

    char_window = game.gEngine.console_new(width/2, height/2)
    c_header, c_pos = get_centered_text(("%s's Skills and Abilities" % game.player.name), width/4)

    skill_desc_window = game.gEngine.console_new(width/2, height/2)
    skill_desc_pos = height/2
    d_header, d_pos = get_centered_text("Description", width/4)

    exit_button = Button(label='Exit', game=game, x_pos=(width/2)-9, y_pos=height-6,
                         window=skill_window, dest_x=width/2, dest_y=0)
    current_selection = 0
    key = libtcod.console_check_for_keypress()
    while key.vk != libtcod.KEY_ESCAPE:
        game.gEngine.console_flush()
        # get input just after flush
        key = libtcod.console_check_for_keypress(True)
        mouse = libtcod.mouse_get_status()
        exit_input = exit_button.display(mouse)

        game.gEngine.console_blit(char_window, 0, 0, width/2, height/2, 0, 0, 0, 1.0, 1.0)
        game.gEngine.console_blit(skill_window, 0, 0, width/2, height, 0, skill_window_y_pos, 0, 1.0, 1.0)
        game.gEngine.console_blit(skill_desc_window, 0, 0, width/2, height/2, 0, 0, skill_desc_pos, 1.0, 1.0)

        game.gEngine.console_clear(char_window)
        game.gEngine.console_clear(skill_desc_window)
        game.gEngine.console_clear(skill_window)

        #Draw Character info
        r, g, b = libtcod.white
        game.gEngine.console_set_default_foreground(char_window, r, g, b)
        game.gEngine.console_print_frame(char_window, 0, 0, width/2, height/2, True)
        game.gEngine.console_print(char_window, c_pos, 0, c_header)
        game.gEngine.console_print(char_window, 1, 1, 'Name: %s' % game.player.name)
        game.gEngine.console_print(char_window, 1, 2, 'Hit Points: %d/%d' % (game.player.fighter.hp, game.player.fighter.max_hp))

        game.gEngine.console_print(char_window, 1, 4, 'Level: %d' % game.player.fighter.level)
        game.gEngine.console_print(char_window, 1, 5, 'To Next Level: %d' % game.player.fighter.xp_to_next_level)

        s = color_text(str(game.player.fighter.stats[0]), libtcod.light_gray)
        d = color_text(str(game.player.fighter.stats[1]), libtcod.light_gray)
        i = color_text(str(game.player.fighter.stats[2]), libtcod.light_gray)
        c = color_text(str(game.player.fighter.stats[3]), libtcod.light_gray)
        game.gEngine.console_print(char_window, 1, 7, 'Stats: Str [%s], Dex [%s]' % (s, d))
        game.gEngine.console_print(char_window, 1, 8, '       Int [%s], Con [%s]' % (i, c))

        bonus = color_text(str(game.player.fighter.armor_bonus), libtcod.green)
        bonus2 = color_text('10 +%d' % game.player.fighter.armor_bonus, libtcod.green)
        game.gEngine.console_print(char_window, 1, 10, 'Bonus to Armor Roll  : [%s](%s) ' % (bonus, bonus2))

        penalty = color_text(str(game.player.fighter.armor_penalty), libtcod.red)
        penalty2 = color_text('1d20 -%d' % game.player.fighter.armor_penalty, libtcod.red)
        game.gEngine.console_print(char_window, 1, 11, 'Penalty to Dodge Roll: [%s](%s)' % (penalty, penalty2))

        speed = color_text(str(game.player.fighter.speed), libtcod.light_gray)
        game.gEngine.console_print(char_window, 1, 13, 'Turn Speed: [%s]' % speed)

        r, g, b = libtcod.white
        game.gEngine.console_set_default_foreground(skill_window, r, g, b)
        game.gEngine.console_print_frame(skill_window, 0, 0, width/2, height, True)
        game.gEngine.console_print(skill_window, s_pos, 0, s_header)
        t, p = get_centered_text('Unspent Skill Points: [%d]' % game.player.fighter.unused_skill_points, width/4)
        game.gEngine.console_print(skill_window, p, 1, t)

        y = 2
        letter_index = ord('a')
        skill_max = 5
        for skill in game.player.fighter.skills:
            s_name = skill.get_name()
            s_bonus = skill.get_bonus()
            s_index = chr(letter_index)
            col = libtcod.white
            if s_bonus == skill_max:
                s_name = color_text(s_name, libtcod.green)
                s_bonus = color_text(str(s_bonus), libtcod.green)
                s_index = color_text(s_index, libtcod.green)
                col = libtcod.green
            elif s_bonus < skill_max and s_bonus > 0:
                s_name = color_text(s_name, libtcod.light_gray)
                s_bonus = color_text(str(s_bonus), libtcod.lighter_gray)
                s_index = color_text(s_index, libtcod.lighter_gray)
                col = libtcod.lighter_gray
            elif s_bonus == 0:
                s_name = color_text(s_name, libtcod.dark_gray)
                s_bonus = color_text(str(s_bonus), libtcod.dark_gray)
                s_index = color_text(s_index, libtcod.dark_gray)
                col = libtcod.dark_gray
            else:
                s_name = color_text(s_name, libtcod.red)
                s_bonus = color_text(str(s_bonus), libtcod.red)
                s_index = color_text(s_index, libtcod.red)
                col = libtcod.red
            text = '(%s) %s: [%s]' % (s_index, s_name, s_bonus)
            game.gEngine.console_print(skill_window, 1, y, text)
            if current_selection == y-2:
                r, g, b = libtcod.color_lerp(col, libtcod.blue, 0.5)
                game.gEngine.console_set_default_background(skill_window, r, g, b)
            else:
                game.gEngine.console_set_default_background(skill_window, 0, 0, 0)


            game.gEngine.console_print_ex(skill_window, 1, y,libtcod.BKGND_SET, libtcod.LEFT, text)
            y += 1
            letter_index += 1
        game.gEngine.console_set_default_background(skill_window, 0, 0, 0)

        r, g, b = libtcod.white
        game.gEngine.console_set_default_foreground(skill_desc_window, r, g, b)
        game.gEngine.console_print_frame(skill_desc_window, 0, 0, width/2, height/2, True)
        game.gEngine.console_print(skill_desc_window, d_pos, 0, d_header)

        #mouse input
        if mouse.cx >= width/2 +3:
            if mouse.cy-2 < len(game.player.fighter.skills) and mouse.cy >= 0:
                current_selection = mouse.cy-2
                skill = game.player.fighter.skills[current_selection]
                desc = color_text(skill.get_description(), libtcod.light_gray)
                desc = "Skill Description: %s" % desc
                cat = color_text(skill.get_category(), libtcod.light_gray)
                cat = "Skill Category   : %s" % cat
                bonus = skill.get_bonus()
                name = skill.get_name()
                if bonus == skill_max:
                    bonus = color_text(str(bonus), libtcod.green)
                    name = color_text(name, libtcod.green)
                elif bonus < skill_max and bonus > 0:
                    bonus = color_text(str(bonus), libtcod.lighter_gray)
                    name = color_text(name, libtcod.lighter_gray)
                elif bonus == 0:
                    bonus = color_text(str(bonus), libtcod.dark_gray)
                    name = color_text(name, libtcod.dark_gray)
                else:
                    bonus = color_text(str(bonus), libtcod.red)
                    name = color_text(name, libtcod.red)
                if skill.get_category() == 'Discipline':
                    bonus = 'Increases your (%s) to-hit rolls by [%s].' % (name, bonus)
                elif skill.get_category() == 'Weapon':
                    bonus = 'Increases your (%s) damage by [%s].' % (name, bonus)

                game.gEngine.console_print_rect(skill_desc_window, 1, 1, width/2-2, 3, desc)
                game.gEngine.console_print(skill_desc_window, 1, 5, cat)
                game.gEngine.console_print_rect(skill_desc_window, 1, 7, width/2-2, 3, bonus)
                if mouse.lbutton_pressed:
                    game.player.fighter.apply_skill_points(game.player.fighter.skills[current_selection]) # use unused player skill points

        for i in exit_input:
            if i != -1:
                key.vk = libtcod.KEY_ESCAPE
                break

    exit_button.destroy_button()
    game.gEngine.console_remove_console(skill_desc_window)
    game.gEngine.console_remove_console(char_window)
    game.gEngine.console_remove_console(skill_window)

    return None