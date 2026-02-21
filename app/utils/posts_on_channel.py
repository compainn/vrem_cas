from aiogram import Bot
from aiogram.types import FSInputFile
from config import CHANNEL_ID, SUPPORT, CHANNEL_URL, INFO_CHANNEL
import asyncio
import os

async def post_dice_on_channel(
        bot: Bot,
        user_id: int,
        username: str,
        amount: float,
        bet_type: str,
        hide_nickname: bool = False
):
    if hide_nickname:
        display_name = "Имя скрыто"
    else:
        display_name = f"@{username}"

    bet_type_translation = {
        "more": "Больше",
        "less": "Меньше",
        "even": "Чёт",
        "odd": "Нечёт"
    }

    bet_message = await bot.send_message(
        chat_id=CHANNEL_ID,
        text=f'<b>{display_name} ставит {amount}$ на {bet_type_translation[bet_type]}\n\n</b>'
        f'<blockquote><b>Коэффициент 1.85x\n</b></blockquote>'
        f'<blockquote><b>Предполагаемый выйгрыш {amount * 1.85:.2f}$\n</b></blockquote>',
        parse_mode='HTML'
    )

    message_id = bet_message.message_id
    post_link = f"{CHANNEL_URL}/{message_id}"

    await asyncio.sleep(1)
    dice_msg = await bot.send_dice(chat_id=CHANNEL_ID, emoji='🎲')
    await asyncio.sleep(4.5)

    dice_value = dice_msg.dice.value

    if bet_type == "more":
        is_win = dice_value > 3
    elif bet_type == "less":
        is_win = dice_value < 4
    elif bet_type == "even":
        is_win = dice_value % 2 == 0
    else:
        is_win = dice_value % 2 == 1

    win_amount = round(amount * 1.85, 2) if is_win else 0

    if is_win:
        video = FSInputFile('image/win.mp4')
        await bot.send_video(
            chat_id=CHANNEL_ID,
            video=video,
            caption=f'<b>Вы выйграли!</b>\n\n'
            f'<blockquote><b>{win_amount}$ зачислены на баланс в нашем боте</b></blockquote>\n\n'
            f'<a href="{INFO_CHANNEL}"><b>Наш канал </b></a>| <a href="{SUPPORT}"><b>Обратится за помощью</b></a>',
            parse_mode='HTML',
        )
    else:
        video = FSInputFile('image/lose.mp4')
        await bot.send_video(
            chat_id=CHANNEL_ID,
            video=video,
            caption=f'❌ Вы проиграли...\n\n'
            f'<blockquote><b>Удача любит настойчивых. Попробуй снова!</b></blockquote>\n\n'
            f'<a href="{INFO_CHANNEL}"><b>Наш канал </b></a>| <a href="{SUPPORT}"><b>Обратится за помощью</b></a>',
            parse_mode='HTML'
        )

    return {
        "dice_value": dice_value,
        "is_win": is_win,
        "win_amount": win_amount,
        "post_link": post_link
    }


async def post_basket_on_channel(
        bot: Bot,
        user_id: int,
        username: str,
        amount: float,
        bet_type: str,
        hide_nickname: bool = False
):
    if hide_nickname:
        display_name = "Имя скрыто"
    else:
        display_name = f"@{username}"

    bet_type_translation = {
        "goal": "гол",
        "away": "мимо",
        "stuck": "застрял",
        "clean": "чистый"
    }

    coefficient_list = {
        'goal': 1.7,
        'away': 1.3,
        'stuck': 4.6,
        'clean': 4.6
    }

    coefficient = coefficient_list[bet_type]

    bet_message = await bot.send_message(
        chat_id=CHANNEL_ID,
        text=f'<b>{display_name} ставит {amount}$ на {bet_type_translation[bet_type]}\n\n</b>'
        f'<blockquote><b>Коэффициент {coefficient}\n</b></blockquote>'
        f'<blockquote><b>Предполагаемый выйгрыш {amount * coefficient:.2f}$\n</b></blockquote>',
        parse_mode='HTML'
    )

    message_id = bet_message.message_id
    post_link = f"{CHANNEL_URL}/{message_id}"

    await asyncio.sleep(1)
    basket_msg = await bot.send_dice(chat_id=CHANNEL_ID, emoji='🏀')
    await asyncio.sleep(4.5)

    basket_value = basket_msg.dice.value

    if bet_type == "goal":
        is_win = basket_value == 4
    elif bet_type == "away":
        is_win = basket_value in [1, 2]
    elif bet_type == "stuck":
        is_win = basket_value == 3
    else:
        is_win = basket_value == 5

    win_amount = round(amount * coefficient, 2) if is_win else 0

    if is_win:
        video = FSInputFile('image/win.mp4')
        await bot.send_video(
            chat_id=CHANNEL_ID,
            video=video,
            caption=f'<b>Вы выйграли!</b>\n\n'
            f'<blockquote><b>{win_amount}$ зачислены на баланс в нашем боте</b></blockquote>\n\n'
            f'<a href="{INFO_CHANNEL}"><b>Наш канал </b></a>| <a href="{SUPPORT}"><b>Обратится за помощью</b></a>',
            parse_mode='HTML'
        )
    else:
        video = FSInputFile('image/lose.mp4')
        await bot.send_video(
            chat_id=CHANNEL_ID,
            video=video,
            caption=f'❌ Вы проиграли...\n\n'
            f'<blockquote><b>Удача любит настойчивых. Попробуй снова!</b></blockquote>\n\n'
            f'<a href="{INFO_CHANNEL}"><b>Наш канал </b></a>| <a href="{SUPPORT}"><b>Обратится за помощью</b></a>',
            parse_mode='HTML'
        )

    return {
        "dice_value": basket_value,
        "is_win": is_win,
        "win_amount": win_amount,
        "post_link": post_link
    }


