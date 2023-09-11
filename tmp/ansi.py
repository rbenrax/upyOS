"""
Displays ANSI escape sequences

(c)2023/07 Krzysztof Krystian Jankowski
Homepage: https://smol.p1x.in/os/
"""

class Ansi:
    def __init__(self):
        self.text_attributes = {
            "Bold": "\033[1m",
            "Faint": "\033[2m",
            "Underline": "\033[4m",
            "Blink": "\033[5m",
            "Reverse video": "\033[7m",
            "Conceal": "\033[8m",
            "Crossed-out": "\033[9m",
        }

        self.text_colors = {
            "Black": "\033[30m",
            "Red": "\033[31m",
            "Green": "\033[32m",
            "Yellow": "\033[33m",
            "Blue": "\033[34m",
            "Magenta": "\033[35m",
            "Cyan": "\033[36m",
            "White": "\033[37m",
        }

        self.background_colors = {
            "Black": "\033[40m",
            "Red": "\033[41m",
            "Green": "\033[42m",
            "Yellow": "\033[43m",
            "Blue": "\033[44m",
            "Magenta": "\033[45m",
            "Cyan": "\033[46m",
            "White": "\033[47m",
        }

    def list_sequences(self, title, sequences):
        print(f"\033[0;1m{title}\033[0m\n")
        for name, code in sequences.items():
            print(f"{code}{name}\t\t{code}\033[0m")
        self.reset_attributes()

    def reset_attributes(self):
        print("\033[0m")

    def run(self, argument=""):
        print("\n\033[1mANSI Escape Sequences\n")
        print("\033[0mReset all attributes\t\\033[0m\n")

        self.list_sequences("Text Attributes", self.text_attributes)
        self.list_sequences("Text Colors", self.text_colors)
        self.list_sequences("Background Colors", self.background_colors)
        
        
if __name__ == '__main__':
    ansi = Ansi()
    ansi.run()
