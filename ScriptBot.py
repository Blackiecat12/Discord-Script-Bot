import os
import time

from ScriptObject import ScriptObject
from discord.ext import commands
from threading import Thread
from queue import Queue, Empty


class ScriptBot(commands.Bot):

    def __init__(self, script_folder: str, **kwargs):
        """ Initialises Discord Bot with Scripts from folder.
        Internal variables storing the available scripts and running scripts are created. Scripts are loaded from the
        file folder.
        :param script_folder: Folder to get scripts from.
        :param kwargs: Discord Bot parameters.
        """
        # Variables
        super().__init__(**kwargs)
        self.script_folder = script_folder
        self.scripts: list[ScriptObject] = list()
        self.running_scripts: dict = dict()
        # Init dynamic vars
        self.load_scripts()
        # Run the start up bot command
        # TODO Start up diagnostics

    def load_scripts(self, folder: str = None) -> bool:
        """ Loads Python Scripts from folder.
        Checks folder exists and initialises a ScriptObject for each python file to add to the internal list.
        :param folder: Folder to load Scripts from.
        :return bool: Reloaded Scripts.
        """
        scripts = []
        if folder is not None:
            if os.path.isdir(folder):
                self.script_folder = folder
            else:
                return False, folder
        if os.path.isdir(self.script_folder):
            for file in os.listdir(self.script_folder):
                if file.endswith('.py'):
                    scripts.append(ScriptObject(self.script_folder + "\\" + file))
        self.scripts = scripts
        return True, self.script_folder

    def format_running_scripts_string(self):
        """ Returns formatted running scripts.
        :return scripts: Formatted string
        """
        formatted_string = f"{len(self.running_scripts)} Scripts Running:"
        for script in self.running_scripts.keys():
            formatted_string += f"\n\t{script}"
        return formatted_string

    def format_all_scripts_string(self):
        """ Returns formatted available scripts.
        :return scripts: Formatted string
        """
        formatted_string = f"{len(self.scripts)} Scripts Available:"
        for script in self.scripts:
            formatted_string += f"\n\t{script.name}"
        return formatted_string

    def run_script(self, script_name, args):
        """ Runs a script.
        Checks that script not running, then finds the matching script from the arguments and name.
        :param script_name: Script file name to run.
        :param args: Arguments to run script with.
        """
        # Check valid name and not running
        if script_name in self.running_scripts.keys():
            return f"Already running {script_name}"
        for script in self.scripts:
            try:
                if script.check_match(script_name, args):
                    self.running_scripts[script_name] = script.run_script(args)
                    return f"Running Script: {script_name}"
            except ScriptObject.ParserError as parse_error:
                return str(parse_error)
                pass
        return f"No matching Script Name {script_name}"

    def get_script_output(self, script_name):
        """ Returns the string version of the given scripts terminal output.
        :param script_name: The name of the script to investigate.
        :return output: Terminal output of the script.
        """
        if self._check_script_running(script_name):
            q = Queue()
            t = Thread(target=enqueue_output, args=(self.running_scripts[script_name].stdout, q))
            t.daemon = True  # thread dies with the program
            t.start()
            try:
                line = q.get_nowait().decode("utf-8")
            except Empty:
                line = "None"
            t.join()
            return f"Output of {script_name}:\n" + line
        return f"Script {script_name} not running or not valid. "

    def kill_all_scripts(self):
        """ Forcefully close all scripts.
        Sends kill to all terminals, then checks for surviving. Removes terminals that died from self.running_scripts
        """
        killed_scripts = []
        # Kill scripts
        for script_name, terminal in self.running_scripts.items():
            terminal.kill()
            time.sleep(0.1)
            if terminal.poll() is not None:
                killed_scripts.append(script_name)
        # Remove the killed scripts
        for script in killed_scripts:
            self.running_scripts.pop(script)

    def _check_script_running(self, script_name):
        """ Checks the given script is still running.
        :param script_name: Script to check
        :return bool: True if script exists and is running else false.
        """
        if script_name in self.running_scripts.keys():
            return self.running_scripts[script_name].poll() is not None
        return False

    # TODO clean running scripts.


def enqueue_output(out, queue):
    """ Queues output from terminal. """
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()
