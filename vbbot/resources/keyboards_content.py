"""Keyboards for Viber bot messages."""
from .tools import keyboard_consctructor


GO_TO_MENU_KEYBOARD = {
    "DefaultHeight": False,
    "BgColor": "#FFFFFF",
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "menu",
            "ReplyType": "message",
            "Text": "Меню"
        }
    ]
}

MENU_KEYBOARD = {
    "DefaultHeight": False,
    "BgColor": "#FFFFFF",
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "newday-menu",
            "ReplyType": "message",
            "Text": "Вакансии за день"
        },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "menu",
            "ReplyType": "message",
            "Text": "Фильтр вакансий"
        }
    ]
}


CONTROL_KEYBOARD_MENU_MORE = {
    "DefaultHeight": False,
    "BgColor": "#FFFFFF",
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "menu",
            "ReplyType": "message",
            "Text": "Меню"
        },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "newday-more",
            "ReplyType": "message",
            "Text": "Еще"
        }
    ]
}


CONTROL_KEYBOARD_MENU_BACK = {
    "DefaultHeight": False,
    "BgColor": "#FFFFFF",
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "menu",
            "ReplyType": "message",
            "Text": "Меню"
        },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "newday-back",
            "ReplyType": "message",
            "Text": "Назад"
        }
    ]
}


CONTROL_KEYBOARD_ALL = {
    "DefaultHeight": False,
    "BgColor": "#FFFFFF",
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 2,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "menu",
            "ReplyType": "message",
            "Text": "Меню"
        },
        {
            "Columns": 2,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "newday-back",
            "ReplyType": "message",
            "Text": "Назад"
        },
        {
            "Columns": 2,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "newday-more",
            "ReplyType": "message",
            "Text": "Еще"
        }
    ]
}


BACK_KEYBOARD = {
    "DefaultHeight": False,
    "BgColor": "#FFFFFF",
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "menu",
            "ReplyType": "message",
            "Text": "Меню"
        },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "newday-back",
            "ReplyType": "message",
            "Text": "Назад"
        }
    ]
}


RETURN_KEYBOARD = {
    "DefaultHeight": False,
    "BgColor": "#FFFFFF",
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "menu",
            "ReplyType": "message",
            "Text": "Меню"
        },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "newday-return",
            "ReplyType": "message",
            "Text": "Назад"
        }
    ]
}


# MENU_KEYBOARD = keyboard_consctructor(MENU_NAMES)
# SETS_ROLLS_KEYBOARD = keyboard_consctructor(SETS_ROLLS_MENU)
# GUNCANS_SUSHI_KEYBOARD = keyboard_consctructor(GUNCANS_SUSHI_MENU)
# PIZZA_SNACKS_KEYBOARD = keyboard_consctructor(PIZZA_SNACKS_MENU)
# OTHER_KEYBOARD = keyboard_consctructor(OTHER_MENU)
