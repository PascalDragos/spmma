import enum

class MessageType(enum.Enum):
    I2C_MESSAGE = 1
    I2S_MESSAGE = 2
    BTN_MESSAGE = 3

class ButtonType(enum.Enum):
    SLEEP = 0
    NEXT = 1