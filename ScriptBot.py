import os
from ScriptObject import ScriptObject
from discord.ext import commands


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

    def kill_all_scripts(self):
        """ Forcefully close all scripts. """
        self.running_scripts = []
        pass

    class ParserError(Exception):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)