from src.ctOS.start.init import demo
from src.ctOS.start.start import start
from src.ctOS.help import help
import sys
from dotenv import load_dotenv
from src.tranquillity import init as tranquillity
from src.ctOS.music.music import music_command
from src.ctOS.music.init_token import init
load_dotenv()

def main():
    nb = len(sys.argv)
    
    if nb <= 1:
        help()
        return
    if sys.argv[1] == "--test":
        tranquillity()
        return
    if sys.argv[1] == "--music":
        music_command()
        return
    if sys.argv[1] == "--init":
        init()
        return
    if sys.argv[1] == "--start":
        demo()
        start()
        return
    if sys.argv[1] == "--help" or "-h":
        help()
    else:
        return 84
main()