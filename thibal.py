import discord
import matplotlib.pyplot as plt
from datetime import datetime
from pytz import timezone
import calendar
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

d, h = 7, 24
week_data = [[0 for x in range(h)] for y in range(d)]
hours = [str(x)+'h' for x in range(h)]

def utc_to_local(time):
	utc_tz = timezone('Etc/UTC')
	paris_tz = timezone('Europe/Paris')
	return utc_tz.localize(time).astimezone(paris_tz)

bot = discord.Client()

@bot.event
async def on_ready():
	print('Je suis connecté en tant que {0.user}.'.format(bot))

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	if message.content.startswith('C\'est l\'heure de la pause!'):
		#collect data from discord
		await message.channel.trigger_typing()
		guild = message.channel.guild
		bot_member = guild.get_member(bot.user.id)
		for channel in guild.text_channels:
			if bot_member.permissions_in(channel).read_messages:
				async for msg in channel.history():
					#Caengal
					if "twitter.com" in msg.content and msg.author.name == "Drahigan":
						msg_time = utc_to_local(msg.created_at)
						print(calendar.day_name[msg_time.weekday()], "à", msg_time.hour, "h")
						week_data[msg_time.weekday()][msg_time.hour] = week_data[msg_time.weekday()][msg_time.hour] + 1

		#create plot
		thibal_week = np.array(week_data)
		fig, ax = plt.subplots()
		im = ax.imshow(thibal_week, interpolation='nearest')
		divider = make_axes_locatable(ax)
		cax = divider.append_axes('right', size='5%', pad=0.1)

		ax.set_xticks(np.arange(h))
		ax.set_yticks(np.arange(d))
		ax.set_yticklabels(calendar.day_name)
		ax.set_xticklabels(hours, fontsize = 6)

		ax.set_title("Les pauses de Thibal")
		fig.tight_layout()
		fig_name = "Thibal_week_" + utc_to_local(datetime.now()).strftime("%d_%m_%Y__%H:%M:%S") + ".png"

		mn=int(np.floor(thibal_week.min()))
		mx=int(np.ceil(thibal_week.max()))
		cbar = fig.colorbar(im, ticks=[mn, mx], cax=cax, orientation='vertical')
		cbar.ax.set_yticklabels(['Min', 'Max'])

		plt.savefig(fig_name, bbox_inches = 'tight', pad_inches = 0)

		#reset data
		for x in range(h):
			for y in range(d):
				week_data[y][x] = 0

		#send image
		await message.channel.send(file=discord.File(fig_name))

		print("Done!")

bot.run('SECRET_KEY')
