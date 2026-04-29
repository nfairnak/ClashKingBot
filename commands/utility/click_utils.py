import disnake
from disnake.ext import commands
from datetime import datetime

from classes.bot import CustomClient


class UtilityButtons(commands.Cog):
    def __init__(self, bot: CustomClient):
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, res: disnake.MessageInteraction):

        # ===============================
        # DOWNLOAD BUTTON CLICK
        # ===============================
        if res.data.custom_id == 'link':

            results = await self.bot.bases.find_one({'message_id': res.message.id})
            count = results.get('downloads')

            # Update buttons (same as before)
            row_one = disnake.ui.ActionRow(
                disnake.ui.Button(
                    label='Link',
                    emoji='🔗',
                    style=disnake.ButtonStyle.grey,
                    custom_id='link',
                ),
                disnake.ui.Button(
                    label=f'{count + 1} Downloads',
                    emoji='📈',
                    style=disnake.ButtonStyle.grey,
                    custom_id='who',
                ),
            )

            await res.message.edit(components=[row_one])

            # ===============================
            # TRACK DOWNLOAD (ORIGINAL SYSTEM)
            # ===============================
            await self.bot.bases.update_one(
                {'message_id': res.message.id},
                {
                    '$inc': {'downloads': 1},
                    '$push': {
                        'downloaders': f'{res.author.mention} [{res.author.name}]'
                    },
                },
            )

            # ===============================
            # NEW TRACKING SYSTEM
            # ===============================
            user_id = res.user.id
            username = res.user.name
            base_link = results.get('link')

            # Extract base ID
            base_id = base_link.split('&id=')[-1]

            # Timestamp
            click_time = datetime.utcnow()

            # Save to Mongo (optional but useful)
            await self.bot.base_clicks.insert_one({
                "user_id": user_id,
                "username": username,
                "base_id": base_id,
                "message_id": res.message.id,
                "timestamp": click_time
            })

            # ===============================
            # CREATE TRACKED LINK (LIVE URL)
            # ===============================
            tracked_link = f"https://clashkingbot.onrender.com/base?u={user_id}&b={base_id}"

            await res.send(
                content=tracked_link,
                ephemeral=True
            )

        # ===============================
        # SHOW DOWNLOADERS BUTTON
        # ===============================
        elif res.data.custom_id == 'who':

            results = await self.bot.bases.find_one({'message_id': res.message.id})
            ds = results.get('downloaders')

            if ds == []:
                embed = disnake.Embed(
                    description='No Downloads Currently.',
                    color=disnake.Color.red()
                )
                return await res.send(embed=embed, ephemeral=True)

            text = ''
            for down in ds:
                text += '➼ ' + str(down) + '\n'

            embed = disnake.Embed(
                title='**Base Downloads:**',
                description=text,
                color=disnake.Color.green(),
            )

            return await res.send(embed=embed, ephemeral=True)

        # ===============================
        # ARMY SHARE (UNCHANGED)
        # ===============================
        elif str(res.data.custom_id).startswith("armyshare_"):

            id = str(res.data.custom_id).split("_")[-1]

            await self.bot.user_settings.update_one(
                {"discord_user": res.user.id},
                {"$addToSet": {"armies": id}},
                upsert=True
            )

            await self.bot.user_settings.update_one(
                {"discord_user": res.user.id},
                {"$push": {"armies": {"$each": [], "$slice": -25}}}
            )

            await res.send(
                f"Army Saved! Use {self.bot.command_mention('army share')} to manage/post/share your armies",
                ephemeral=True,
                delete_after=15
            )