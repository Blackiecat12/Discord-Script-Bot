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
    async def reload_scripts(ctx, new_folder: str = None):
        did_load, folder = bot.load_scripts(new_folder)
        if did_load:
            await ctx.send(f"Reloaded Scripts from {folder}")
        else:
            await ctx.send(f"Failed to load scripts from {folder}")

    @bot.command(name="all_scripts", help="Prints available scripts")
    async def print_scripts(ctx):
        await ctx.send(bot.format_all_scripts_string())

    @bot.command(name="running_scripts", help="Prints currently running scripts")
    async def print_running_scripts(ctx):
        await ctx.send(bot.format_running_scripts_string())

    @bot.command(name="run", help="Runs the given script")
    async def run_script(ctx, script_name, *args):
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

    bot = ScriptBot("Scripts", command_prefix="!", intents=intents)
    return bot


def get_api_params():
    """ Pulls the Endpoint and Authentication key from key.txt. These are laid out in consecutive lines.
    :return: {url: _, key: _}"""
    file = open("key.txt", 'r')
    token = file.readline()[:-1]  # Remove new line char
    server_name = file.readline()[:-1]
    return {"TOKEN": token, "SERVER": server_name}


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
        self.running_scripts: list[str] = list()
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
        for script in self.running_scripts:
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
        if script_name in self.running_scripts:
            return f"Already running {script_name}"
        for script in self.scripts:
            try:
                if script.check_match(script_name, args):
                    script.run_script(args)
                    self.running_scripts.append(script.name)
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


if __name__ == "__main__":
    main()
