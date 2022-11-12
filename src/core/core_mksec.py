#!/usr/bin/env python
#
# Centralized core modules for MKSEC
#
import re
import sys
import socket
import subprocess
import shutil
import os
import time
import datetime
import random
import inspect
from src.core import dictionaries
import io

# python 2 and 3 compatibility
try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen
import multiprocessing

if sys.version_info >= (3, 0):
    # python 3 removes reduce from builtin and into functools
    from functools import *

# needed for backwards compatibility of python2 vs 3 - need to convert to
# threading eventually
try:
    import thread
except ImportError:
    import _thread as thread

try:
    raw_input
except:
    raw_input = input

# get the main MKSEC path

def definepath():
    if check_os() == "posix":
        if os.path.isfile("mksec"):
            return os.getcwd()
        else:
            return "/usr/share/mksec/"
    else:
        return os.getcwd()

# check operating system

def check_os():
    if os.name == "nt":
        operating_system = "windows"
    if os.name == "posix":
        operating_system = "posix"
    return operating_system

# class for colors
if check_os() == "posix":
    class bcolors:
        PURPLE = '\033[95m'
        CYAN = '\033[96m'
        DARKCYAN = '\033[36m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        UNDERL = '\033[4m'
        ENDC = '\033[0m'
        backBlack = '\033[40m'
        backRed = '\033[41m'
        backGreen = '\033[42m'
        backYellow = '\033[43m'
        backBlue = '\033[44m'
        backMagenta = '\033[45m'
        backCyan = '\033[46m'
        backWhite = '\033[47m'

        def disable(self):
            self.PURPLE = ''
            self.CYAN = ''
            self.BLUE = ''
            self.GREEN = ''
            self.YELLOW = ''
            self.RED = ''
            self.ENDC = ''
            self.BOLD = ''
            self.UNDERL = ''
            self.backBlack = ''
            self.backRed = ''
            self.backGreen = ''
            self.backYellow = ''
            self.backBlue = ''
            self.backMagenta = ''
            self.backCyan = ''
            self.backWhite = ''
            self.DARKCYAN = ''

# if we are windows or something like that then define colors as nothing
else:
    class bcolors:
        PURPLE = ''
        CYAN = ''
        DARKCYAN = ''
        BLUE = ''
        GREEN = ''
        YELLOW = ''
        RED = ''
        BOLD = ''
        UNDERL = ''
        ENDC = ''
        backBlack = ''
        backRed = ''
        backGreen = ''
        backYellow = ''
        backBlue = ''
        backMagenta = ''
        backCyan = ''
        backWhite = ''

        def disable(self):
            self.PURPLE = ''
            self.CYAN = ''
            self.BLUE = ''
            self.GREEN = ''
            self.YELLOW = ''
            self.RED = ''
            self.ENDC = ''
            self.BOLD = ''
            self.UNDERL = ''
            self.backBlack = ''
            self.backRed = ''
            self.backGreen = ''
            self.backYellow = ''
            self.backBlue = ''
            self.backMagenta = ''
            self.backCyan = ''
            self.backWhite = ''
            self.DARKCYAN = ''

# this will be the home for the set menus

def setprompt(category, text):
    # if no special prompt and no text, return plain prompt
    if category == '0' and text == "":
        return bcolors.UNDERL + bcolors.DARKCYAN + "mksec" + bcolors.ENDC + " > "
    # if the loop is here, either category or text was positive
    # if it's the category that is blank...return prompt with only the text
    if category == '0':
        return bcolors.UNDERL + bcolors.DARKCYAN + "mksec" + bcolors.ENDC + "> " + text + ": "
    # category is NOT blank
    else:
        # initialize the base 'mksec' prompt
        prompt = bcolors.UNDERL + bcolors.DARKCYAN + "mksec" + bcolors.ENDC
        # if there is a category but no text
        if text == "":
            for level in category:
                level = dictionaries.category(level)
                prompt += ":" + bcolors.UNDERL + \
                    bcolors.DARKCYAN + level + bcolors.ENDC
            promptstring = str(prompt)
            promptstring += " > "
            return promptstring
        # if there is both a category AND text
        else:
            # iterate through the list received
            for level in category:
                level = dictionaries.category(level)
                prompt += ":" + bcolors.UNDERL + \
                    bcolors.DARKCYAN + level + bcolors.ENDC
            promptstring = str(prompt)
            promptstring = promptstring + " > " + text + ": "
            return promptstring


def yesno_prompt(category, text):
    valid_response = False
    while not valid_response:
        response = raw_input(setprompt(category, text))
        response = str.lower(response)
        if response == "no" or response == "n":
            response = "NO"
            valid_response = True
        elif response == "yes" or response == "y":
            response = "YES"
            valid_response = True
        else:
            print_warning("valid responses are 'n|y|N|Y|no|yes|No|Yes|NO|YES'")
    return response


def return_continue():
    print(("\n      Press " + bcolors.RED + "<return> " + bcolors.ENDC + "to continue"))
    pause = raw_input()

# DEBUGGING #############
# ALWAYS SET TO ZERO BEFORE COMMIT!
DEBUG_LEVEL = 0
#  0 = Debugging OFF
#  1 = debug imports only
#  2 = debug imports with pause for <ENTER>
#  3 = imports, info messages
#  4 = imports, info messages with pause for <ENTER>
#  5 = imports, info messages, menus
#  6 = imports, info messages, menus with pause for <ENTER>

debugFrameString = '-' * 72


def debug_msg(currentModule, message, msgType):
    if DEBUG_LEVEL == 0:
        pass  # stop evaluation efficiently
    else:
        if msgType <= DEBUG_LEVEL:
            # a bit more streamlined
            print(bcolors.RED + "\nDEBUG_MSG: from module '" +
                  currentModule + "': " + message + bcolors.ENDC)

            if DEBUG_LEVEL == 2 or DEBUG_LEVEL == 4 or DEBUG_LEVEL == 6:
                raw_input("waiting for <ENTER>\n")


def mod_name():
    frame_records = inspect.stack()[1]
    calling_module = inspect.getmodulename(frame_records[1])
    return calling_module

# runtime messages

def print_status(message):
    print(bcolors.GREEN + bcolors.BOLD + "[*] " + bcolors.ENDC + str(message))

def print_info(message):
    print(bcolors.BLUE + bcolors.BOLD + "[-] " + bcolors.ENDC + str(message))

def print_info_spaces(message):
    print(bcolors.BLUE + bcolors.BOLD + "  [-] " + bcolors.ENDC + str(message))

def print_warning(message):
    print(bcolors.YELLOW + bcolors.BOLD + "[!] " + bcolors.ENDC + str(message))

def print_error(message):
    print(bcolors.RED + bcolors.BOLD + "[!] " + bcolors.ENDC + bcolors.RED + str(message) + bcolors.ENDC)


def get_version():
    define_version = open("src/core/mksec.version", "r").read().rstrip()
    # define_version = '1.0.0'
    return define_version

class create_menu:

    def __init__(self, text, menu):
        self.text = text
        self.menu = menu
        print(text)
        for i, option in enumerate(menu):

            menunum = i + 1
            # Check to see if this line has the 'return to main menu' code
            match = re.search("0D", option)
            # If it's not the return to menu line:
            if not match:
                if menunum < 10:
                    print(('   %s) %s' % (menunum, option)))
                else:
                    print(('  %s) %s' % (menunum, option)))
            else:
                print('\n  99) Return to Main Menu\n')
        return

#ifconfig

def detect_public_ip():
    """
    Helper function to auto-detect our public IP(v4) address.
    """
    rhost = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rhost.connect(('google.com', 0))
    rhost.settimeout(2)
    return rhost.getsockname()[0]

def validate_ip(address):
    """
    Validates that a given string is an IPv4 dotted quad.
    """
    try:
        if socket.inet_aton(address):
            if len(address.split('.')) == 4:
                debug_msg("core_mksec", "this is a valid IP address", 5)
                return True
            else:
                print_error("This is not a valid IP address...")
                raise socket.error

        else:
            raise socket_error

    except socket.error:
        return False

#####config duzenlemek icin kullanilabilecek 2 kod parcasi
    # # this is an option if we don't want to use Metasploit period
    # check_metasploit = check_config("METASPLOIT_MODE=").lower()
    # if check_metasploit != "on":
    #     msf_path = False
    # return msf_path

# def meta_database():
#     # DEFINE METASPLOIT PATH
#     meta_path = open("/etc/setoolkit/set.config", "r").readlines()
#     for line in meta_path:
#         line = line.rstrip()
#         match = re.search("METASPLOIT_DATABASE=", line)
#         if match:
#             line = line.replace("METASPLOIT_DATABASE=", "")
#             msf_database = line.rstrip()
#             return msf_database

# update mksec

def update_set():
    backbox = check_backbox()
    kali = check_kali()

    if backbox == "BackBox":
        # print_status("You are running BackBox Linux which already implements MKSEC updates.") maybe :(
        # print_status("No need for further operations, just update your system.")
        # time.sleep(2)
        print_info("Kali or BackBox Linux not detected, manually updating...")
        print_info("Updating the MKSEC, be patient...")
        print_info("Performing cleanup first...")
        subprocess.Popen("git clean -fd", shell=True).wait()
        print_info("Updating... This could take a little bit...")
        subprocess.Popen("git pull", shell=True).wait()
        print_status("The updating has finished, returning to main menu...")
        time.sleep(2)

    elif kali == "Kali":
        # print_status("You are running Kali Linux which maintains MKSEC updates.")
        # time.sleep(2)
        print_info("Kali or BackBox Linux not detected, manually updating...")
        print_info("Updating the MKSEC, be patient...")
        print_info("Performing cleanup first...")
        subprocess.Popen("git clean -fd", shell=True).wait()
        print_info("Updating... This could take a little bit...")
        subprocess.Popen("git pull", shell=True).wait()
        print_status("The updating has finished, returning to main menu...")
        time.sleep(2)

    # if we aren't running Kali or BackBox :(
    else:
        print_info("Kali or BackBox Linux not detected, manually updating...")
        print_info("Updating the MKSEC, be patient...")
        print_info("Performing cleanup first...")
        subprocess.Popen("git clean -fd", shell=True).wait()
        print_info("Updating... This could take a little bit...")
        subprocess.Popen("git pull", shell=True).wait()
        print_status("The updating has finished, returning to main menu...")
        time.sleep(2)

# pull the help menu here

def help_menu():
    fileopen = open("README.md", "r").readlines()
    for line in fileopen:
        line = line.rstrip()
        print(line)
    fileopen = open("readme/CREDITS", "r").readlines()
    print("\n")
    for line in fileopen:
        line = line.rstrip()
        print(line)
    return_continue()

# this is a small area to generate the date and time

def date_time():
    now = str(datetime.datetime.today())
    return now

# expand the filesystem windows directory

def windows_root():
    return os.environ['WINDIR']

# core log file routine for MKSEC

def log(error):
    try:
        # open log file only if directory is present (may be out of directory
        # for some reason)
        if not os.path.isfile("%s/src/logs/set_logfile.log" % (definepath())):
            filewrite = open("%s/src/logs/set_logfile.log" %
                             (definepath()), "w")
            filewrite.write("")
            filewrite.close()
        if os.path.isfile("%s/src/logs/set_logfile.log" % (definepath())):
            error = str(error)
            # open file for writing
            filewrite = open("%s/src/logs/set_logfile.log" %
                             (definepath()), "a")
            # write error message out
            filewrite.write("ERROR: " + date_time() + ": " + error + "\n")
            # close the file
            filewrite.close()
    except IOError as err:
        pass

#show banner
def show_banner(define_version, graphic):
    if graphic == "1":
        if check_os() == "posix":
            os.system("clear")
        if check_os() == "windows":
            os.system("cls")
        show_graphic()
    else:
        os.system("clear")

    print(bcolors.BLUE + """
        [ mksec """ + "v%s" % (define_version) + """ ]""")

    # here we check if there is a new version of MKSEC - if there is, then
    # display a banner
    cv = get_version()

    # pull version
    try:
        version = ""

        def pull_version():
            if not os.path.isfile(userconfigpath + "version.lock"):
                try:

                    url = (
                        'https://raw.githubusercontent.com/generatorexit/mksec/master/src/core/mksec.version')
                    version = urlopen(url).read().rstrip().decode('utf-8')
                    filewrite = open(userconfigpath + "version.lock", "w")
                    filewrite.write(version)
                    filewrite.close()

                except KeyboardInterrupt:
                    version = "keyboard interrupt"

            else:
                version = open(userconfigpath + "version.lock", "r").read()

            if cv != version:
                if version != "":
                    print(bcolors.RED + "          There is a new version of MKSEC available.\n                    " + bcolors.GREEN + " Your version: " + bcolors.RED + cv + bcolors.GREEN +
                          "\n                  Current version: " + bcolors.ENDC + version + bcolors.YELLOW + "\nPlease update MKSEC to the latest before submitting any git issues.\n" + bcolors.ENDC)

        # why urllib and sockets cant control DNS resolvers is beyond me - so
        # we use this as a hack job to add a delay and kill if updates are
        # taking too long
        p = multiprocessing.Process(target=pull_version)
        p.start()

        # Wait for 5 seconds or until process finishes
        p.join(8)

        # If thread is still active
        if p.is_alive():
            print(
                bcolors.RED + " Unable to check for new version of MKSEC (is your network up?)\n" + bcolors.ENDC)
            # terminate the process
            p.terminate()
            p.join()

    except Exception as err:
        print(err)
        # pass


def show_graphic():
    menu = random.randrange(1, 14)
    if menu == 1:
        print(bcolors.YELLOW + r"""
        0111100101101111011101010010000001110010
        0110010101100001011011000110110001111001
        0010000001101000011000010111011001100101
        0010000001110100011011110010000001101101
        0111010101100011011010000010000001110100
        0110100101101101011001010010000001101111
        0110111000100000011110010110111101110101
        0111001000100000011010000110000101101110
        0110010001110011001000000010100000111010
        0010000001110100011010000110000101101110
        0110101101110011001000000110011001101111
        0111001000100000011101010111001101101001
        0110111001100111001000000111010001101000
        0110010100100000011011010110101101110011
        0110010101100011001011100010000000101010
        0110100001110101011001110111001100101010""" + bcolors.ENDC)
        return

    if menu == 2:
        print("""\x1b[36m
        .##.....##.##....##..######..########..######.
        .###...###.##...##..##....##.##.......##....##
        .####.####.##..##...##.......##.......##......
        .##.###.##.#####.....######..######...##......
        .##.....##.##..##.........##.##.......##......
        .##.....##.##...##..##....##.##.......##....##
        .##.....##.##....##..######..########..######.""" + bcolors.ENDC)
        return

    if menu == 3:
        print("""\x1b[36m
        ##::::'##:'##:::'##::'######::'########::'######::
        ###::'###: ##::'##::'##... ##: ##.....::'##... ##:
        ####'####: ##:'##::: ##:::..:: ##::::::: ##:::..::
        ## ### ##: #####::::. ######:: ######::: ##:::::::
        ##. #: ##: ##. ##::::..... ##: ##...:::: ##:::::::
        ##:.:: ##: ##:. ##::'##::: ##: ##::::::: ##::: ##:
        ##:::: ##: ##::. ##:. ######:: ########:. ######::
        ..:::::..::..::::..:::......:::........:::......::""" + bcolors.ENDC)

    if menu == 4:
        print(bcolors.RED + """
                   ,   ,
                 ,-`{-`/
              ,-~ , \ {-~~-,
            ,~  ,   ,`,-~~-,`,
          ,`   ,   { {      } }                                             \x1b[32m}/\x1b[31m
         ;     ,--/`\ \    / /                                     \x1b[32m}/      /,/\x1b[31m
        ;  ,-./      \ \  { {  (                                  \x1b[32m/,;    ,/ ,/\x1b[31m
        ; /   `       } } `, `-`-.___                            \x1b[32m/ `,  ,/  `,/\x1b[31m
         \|         ,`,`    `~.___,---}                         \x1b[32m/ ,`,,/  ,`,;\x1b[31m
          `        { {                                     \x1b[32m__  /  ,`/   ,`,;\x1b[31m
                /   \ \                                 \x1b[32m_,`, `{  `,{   `,`;`\x1b[31m
               {     } }       \x1b[37m/~\         \x1b[33m.-:::-.     \x1b[32m(--,   ;\ `,}  `,`;\x1b[31m
               \\._./ /       \x1b[37m/` , \      \x1b[33m,:::::::::,     \x1b[32m`~;   \},/  `,`;     ,-=-\x1b[31m
                `-..-`      \x1b[37m/. `  .\_   \x1b[33m;:::::::::::;  \x1b[32m__,{     `/  `,`;     {\x1b[31m
                           \x1b[37m/ , ~ . ^ `~`\\\x1b[33m:::::::::::\x1b[32m<<~>-,,`,    `-,  ``,_    }\x1b[31m
                        \x1b[37m/~~ . `  . ~  , .`~~\\\x1b[33m:::::::;    \x1b[32m_-~  ;__,        `,-`\x1b[31m
               \x1b[37m/`\    /~,  . ~ , '  `  ,  .` \\\x1b[33m::::;`   \x1b[32m<<<~```   ``-,,__   ;\x1b[31m
              \x1b[37m/` .`\ /` .  ^  ,  ~  ,  . ` . ~\~                       \x1b[32m\\\\, `,__\x1b[31m
             \x1b[37m/ ` , ,`\.  ` ~  ,  ^ ,  `  ~ . . ``~~~`,                   \x1b[32m`-`--, \\\x1b[31m
            \x1b[37m/ , ~ . ~ \ , ` .  ^  `  , . ^   .   , ` .`-,___,---,__            \x1b[32m``\x1b[31m
           \x1b[37m/` ` . ~ . ` `\ `  ~  ,  .  ,  `  ,  . ~  ^  ,  .  ~  , .`~---,___
         \x1b[37m/` . `  ,  . ~ , \  `  ~  ,  .  ^  ,  ~  .  `  ,  ~  .  ^  ,  ~  .  `-,""" + bcolors.ENDC)
        return

    if menu == 5:
        print("""\x1b[33m
                                      A
                                     /_\\
                             :      /_|_\\
                            :::    /|__|_\\
                           ::.::  /|_|__|_\      :
                          ::.:.::/__|_|__|_\    :.:
                         :..:.:./_|__|__|__|\  :.:.:
                        :.:..:./|__|___|__|__\:.:..::
         ..............::..:../__|___|__|___|_\..:..::................
            ..........:..:..:/_|__|___|___|___|\:..:..::::::::::::::::::::
        ::::::::::::::.:..:./___|___|___|___|___\....................
                .........../..!...!...!...!...!..\...............
                                  \x1b[36m \x1b[5m-mksec-  \x1b[0m""" + bcolors.ENDC)
        return

    if menu == 6:
        print("""\x1b[33m
                                /\\
          \x1b[36m___                  \x1b[33m/  \                  \x1b[36m___
         \x1b[36m/   \     __         \x1b[33m/    \         \x1b[36m__     /
        \x1b[36m/     \   /  \   _   \x1b[33m/ <()> \   \x1b[36m_   /  \   /
               \x1b[36m\_/    \_/ \_\x1b[33m/________\\\x1b[36m_/ \_/    \_/
         \x1b[37m__________________\x1b[33m/__I___I___\\\x1b[37m________________\x1b[33m
                          /_I___I___I__\\
                         /I___I___I___I_\\
                        /___I___I___I___I\\
                       /__I___I___I___I___\\
                      /_I___I___I___I___I__\\
                     /I___I___I___I___I___I_\\
                    /___I___I___I___I___I___I\\
                   /__I___I___I___I___I___I___\\
                  /_I___I___I___I___I___I___I__\\
                            \x1b[36m \x1b[5m-mksec-  \x1b[0m""" + bcolors.ENDC)
        return

    if menu == 7:
        print('''\x1b[31m
        ILOVEYOUILOVEYOUILOVEYOUILOVEYOUILOVEYOUILO
        ILOVEYOUILO \x1b[37m****** \x1b[31mVEYOU \x1b[37m****** \x1b[31mILOVEYOUILO
        ILOVEYOU \x1b[37m*********** \x1b[31mI \x1b[37m*********** \x1b[31mLOVEYOUI
        OUIUI \x1b[37m*************** *************** \x1b[31mVEYOU
        YOUI \x1b[37m********************************** \x1b[31mLOV
        IL \x1b[37m************************************* \x1b[31mOV
        L \x1b[37m*****************\x1b[36m\x1b[5mmksec\x1b[0m***************** \x1b[31mO
        I \x1b[37m*************************************** \x1b[31mL
        U \x1b[37m*************************************** \x1b[31mI
        OU \x1b[37m************************************* \x1b[31mIL
        UIL \x1b[37m*********************************** \x1b[31mOVE
        OVEYO \x1b[37m******************************* \x1b[31mULOVE
        OVEYOUI \x1b[37m**************************** \x1b[31mLOVEYO
        EYOUILOVE \x1b[37m*********************** \x1b[31mYOUILOVEY
        VEYOUILOVEYOU \x1b[37m***************** \x1b[31mILOVEYOUILO
        ILOVEYOUILOVEYO \x1b[37m************* \x1b[31mLOVEYOUILOVEY
        UILOVEYOUILOVEYOU \x1b[37m********* \x1b[31mLOVEYOUILOVEYOU
        LOVEYOUILOVEYOUILOV \x1b[37m***** \x1b[31mILOVEYOUILOVEYOUI
        EYOUILOVEYOUILOVEYOU \x1b[37m*** \x1b[31mYOULOVEYOUILOVEYOU
        VEYOUILOVEYOUILOVEYOU \x1b[37m* \x1b[31mVEYOUILOVEYOUILOVEY
        OVEYOUILOVEYOUILOVEYOUILOVEYOUILOVEYOUILOVE'''+ bcolors.ENDC)

    if menu == 8:
        print("""\x1b[37m
        888888888888888888888888888888888888888888888888888888888888
        888888888888888888888888888888888888888888888888888888888888
        8888888888888888888888888P""  ""9888888888888888888888888888
        8888888888888888P"88888P          988888"9888888888888888888
        8888888888888888  "9888            888P"  888888888888888888
        888888888888888888bo "9  d8o  o8b  P" od88888888888888888888
        888888888888888888888bob 98"  "8P dod88888888888888888888888
        888888888888888888888888    db    88888888888888888888888888
        88888888888888888888888888      8888888888888888888888888888
        88888888888888888888888P"9bo  odP"98888888888888888888888888
        88888888888888888888P" od88888888bo "98888888888888888888888
        888888888888888888   d88888888888888b   88888888888888888888
        8888888888888888888oo8888888888888888oo888888888888888888888
        888888888888888888888888888888888888888888888888888888888888""" + bcolors.ENDC)

    if menu == 9:
        print("""\x1b[33m
                        .,aadd"'    `"bbaa,.
                    ,ad8888P'          `Y8888ba,
                 ,a88888888    \x1b[36m\x1b[5mmksec\x1b[0m\x1b[33m     88888888a,
               a88888888888              88888888888a
             a8888888888888b,          ,d8888888888888a
            d8888888888888888b,_    _,d8888888888888888b
           d88888888888888888888888888888888888888888888b
          d8888888888888888888888888888888888888888888888b
         I888888888888888888888888888888888888888888888888I
        ,88888888888888888888888888888888888888888888888888,
        I8888888888888888PY8888888PY88888888888888888888888I
        8888888888888888"  "88888"  "88888888888888888888888
        8::::::::::::::'    `:::'    `:::::::::::::::::::::8
        Ib:::::::::::"        "        `::::::' `:::::::::dI
        `8888888888P            Y88888888888P     Y88888888'
         Ib:::::::'              `:::::::::'       `:::::dI
          Yb::::"                  ":::::"           "::dP
           Y88P                      Y8P               `P
            Y'                        "
                                        `:::::::::::;8"
               "888888888888888888888888888888888888"
                 `"8;::::::::::::::::::::::::::;8"'
                    `"Ya;::::::::::::::::::;aP"'
                        ``""YYbbaaaaddPP""''""" + bcolors.ENDC)

    if menu == 10:
        print("""\x1b[33m
                                            \  /
                                            (())
                                            ,~L_
                                           2~~ <\\
                                           )>-\y(((GSSSSSSssssss>=  _/
         ___________________________________)v_\__________________________________
        (_// / / / (///////\3__________((_/      _((__________E/\\\\\\\\\\\\\) \ \ \ \\\\_)
          (_/ / / / (////////////////////(c  (c /|\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\) \ \ \ \_)
            "(_/ / / /(/(/(/(/(/(/(/(/(/(/\_    /\)\)\)\)\)\)\)\)\)\)\ \ \ \_)"
               "(_/ / / / / / / / / / / / /|___/\ \ \ \ \ \ \ \ \ \ \ \ \_)"
                  "(_(_(_(_(_(_(_(_(_(_(_(_[_]_|_)_)_)_)_)_)_)_)_)_)_)_)"
                                           |    \\
                                          /      |
                                         / /    /___
                                        /           "~~~~~__
                                        \_\_______________\_"_?"""+ bcolors.ENDC)

    if menu == 11:
        print('''\x1b[33m
                                      /^\\
                   \x1b[35mL L               \x1b[33m/   \               \x1b[35mL L
                __/|/|_             \x1b[33m/  .  \             \x1b[35m_|\|\__
               /_| [_[_\           \x1b[33m/     .-\           \x1b[35m/_]_] |_\\
              /__\  __`-\_____    \x1b[33m/    .    \    \x1b[35m_____/-`__  /__\\
             /___] /=@>  _   {>  \x1b[33m/-.         \  \x1b[35m<}   _  <@=\ [___\\
            /____/     /` `--/  \x1b[33m/      .      \  \x1b[35m\--` `\     \____\\
           /____/  \____/`-._> \x1b[33m/               \ \x1b[35m<_.-`\____/  \____\\
          /____/    /__/      \x1b[33m/-._     .   _.-  \      \x1b[35m\__\    \____\\
         /____/    /__/      \x1b[33m/         .         \      \x1b[35m\__\    \____\\
        |____/_  _/__/      \x1b[33m/          .          \      \x1b[35m\__\_  _\____|
         \__/_ ``_|_/      \x1b[33m/      -._  .        _.-\      \x1b[35m\_|_`` _\___/
           /__`-`__\      \x1b[33m<_         `-;           _>      \x1b[35m/__`-`__\\
              `-`           \x1b[33m`-._       ;       _.-`           \x1b[35m`-`
                                \x1b[33m`-._   ;   _.-`
                                    \x1b[33m`-._.-`
'''+ bcolors.ENDC)

    if menu == 12:
        print("""\x1b[33m


                                                    \x1b[37m ___
                                                  \x1b[37m,o88888
                                               \x1b[37m,o8888888'
                         \x1b[33m,:o:o:oooo.        \x1b[37m,8O88Pd8888"
                     \x1b[33m,.::.::o:ooooOoOoO. \x1b[37m,oO8O8Pd888'"
                   \x1b[33m,.:.::o:ooOoOoOO8O8OOo.\x1b[37m8OOPd8O8O"
                  \x1b[33m, ..:.::o:ooOoOOOO8OOOOo.\x1b[37mFdO8O8"
                 \x1b[33m, ..:.::o:ooOoOO8O888O8O\x1b[37m,COmCOO"
                \x1b[33m, . ..:.::o:ooOoOOOO8OOO\x1b[37mOCOCO"
                 \x1b[33m. ..:.::o:ooOoOoOO8O\x1b[37m8OCCCC"\x1b[33mo
                    \x1b[33m. ..:.::o:ooooO\x1b[37moCoCCC"\x1b[33mo:o
                    \x1b[33m. ..:.::o:o:\x1b[37m,cooooCo"\x1b[33moo:o:
                 \x1b[33m`   . . ..:.\x1b[37m:cocoooo"'\x1b[33mo:o:::'
                 \x1b[37m.\x1b[33m`   . ..\x1b[37m::ccccoc"'\x1b[33mo:o:o:::'
                \x1b[37m:.:.\x1b[33m    \x1b[37m,c:cccc"'\x1b[33m:.:.:.:.:.'
              \x1b[37m..:.:"'\x1b[33m`\x1b[37m::::c:"'\x1b[33m..:.:.:.:.:.'
            \x1b[37m...:.'.:.::::"'\x1b[33m    . . . . .'
           \x1b[37m.. . ....:."' \x1b[33m`   .  . . ''
         \x1b[37m. . . ...."'
         \x1b[37m.. . ."'
        \x1b[37m."""+ bcolors.ENDC)

    if menu == 13:
        print("""\x1b[31m
                        ..:::::::::..
                   ..:::\x1b[37maad8888888baa\x1b[31m:::..
                .::::\x1b[37md:?88888888888?::8b\x1b[31m::::.
              .:::\x1b[37md8888:?88888888??a888888b\x1b[31m:::.
            .:::\x1b[37md8888888a8888888aa8888888888b\x1b[31m:::.
           ::::\x1b[37mdP::::::::88888888888::::::::Yb\x1b[31m::::
          ::::\x1b[37mdP:::::::::Y888888888P:::::::::Yb\x1b[31m::::
         ::::\x1b[37md8:::::::::::Y8888888P:::::::::::8b\x1b[31m::::
        .::::\x1b[37m88::::::::::::Y88888P::::::::::::88\x1b[31m::::.
        :::::\x1b[37mY8baaaaaaaaaa88P:T:Y88aaaaaaaaaad8P\x1b[31m:::::
        :::::::\x1b[37mY88888888888P::|::Y88888888888P\x1b[31m:::::::
        ::::::::::::::::\x1b[37m888:::|:::888\x1b[31m::::::::::::::::
        `:::::::::::::::\x1b[37m8888888888888b\x1b[31m::::::::::::::'
         :::::::::::::::\x1b[37m88888888888888\x1b[31m::::::::::::::
          :::::::::::::\x1b[37md88888888888888\x1b[31m:::::::::::::
           ::::::::::::\x1b[37m88::88::88:::88\x1b[31m::::::::::::
            `::::::::::\x1b[37m88::88::88:::88\x1b[31m::::::::::'
              `::::::::\x1b[37m88::88::P::::88\x1b[31m::::::::'
                `::::::\x1b[37m88::88:::::::88\x1b[31m::::::'
                   ``:::::::::::::::::::''
                        ``:::::::::'' """ + bcolors.ENDC)

# identify if set interactive shells are disabled

def set_check():
    fileopen = open("/etc/setoolkit/set.config", "r")
    for line in fileopen:
        match = re.search("SET_INTERACTIVE_SHELL=OFF", line)
        # if we turned it off then we return a true else return false
        if match:
            return True
        match1 = re.search("SET_INTERACTIVE_SHELL=ON", line)
        # return false otherwise
        if match1:
            return False

# if the user specifies 99

def menu_back():
    print_info("Returning to the previous menu...")

# routine for checking length of a payload: variable equals max choice
def check_length(choice, max):
    # start initital loop
    counter = 0
    while 1:
        if counter == 1:
            choice = raw_input(bcolors.YELLOW + bcolors.BOLD + "[!] " + bcolors.ENDC + "Invalid choice try again: ")
        # try block in case its not a integer
        try:
            # check to see if its an integer
            choice = int(choice)
            # okay its an integer lets do the compare
            if choice > max:
                # trigger an exception as not an int
                choice = "blah"
                choice = int(choice)
            # if everythings good return the right choice
            return choice
        # oops, not a integer
        except Exception:
            counter = 1

# valid if IP address is legit

def is_valid_ip(ip):
    return is_valid_ipv4(ip) or is_valid_ipv6(ip)

# ipv4

def is_valid_ipv4(ip):
    pattern = re.compile(r"""
        ^
        (?:
          # Dotted variants:
          (?:
            # Decimal 1-255 (no leading 0's)
            [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
          |
            0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
          |
            0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
          )
          (?:                  # Repeat 0-3 times, separated by a dot
            \.
            (?:
              [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
            |
              0x0*[0-9a-f]{1,2}
            |
              0+[1-3]?[0-7]{0,2}
            )
          ){0,3}
        |
          0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
        |
          0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
        |
          # Decimal notation, 1-4294967295:
          429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
          42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
          4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
        )
        $
    """, re.VERBOSE | re.IGNORECASE)
    return pattern.match(ip) is not None

# ipv6

def is_valid_ipv6(ip):
    """Validates IPv6 addresses.
    """
    pattern = re.compile(r"""
        ^
        \s*                         # Leading whitespace
        (?!.*::.*::)                # Only a single whildcard allowed
        (?:(?!:)|:(?=:))            # Colon iff it would be part of a wildcard
        (?:                         # Repeat 6 times:
            [0-9a-f]{0,4}           # A group of at most four hexadecimal digits
            (?:(?<=::)|(?<!::):)    # Colon unless preceeded by wildcard
        ){6}                        #
        (?:                         # Either
            [0-9a-f]{0,4}           # Another group
            (?:(?<=::)|(?<!::):)    # Colon unless preceeded by wildcard
            [0-9a-f]{0,4}           # Last group
            (?: (?<=::)             # Colon iff preceeded by exacly one colon
             |  (?<!:)              #
             |  (?<=:) (?<!::) :    #
             )                      # OR
         |                          # A v4 address with NO leading zeros
            (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            (?: \.
                (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            ){3}
        )
        \s*                         # Trailing whitespace
        $
    """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
    return pattern.match(ip) is not None

# check the config file and return value
def check_config(param):
    fileopen = open("/etc/setoolkit/set.config", "r")
    for line in fileopen:
        line = line.rstrip()
        # print line
        # if the line starts with the param we want then we are set, otherwise
        # if it starts with a # then ignore
        if line.startswith(param) != "#":
            if line.startswith(param):
                line = line.rstrip()
                # remove any quotes or single quotes
                line = line.replace('"', "")
                line = line.replace("'", "")
                line = line.split("=", 1)
                return line[1]

# copy an entire folder function

def copyfolder(sourcePath, destPath):
    for root, dirs, files in os.walk(sourcePath):

        # figure out where we're going
        dest = destPath + root.replace(sourcePath, '')

        # if we're in a directory that doesn't exist in the destination folder
        # then create a new folder
        if not os.path.isdir(dest):
            os.mkdir(dest)

        # loop through all files in the directory
        for f in files:

            # compute current (old) & new file locations
            oldLoc = root + '/' + f
            newLoc = dest + '/' + f

            if not os.path.isfile(newLoc):
                try:
                    shutil.copy2(oldLoc, newLoc)
                except IOError:
                    pass


# this routine will be used to check config options within the set.options

def check_options(option):
        # open the directory
    trigger = 0
    if os.path.isfile(userconfigpath + "set.options"):
        fileopen = open(userconfigpath + "set.options", "r").readlines()
        for line in fileopen:
            match = re.search(option, line)
            if match:
                line = line.rstrip()
                line = line.replace('"', "")
                line = line.split("=")
                return line[1]
                trigger = 1

    if trigger == 0:
        return trigger

# future home to update one localized set configuration file

def update_options(option):
        # if the file isn't there write a blank file
    if not os.path.isfile(userconfigpath + "set.options"):
        filewrite = open(userconfigpath + "set.options", "w")
        filewrite.write("")
        filewrite.close()

    # remove old options
    fileopen = open(userconfigpath + "set.options", "r")
    old_options = ""
    for line in fileopen:
        match = re.search(option, line)
        if match:
            line = ""
        old_options = old_options + line
    # append to file
    filewrite = open(userconfigpath + "set.options", "w")
    filewrite.write(old_options + "\n" + option + "\n")
    filewrite.close()

# exit routine

def exit_mksec():
    print("\n\n[*] Exiting the mksec")
    sys.exit()


# compare ports to make sure its not already in a config file for metasploit

# def check_ports(filename, port):
#     fileopen = open(filename, "r")
#     data = fileopen.read()
#     match = re.search("LPORT " + port, data)
#     if match:
#         return True
#     else:
#         return False


# the main ~./set path for MKSEC
def setdir():
    if check_os() == "posix":
        return os.path.join(os.path.expanduser('~'), '.set' + '/')
    if check_os() == "windows":
        return "src/program_junk/"

# set the main directory for MKSEC
userconfigpath = setdir()

# capture output from a function

def capture(func, *args, **kwargs):
    """Capture the output of func when called with the given arguments.
    The function output includes any exception raised. capture returns
    a tuple of (function result, standard output, standard error).
    """
    stdout, stderr = sys.stdout, sys.stderr
    sys.stdout = c1 = io.StringIO()
    sys.stderr = c2 = io.StringIO()
    result = None
    try:
        result = func(*args, **kwargs)
    except:
        traceback.print_exc()
    sys.stdout = stdout
    sys.stderr = stderr
    return (result, c1.getvalue(), c2.getvalue())

# check to see if we are running backbox linux

def check_backbox():
    if os.path.isfile("/etc/issue"):
        backbox = open("/etc/issue", "r")
        backboxdata = backbox.read()
        if "BackBox" in backboxdata:
            return "BackBox"
        # if we aren't running backbox
        else:
            return "Non-BackBox"
    else:
        print("[!] Not running a Debian variant..")
        return "Non-BackBox"

# check to see if we are running kali linux

def check_kali():
    if os.path.isfile("/etc/apt/sources.list"):
        kali = open("/etc/apt/sources.list", "r")
        kalidata = kali.read()
        if "kali" in kalidata:
            return "Kali"
        # if we aren't running kali
        else:
            return "Non-Kali"
    else:
        print("[!] Not running a Debian variant..")
        return "Non-Kali"

# reload module function for python 2 and python 3

def module_reload(module):
    if sys.version_info >= (3, 0):
        import importlib
        importlib.reload(module)
    else:
        reload(module)

# used to replace any input that we have from python 2 to python 3

def input(string):
    return raw_input(string)
