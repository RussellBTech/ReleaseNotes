import random

# Define a list of ASCII smiley faces
ascii_kirbys = [
    "(>'-')>",
    "<('-'<)",
    "^('-')^",
    "v('-')v",
    "(>'-')^",
    "^('-'<)",
    "(^'-')^",
    "v('-')v",
    "(>'-')v",
    "v('-'<)",
    "(^'-')>",
    "<('-'^)",
    "(>'-')<",
    ">(^-^)<",
    "<(^-^)>",
    "<(^-^<)",
    "(>^-^)>",
    "<(^-^)^",
    "^(^-^<)",
    "(>^-^)^",
    "^(^-^)>"
]

def get_random_kirby():
    # Randomly select a smiley from the list
    selected_smiley = random.choice(ascii_kirbys)
    return selected_smiley

# Function to generate a line of random kirbys
def get_kirby_line():
    kirby_line = ""
    while len(kirby_line) < 50:
        kirby_line += get_random_kirby() + " "
    return kirby_line.rstrip()