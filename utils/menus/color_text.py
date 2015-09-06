__author__ = 'Grishnak'
import libtcodpy as libtcod


def color_text(text,color_f=None,color_b=None,game=None):
##============================================================================
    #changed to not use color codes, as the items were all colored the same
    #this gives the intended effect
    #txt = text.capitalize()
    txt =text
    if color_f:
        rf,gf,bf = color_f
        #make sure none of the rgb vlaues are 0
        if rf == 0:rf=1
        if gf == 0:gf=1
        if bf == 0:bf=1
    if color_b:
        rb,gb,bb = color_b
        #make sure none of the rgb vlaues are 0
        if rb == 0:rb=1
        if gb == 0:gb=1
        if bb == 0:bb=1
    ##if text is colored and we just need background changed (highlighting)
    ##Cant just change the background color here. not working for some stupid reason
    if not color_f and color_b:
        return '%c%c%c%c%s%c'%(libtcod.COLCTRL_BACK_RGB,rb,gb,bb,txt,libtcod.COLCTRL_STOP)
    if color_f and not color_b:
        return '%c%c%c%c%s%c'%(libtcod.COLCTRL_FORE_RGB,rf,gf,bf,txt,libtcod.COLCTRL_STOP)
    if color_f and color_b:
        return "%c%c%c%c%c%c%c%c%s%c"%(libtcod.COLCTRL_FORE_RGB,rf,gf,bf,
            libtcod.COLCTRL_BACK_RGB,rb,gb,bb,txt,libtcod.COLCTRL_STOP)