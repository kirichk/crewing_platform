import pyautogui
import platform


screenWidth, screenHeight = pyautogui.size()


def platform_settings():
    if platform.system() == 'Darwin':
        # MACOS
        return {
            'SEARCH_FIELD_X': screenWidth / 14.4,
            'SEARCH_FIELD_Y': screenHeight / 6.9,
            'SEARCH_RESULT_FIELD_X': screenWidth / 14.4,
            'SEARCH_RESULT_FIELD_Y': screenHeight / 3.6,
            'MESSAGE_FIELD_X': screenWidth / 2.88,
            'MESSAGE_FIELD_Y': screenHeight / 1.035,
            'SEND_FIELD_X': screenWidth / 1.3,
            'SEND_FIELD_Y': screenHeight / 1.035,
            'TOP_LEFT_CONTACT_FIELD_X': 0,
            'TOP_LEFT_CONTACT_FIELD_Y': int(screenWidth / 6.15),
            'BOTTOM_LEFT_CONTACT_FIELD_X': screenWidth / 4.8,
            'BOTTOM_LEFT_CONTACT_FIELD_Y': screenWidth / 4.8,
            'CONTACT_FIELD_WEIGHT': int(screenWidth / 4.8),
            'CONTACT_FIELD_HEIGHT': int(screenWidth / 6.15 - screenWidth / 4.8)
        }
    return {
        'SEARCH_FIELD_X': screenWidth / 14.4,
        'SEARCH_FIELD_Y': screenHeight / 5.5,
        'SEARCH_RESULT_FIELD_X': screenWidth / 14.4,
        'SEARCH_RESULT_FIELD_Y': screenHeight / 3,
        'MESSAGE_FIELD_X': screenWidth / 2.88,
        'MESSAGE_FIELD_Y': screenHeight / 1.1,
        'SEND_FIELD_X': screenWidth / 1.28,
        'SEND_FIELD_Y': screenHeight / 1.08,
        'TOP_LEFT_CONTACT_FIELD_X': 0,
        'TOP_LEFT_CONTACT_FIELD_Y': screenWidth / 6.15,
        'BOTTOM_LEFT_CONTACT_FIELD_X': screenWidth / 4.8,
        'BOTTOM_LEFT_CONTACT_FIELD_Y': screenWidth / 4.8,
    }
