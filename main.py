import discord
from ScriptBot import ScriptBot


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

    @bot.command(name="query", help="Prints command line output of the given script")
    async def run_script(ctx, script_name: str):
        response = bot.get_script_output(script_name)
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


if __name__ == "__main__":
    main()
