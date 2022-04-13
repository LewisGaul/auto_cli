# February 2018, Lewis Gaul

"""
main.py

"""

import sys

from bytearray import Buffer
from keys import *
from utils import putstr

display_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-= /"

opts = ["hello", "display", "foo", "bar", "baz", "barbaz", "exit", "x"]


def getch():
    """
    Get a keypress from stdin. This function uses msvcrt.getch(), and is
    therefore blocking - use msvcrt.kbhit() to avoid getting blocked.
    The keypress is attempted to be decoded to a regular string, and if it fails
    None will be returned.
    """
    if sys.platform.startswith("win"):
        import msvcrt

        try:
            char = msvcrt.getch()
            if char == b"\xe0":
                char = "\xe0" + msvcrt.getch().decode()
            else:
                char = char.decode()
        except UnicodeDecodeError:
            char = None
    else:
        import termios, tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return char


def prompt():
    putstr("auto_cli:$")


def get_matching_opts(start):
    return [opt for opt in opts if opt.startswith(start)]


def response(func):
    """
    Decorator for any function acting as a response to user input which prints
    a newline at the beginning and a prompt at the end.
    """

    def response_func(cmd, *args, **kwargs):
        putstr("\n")
        ret = func(str(cmd).strip(), *args, **kwargs)
        putstr("\n")
        prompt()
        return ret

    return response_func


@response
def qmark_response(cmd):
    """
    Question mark was pressed - give the appropriate response. This mainly
    involves displaying the available options.
    
    Return: True | False
        Whether the command was valid.
    """
    matching_opts = get_matching_opts(cmd)
    if matching_opts:
        for opt in matching_opts:
            putstr(opt, end="\n")
        return True
    else:
        putstr("Invalid command\n")
        return False


@response
def enter_response(cmd):
    """
    Enter was hit - perform the action corresponding to the command given.
    """
    matching_opts = get_matching_opts(cmd)
    if len(matching_opts) == 0:
        putstr("Invalid command\n")
        return
    elif len(matching_opts) > 1 and cmd not in opts:
        putstr("Ambiguous command\n")
        return
    else:
        cmd = matching_opts[0]
    if cmd == "hello":
        putstr("Hello there\n")
    elif cmd == "display":
        putstr("Quit with 'x'\n")
        output = ""
        while output not in [b"x", "x"]:
            output = getch()
            putstr(str(output), end=" ")
            # while msvcrt.kbhit():
            #     output += msvcrt.getch()
            # putstr(str(output)[2:-1], end=" ")
        putstr("\n")
    elif cmd in ["exit", "x"]:
        exit()
    else:
        putstr("No action attached to command '{}'".format(cmd))


def auto_complete(cmd):
    cmd = str(cmd).strip()
    matching_opts = get_matching_opts(cmd)
    if matching_opts:
        ret = ""
        opt1 = matching_opts[0]
        i = len(cmd)
        while len(opt1) > i and all(
            [len(opt) > i and opt[i] == opt1[i] for opt in matching_opts]
        ):
            ret += opt1[i]
            i += 1
    else:
        ret = None
    return ret


def rewrite_cmd(cmd, old_length, start):
    putstr(cmd[start:])
    if old_length > len(cmd):
        clear_chars = old_length - len(cmd)
        # Clear the characters from the end.
        putstr(clear_chars * " " + clear_chars * "\b")
    # Back to where we started.
    putstr((len(cmd) - start) * "\b")


def clear_cmd(old_length, start):
    # Back to index 0.
    putstr(start * "\b")
    # Clear old command and back to start.
    putstr(old_length * " " + old_length * "\b")


if __name__ == "__main__":
    # List of commands entered.
    recent_cmds = [""]
    cmds_index = 0

    user_input = Buffer()
    input_index = 0
    prompt()

    # Event loop.
    while True:
        char = getch()
        if char and char in display_chars:
            putstr(char)
            user_input.insert(input_index, char)
            input_index += 1
            rewrite_cmd(user_input, len(user_input) - 1, input_index)

        if char == "\r":
            ## Enter hit - do response corresponding to text entered and reset
            ##  prompt.
            user_input.strip()
            if user_input:
                enter_response(user_input)
                # Add to recent commands if not the same command twice in a row.
                if len(recent_cmds) <= 1 or str(user_input) != recent_cmds[1]:
                    recent_cmds.insert(1, str(user_input))
                user_input.clear()
            else:
                putstr("\n")
                prompt()
            input_index = 0
            cmds_index = 0

        elif char == "?":
            ## Question mark - show available options.
            # Put question mark at the end of typed line.
            putstr(user_input[input_index:] + "?")
            user_input.strip(leave_trailing_space=True)
            cmd_is_valid = qmark_response(user_input)
            # If the command was valid display it on the next line after showing
            #  the options, otherwise clear user_input but add the last command
            #  to the command history so that it can be used to correct errors.
            if cmd_is_valid:
                putstr(user_input)
            else:
                if len(recent_cmds) <= 1 or str(user_input) != recent_cmds[1]:
                    recent_cmds.insert(1, str(user_input))
                user_input.clear()
            input_index = len(user_input)
            cmds_index = 0

        elif char == CTRL_C:
            ## Quit the current line (like enter but with no action).
            putstr("^C\n")
            prompt()
            user_input.clear()
            input_index = 0
            cmds_index = 0

        elif char == "\t":
            ## Tab auto-completion.
            completion = auto_complete(user_input)
            if completion is not None:
                # Clear command to rewrite cleaned up command below.
                clear_cmd(len(user_input), input_index)
                user_input.strip()
                user_input += completion
                # If the command is complete, end with a space.
                if len(get_matching_opts(str(user_input))) == 1:
                    user_input += " "
                # Rewrite the command without extra spaces and move to the end.
                putstr(user_input)
                input_index = len(user_input)

        elif char == "\b" and len(user_input) > 0:
            ## Backspace needs handling.
            putstr("\b")
            user_input.pop(input_index - 1)
            input_index -= 1
            rewrite_cmd(user_input, len(user_input) + 1, input_index)

        elif char == DEL and input_index < len(user_input):
            ## Delete handling.
            user_input.pop(input_index)
            rewrite_cmd(user_input, len(user_input) + 1, input_index)

        elif char == LEFT and input_index > 0:
            ## Left-arrow pressed.
            putstr("\b")
            input_index -= 1

        elif char == RIGHT and input_index < len(user_input):
            ## Right-arrow pressed.
            putstr(user_input[input_index])
            input_index += 1

        elif char == HOME:
            putstr(input_index * "\b")
            input_index = 0

        elif char == END:
            putstr(user_input[input_index:])
            input_index = len(user_input)

        elif char == UP and cmds_index < len(recent_cmds) - 1:
            ## Cycle through recent entered commands.
            cmds_index += 1
            clear_cmd(len(user_input), input_index)
            old_len = len(user_input)
            user_input.set(recent_cmds[cmds_index])
            input_index = len(user_input)
            # Delete what was written and go back to the start of the line.
            putstr(user_input)

        elif char == DOWN and cmds_index > 0:
            ## Cycle through recent entered commands.
            cmds_index -= 1
            clear_cmd(len(user_input), input_index)
            old_len = len(user_input)
            user_input.set(recent_cmds[cmds_index])
            input_index = len(user_input)
            # Delete what was written and go back to the start of the line.
            putstr(user_input)

        elif char == CTRL_LEFT:
            ## Move to next space on the left.
            new_input_index = user_input.stripped()[: input_index - 1].rfind(" ") + 1
            if new_input_index != -1:
                putstr((input_index - new_input_index) * "\b")
                input_index = new_input_index
