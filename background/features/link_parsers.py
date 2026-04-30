import re
from urllib.parse import parse_qs, urlparse

import disnake
from disnake.ext import commands

from classes.bot import CustomClient
from commands.clan.utils import basic_clan_board
from commands.player.utils import basic_player_board
from commands.utility.utils import army_embed
from utility.general import safe_run


class LinkParsing(commands.Cog):
    def __init__(self, bot: CustomClient):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):

        # prevents webhooks from triggering the message parser
        if message.webhook_id is not None:
            return

        if message.guild is None:
            return

        # if message.guild.id in self.bot.OUR_GUILDS:
        if True:

            if (
                'https://link.clashofclans.com/' in message.content
                and 'action=OpenPlayerProfile&tag=' in message.content
            ):
                server_settings = await self.bot.ck_client.get_server_settings(server_id=message.guild.id)

                if (
                    not server_settings.player_link_parse
                    or (
                        server_settings.link_parse_channels
                        and message.channel.id not in server_settings.link_parse_channels
                    )
                ):
                    return

                tag = self.extract_url(text=message.content)
                player = await self.bot.getPlayer(tag)

                embed = await basic_player_board(
                    bot=self.bot,
                    player=player,
                    embed_color=server_settings.embed_color
                )

                stat_buttons = [
                    disnake.ui.Button(label='Open In-Game', url=player.share_link),
                    disnake.ui.Button(
                        label='Clash of Stats',
                        url=f"https://www.clashofstats.com/players/{player.tag.strip('#')}/summary",
                    ),
                    disnake.ui.Button(
                        label='Clash Ninja',
                        url=f"https://www.clash.ninja/stats-tracker/player/{player.tag.strip('#')}",
                    ),
                ]

                buttons = disnake.ui.ActionRow()
                for button in stat_buttons:
                    buttons.append_item(button)

                await message.channel.send(embed=embed, components=[buttons])
                await safe_run(func=message.delete)

            elif (
                'https://link.clashofclans.com/' in message.content
                and 'OpenClanProfile' in message.content
            ):
                server_settings = await self.bot.ck_client.get_server_settings(server_id=message.guild.id)

                if (
                    not server_settings.clan_link_parse
                    or (
                        server_settings.link_parse_channels
                        and message.channel.id not in server_settings.link_parse_channels
                    )
                ):
                    return

                clan_tag = self.extract_url(message.content)
                clan = await self.bot.getClan(clan_tag=clan_tag)

                embed = await basic_clan_board(
                    bot=self.bot,
                    clan=clan,
                    embed_color=server_settings.embed_color
                )

                stat_buttons = [
                    disnake.ui.Button(label='Open In-Game', url=clan.share_link),
                    disnake.ui.Button(
                        label='Clash of Stats',
                        url=f"https://www.clashofstats.com/clans/{clan.tag.strip('#')}/summary",
                    ),
                ]

                buttons = disnake.ui.ActionRow()
                for button in stat_buttons:
                    buttons.append_item(button)

                await message.channel.send(embed=embed, components=[buttons])

            elif (
                'https://link.clashofclans.com/' in message.content
                and 'CopyArmy' in message.content
            ):
                server_settings = await self.bot.ck_client.get_server_settings(server_id=message.guild.id)

                if (
                    not server_settings.army_link_parse
                    or (
                        server_settings.link_parse_channels
                        and message.channel.id not in server_settings.link_parse_channels
                    )
                ):
                    return

                embed = await army_embed(
                    bot=self.bot,
                    nick='Results',
                    link=message.content,
                    embed_color=server_settings.embed_color,
                )

                buttons = disnake.ui.ActionRow(
                    disnake.ui.Button(
                        label='Copy Link',
                        emoji=self.bot.emoji.troop.partial_emoji,
                        url=message.content,
                    )
                )

                await message.channel.send(embed=embed, components=[buttons])
                await safe_run(func=message.delete)

            elif (
                'https://link.clashofclans.com/' in message.content
                and '=OpenLayout&id=' in message.content
                and message.attachments
                and message.attachments[0].content_type
                and 'image' in message.attachments[0].content_type
            ):
                server_settings = await self.bot.ck_client.get_server_settings(server_id=message.guild.id)

                if (
                    not server_settings.base_link_parse
                    or (
                        server_settings.link_parse_channels
                        and message.channel.id not in server_settings.link_parse_channels
                    )
                ):
                    return

                base_url = self.extract_url(text=message.content, url_only=True)

                if base_url is None:
                    return

                description = message.content.replace(base_url, '').strip()

                # Pull the Clash layout id out of the original Clash link.
                parsed_url = urlparse(base_url)
                query_params = parse_qs(parsed_url.query)
                base_id = query_params.get("id", [None])[0]

                if base_id is None:
                    await message.channel.send("Could not read the base ID from that Clash link.")
                    return

                row_one = disnake.ui.ActionRow(
                    disnake.ui.Button(
                        label='Link',
                        emoji='🔗',
                        style=disnake.ButtonStyle.grey,
                        custom_id='link',
                    ),
                    disnake.ui.Button(
                        label='0 Downloads',
                        emoji='📈',
                        style=disnake.ButtonStyle.grey,
                        custom_id='who',
                    ),
                )

                attachment = await message.attachments[0].to_file(use_cached=True)

                sent_message = await message.channel.send(
                    file=attachment,
                    content=description,
                    components=[row_one],
                )

                await safe_run(func=message.delete)

                await self.bot.bases.insert_one(
                    {
                        'link': base_url,
                        'base_id': base_id,
                        'message_id': sent_message.id,
                        'channel_id': sent_message.channel.id,
                        'guild_id': sent_message.guild.id if sent_message.guild else None,
                        'downloads': 0,
                        'downloaders': [],
                        'feedback': [],
                        'new': True,
                    }
                )

            elif message.content.startswith('-show '):
                server_settings = await self.bot.ck_client.get_server_settings(server_id=message.guild.id)

                if not server_settings.show_command_parse:
                    return

                clans = message.content.replace('-show ', '')

                if clans == '':
                    return

                if ',' not in clans:
                    clans = [clans]
                else:
                    clans = clans.split(', ')[:5]

                clan_tags = []

                for clan in clans:
                    results = await self.bot.clan_db.find_one(
                        {
                            '$and': [
                                {'server': message.guild.id},
                                {'name': {'$regex': f'^(?i).*{clan}.*$'}},
                            ]
                        }
                    )

                    if not results:
                        continue

                    clan_tags.append(results.get('tag'))

                if clan_tags:
                    embeds = []
                    clans = await self.bot.get_clans(tags=clan_tags)

                    for clan in clans:
                        embed = await basic_clan_board(
                            bot=self.bot,
                            clan=clan,
                            embed_color=server_settings.embed_color,
                        )
                        embeds.append(embed)

                    await message.channel.send(embeds=embeds)

    def extract_url(self, text, url_only: bool = False):
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)

        if urls:
            url = urls[0]

            if url_only:
                return url

            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)

            tag = query_params.get('tag', [None])[0]
            return tag

        return None


def setup(bot: CustomClient):
    bot.add_cog(LinkParsing(bot))