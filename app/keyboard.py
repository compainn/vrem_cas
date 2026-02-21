from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from config import CHANNEL_URL


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🎲 играть')],
    [KeyboardButton(text='👤 профиль')]
], resize_keyboard=True)


profil = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='💸 пополнить', callback_data='deposit'),
        InlineKeyboardButton(text='📤 вывести', callback_data='withdraw')
    ],
    [
        InlineKeyboardButton(text='👥 Рефералы', callback_data='referrals'),
        InlineKeyboardButton(text='⚙️ настройки', callback_data='settings')
    ],
    [InlineKeyboardButton(text='📊 статистика', callback_data='stats')]
])


back_profil = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='◀️ назад', callback_data='back_profil')]
])


referral_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💸 Вывод реферальных', callback_data='withdraw_referral')],
    [InlineKeyboardButton(text='◀️ Назад', callback_data='back_profil')]
])


def get_deposit_kb(pay_url: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='💳 Оплатить', url=pay_url)],
        [InlineKeyboardButton(text='✅ Я оплатил', callback_data='check_payment')],
        [InlineKeyboardButton(text='◀️ Назад', callback_data='back_profil')]
    ])

withdraw_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📤 Вывести', callback_data='confirm_withdraw')],
    [InlineKeyboardButton(text='◀️ Назад', callback_data='back_profil')]
])

def get_withdraw_success_kb(pay_url: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='💸 Забрать', url=pay_url)]
    ])


games_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎲 Кубик', callback_data='game_dice')],
    [
        InlineKeyboardButton(text='🏀 Баскетбол', callback_data='game_basketball'),
        InlineKeyboardButton(text='⚽ Футбол', callback_data='game_football')
    ],
    [
        InlineKeyboardButton(text='🎯 Дартс', callback_data='game_darts'),
        InlineKeyboardButton(text='🎳 Боулинг', callback_data='game_bowling')
    ]
])

dice_list = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Больше ┃ 1.85', callback_data='dice_more'),
        InlineKeyboardButton(text='Меньше ┃ 1.85', callback_data='dice_less')
    ],
    [
        InlineKeyboardButton(text='Чёт ┃ 1.85', callback_data='dice_even'),
        InlineKeyboardButton(text='Нечёт ┃ 1.85', callback_data='dice_odd')
    ],
    [InlineKeyboardButton(text='◀️ назад', callback_data='back_games_list')]
])

basketball_list = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Гол | 1.7x', callback_data='basket_goal'),
        InlineKeyboardButton(text='Мимо | 1.3x', callback_data='basket_away')
    ],
    [
        InlineKeyboardButton(text='Застрял | 4.6x', callback_data='basket_stuck'),
        InlineKeyboardButton(text='Чистый | 4.6x', callback_data='basket_clean')
    ],
    [InlineKeyboardButton(text='◀️ Назад', callback_data='back_games_list')]
])

back_games_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='◀️ назад', callback_data='back_games_list_2')]
])

def create_bet_button(post_link=None):
    url = post_link if post_link else CHANNEL_URL
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Ваша ставка', url=url)]
    ])

football_list = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='гол | 1.3x', callback_data='football_goal'),
        InlineKeyboardButton(text='мимо | 1.7x', callback_data='football_away')
    ],
    [InlineKeyboardButton(text='◀️ Назад', callback_data='back_games_list')]
])

darts_list = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='мимо | 2.5x', callback_data='darts_away'),
        InlineKeyboardButton(text='красное | 1.7x', callback_data='darts_red')
    ],
    [
        InlineKeyboardButton(text='белое | 1.7x', callback_data='darts_white'),
        InlineKeyboardButton(text='центр | 2.5x', callback_data='darts_center')
    ],
    [InlineKeyboardButton(text='◀️ Назад', callback_data='back_games_list')]
])

settings_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='скрыть никнейм', callback_data='hide_nickname')],
    [InlineKeyboardButton(text='показывать никнейм', callback_data='show_nickname')]
])
