import discord
from discord.ext import commands
from utils import like_post, unlike_post, get_posts, send_message, split_message
from config import bot_token

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='!памаги'))
    print(f'Эта хуйня {bot.user} ждёт тебя в постели!')

@bot.command()
async def check(ctx, discussion_id: str):
    posts, discussion_title = get_posts(discussion_id)

    if not posts:
        await ctx.send('Не удалось получить сообщения из дискуссии.')
        return
    
    embed = discord.Embed(title=f'{discussion_title} (ID: {discussion_id})', color=discord.Color.yellow())
    await ctx.send(embed=embed)

    for post_id, (author, content, images, avatar_url, post_time) in posts.items():
        content_parts = split_message(content)

        for part in content_parts:
            embed = discord.Embed(description=part, color=discord.Color.yellow())
            if avatar_url:
                embed.set_author(name=f'{author} (ID: {post_id})', icon_url=avatar_url)

            for img in images:
                embed.set_image(url=img)

            embed.set_footer(text=f'{post_time}')
            await ctx.send(embed=embed)

@bot.command()
async def send(ctx, discussion_id: str, *, content: str):
    message = send_message(discussion_id, content)
    
    embed = discord.Embed(title=f'Сообщение в {discussion_id}', description=message, color=discord.Color.yellow())
    await ctx.send(embed=embed)

@bot.command()
async def like(ctx, post_id: str):
    message = like_post(post_id)
    
    embed = discord.Embed(title=f'Лайк на сообщение {post_id}', description=message, color=discord.Color.yellow())
    await ctx.send(embed=embed)

@bot.command()
async def unlike(ctx, post_id: str):
    message = unlike_post(post_id)
    
    embed = discord.Embed(title=f'Лайк убран у сообщения {post_id}', description=message, color=discord.Color.yellow())
    await ctx.send(embed=embed)

@bot.command()
async def памаги(ctx):
    embed = discord.Embed(title=f'Все доступные команды:', description='!check - отправляет дискуссию, айди которой ты указал;\n!send - отправляет сообщение в выбранную дискуссию;\n!like - лайкает пост, айди которого ты указал;\n!unlike - убирает лайк с поста, айди которого ты указал.', color=discord.Color.yellow())
    await ctx.send(embed=embed)

bot.run(bot_token)
