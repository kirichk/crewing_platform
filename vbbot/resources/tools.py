"""Additional functions for Viber bot."""

def keyboard_consctructor(items: list) -> dict:
    """Pasting infromation from list of items to keyboard menu template."""
    keyboard = {
        "DefaultHeight": False,
        "BgColor": "#FFFFFF",
        "Type": "keyboard",
        "Buttons": [{
                "Columns": 3,
                "Rows": 1,
                "BgColor": "#e6f5ff",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": item[0],
                "ReplyType": "message",
                "Text": item[1]
        } for item in items]
    }
    return keyboard
