import asyncio
import ctypes
import os
import re
import sys
import time
from datetime import datetime
from itertools import cycle
import aiohttp
import colorama
import discord
import json
from colorama import Fore
from discord.ext import commands
from loading import Loader
import NitroRedeemer

try:
    ctypes.windll.kernel32.SetConsoleTitleW("Adam's Sniper & Giveaway Joiner")
except:
    pass

colorama.init()


def log(string):
    print(f"[{Fore.YELLOW}{datetime.now()}{Fore.WHITE}] {string}")


def clear():
    os.system("clear" if os.name == 'posix' else "cls")


def pad_to_center(l: list, w: int) -> str:
    return '\n'.join([' ' * (w // 2 - (len(max(l, key=len)) // 2)) + x for x in l])


def print_nitro():
    text = f'''{Fore.CYAN}
@@@@@@@@@@@@@@@@@@@################################@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@#######################################@@@@@@@@@@@@@
((((((((((((((((((@@########################################%@@@@@@@@@
(((((((((((((((((((((((((((((@%########////////////############@@@@@@@
((((&&((((((((%&&&&&&&&&&&&&@@#####/////%@@@@@@@@&/////##########@@@@@
(@@****@@(((@###################(///&@&            ,@@////########@@@@
@@@@@@@@((((@@@@@@@@@@@@@######///@@                  @@///########@@@
@@@@@@@&(((((((((((((((((@####///@      ,,,,,,,,,,      @///########@@
######((((((((((((@@@@@@@%###///@(    ,,,,,,,,,,,,,,     @///#######@@
((((((((((((((((%@###########///@    ,,,,,,,,,,,,,,,,    @///#######@@
((((((((((((((((((@@@@#######///@/    .,,,,,,,,,,,,.     @///#######@@
&&&&&&&&&&(((((((((((@########///@      ,,,,,,,,,,      @///########@@
@@@@@@@@@@%&(((((((((#@########///@@                  @@///########@@@
@@@@    @@@&&(((((((((#@########(///&@@            @@@////########@@@@
@@@@@@@@@@&&((((((((((((@&#########/////(@@@@@@@@#/////##########@@@@@
&&&&&&&&&&(((((((((((((((#@############(///////////############@@@@@@@
(((((((((((((((( (( ((((((((@@##############################@@@@@@@@@@
(((((((((((((((((**((((((((((((@@########################@@@@@@@@@@@@@
&&&&&&&&&((&&&(((((((((((((((((((((@@@@%##########%@@@@@@@@@@@@@@@@@@@{Fore.WHITE}
    '''.replace('@', ' ')

    width = os.get_terminal_size().columns
    print(pad_to_center(text.splitlines(), width))


def print_title():
    text = f'''{Fore.CYAN}
░█████╗░██████╗░░█████╗░███╗░░░███╗██╗░██████╗  ░██████╗███╗░░██╗██╗██████╗░███████╗██████╗░
██╔══██╗██╔══██╗██╔══██╗████╗░████║╚█║██╔════╝  ██╔════╝████╗░██║██║██╔══██╗██╔════╝██╔══██╗
███████║██║░░██║███████║██╔████╔██║░╚╝╚█████╗░  ╚█████╗░██╔██╗██║██║██████╔╝█████╗░░██████╔╝
██╔══██║██║░░██║██╔══██║██║╚██╔╝██║░░░░╚═══██╗  ░╚═══██╗██║╚████║██║██╔═══╝░██╔══╝░░██╔══██╗
██║░░██║██████╔╝██║░░██║██║░╚═╝░██║░░░██████╔╝  ██████╔╝██║░╚███║██║██║░░░░░███████╗██║░░██║
╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝╚═╝░░░░░╚═╝░░░╚═════╝░  ╚═════╝░╚═╝░░╚══╝╚═╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝
{Fore.WHITE}'''.replace('░', ' ')

    width = os.get_terminal_size().columns
    print(pad_to_center(text.splitlines(), width))


# TODO NICE GUI, PRIVNOTE
print_nitro()
print_title()

if 'config.json' not in os.listdir():
    log(f'{Fore.RED}Config file not found. Exiting...{Fore.WHITE}')
    input()
    sys.exit(1)

print(f'''{Fore.CYAN}┍━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃  Welcome to Adams Sniper & Giveaway Joiner.{Fore.WHITE}''')
loader = Loader(f"{Fore.CYAN}┃{Fore.GREEN}  Connecting to discord...", "Connected.", 0.05).start()

giveawaymessagere = re.compile("<https://discord.com/channels/(.*)/(.*)/(.*)>")
giveawayre = {
    re.compile("You won the \\*\\*(.*)\\*\\*"): 15,
    re.compile("You have won : \\*\\*(.*)\\*\\*"): 17,
    re.compile("You won \\*\\*(.*)\\*\\*"): 10
}
giveawayhostre = re.compile("Hosted by: <@[0-9]+>")
invitelinkre = re.compile("discord.gg\/([0-9a-zA-Z]+)")


def get_config() -> dict:
    with open('config.json') as f:
        return json.load(f)


def rainbow(text):
    colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX,
              Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
              Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX,
              Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW]
    rainbow_text = ""

    for char, color in zip(text, cycle(colors)):
        rainbow_text += color + char
    rainbow_text += Fore.WHITE

    return rainbow_text


def log_to_file(file, string):
    with open(file, 'a') as f:
        f.write(string)


class Sniper(commands.Bot):
    def __init__(self, token, alt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token
        self.uptime = time.time()
        self.alt = alt
        self.payment_source_id = None
        self.webhook = get_config()["WEBHOOK"]
        self.sniped_invites = 0
        self.invite_sniper = True

    def get_headers(self):
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 OPR/75.0.3969.285',
            'Authorization': self.token
        }
        return headers

    async def notify_webhook(self, text):
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(self.webhook, adapter=discord.AsyncWebhookAdapter(session))

            try:
                await webhook.send(text)
            except:
                pass

    async def get_payment(self):
        async with aiohttp.ClientSession() as session:
            r = await session.get("https://discord.com/api/v8/users/@me/billing/payment-sources",
                                  headers=self.get_headers())
            return await r.json()

    async def on_ready(self):
        global nitro_redeemer

        if get_config()['NITRO']['PAYMENT_METHOD']:
            payment_methods = await self.get_payment()

            if payment_methods:
                default_payment_method = [x for x in payment_methods if x["default"]]
                if default_payment_method:
                    self.payment_source_id = default_payment_method[0]["id"]

        if self.alt:
            await main.wait_until_ready()

            print(len(self.guilds))
            log(f'{Fore.GREEN}{self.user} is ready.{Fore.WHITE}')
            return

        loader.stop()
        clear()
        print_nitro()
        print_title()

        ready_text = rainbow(f"Connected to discord.")
        report_webhook = f"{Fore.GREEN}Specified.{Fore.WHITE}" if self.webhook else f"{Fore.RED}Not specified.{Fore.WHITE}"
        payment_method = f"{Fore.GREEN}Found.{Fore.WHITE}" if self.payment_source_id else f"{Fore.RED}Not Found.{Fore.WHITE}"

        print(Fore.CYAN + f'''┍━━ INFO
┃  Payment Method: {Fore.GREEN}{payment_method}
{Fore.CYAN}┃  Reporting webhook: {report_webhook}
{Fore.CYAN}┃  {ready_text}{Fore.CYAN}
┃''' + Fore.WHITE)

        notes = []
        if not self.payment_source_id:
            notes.append('Payment method not found on main account, Some nitro codes cannot be redeemed.')
        if not self.webhook:
            notes.append('Reporting webhook not found. You will not be alerted in discord.')

        print(Fore.CYAN + '┍━━ NOTES' + Fore.WHITE)
        for note in notes:
            print(Fore.CYAN + '┃' + Fore.WHITE + '  ' + Fore.RED + note + Fore.WHITE)
        print()

        nitro_redeemer = NitroRedeemer.NitroRedeemer({bot.token: bot.payment_source_id for bot in bots}, NitroRedeemer.ErrorHandler())

    async def on_message(self, message):
        if codes := nitro_redeemer.find_codes(message.content):
            if message.author == self.user:
                return

            await asyncio.sleep(
                get_config()["NITRO"]["DM_DELAY"] if not message.guild else get_config()["NITRO"]["DELAY"])

            for code in codes:
                response = await nitro_redeemer.redeem_code(code)

                additional_data = f" - [{Fore.CYAN}{code}{Fore.WHITE}] - [{Fore.YELLOW}{message.guild if message.guild else 'DM'}{Fore.WHITE}] - [{Fore.YELLOW}{message.author}{Fore.WHITE}] [{Fore.YELLOW}{response[0]}{Fore.WHITE}]"
                log(f'[{Fore.CYAN}{response[1].name}{Fore.WHITE}]' + additional_data)

                if response[1] == NitroRedeemer.Responses.CLAIMED:
                    await self.notify_webhook(f"Claimed nitro gift, Check console for more details.")

        await self.process_commands(message)

        if get_config()["GIVEAWAY"]["ENABLED"]:
            if message.author.bot and '**G I V E A W A Y' in message.content or "**GIVEAWAY" in message.content and '<:yay:' in message.content or ':santa_lunar_gifts:' in message.content or ':PQ_giveaway:' in message.content:
                if not message.embeds:
                    return

                title = message.embeds[0].author.name
                # get title
                if not any(x in title for x in get_config()["GIVEAWAY"]["BLACKLISTED_WORDS"]):
                    if not any(x in title for x in get_config()["GIVEAWAY"]["WHITELISTED_WORDS"]) and \
                            get_config()["GIVEAWAY"]["WHITELIST_ONLY"]:
                        return

                    await asyncio.sleep(1)

                    reactions = message.reactions
                    if reactions:
                        await asyncio.sleep(get_config()["GIVEAWAY"]["DELAY"] - 1)
                        try:
                            await message.add_reaction(reactions[0])
                            log(
                                f"{Fore.GREEN}[Entered a giveaway.]{Fore.WHITE} - [{Fore.YELLOW}{title}{Fore.WHITE}] - [{Fore.YELLOW}{message.guild.name}{Fore.WHITE}] - [{Fore.YELLOW}{self.user}{Fore.WHITE}]")
                        except:
                            return

            elif ('You won' in message.content or 'You have won' in message.content) and message.author.bot and str(
                    self.user.id) in message.content:
                log(message.content, message.guild)
                prize = None
                for giveawayregex in giveawayre:
                    if giveawayregex.match(message.content):
                        prize = giveawayregex.search(message.content).group(0)[giveawayre[giveawayregex]:-2]
                        break

                additional_data = f' - [{Fore.YELLOW}{prize}{Fore.WHITE}] - [{Fore.YELLOW}{message.guild.name}{Fore.WHITE}] - [{Fore.YELLOW}{self.user}{Fore.WHITE}]'

                log(f'{Fore.GREEN}[Won a giveaway!]{Fore.WHITE}' + additional_data)
                await self.notify_webhook(f'Won a giveaway, check console for more information.')

                giveaway_message = giveawaymessagere.search(message.embeds[0].description).group(0)
                message_id = giveaway_message[-19:-1]
                msg = discord.utils.get(await message.channel.history(limit=300).flatten(), id=int(message_id))
                if not msg:
                    log(f"{Fore.RED}[Giveaway message not found.]{Fore.WHITE}" + additional_data)
                    return

                host = giveawayhostre.search(msg.embeds[0].description)
                if not host:
                    log(f'{Fore.RED}[Giveaway host is not found.]{Fore.WHITE}' + additional_data)
                    return

                host_id = host.group(0)[13:-1]
                host = await self.fetch_user(host_id)
                if not host:
                    log(f'{Fore.RED}[Giveaway host cannot be fetched.]{Fore.WHITE}' + additional_data)
                    return

                await asyncio.sleep(get_config()["GIVEAWAY"]["DM_DELAY"])
                try:
                    await host.send(get_config()["GIVEAWAY"]["DM_MESSAGE"])
                except discord.HTTPException:
                    log(f'{Fore.RED}[Failed sending DM to host.]{Fore.WHITE}' + additional_data)
                    return

                log(f'{Fore.GREEN}[Sent DM to host.]{Fore.WHITE}' + additional_data)

            elif '🎉' in message.content and 'The new winner' in message.content and str(
                    self.user.id) in message.content and message.author.bot:
                additional_data = f' - [{Fore.YELLOW}{message.guild.name}{Fore.WHITE}] - [{Fore.YELLOW}{self.user}{Fore.WHITE}]'

                log(f'{Fore.GREEN}[Won a rerolled giveaway!]{Fore.WHITE}' + additional_data)
                await self.notify_webhook(f'Won a rerolled giveaway, check console for more information.')

        # idk why it phoneban me

        # print(message.content if invitelinkre.match(message.content) else '', end='')
        # if invitelinkre.match(message.content) and self.invite_sniper:
        #     print('1')
        #     if get_config()['INVITE']['ALT_ONLY'] and not self.alt:
        #         return
        #
        #     code = invitelinkre.search(message.content).group(0)
        #     code = code.replace('discord.gg/', '')
        #
        #     url = "https://discord.com/api/v8/invites/" + code
        #     async with aiohttp.ClientSession() as session:
        #         r = await session.get(url)
        #
        #         r_data = await r.json()
        #         print('a', r_data)
        #         if "WELCOME_SCREEN_ENABLED" in r_data['guild']['features'] and not get_config()['INVITE']['JOIN_WELCOME_SCREEN']:
        #             # will add auto accepter soon
        #             return
        #
        #         print('b')
        #         if any(x in str(r_data) for x in get_config()['INVITE']['BLACKLISTED_WORDS']):
        #             return
        #
        #         print('c')
        #         if not any(x in str(r_data) for x in get_config()['INVITE']['WHITELISTED_WORDS']) and get_config()['INVITE']['WHITELIST_ONLY']:
        #             return
        #
        #         print('d')
        #         r = await session.post(url, headers=self.get_headers())  # join lol
        #
        #     if self.sniped_invites >= get_config()['INVITE']['MAX_SERVERS']:
        #         self.invite_sniper = False
        #         print(f'[{Fore.GREEN}Invite Sniper Turing Off{Fore.WHITE}]')
        #
        #         await asyncio.sleep(3600 * get_config()["INVITE"]['COOLDOWN'])
        #
        #         print(f'[{Fore.GREEN}Invite Sniper Turning On{Fore.WHITE}]')
        #         self.invite_sniper = True

    async def run(self):
        await super().start(self.token)


main_token = get_config()["TOKENS"]["MAIN"]
main = Sniper(token=main_token, alt=False, command_prefix="<<<", self_bot=True, help_command=None)
alts = []
for alt_token in get_config()["TOKENS"]["ALTS"]:
    alts.append(Sniper(token=alt_token, alt=True, command_prefix="<<<", self_bot=True, help_command=None))

bots = [main] + alts


@main.command()
async def history(ctx):
    code_string = ""
    for code in nitro_redeemer.cache:
        code_string += f"Code: {code}, {nitro_redeemer.cache[code]}\n"

    list_strings = [code_string[i:i + 2000] for i in range(0, len(code_string), 2000)]
    for string in list_strings:
        await ctx.send(string)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.create_task(main.run())

    for alt in alts:
        loop.create_task(alt.run())
    loop.run_forever()

input()
