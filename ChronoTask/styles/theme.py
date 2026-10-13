THEMES = {
    "default": {"window":"#151D2B","surface":"#253349","surface_alt":"#182133","input":"#202C40","border":"#40506C","border_soft":"#34425D","accent":"#3E8AC4","accent_hover":"#59B7FF","text":"#F4F7FF","muted":"#8291AE"},
    "lavender": {"window":"#11121F","surface":"#302E46","surface_alt":"#191A2B","input":"#222238","border":"#625D86","border_soft":"#454263","accent":"#9B7BFF","accent_hover":"#B79FFF","text":"#F7F4FF","muted":"#AAA5C8"},
    "tokyo_night": {"window":"#111629","surface":"#293354","surface_alt":"#19213A","input":"#202945","border":"#4E618E","border_soft":"#37486E","accent":"#6E9CFF","accent_hover":"#8EB7FF","text":"#F0F4FF","muted":"#95A8CF"},
    "nord": {"window":"#1E242D","surface":"#384351","surface_alt":"#282F39","input":"#303946","border":"#607080","border_soft":"#485765","accent":"#88C0D0","accent_hover":"#A2D5E1","text":"#ECEFF4","muted":"#ADB9C6"},
    "midnight_dusk": {"window":"#18171D","surface":"#30242C","surface_alt":"#211C22","input":"#292229","border":"#60434F","border_soft":"#46343C","accent":"#E34B78","accent_hover":"#F16B91","text":"#FFF2F6","muted":"#B89CA7"},
    "tidal_wave": {"window":"#07182E","surface":"#16446D","surface_alt":"#0B2744","input":"#103653","border":"#34739A","border_soft":"#235A7C","accent":"#55C7F2","accent_hover":"#83DAF8","text":"#EEFAFF","muted":"#9FC5D9"},
    "teal": {"window":"#111C1C","surface":"#304748","surface_alt":"#1B292A","input":"#223637","border":"#4B7473","border_soft":"#355B5B","accent":"#53D1C7","accent_hover":"#7FE1D8","text":"#F0FFFD","muted":"#A1C3BF"},
    "yotsuba": {"window":"#191512","surface":"#463732","surface_alt":"#28211D","input":"#342923","border":"#70574E","border_soft":"#554039","accent":"#FFAA8B","accent_hover":"#FFC3AD","text":"#FFF5F0","muted":"#C6ADA4"},
    "monochrome": {"window":"#111111","surface":"#262626","surface_alt":"#1A1A1A","input":"#202020","border":"#707070","border_soft":"#454545","accent":"#666666","accent_hover":"#808080","text":"#F5F5F5","muted":"#B8B8B8"},
}

THEME_LABELS = {
    "default":"Default", "lavender":"Lavender", "tokyo_night":"Tokyo Night", "nord":"Nord",
    "midnight_dusk":"Midnight Dusk", "tidal_wave":"Tidal Wave", "teal":"Teal & Turquoise",
    "yotsuba":"Yotsuba", "monochrome":"Monochrome",
}


def palette(name):
    return THEMES.get(name, THEMES["default"])