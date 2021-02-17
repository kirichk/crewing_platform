import pyautogui
import time


MESSAGE = 'Ну привет отец'

screenWidth, screenHeight = pyautogui.size()
print(screenWidth, screenHeight)

# MACOS
# SEARCH_FIELD_X = screenWidth / 14.4
# SEARCH_FIELD_Y = screenHeight / 6.9
#
# SEARCH_RESULT_FIELD_X = screenWidth / 14.4
# SEARCH_RESULT_FIELD_Y = screenHeight / 3.6
#
# MESSAGE_FIELD_X = screenWidth / 2.88
# MESSAGE_FIELD_Y = screenHeight / 1.035
#
# SEND_FIELD_X = screenWidth / 1.3
# SEND_FIELD_Y = screenHeight / 1.035

# Windows
SEARCH_FIELD_X = screenWidth / 14.4
SEARCH_FIELD_Y = screenHeight / 5.5

SEARCH_RESULT_FIELD_X = screenWidth / 14.4
SEARCH_RESULT_FIELD_Y = screenHeight / 3

MESSAGE_FIELD_X = screenWidth / 2.88
MESSAGE_FIELD_Y = screenHeight / 1.1

SEND_FIELD_X = screenWidth / 1.28
SEND_FIELD_Y = screenHeight / 1.08

# text_to_send = pyautogui.prompt(text='Введите текст для рассылки сообщений',
#                       title='Ввод текста',
#                       default='Привет')

def get_names_from_vcf():
    with open('test.vcf', mode='r') as vcf:
        data = vcf.read().split('\n')
        result = []
        for item in data:
            if item[:2] == 'FN':
                result.append(item.split(':')[1])
        return result


def sending_funnel(contacts: list):
    print('Program started, you have 5 seconds to open Viber on a fullscreen')
    time.sleep(5)
    for contact in contacts:
        pyautogui.click(SEARCH_FIELD_X, SEARCH_FIELD_Y)
        for letter in contact:
            pyautogui.press(letter)
        time.sleep(2)
        pyautogui.click(SEARCH_RESULT_FIELD_X, SEARCH_RESULT_FIELD_Y)
        time.sleep(1)
        pyautogui.click(MESSAGE_FIELD_X, MESSAGE_FIELD_Y)
        pyautogui.write('Test')
        time.sleep(1)
        pyautogui.click(SEND_FIELD_X, SEND_FIELD_Y)
        time.sleep(10)


if __name__ == '__main__':
    contacts = get_names_from_vcf()
    sending_funnel(['Crewing'])