async def post_football_on_channel(
        bot: Bot,
        user_id: int,
        username: str,
        amount: float,
        bet_type: str,
        hide_nickname: bool = False
):
    if hide_nickname:
        display_name = "Имя скрыто"
    else:
        display_name = f"@{username}"

    bet_type_translation = {
        "goal": "гол",
        "away": "мимо"
    }

    coefficient_list = {
        'goal': 1.3,
        'away': 1.7,
    }

    coefficient = coefficient_list[bet_type]

    bet_message = await bot.send_message(
        chat_id=CHANNEL_ID,
        text=f'<b>{display_name} ставит {amount}$ на {bet_type_translation[bet_type]}\n\n</b>'
        f'<blockquote><b>Коэффициент {coefficient}\n</b></blockquote>'
        f'<blockquote><b>Предполагаемый выйгрыш {amount * coefficient:.2f}$\n</b></blockquote>',
        parse_mode='HTML'
    )

    message_id = bet_message.message_id
    post_link = f"{CHANNEL_URL}/{message_id}"

    await asyncio.sleep(1)
    basket_msg = await bot.send_dice(chat_id=CHANNEL_ID, emoji='⚽')
    await asyncio.sleep(4.5)

    basket_value = basket_msg.dice.value

    if bet_type == "goal":
        is_win = basket_value in [3, 4, 5]
    elif bet_type == "away":
        is_win = basket_value in [1, 2]

    win_amount = round(amount * coefficient, 2) if is_win else 0

    if is_win:
        video = FSInputFile('image/win.mp4')
        await bot.send_video(
            chat_id=CHANNEL_ID,
            video=video,
            caption=f'<b>Вы выйграли!</b>\n\n'
            f'<blockquote><b>{win_amount}$ зачислены на баланс в нашем боте</b></blockquote>\n\n'
            f'<a href="{INFO_CHANNEL}"><b>Наш канал </b></a>| <a href="{SUPPORT}"><b>Обратится за помощью</b></a>',
            parse_mode='HTML'
        )
    else:
        video = FSInputFile('image/lose.mp4')
        await bot.send_video(
            chat_id=CHANNEL_ID,
            video=video,
            caption=f'❌ Вы проиграли...\n\n'
            f'<blockquote><b>Удача любит настойчивых. Попробуй снова!</b></blockquote>\n\n'
            f'<a href="{INFO_CHANNEL}"><b>Наш канал </b></a>| <a href="{SUPPORT}"><b>Обратится за помощью</b></a>',
            parse_mode='HTML'
        )

    return {
        "dice_value": basket_value,
        "is_win": is_win,
        "win_amount": win_amount,
        "post_link": post_link
    }


