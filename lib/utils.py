import sys, tty, termios

COLORS = {
	'none'		: '\033[0m',
	'red'		: '\033[31m',
	'green'		: '\033[32m',
	'orange'	: '\033[33m',
	'blue'		: '\033[34m',
	'purple'	: '\033[35m',
	'cyan'		: '\033[36m',
	'lightgrey'	: '\033[37m',
	'darkgrey'	: '\033[90m',
	'lightred'	: '\033[91m',
	'lightgreen': '\033[92m',
	'yellow'	: '\033[93m',
	'lightblue'	: '\033[94m',
	'pink'		: '\033[95m',
	'lightcyan'	: '\033[96m'
}

def getch():
    """Get a single character from stdin, Unix version"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())          # Raw read
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def cprint(string, color):
	print(COLORS[color] + format(string) + COLORS['none'], end='')  