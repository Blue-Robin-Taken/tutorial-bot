import discord
import os
import pymongo
import pymongo.errors
from pymongo import MongoClient

server_ids = [912361242985918464]
token = os.environ['token']

id = 0

bot = discord.Bot()

password = os.environ["MongoDB password"]

client = pymongo.MongoClient(f"mongodb+srv://Test:{password}@cluster0.hbuueev.mongodb.net/?retryWrites=true&w=majority")
db = client.warns
coll = db.serverwarns


@bot.event
async def on_ready():
  print("I am online")

@bot.slash_command(guild_ids = server_ids, name="warn", description = "Warn a user.")
async def warn(ctx, user:discord.Option(discord.Member, description="What user do you want to warn?"), reason:discord.Option(str)):
  if user.guild_permissions.manage_guild:
    embed = discord.Embed(
      title= "You were warned",
      description= f"{ctx.author.mention} warned {user.mention} \n Reason: {reason}",
      color = discord.Color.random()
    )
    await ctx.respond(embed=embed)
  
    try:
      coll.insert_one({"_id":{"guild":user.guild.id, "user_id":user.id}, "count":1})
    except pymongo.errors.DuplicateKeyError:
      coll.update_one({"_id":{"guild":user.guild.id, "user_id":user.id}}, {"$inc":{"count":1}})
  else:
    await ctx.respond("You don't have permission to do that!", ephemeral = True)
    
@bot.slash_command(guild_ids = server_ids, name="warns", description="See all warns")
async def warns(ctx):
  users = coll.find({})
  end_str = ""
  for user in users:
    print(ctx.guild.id, user["_id"]["guild"])
    if user["_id"]["guild"] == ctx.guild.id:
      end_str += f"Member: {ctx.guild.get_member(user['_id']['user_id'])} has {user['count']} warn(s)"
  embed = discord.Embed(
    title = "Server warns",
    description = end_str,
    color = discord.Color.random()
  )
  if not end_str:
    embed = discord.Embed(
      title = "This server doesn't have any warns.",
      color = discord.Color.random()
    )
  
  await ctx.respond(embed = embed)

@bot.slash_command(guild_ids = server_ids, name="removewarns", description = "Remove a user's warns")
async def removewarns(ctx, user:discord.Option(discord.Member), amount:int):
  if user.guild_permissions.manage_guild:
    if amount < 1:
      await ctx.respond("You can't do that. Amount must be greater or equal to one.",  ephemeral = True)
      return 0
    coll.update_one({"_id":{"guild":user.guild.id, "user_id":user.id}}, {"$inc":{"count":-amount}})
    if coll.find_one({"_id":{"guild":user.guild.id, "user_id":user.id}})["count"] <= 0:
      coll.delete_one({"_id":{"guild":user.guild.id, "user_id":user.id}})
    embed = discord.Embed(
      title = "Removed warn",
      description = f"Removed warn(s) for {user.mention} \n Removed {amount} warn(s)"
    )
    
    await ctx.respond(embed = embed)
  else:
    await ctx.respond("You don't have permission to do that!", ephemeral = True)
    

@bot.slash_command(guild_ids = server_ids, name = "test", description = "Amazing Command")
async def test(ctx):
  await ctx.respond("The command works.")

bot.run(token)