async def post_darts_on_channel(
        bot: Bot,
        user_id: int,
        username: str,
        amount: float,
        bet_type: str,
        hide_nickname: bool = False
):
    if hide_nickname:
        display_name = "Имя скрыто"
    else:
        display_name = f"@{username}"

    bet_type_translation = {
        "red": "красное",
        "away": "мимо",
        "white": "белое",
        "center": "центр"
    }

    coefficient_list = {
        'red': 1.7,
        'away': 2.5,
        'white': 1.7,
        'center': 2.5
    }

    coefficient = coefficient_list[bet_type]

    bet_message = await bot.send_message(
        chat_id=CHANNEL_ID,
        text=f'<b>{display_name} ставит {amount}$ на {bet_type_translation[bet_type]}\n\n</b>'
        f'<blockquote><b>Коэффициент {coefficient}\n</b></blockquote>'
        f'<blockquote><b>Предполагаемый выйгрыш {amount * coefficient:.2f}$\n</b></blockquote>',
        parse_mode='HTML'
    )

    message_id = bet_message.message_id
    post_link = f"{CHANNEL_URL}/{message_id}"

    await asyncio.sleep(1)
    darts_msg = await bot.send_dice(chat_id=CHANNEL_ID, emoji='🎯')
    await asyncio.sleep(4.5)

    darts_value = darts_msg.dice.value

    if bet_type == "away":
        is_win = darts_value == 1
    elif bet_type == "red":
        is_win = darts_value in [4, 2]
    elif bet_type == "white":
        is_win = darts_value in [3, 5]
    else:
        is_win = darts_value == 6

    win_amount = round(amount * coefficient, 2) if is_win else 0

    if is_win:
        video = FSInputFile('image/win.mp4')
        await bot.send_video(
            chat_id=CHANNEL_ID,
            video=video,
            caption=f'<b>Вы выйграли!</b>\n\n'
            f'<blockquote><b>{win_amount}$ зачислены на баланс в нашем боте</b></blockquote>\n\n'
            f'<a href="{INFO_CHANNEL}"><b>Наш канал </b></a>| <a href="{SUPPORT}"><b>Обратится за помощью</b></a>',
            parse_mode='HTML'
        )
    else:
        video = FSInputFile('image/lose.mp4')
        await bot.send_video(
            chat_id=CHANNEL_ID,
            video=video,
            caption=f'❌ Вы проиграли...\n\n'
            f'<blockquote><b>Удача любит настойчивых. Попробуй снова!</b></blockquote>\n\n'
            f'<a href="{INFO_CHANNEL}"><b>Наш канал </b></a>| <a href="{SUPPORT}"><b>Обратится за помощью</b></a>',
            parse_mode='HTML'
        )

    return {
        "dice_value": darts_value,
        "is_win": is_win,
        "win_amount": win_amount,
        "post_link": post_link
    }


async def post_bowling_on_channel(
        bot: Bot,
        user_id: int,
        username: str,
        amount: float,
        bet_type: str,
        hide_nickname: bool = False
):
    if hide_nickname:
        display_name = "Имя скрыто"
    else:
        display_name = f"@{username}"

    coefficient = 1.85
    commission = 0.05

    bet_message = await bot.send_message(
        chat_id=CHANNEL_ID,
        text=f'<b>{display_name} ставит {amount}$ на Боулинг\n\n</b>'
        f'<blockquote><b>Коэффициент {coefficient}\n</b></blockquote>'
        f'<blockquote><b>Предполагаемый выйгрыш {amount * coefficient:.2f}$\n</b></blockquote>',
        parse_mode='HTML'
    )

    message_id = bet_message.message_id
    post_link = f"{CHANNEL_URL}/{message_id}"

    await asyncio.sleep(1)
    user_msg = await bot.send_dice(chat_id=CHANNEL_ID, emoji='🎳')
    bot_msg = await bot.send_dice(chat_id=CHANNEL_ID, emoji='🎳')
    await asyncio.sleep(4.5)

    user_bowling_value = user_msg.dice.value
    bot_bowling_value = bot_msg.dice.value

    if user_bowling_value > bot_bowling_value:
        is_win = True
        is_draw = False
        win_amount = round(amount * coefficient, 2)
        video = FSInputFile('image/win.mp4')
        caption = f'<b>Вы выйграли!</b>\n\n<blockquote><b>{win_amount}$ зачислены на баланс в нашем боте</b></blockquote>\n\n<a href="{INFO_CHANNEL}"><b>Наш канал </b></a>| <a href="{SUPPORT}"><b>Обратится за помощью</b></a>'
    elif user_bowling_value < bot_bowling_value:
        is_win = False
        is_draw = False
        win_amount = 0
        video = FSInputFile('image/lose.mp4')
        caption = f'❌ Вы проиграли...\n\n<blockquote><b>Удача любит настойчивых. Попробуй снова!</b></blockquote>\n\n<a href="{INFO_CHANNEL}"><b>Наш канал </b></a>| <a href="{SUPPORT}"><b>Обратится за помощью</b></a>'
    else:
        is_win = False
        is_draw = True
        commission_amount = round(amount * commission, 2)
        return_amount = round(amount - commission_amount, 2)
        win_amount = return_amount
        video = FSInputFile('image/draw.mp4') if os.path.exists('image/draw.mp4') else FSInputFile('image/win.mp4')
        caption = f'<b>🤝 Ничья!</b>\n\n<blockquote><b>Ваша ставка возвращена с комиссией 5% ({commission_amount}$)\nВозвращено: {return_amount}$</b></blockquote>\n\n<a href="{INFO_CHANNEL}"><b>Наш канал </b></a>| <a href="{SUPPORT}"><b>Обратится за помощью</b></a>'

    await bot.send_video(
        chat_id=CHANNEL_ID,
        video=video,
        caption=caption,
        parse_mode='HTML'
    )

    return {
        "user_bowling_value": user_bowling_value,
        "bot_bowling_value": bot_bowling_value,
        "is_win": is_win,
        "is_draw": is_draw,
        "win_amount": win_amount,
        "post_link": post_link
    }
