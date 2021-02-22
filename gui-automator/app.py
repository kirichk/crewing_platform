import pyautogui
import time
import platform
from settings import platform_settings



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
        a = pyautogui.locateAllOnScreen(image='img.png',
                                       region=(TOP_LEFT_CONTACT_FIELD_Y,
                                               TOP_LEFT_CONTACT_FIELD_X,
                                               CONTACT_FIELD_WEIGHT,
                                               CONTACT_FIELD_HEIGHT))
        print(a)
        time.sleep(2)
        pyautogui.moveTo(BOTTOM_LEFT_CONTACT_FIELD_X, BOTTOM_LEFT_CONTACT_FIELD_Y)
        # pyautogui.click(SEARCH_RESULT_FIELD_X, SEARCH_RESULT_FIELD_Y)
        # time.sleep(1)
        # pyautogui.click(MESSAGE_FIELD_X, MESSAGE_FIELD_Y)
        # pyautogui.write('Test')
        # time.sleep(1)
        # pyautogui.click(SEND_FIELD_X, SEND_FIELD_Y)
        # time.sleep(10)


if __name__ == '__main__':
    locals().update(platform_settings())
    contacts = get_names_from_vcf()
    sending_funnel(['Dataforest'])
