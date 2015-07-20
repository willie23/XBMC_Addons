menu = []
menu.append(label)
menu.append('Settings')
choice = xbmcgui.Dialog().select('PLTV', menu)

if choice == None:
    return

if choice == 0:
    #call you function
    return

if choice == 1:
    xbmcaddon.Addon('plugin.program.super.favourites').openSettings()
    return