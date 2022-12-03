import os
import re
import argparse
from subprocess import Popen, PIPE


class ScriptObject:
    """
    Holds information about a script that can be called by the ScriptBot. This allows easy storage/
    modification/loading of scripts.
    """

    def __init__(self, file_path):
        """ Parses Script from file.
        Check that the file exists and if so we
        start by taking the name then searching for the arguments. Arguments should be done via a argparse to be
        detected.
        :param file_path: File path of the Script to parse.
        """
        if os.path.exists(file_path):
            self.name = os.path.basename(file_path)
            self.path = file_path
            self.parser = argparse.ArgumentParser()
            # Read the file and pull all .add_argument(__)
            arguments = [re.findall(r'\.add_argument\(.*\)', line) for line in open(file_path, 'r')]
            for arg in arguments:
                # Eval the argument if it exists
                if len(arg) > 0:
                    eval("self.parser" + arg[0])
        else:
            raise FileNotFoundError(f"Could not find file: {file_path}")

    def check_match(self, name: str, args: [str]):
        """ Checks input matches script input.
        Checks the name and tries to parse arguments with internal parser.
        :param name: Script Name.
        :param args: Input arguments for the script.
        :return boolean: Script can be run from input.
        :raises ParserError: Arguments don't match the name.
        """
        if name in self.name:
            try:
                self.parser.parse_args(args)
            except SystemExit as sys_exit:
                raise self.ParserError(self.parser.format_help())
            return True
        return False

    def run_script(self, args: [str]):
        """ Runs Script.
        Creates the command line call for the script and executes it.
        :param args: Script arguments
        """
        terminal = Popen(['python', self.path, *args], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        return terminal
