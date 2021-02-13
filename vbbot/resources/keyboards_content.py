"""Keyboards for Viber bot messages."""
from .tools import keyboard_consctructor


GO_TO_MENU_BUTTONS = [("menu", "Меню", 6)]

MENU_BUTTONS = [("newday-search", "Вакансии за день", 6),
                ("menu", "Фильтр вакансий", 6)]

CONTROL_MENU_MORE_BUTTONS = [("menu", "Меню", 3),
                             ("newday-more", "Еще", 3)]

CONTROL_MENU_BACK_BUTTONS = [("menu", "Меню", 3),
                             ("newday-back", "Назад", 3)]

CONTROL_ALL_BUTTONS = [("menu", "Меню", 2),
                             ("newday-back", "Назад", 2),
                             ("newday-more", "Еще", 2)]

RETURN_BUTTONS = [("menu", "Меню", 3),
                  ("newday-return", "Назад", 3)]

FILTER_BUTTONS = [("title", "Должность", 3),
                ("salary", "Зарплата", 3),
                ("filter-reset", "Сбросить (Off)", 3),
                ("menu", "Меню", 3),
                ("filter-search", " Поиск (Off)", 6)]

GO_TO_MENU_KEYBOARD = keyboard_consctructor(GO_TO_MENU_BUTTONS)
MENU_KEYBOARD = keyboard_consctructor(MENU_BUTTONS)
CONTROL_KEYBOARD_MENU_MORE = keyboard_consctructor(CONTROL_MENU_MORE_BUTTONS)
CONTROL_KEYBOARD_MENU_BACK = keyboard_consctructor(CONTROL_MENU_BACK_BUTTONS)
CONTROL_KEYBOARD_ALL = keyboard_consctructor(CONTROL_ALL_BUTTONS)
RETURN_KEYBOARD = keyboard_consctructor(RETURN_BUTTONS)
FILTER_KEYBOARD = keyboard_consctructor(FILTER_BUTTONS)
