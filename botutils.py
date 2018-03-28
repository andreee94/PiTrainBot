from telebot import types
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent

class BotUtils:

	@classmethod
	def markupFromListInline(self, list):
		# markup = InlineKeyboardMarkup(inline_keyboard=[
		#              [dict(text='Telegram URL', url='https://core.telegram.org/')],
		#              [InlineKeyboardButton(text='Callback - show notification', callback_data='notification')],
		#              [dict(text='Callback - show alert', callback_data='alert')],
		#              [InlineKeyboardButton(text='Callback - edit message', callback_data='edit')],
		#              [dict(text='Switch to using bot inline', switch_inline_query='initial query')],
		#          ])
		# return markup
		# markup = types.InlineKeyboardMarkup()
		# for l in list:
		#     item = types.InlineKeyboardButton(text=l)
		#     markup.row(item)
		# return markup
		if len(list) == 2:
			markup = InlineKeyboardMarkup(inline_keyboard=[
					 [InlineKeyboardButton(text=list[0], callback_data=list[0])],
					 [InlineKeyboardButton(text=list[1], callback_data=list[1])]])
		elif len(list) == 3:
			markup = InlineKeyboardMarkup(inline_keyboard=[
				[InlineKeyboardButton(text=list[0], callback_data=list[0])],
				[InlineKeyboardButton(text=list[1], callback_data=list[1])],
				[InlineKeyboardButton(text=list[2], callback_data=list[2])]])
		return markup

		# keyboard = [[0 for x in range(1)] for y in range(len(list))]
		# for i in range(len(list)):
		# 	keyboard[i][0] = [InlineKeyboardButton(text=list[i], callback_data=list[i])]
		# markup = InlineKeyboardMarkup(inline_keyboard=[keyboard])
		# return markup
					# markup = types.ReplyKeyboardMarkup()
			# for item in list:
			# 	markup.row(types.KeyboardButton(text=item))
			# return markup

	@classmethod
	def markupFromListKeyboard(self, list):
		if len(list) == 2:
			markup = ReplyKeyboardMarkup(keyboard=[
						[KeyboardButton(text=list[0])],
						[KeyboardButton(text=list[1])],
						], one_time_keyboard=True,  selective=True)
		elif len(list) == 3:
			markup = ReplyKeyboardMarkup(keyboard=[
						[KeyboardButton(text=list[0])],
						[KeyboardButton(text=list[1])],
						[KeyboardButton(text=list[2])],
						 ], one_time_keyboard=True,  selective=True)
		return markup

	@classmethod
	def markupRemoveKeyboard(self):
		markup = ReplyKeyboardRemove()
		return markup
