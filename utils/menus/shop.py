__author__ = 'Grishnak'
from button import *
from check_box import *
from color_text import *
from dialog_box import *
import libtcodpy as libtcod


def shop(con, player, game, container=None, bg=None, header=None, width=80, height=50, splash=False):
    """
    TODO:
        Make sure you cannot buy items if it were to put you over inventory limit - Done
        Attach this to a shopkeeper to control splash and inventory.
        Add a buyback screen to buy back things sold by accident

    :param con: Destination Console (not used atm)
    :param player: The Player Object
    :param game: The main game object
    :param container: The contents of the store
    :param bg: The background image to use
    :param header: The title of the store
    :param width: width of the shop
    :param height: height of the shop
    :param splash: Whether or not to display the splash screen
    :return: Nothing
    """
    if bg:
        dark_bg = game.gEngine.image_load(bg)
        bg = game.gEngine.image_load(bg)
        w, h = game.gEngine.image_get_size(dark_bg)
        for y in range(w):
            for x in range(h):
                col = game.gEngine.image_get_pixel(dark_bg, y, x)
                col = libtcod.color_lerp(col, libtcod.black, 0.9)
                #col = libtcod.color_lerp(col, libtcod.light_azure, 0.2)
                r, g, b = col
                game.gEngine.image_put_pixel(dark_bg, y, x, r, g, b)

    shop_height = 28
    compare_height = height - shop_height
    s_options = []
    s_gold = []
    s_size = 0
    if container:
        for obj in container:
            obj_text = color_text(obj.name.capitalize(), obj.color)
            ob_value = color_text(obj.item.value, libtcod.gold)
            ob_value = '(%s)' % ob_value
            s_gold.append(ob_value)
            opt = '[%s] ' % obj_text
            s_options.append(opt)
            if len(obj.name)+2 > s_size:
                s_size = len(obj.name)+2
    r, g, b = libtcod.white
    compare_y = shop_height

    inventory_window = game.gEngine.console_new(width/2, height)
    game.gEngine.console_set_default_foreground(inventory_window, r, g, b)
    game.gEngine.console_print_frame(inventory_window, 0, 0, width/2, height, True)

    shop_window = game.gEngine.console_new(width/2, shop_height)
    game.gEngine.console_set_default_foreground(shop_window, r, g, b)
    game.gEngine.console_print_frame(shop_window, 0, 0, width/2, shop_height, True)

    compare_window = game.gEngine.console_new(width/2, compare_height)
    game.gEngine.console_set_default_foreground(compare_window, r, g, b)
    game.gEngine.console_print_frame(compare_window, 0, 0, width/2, compare_height, True)

    i_check_boxes = []
    s_check_boxes = []

    exit_button = Button(label='Exit', game=game, x_pos=(width/2)-9, y_pos=height-6,
                         window=inventory_window, dest_x=width/2, dest_y=0)

    sell_button = Button(label='Sell', game=game, x_pos=1, y_pos=height-6,
                         window=inventory_window, dest_x=width/2, dest_y=0)

    buy_button = Button(label='Buy', game=game, x_pos=1, y_pos=compare_height-6,
                        window=compare_window, dest_x=0, dest_y=compare_y)

    if len(player.fighter.inventory) == 0:
        inventory_items = ['Inventory is empty.']
    else:
        inventory_items = []
        for x in range(len(player.fighter.inventory)):
            i_check_boxes.append(CheckBox(x=1, y=x+1))
            inventory_items.append(color_text(player.fighter.inventory[x].name.capitalize(),player.fighter.inventory[x].color))
    for x in range(len(container)):
        s_check_boxes.append(CheckBox(x=1, y=x+1))

    i_header = 'Inventory'
    i_header_size = len(i_header)
    i_header_pos = (width/4)-(i_header_size/2)

    if header:
        s_header = header
    else:
        s_header = 'Shop'
    s_header_size = len(s_header)
    s_header_pos = (width/4) - (s_header_size/2)

    c_header = 'Compare/Examine'
    c_header_size = len(c_header)
    c_header_pos = (width/4) - (c_header_size/2)

    key = libtcod.console_check_for_keypress()
    mouse = libtcod.mouse_get_status()
    current_selection = 0
    s_current_selection = 0
    i_master_check = CheckBox(1, 30, "Check/Uncheck All")
    s_master_check = CheckBox(1, 26, "Check/Uncheck All")
    fade = 1
    if splash:
        splash_screen = game.gEngine.console_new(width, height)
    while key.vk != libtcod.KEY_ESCAPE:
        game.gEngine.console_flush()
        # get input just after flush
        key = libtcod.console_check_for_keypress(True)
        mouse = libtcod.mouse_get_status()
        exit_input = exit_button.display(mouse)
        sell_input = sell_button.display(mouse)
        buy_input = buy_button.display(mouse)

        game.gEngine.console_blit(inventory_window, 0, 0, width/2, height, 0, (width/2), 0, 1.0, 1.0)
        game.gEngine.console_blit(shop_window, 0, 0, width/2, shop_height, 0, 0, 0, 1.0, 1.0)
        game.gEngine.console_blit(compare_window, 0, 0, width/2, compare_height, 0, 0, compare_y, 1.0, 1.0)
        if splash:
            if bg:
                if fade > 0:
                    game.gEngine.console_blit(splash_screen, 0, 0, width, height, 0, 0, 0, fade, fade)
                    game.gEngine.image_blit_2x(bg, splash_screen, 0, 0, 0, 0)
                    fade -= 0.045
                else:
                    fade = 0
        game.gEngine.console_clear(inventory_window)
        game.gEngine.console_clear(shop_window)
        game.gEngine.console_clear(compare_window)

        # set up draw screen
        r, g, b = libtcod.white

        # ========================================================================
        # print inventory
        # ========================================================================
        if bg:
            game.gEngine.image_blit_2x(dark_bg, inventory_window, 0, 0, width, 0)
        game.gEngine.console_set_default_foreground(inventory_window, r, g, b)
        game.gEngine.console_print_frame(inventory_window, 0, 0, width/2, height, False)
        game.gEngine.console_print(inventory_window, i_header_pos, 0, i_header)
        if len(player.fighter.inventory) > 0:
            letter_index = ord('a')
            y = 1
            for i in range(len(inventory_items)):
                text = '  (' + chr(letter_index) + ') ' + inventory_items[i]
                if current_selection == y - 1:
                    r, g, b = libtcod.color_lerp(player.fighter.inventory[i].color, libtcod.blue, 0.5)
                    game.gEngine.console_set_default_background(inventory_window, r, g, b)
                else:
                    game.gEngine.console_set_default_background(inventory_window, 0, 0, 0)
                game.gEngine.console_print_ex(inventory_window, 1, y, libtcod.BKGND_SET, libtcod.LEFT, text)
                y += 1
                letter_index += 1
        game.gEngine.console_set_default_background(inventory_window, 0, 0, 0)
        game.gEngine.console_print(inventory_window, 1, 31, 'Gold: ' + color_text(str(player.fighter.money), libtcod.gold))
        r, g, b = libtcod.white

        # ========================================================================
        # Print Shop Window
        # ========================================================================
        if bg:
            game.gEngine.image_blit_2x(dark_bg, shop_window, 0, 0)
        game.gEngine.console_set_default_foreground(shop_window, r, g, b)
        game.gEngine.console_print_frame(shop_window, 0, 0, width/2, shop_height, False)
        game.gEngine.console_print(shop_window, s_header_pos, 0, s_header)
        if len(s_options) > 0:
            letter_index = ord('0')
            y = 1
            for i in range(len(s_options)):
                text = '  (' + chr(letter_index) + ') ' + s_options[i]
                if s_current_selection == y -1:
                    rr, gg, bb = libtcod.color_lerp(container[i].color, libtcod.blue, 0.5)
                    game.gEngine.console_set_default_background(shop_window, rr, gg, bb)
                else:
                    game.gEngine.console_set_default_background(shop_window, 0, 0, 0)
                game.gEngine.console_print_ex(shop_window, 1, y, libtcod.BKGND_SET, libtcod.LEFT, text)
                game.gEngine.console_print_ex(shop_window, s_size+10, y, libtcod.BKGND_SET, libtcod.RIGHT, s_gold[i])
                y += 1
                letter_index += 1
            game.gEngine.console_set_default_background(inventory_window, 0, 0, 0)
            r, g, b = libtcod.white

        # ========================================================================
        # Print Compare Window
        # ========================================================================
        if bg:
            game.gEngine.image_blit_2x(dark_bg, compare_window, 0, 0, sx=0, sy=compare_y*2)
        game.gEngine.console_set_default_foreground(compare_window, r, g, b)
        game.gEngine.console_print_frame(compare_window, 0, 0, width/2, compare_height, False)
        game.gEngine.console_print(compare_window, c_header_pos, 0, c_header)

        # ========================================================================
        # handle mouse input
        # ========================================================================
        #Render check boxes
        #inventory check boxes
        i_mc = i_master_check.update(mouse, width)
        i_master_check.render(inventory_window, game)
        sell_value = 0
        if not i_mc:
            for box in i_check_boxes:
                box.update(mouse, width)
                box.render(inventory_window, game)
                if box.get_checked():
                    sell_value += player.fighter.inventory[box.y-1].item.value/2
        else:
            for box in i_check_boxes:
                box.set_checked(i_master_check.get_checked())
                box.render(inventory_window, game)
                if box.get_checked():
                    sell_value += player.fighter.inventory[box.y-1].item.value/2
        game.gEngine.console_print(inventory_window, 1, 32, 'Sell Value: ' + color_text(str(sell_value), libtcod.gold))

        #Shop check boxes
        s_mc = s_master_check.update(mouse)
        s_master_check.render(shop_window, game)
        buy_value = 0
        if not s_mc:
            for box in s_check_boxes:
                box.update(mouse)
                box.render(shop_window, game)
                if box.get_checked():
                    buy_value += container[box.y-1].item.value
        else:
            for box in s_check_boxes:
                box.set_checked(s_master_check.get_checked())
                box.render(shop_window, game)
                if box.get_checked():
                    buy_value += container[box.y-1].item.value
        game.gEngine.console_print(shop_window, 1, 25, 'Buy Value: ' + color_text(str(buy_value), libtcod.gold))

        # Inventory input
        if mouse.cx >= width/2+3 and mouse.cx < width-2:  # inventory screen dims
            if (mouse.cy-1) < len(player.fighter.inventory) and mouse.cy-1 >= 0:
                item = player.fighter.inventory[mouse.cy-1]
                current_selection = mouse.cy-1
                game.gEngine.console_set_default_background(compare_window, 0, 0, 0)
                if item.item.equipment:
                    game.gEngine.console_print_ex(compare_window, 1, 2, libtcod.BKGND_SET, libtcod.LEFT, 'Name    : ' + color_text(item.name.capitalize(), item.color))
                    game.gEngine.console_print_ex(compare_window, 1, 3, libtcod.BKGND_SET, libtcod.LEFT, 'Type    : ' + item.item.equipment.type.capitalize())
                    if item.item.equipment.type == 'melee':
                        damage = '%dd%d+%d' % (item.item.equipment.damage.nb_dices, item.item.equipment.damage.nb_faces, item.item.equipment.damage.addsub )
                        game.gEngine.console_print_ex(compare_window, 1, 4, libtcod.BKGND_SET, libtcod.LEFT, 'Damage  : ' + damage)
                        game.gEngine.console_print_ex(compare_window, 1, 5, libtcod.BKGND_SET, libtcod.LEFT, 'Accuracy: ' + str(item.item.equipment.accuracy))
                        game.gEngine.console_print_ex(compare_window, 1, 7, libtcod.BKGND_SET, libtcod.LEFT, 'Skill   : ' + item.item.equipment.damage_type)
                    else:
                        game.gEngine.console_print_ex(compare_window, 1, 4, libtcod.BKGND_SET, libtcod.LEFT, 'Armor   : ' + str(item.item.equipment.bonus))
                        game.gEngine.console_print_ex(compare_window, 1, 5, libtcod.BKGND_SET, libtcod.LEFT, 'Penalty : ' + str(item.item.equipment.penalty))
                        game.gEngine.console_print_ex(compare_window, 1, 7, libtcod.BKGND_SET, libtcod.LEFT, 'Location: ' + item.item.equipment.location.capitalize())
                    game.gEngine.console_print_ex(compare_window, 1, 6, libtcod.BKGND_SET, libtcod.LEFT, 'Value   : ' + str(item.item.value))
                if item.item.spell:
                    game.gEngine.console_print_ex(compare_window, 1, 2, libtcod.BKGND_SET, libtcod.LEFT, 'Name  : ' + color_text(item.name.capitalize(), item.color))
                    game.gEngine.console_print_ex(compare_window, 1, 3, libtcod.BKGND_SET, libtcod.LEFT, 'Type  : ' + item.item.spell.type.capitalize())
                    game.gEngine.console_print_ex(compare_window, 1, 4, libtcod.BKGND_SET, libtcod.LEFT, 'Power : ' + str(item.item.spell.min) + '-' + str(item.item.spell.max))
                    game.gEngine.console_print_ex(compare_window, 1, 5, libtcod.BKGND_SET, libtcod.LEFT, 'Range : ' + str(item.item.spell.range))
                    game.gEngine.console_print_ex(compare_window, 1, 6, libtcod.BKGND_SET, libtcod.LEFT, 'Radius: ' + str(item.item.spell.radius))
                    game.gEngine.console_print_ex(compare_window, 1, 7, libtcod.BKGND_SET, libtcod.LEFT, 'Value : ' + str(item.item.value))
                if mouse.lbutton_pressed:
                    i_n = color_text(item.name.capitalize(), item.color)
                    price = color_text(item.item.value/2, libtcod.gold)
                    message = 'Sell %s for %s?' % (i_n, price)
                    w = len(message)+2
                    d_box = DialogBox(game, w, 10, width/4, height/2, message, type='option', con=inventory_window)
                    confirm = d_box.display_box()
                    if confirm == 1:
                        player.fighter.money += item.item.value/2
                        player.fighter.inventory.remove(item)
                        inventory_items = []
                        i_check_boxes = []
                        for x in range(len(player.fighter.inventory)):
                            i_check_boxes.append(CheckBox(x=1, y=x+1))
                            inventory_items.append(color_text(player.fighter.inventory[x].name.capitalize(), player.fighter.inventory[x].color))


        # shop input
        if mouse.cx >= 0 and mouse.cx < width/2-2:  # shop screen dims
            if (mouse.cy-1) < len(container) and mouse.cy-1 >= 0:
                item = container[mouse.cy-1]
                s_current_selection = mouse.cy-1
                game.gEngine.console_set_default_background(compare_window, 0, 0, 0)
                if item.item.equipment:
                    game.gEngine.console_print_ex(compare_window, 1, 2, libtcod.BKGND_SET, libtcod.LEFT, 'Name    : ' + color_text(item.name.capitalize(), item.color))
                    game.gEngine.console_print_ex(compare_window, 1, 3, libtcod.BKGND_SET, libtcod.LEFT, 'Type    : ' + item.item.equipment.type.capitalize())
                    if item.item.equipment.type == 'melee':
                        damage = '%dd%d+%d' % (item.item.equipment.damage.nb_dices, item.item.equipment.damage.nb_faces, item.item.equipment.damage.addsub )
                        game.gEngine.console_print_ex(compare_window, 1, 4, libtcod.BKGND_SET, libtcod.LEFT, 'Damage  : ' + damage)
                        game.gEngine.console_print_ex(compare_window, 1, 5, libtcod.BKGND_SET, libtcod.LEFT, 'Accuracy: ' + str(item.item.equipment.accuracy))
                        game.gEngine.console_print_ex(compare_window, 1, 7, libtcod.BKGND_SET, libtcod.LEFT, 'Skill   : ' + item.item.equipment.damage_type)
                    else:
                        game.gEngine.console_print_ex(compare_window, 1, 4, libtcod.BKGND_SET, libtcod.LEFT, 'Armor   : ' + str(item.item.equipment.bonus))
                        game.gEngine.console_print_ex(compare_window, 1, 5, libtcod.BKGND_SET, libtcod.LEFT, 'Penalty : ' + str(item.item.equipment.penalty))
                        game.gEngine.console_print_ex(compare_window, 1, 7, libtcod.BKGND_SET, libtcod.LEFT, 'Location: ' + item.item.equipment.location.capitalize())
                    game.gEngine.console_print_ex(compare_window, 1, 6, libtcod.BKGND_SET, libtcod.LEFT, 'Value   : ' + str(item.item.value))

                if item.item.spell:
                    game.gEngine.console_print_ex(compare_window, 1, 2, libtcod.BKGND_SET, libtcod.LEFT, 'Name  : ' + color_text(item.name.capitalize(), item.color))
                    game.gEngine.console_print_ex(compare_window, 1, 3, libtcod.BKGND_SET, libtcod.LEFT, 'Type  : ' + item.item.spell.type.capitalize())
                    game.gEngine.console_print_ex(compare_window, 1, 4, libtcod.BKGND_SET, libtcod.LEFT, 'Power : ' + str(item.item.spell.min) + '-' + str(item.item.spell.max))
                    game.gEngine.console_print_ex(compare_window, 1, 5, libtcod.BKGND_SET, libtcod.LEFT, 'Range : ' + str(item.item.spell.range))
                    game.gEngine.console_print_ex(compare_window, 1, 6, libtcod.BKGND_SET, libtcod.LEFT, 'Radius: ' + str(item.item.spell.radius))
                    game.gEngine.console_print_ex(compare_window, 1, 7, libtcod.BKGND_SET, libtcod.LEFT, 'Value : ' + str(item.item.value))
                    
                if mouse.lbutton_pressed and mouse.cx >= 3:
                    if len(player.fighter.inventory) >= 26:
                        if not item.item.check_stackable():
                            message = 'Not enough inventory space!'
                            w = len(message)+2
                            d_box = DialogBox(game, w, 10, width/2-w/2, height/2-5, message, type='dialog', con=inventory_window)
                            d_box.display_box()
                        else:
                            pass
                    elif item.item.value > player.fighter.money:
                        message = 'Not enough money!'
                        w = len(message)+2
                        d_box = DialogBox(game, w, 10, width/2-w/2, height/2-5, message, type='dialog', con=inventory_window)
                        d_box.display_box()
                        s_master_check.set_checked(False)
                        for box in s_check_boxes:
                            box.set_checked(s_master_check.get_checked())
                    else:
                        i_n = color_text(item.name.capitalize(), item.color)
                        price = color_text(item.item.value, libtcod.gold)
                        message = 'Buy %s for %s?' % (i_n, price)
                        w = len(message)+2
                        d_box = DialogBox(game, w, 10, width/4, height/2, message, type='option', con=inventory_window)
                        confirm = d_box.display_box()
                        if confirm == 1:
                            player.fighter.money -= item.item.value
                            player.fighter.inventory.append(item)
                            container.remove(item)
                            inventory_items = []
                            i_check_boxes = []
                            for x in range(len(player.fighter.inventory)):
                                i_check_boxes.append(CheckBox(x=1, y=x+1))
                                inventory_items.append(color_text(player.fighter.inventory[x].name.capitalize(), player.fighter.inventory[x].color))
                            s_check_boxes = []
                            s_options = []
                            if container:
                                for obj in container:
                                    obj_text = color_text(obj.name.capitalize(), obj.color)
                                    ob_value = color_text(obj.item.value, libtcod.gold)
                                    ob_value = '(%s)' % ob_value
                                    s_gold.append(ob_value)
                                    opt = '[%s] ' % obj_text
                                    s_options.append(opt)
                                    if len(obj.name)+2 > s_size:
                                        s_size = len(obj.name)+2
                            for x in range(len(container)):
                                s_check_boxes.append(CheckBox(x=1, y=x+1))

        # keyboard input
        index = key.c - ord('a')
        if key:
            if key.vk == libtcod.KEY_DOWN:
                if current_selection is None:
                    current_selection = 0
                current_selection += 1
                if current_selection > len(inventory_items):
                    current_selection = 0
            if key.vk == libtcod.KEY_UP:
                if current_selection is None:
                    current_selection = 0
                current_selection -= 1
                if current_selection < 0:
                    current_selection = len(inventory_items)
        # ========================================================================
        # handle buttons
        # ========================================================================

        # ========================================================================
        # Sell Button
        # ========================================================================
        for i in sell_input:
            if i != -1:
                message = 'Sell all selected items?'
                w = len(message)+2
                d_box = DialogBox(game, w, 10, width/2-w/2, height/2-5, message, type='option', con=inventory_window)
                confirm = d_box.display_box()
                if confirm == 1:
                    d_box.destroy_box()
                    i_master_check.set_checked(False)
                    items_to_sell = []
                    for box in i_check_boxes:
                        if box.get_checked():
                            items_to_sell.append(player.fighter.inventory[box.y-1])
                    for item_to_sell in items_to_sell:
                        if item_to_sell:
                            player.fighter.money += item_to_sell.item.value/2
                            player.fighter.inventory.remove(item_to_sell)
                    i_check_boxes = []
                    inventory_items = []
                    for x in range(len(player.fighter.inventory)):
                        i_check_boxes.append(CheckBox(x=1, y=x+1))
                        inventory_items.append(color_text(player.fighter.inventory[x].name.capitalize(),
                                                          player.fighter.inventory[x].color))
                else:
                    d_box.destroy_box()

        # ========================================================================
        # buy button
        # ========================================================================
        for i in buy_input:
            if i != -1:
                n = 0
                for box in s_check_boxes:
                    if box.get_checked():
                        n += 1
                if len(player.fighter.inventory)+n > 26:
                        message = 'Not enough inventory space!'
                        w = len(message)+2
                        d_box = DialogBox(game, w, 10, width/2-w/2, height/2-5, message, type='dialog', con=inventory_window)
                        d_box.display_box()
                elif buy_value > player.fighter.money:
                    message = 'Not enough money!'
                    w = len(message)+2
                    d_box = DialogBox(game, w, 10, width/2-w/2, height/2-5, message, type='dialog', con=inventory_window)
                    d_box.display_box()
                    s_master_check.set_checked(False)
                    for box in s_check_boxes:
                        box.set_checked(s_master_check.get_checked())
                else:
                    message = 'Buy all selected items?'
                    w = len(message)+2
                    d_box = DialogBox(game, w, 10, width/2-w/2, height/2-5, message, type='option', con=inventory_window)
                    confirm = d_box.display_box()
                    if confirm == 1:
                        #d_box.destroy_box()
                        s_master_check.set_checked(False)
                        items_to_buy = []
                        for box in s_check_boxes:
                            if box.get_checked():
                                items_to_buy.append(container[box.y-1])
                        for item_to_buy in items_to_buy:
                            if item_to_buy:
                                container.remove(item_to_buy)
                                player.fighter.money -= item_to_buy.item.value
                                player.fighter.inventory.append(item_to_buy)

                        s_check_boxes = []
                        s_options = []
                        if container:
                            for obj in container:
                                obj_text = color_text(obj.name.capitalize(), obj.color)
                                ob_value = color_text(obj.item.value, libtcod.gold)
                                ob_value = '(%s)' % ob_value
                                s_gold.append(ob_value)
                                opt = '[%s] ' % obj_text
                                s_options.append(opt)
                                if len(obj.name)+2 > s_size:
                                    s_size = len(obj.name)+2
                        for x in range(len(container)):
                            s_check_boxes.append(CheckBox(x=1, y=x+1))

                        i_check_boxes = []
                        inventory_items = []
                        for x in range(len(player.fighter.inventory)):
                            i_check_boxes.append(CheckBox(x=1, y=x+1))
                            inventory_items.append(color_text(player.fighter.inventory[x].name.capitalize(),
                                                              player.fighter.inventory[x].color))
            #else:
                    d_box.destroy_box()

        # ========================================================================
        # handle exit button
        # ========================================================================

        for i in exit_input:
            if i != -1:
                key.vk = libtcod.KEY_ESCAPE
                break
    # Remember to remove consoles in reverse order of creation to avoid OOB errors
    if splash:
        game.gEngine.console_remove_console(splash_screen)
    buy_button.destroy_button()
    sell_button.destroy_button()
    exit_button.destroy_button()
    game.gEngine.console_remove_console(compare_window)
    game.gEngine.console_remove_console(shop_window)
    game.gEngine.console_remove_console(inventory_window)

    return