__author__ = 'Grishnak'


def zombie_template(base_creature):
    base_creature.alignment = "neutral evil"
    base_creature.type = "undead"
    base_creature.racial_hd[1] = 8

    s = base_creature.size
    if s == "small":
        base_creature.natural_ac += 1
        base_creature.racial_hd[0] += 1
    elif s == "medium":
        base_creature.natural_ac += 2
        base_creature.racial_hd[0] += 1
    elif s == "large":
        base_creature.natural_ac += 3
        base_creature.racial_hd[0] += 2
    elif s == "huge":
        base_creature.natural_ac += 4
        base_creature.racial_hd[0] += 4
    elif s == "gargantuan":
        base_creature.natural_ac += 7
        base_creature.racial_hd[0] += 6
    elif s == "colossal":
        base_creature.natural_ac += 11
        base_creature.racial_hd[0] += 10
    base_creature.calculate_hp(bonus=base_creature.charisma)

    base_creature.fort_save += (base_creature.final_hd * 1.33)
    base_creature.ref_save  += (base_creature.final_hd * 1.33)
    base_creature.will_save += (base_creature.final_hd * 1.5)
    base_creature.strength += 2
    base_creature.dexterity -= 2
    base_creature.wisdom = 10
    base_creature.charisma = 10
    base_creature.bab *= 1.75
    base_creature.feats = []
    ## add toughness feat here

    return base_creature


def fast_zombie(base_creature):
    base_creature =  zombie_template(base_creature)
    base_creature.speed += 10
    ##remove damage reduction.
    ##remove staggered quality
    ##add quick strikes special attack
    base_creature.dexterity += 4 # to offset th e -2 at zombie creation
    return base_creature

