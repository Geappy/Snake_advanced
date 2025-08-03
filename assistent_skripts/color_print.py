"""script that costomices the printing for the terminal"""

class ValidColors():
    """colors that can be printed in"""
    BLACK = '\033[30m'   # 
    RED = '\033[31m'     # Errors
    GREEN = '\033[32m'   # Text
    YELLOW = '\033[33m'  # Debug
    BLUE = '\033[34m'    # 
    MAGENTA = '\033[35m' # Progress
    CYAN = '\033[36m'    # Instruction
    WHITE = '\033[37m'   # 
    RESET = '\033[0m'    # 

    VALID_COLORS = {BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE}

def custom_print(text:str = "", color: ValidColors = ValidColors.WHITE):
    """prints the given text in the given color

    Args:
        text: the text to be printed
        color: the color of the text
    """
    if color not in ValidColors.VALID_COLORS:
        raise ValueError("Invalid color")

    print(f"{color}{text}{ValidColors.RESET}")
