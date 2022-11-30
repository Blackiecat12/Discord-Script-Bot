import argparse
import os
import re
import discord
from discord.ext import commands


def main():
    AUTH = get_api_params()
    bot = init_bot()

    # Command syntax
    @bot.command(name='test', help='Helpful info')
    async def some_name(ctx):
        """ Example fn
        :param ctx: Context of the command
        :param arg: Arguments given to the command
        """
        await ctx.send("Got")

    @bot.command(name='reload_scripts', help="Reloads the available scripts from file")
    async def reload_scripts(ctx):
        bot.get_scripts()
        await ctx.send("Reloaded Scripts")

    @bot.command(name="scripts", help="Prints available scripts")
    async def get_scripts(ctx):
        await ctx.send(bot.print_scripts())

    @bot.command(name="run", help="Runs the given script")
    async def run_script(ctx, script_name, *args):
        print('running')
        response = bot.run_script(script_name, list(args))
        print(response)
        await ctx.send(response)

    @bot.command(name='kill', help="Kills all scripts")
    async def kill_all_scripts(ctx):
        bot.kill_all_scripts()
        await ctx.send("Killed all Scripts")

    bot.run(AUTH['TOKEN'])


def init_bot():
    """ Initialises the bot. """
    intents = discord.Intents.default()
    intents.message_content = True

    bot = ScriptBot(command_prefix="!", intents=intents)
    return bot


def get_api_params():
    """ Pulls the Endpoint and Authentication key from key.txt. These are laid out in consecutive lines.
    :return: {url: _, key: _}"""
    file = open("key.txt", 'r')
    token = file.readline()[:-1]  # Remove new line char
    server_name = file.readline()[:-1]
    return {"TOKEN": token, "SERVER": server_name}


class ScriptBot(commands.Bot):

    def __init__(self, script_folder: str = "Scripts", **kwargs):
        """ Initialises Discord Bot with Scripts from folder.
        Internal variables storing the available scripts and running scripts are created. Scripts are loaded from the
        file folder.
        :param script_folder: Folder to get scripts from.
        :param kwargs: Discord Bot parameters.
        """
        # Variables
        super().__init__(**kwargs)
        self.script_folder = script_folder
        self.scripts = [ScriptObject]
        self.running_scripts = {}
        # Init dynamic vars
        self.get_scripts()
        # Run the start up bot command
        # TODO Start up diagnostics

    def get_scripts(self):
        """ Loads Python Scripts from internal folder.
        Checks folder exists and initialises a ScriptObject for each python file to add to the internal list.
        """
        scripts = []
        if os.path.exists(self.script_folder):
            for file in os.listdir(self.script_folder):
                if file.endswith('.py'):
                    scripts.append(ScriptBot())
            self.scripts = scripts

    def print_scripts(self):
        """ Returns formatted scripts.
        :return scripts: Formatted string
        """
        script_str = f"{len(self.scripts)} Scripts Available:"
        for script in self.scripts:
            script_str += f"\n\t{script}"
        return script_str

    def run_script(self, script_name, args):
        """ Runs a script. """
        # Check valid name and not running
        for script in self.scripts:
            try:
                script_matches = script.check_match(script_name, args)
            except ScriptObject.ParserError as parse_error:
                # TODO send error
                pass

            if script_matches:
                script.run_script(args)
                return f"Running Script: {script_name}"
        return f"No matching Script Name {script_name}"

    def kill_all_scripts(self):
        """ Forcefully close all scripts. """
        for spawn in self.running_scripts.values():
            spawn.close(force=True)


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
        if os.path.exists():
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
                raise self.ParserError() from sys_exit
            return True
        raise False

    def run_script(self, args: [str]):
        """ Runs Script.
        Creates the command line call for the script and executes it.
        :param args: Script arguments
        """
        pass

    class ParserError(Exception):

        def __init__(self):
            super().__init__()

if __name__ == "__main__":
    main()
