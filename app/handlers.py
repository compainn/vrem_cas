from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
import app.keyboard as kb
import app.database.requests as rq
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config import CHANNEL_URL, INFO_CHANNEL, MIN_AMOUNT, MIN_WITHDRAWAL, MIN_DEPOSIT, ADMIN_PASSWORD, BOT_USERNAME
from app.services.cryptobot import CryptoBotAPI
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()
crypto_api = CryptoBotAPI()


class DiceStates(StatesGroup):
    waiting_bet = State()


class BasketStates(StatesGroup):
    waiting_bet = State()


class FootballStates(StatesGroup):
    waiting_bet = State()


class DartsStates(StatesGroup):
    waiting_bet = State()


class BowlingStates(StatesGroup):
    waiting_bet = State()


class DepositStates(StatesGroup):
    waiting_amount = State()


@router.message(Command('start'))
async def start(message: Message):
    args = message.text.split()
    referrer_id = None

    if len(args) > 1:
        try:
            referrer_id = int(args[1])
        except:
            pass

    await rq.set_user(message.from_user.id, message.from_user.username, referrer_id)
    await message.answer('🎄')
    await message.answer(f'<b>Добро пожаловать, @{message.from_user.username} </b>\n\n'
                         f'канал со ставками - <a href="{CHANNEL_URL}">клик</a>\n'
                         f'новостной канал - <a href="{INFO_CHANNEL}">клик</a>',
                         parse_mode='HTML',
                         disable_web_page_preview=True,
                         reply_markup=kb.main)


@router.message(Command('reset'))
async def reset_state(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Состояние сброшено")


@router.message(F.text == '👤 профиль')
async def profil(message: Message):
    user = await rq.get_user(message.from_user.id)

    if user:
        days = await rq.get_days_with_us(user.created_at)
        str_days = str(days)
        balance = float(user.balance)
        await message.answer('👤', reply_markup=kb.main)

        from run import bot

        photo = FSInputFile('image/profil.jpg')

        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption=f'<b>✦ Профиль @{user.username} ›</b>\n'
                    f'└ Баланс: <code>{balance:.2f}</code> <b>$</b>\n\n'
                    f' Вы с нами уже <code>{str_days}</code> <b>дней</b>',
            parse_mode='HTML',
            reply_markup=kb.profil
        )
    else:
        await message.answer('❌ Произошла ошибка')


@router.callback_query(F.data == 'stats')
async def stats(callback: CallbackQuery):
    user = await rq.get_user(callback.from_user.id)
    await callback.message.delete()
    if user:
        days = await rq.get_days_with_us(user.created_at)
        str_days = str(days)
        total_wagered = float(user.total_wagered)
        await callback.message.answer(f'<b>Cтатистика @{callback.from_user.username}:</b>\n\n'
                                      f'<blockquote>◉ Сыграно<b> - {user.games_played} cтавки</b>\n\n◉ Оборот <b>- {total_wagered:.2f}</b> $\n\n◉ Аккаунту - <b>{str_days} дней</b> </blockquote>\n\n'
                                      f'Пополнений <b>- {user.total_deposited:.2f}</b> $\n\n'
                                      f'Выводов <b>- {user.total_withdrawn:.2f}</b> $',
                                      parse_mode='HTML',
                                      reply_markup=kb.back_profil)


@router.callback_query(F.data == 'referrals')
async def referrals(callback: CallbackQuery):
    info = await rq.get_referral_info(callback.from_user.id)
    if info:
        await callback.message.delete()
        
        from run import bot
        
        try:
            photo = FSInputFile('image/referal.jpg')
            
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=photo,
                caption=f"<b>Реферальная программа</b>\n\n"
                        f"<blockquote>Реферальный баланс: <code>{info['referral_balance']:.2f}</code>$</blockquote>\n\n"
                        f"<blockquote>Рефералов: <code>{info['referrals_count']}</code></blockquote>\n\n"
                        f"Реферальная ссылка:\n"
                        f"<code>{info['referral_link']}</code>",
                parse_mode='HTML',
                reply_markup=kb.referral_kb
            )
        except FileNotFoundError:
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text=f"<b>Реферальная программа</b>\n\n"
                     f"<blockquote>Реферальный баланс: <code>{info['referral_balance']:.2f}</code>$</blockquote>\n\n"
                     f"<blockquote>Рефералов: <code>{info['referrals_count']}</code></blockquote>\n\n"
                     f"Реферальная ссылка:\n"
                     f"<code>{info['referral_link']}</code>",
                parse_mode='HTML',
                disable_web_page_preview=True,
                reply_markup=kb.referral_kb
            )


@router.callback_query(F.data == 'withdraw_referral')
async def withdraw_referral(callback: CallbackQuery):
    amount = await rq.withdraw_referral_balance(callback.from_user.id)
    if amount > 0:
        await callback.answer(f"✅ {amount:.2f}$ переведены на основной баланс", show_alert=True)
        await referrals(callback)
    else:
        await callback.answer("❌ Нет средств для вывода", show_alert=True)


@router.callback_query(F.data == 'settings')
async def settings(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "<b>⚙️ Настройки:</b>",
        reply_markup=kb.settings_list,
        parse_mode='HTML'
    )


@router.callback_query(F.data == 'hide_nickname')
async def hide_name(callback: CallbackQuery):
    await rq.hide_user_nickname(callback.from_user.id)
    await callback.answer("✅ никнейм скрыт")


@router.callback_query(F.data == 'show_nickname')
async def show_name(callback: CallbackQuery):
    await rq.show_user_nickname(callback.from_user.id)
    await callback.answer("✅ никнейм отображается")


@router.callback_query(F.data == 'back_profil')
async def back_profil(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await rq.get_user(callback.from_user.id)
    if user:
        await callback.message.delete()
        days = await rq.get_days_with_us(user.created_at)
        str_days = str(days)
        balance = float(user.balance)

        photo = FSInputFile('image/profil.jpg')

        from run import bot

        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=photo,
            caption=f'<b>✦ Профиль @{user.username} ›</b>\n'
                    f'└ Баланс: <code>{balance:.2f}</code> <b>$</b>\n\n'
                    f' Вы с нами: <code>{str_days}</code> <b>дней</b>',
            parse_mode='HTML',
            reply_markup=kb.profil)


@router.message(F.text == '🎲 играть')
async def game_list(message: Message):
    await message.answer_dice(emoji='🎲')
    await message.answer(
        f'<blockquote><b>Выберете игру, на которую хотите\nсделать ставку</b></blockquote>\n\nПосле оплаты, ваша ставка сыграет в нашем игровом <a href="{CHANNEL_URL}">канале</a>',
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=kb.games_list)


@router.callback_query(F.data == 'game_dice')
async def dice_list(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=kb.dice_list)


@router.callback_query(F.data == 'back_games_list')
async def back_games_list(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=kb.games_list)


@router.callback_query(F.data == 'back_games_list_2')
async def back_games_list(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f'<blockquote><b>Выберете игру, на которую хотите\nсделать ставку</b></blockquote>\n\nПосле оплаты, ваша ставка сыграет в нашем игровом <a href="{CHANNEL_URL}">канале</a>',
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=kb.games_list)


@router.callback_query(F.data.startswith('dice_'))
async def dice_choice(callback: CallbackQuery, state: FSMContext):
    user = await rq.get_user(callback.from_user.id)
    if user:
        bet_type = callback.data.split('_')[1]
        await state.update_data(bet_type=bet_type)
        await callback.message.answer('🎲 <b>Пришлите сумму для игры.</b>\n\n'
                                      f'<blockquote><b>Баланс:</b> <code>{user.balance:.2f} <b>$</b></code>\n<b>Минимум:</b> <code>{MIN_AMOUNT}</code> <b>$</b></blockquote>',
                                      parse_mode='HTML',
                                      reply_markup=kb.back_games_list)
        await state.set_state(DiceStates.waiting_bet)


@router.message(DiceStates.waiting_bet)
async def process_dice_bet(message: Message, state: FSMContext):
    user = await rq.get_user(message.from_user.id)
    if user:
        try:
            text = message.text.strip().replace(',', '.')
            amount = float(text)
            
            if amount < MIN_AMOUNT:
                await message.answer(f'❌ <b>мин: {MIN_AMOUNT}</b> $', parse_mode='HTML')
                return

            balance = user.balance
            if amount > balance:
                await message.answer('❌ <b>недостаточно средств</b> (профиль -> пополнить)\n'
                                     f'<b>текущий баланс:</b> <code>{balance:.2f}</code> <b>$</b>', parse_mode='HTML')
                return

            data = await state.get_data()
            bet_type = data["bet_type"]
            hide_nickname = user.hide_username if hasattr(user, 'hide_username') else False

            await state.clear()

            from run import bot
            msg = await message.answer("💸")

            result = await rq.play_dice_game(
                bot=bot,
                user_id=message.from_user.id,
                username=message.from_user.username,
                amount=amount,
                bet_type=bet_type,
                hide_nickname=hide_nickname,
                message=msg
            )

        except ValueError:
            await message.answer("❗ Введите число (используйте точку или запятую)")


@router.callback_query(F.data == 'game_basketball')
async def basketball_choice(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=kb.basketball_list)


@router.callback_query(F.data.startswith('basket_'))
async def basket_choice(callback: CallbackQuery, state: FSMContext):
    user = await rq.get_user(callback.from_user.id)
    if user:
        bet_type = callback.data.split('_')[1]
        await state.update_data(bet_type=bet_type)
        await callback.message.answer('🎲 <b>Пришлите сумму для игры.</b>\n\n'
                                      f'<blockquote><b>Баланс:</b> <code>{user.balance:.2f}</code> <b>$</b>\n<b>Минимум:</b> <code>{MIN_AMOUNT}</code> <b>$</b></blockquote>',
                                      parse_mode='HTML',
                                      reply_markup=kb.back_games_list)
        await state.set_state(BasketStates.waiting_bet)


@router.message(BasketStates.waiting_bet)
async def process_basket_bet(message: Message, state: FSMContext):
    user = await rq.get_user(message.from_user.id)
    if user:
        try:
            text = message.text.strip().replace(',', '.')
            amount = float(text)
            
            if amount < MIN_AMOUNT:
                await message.answer(f'❌ <b>мин: {MIN_AMOUNT}</b>', parse_mode='HTML')
                return

            balance = user.balance
            if amount > balance:
                await message.answer('❌ <b>недостаточно средств</b>\n'
                                     f'<b>текущий баланс:</b> <code>{balance:.2f}</code>', parse_mode='HTML')
                return

            data = await state.get_data()
            bet_type = data["bet_type"]
            hide_nickname = user.hide_username if hasattr(user, 'hide_username') else False

            await state.clear()

            from run import bot
            msg = await message.answer("💸")

            result = await rq.play_basket_game(
                bot=bot,
                user_id=message.from_user.id,
                username=message.from_user.username,
                amount=amount,
                bet_type=bet_type,
                hide_nickname=hide_nickname,
                message=msg
            )

        except ValueError:
            await message.answer("<b>❗ Введите число (используйте точку или запятую)</b>", parse_mode='HTML')


@router.callback_query(F.data == 'game_football')
async def football_choice(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=kb.football_list)


@router.callback_query(F.data.startswith('football_'))
async def football_choice(callback: CallbackQuery, state: FSMContext):
    user = await rq.get_user(callback.from_user.id)
    if user:
        bet_type = callback.data.split('_')[1]
        await state.update_data(bet_type=bet_type)
        await callback.message.answer('🎲 <b>Пришлите сумму для игры.</b>\n\n'
                                      f'<blockquote><b>Баланс:</b> <code>{user.balance:.2f}</code>\n<b>Минимум:</b> <code>{MIN_AMOUNT}</code> <b>$</b></blockquote>',
                                      parse_mode='HTML',
                                      reply_markup=kb.back_games_list)
        await state.set_state(FootballStates.waiting_bet)


@router.message(FootballStates.waiting_bet)
async def process_football_bet(message: Message, state: FSMContext):
    user = await rq.get_user(message.from_user.id)
    if user:
        try:
            text = message.text.strip().replace(',', '.')
            amount = float(text)
            
            if amount < MIN_AMOUNT:
                await message.answer(f'❌ <b>мин: {MIN_AMOUNT}$</b>', parse_mode='HTML')
                return

            balance = user.balance
            if amount > balance:
                await message.answer('❌ <b>недостаточно средств</b>\n'
                                     f'<b>текущий баланс:</b> <code>{balance:.2f}</code>', parse_mode='HTML')
                return

            data = await state.get_data()
            bet_type = data["bet_type"]
            hide_nickname = user.hide_username if hasattr(user, 'hide_username') else False

            await state.clear()

            from run import bot
            msg = await message.answer("💸")

            result = await rq.play_football_game(
                bot=bot,
                user_id=message.from_user.id,
                username=message.from_user.username,
                amount=amount,
                bet_type=bet_type,
                hide_nickname=hide_nickname,
                message=msg
            )

        except ValueError:
            await message.answer("<b>❗ Введите число (используйте точку или запятую)</b>", parse_mode='HTML')


@router.callback_query(F.data == 'game_darts')
async def darts_choice(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=kb.darts_list)


@router.callback_query(F.data.startswith('darts_'))
async def darts_choice(callback: CallbackQuery, state: FSMContext):
    user = await rq.get_user(callback.from_user.id)
    if user:
        bet_type = callback.data.split('_')[1]
        await state.update_data(bet_type=bet_type)
        await callback.message.answer('🎲 <b>Пришлите сумму для игры.</b>\n\n'
                                      f'<blockquote><b>Баланс:</b> <code>{user.balance:.2f}</code>\n<b>Минимум:</b> <code>{MIN_AMOUNT}</code> </blockquote>',
                                      parse_mode='HTML',
                                      reply_markup=kb.back_games_list)
        await state.set_state(DartsStates.waiting_bet)


@router.message(DartsStates.waiting_bet)
async def process_darts_bet(message: Message, state: FSMContext):
    user = await rq.get_user(message.from_user.id)
    if user:
        try:
            text = message.text.strip().replace(',', '.')
            amount = float(text)
            
            if amount < MIN_AMOUNT:
                await message.answer(f'❌ <b>мин: {MIN_AMOUNT}$</b>', parse_mode='HTML')
                return

            balance = user.balance
            if amount > balance:
                await message.answer('❌ <b>недостаточно средств</b>\n'
                                     f'<b>текущий баланс:</b> <code>{balance}</code>', parse_mode='HTML')
                return

            data = await state.get_data()
            bet_type = data["bet_type"]
            hide_nickname = user.hide_username if hasattr(user, 'hide_username') else False

            await state.clear()

            from run import bot
            msg = await message.answer("💸")

            result = await rq.play_darts_game(
                bot=bot,
                user_id=message.from_user.id,
                username=message.from_user.username,
                amount=amount,
                bet_type=bet_type,
                hide_nickname=hide_nickname,
                message=msg
            )

        except ValueError:
            await message.answer("<b>❗ Введите число (используйте точку или запятую)</b>", parse_mode='HTML')


@router.callback_query(F.data == 'game_bowling')
async def bowling_choice(callback: CallbackQuery, state: FSMContext):
    user = await rq.get_user(callback.from_user.id)
    if user:
        await state.update_data(bet_type='bowling')
        await callback.message.answer('🎲 <b>Пришлите сумму для игры.</b>\n\n'
                                      f'<blockquote><b>Баланс:</b> <code>{user.balance:.2f}</code>\n<b>Минимум:</b> <code>{MIN_AMOUNT}</code> </blockquote>',
                                      parse_mode='HTML',
                                      reply_markup=kb.back_games_list)
        await state.set_state(BowlingStates.waiting_bet)


@router.message(BowlingStates.waiting_bet)
async def process_bowling_bet(message: Message, state: FSMContext):
    user = await rq.get_user(message.from_user.id)
    if user:
        try:
            text = message.text.strip().replace(',', '.')
            amount = float(text)
            
            if amount < MIN_AMOUNT:
                await message.answer(f'❌ <b>мин: {MIN_AMOUNT}</b>', parse_mode='HTML')
                return

            balance = user.balance
            if amount > balance:
                await message.answer('❌ <b>недостаточно средств</b> (профиль -> пополнить)\n'
                                     f'<b>текущий баланс:</b> <code>{balance}</code>', parse_mode='HTML')
                return

            data = await state.get_data()
            bet_type = 'bowling'
            hide_nickname = user.hide_username if hasattr(user, 'hide_username') else False

            await state.clear()

            from run import bot
            msg = await message.answer("💸")

            result = await rq.play_bowling_game(
                bot=bot,
                user_id=message.from_user.id,
                username=message.from_user.username,
                amount=amount,
                bet_type=bet_type,
                hide_nickname=hide_nickname,
                message=msg
            )

        except ValueError:
            await message.answer("<b>❗ Введите число (используйте точку или запятую)</b>", parse_mode='HTML')


@router.callback_query(F.data == 'deposit')
async def deposit_input_amount(callback: CallbackQuery, state: FSMContext):
    user = await rq.get_user(callback.from_user.id)
    balance = user.balance if user else 0
    await callback.message.delete()
    await callback.message.answer(
        f"<b>Введите сумму для пополнения:</b>\n\n"
        f"<blockquote><b>Минимум:</b> <code>{MIN_DEPOSIT}</code></blockquote>\n\n"
        f"<i>Введите сумму:</i>",
        parse_mode='HTML',
        reply_markup=kb.back_profil
    )
    await state.set_state(DepositStates.waiting_amount)


@router.message(DepositStates.waiting_amount)
async def process_deposit_amount(message: Message, state: FSMContext):
    try:
        text = message.text.strip().replace(',', '.')
        amount = float(text)

        if amount < MIN_DEPOSIT:
            await message.answer(f"❌ Минимальная сумма: {MIN_DEPOSIT}$")
            return

        invoice = await crypto_api.create_invoice(
            user_id=message.from_user.id,
            amount=amount
        )

        if not invoice:
            await message.answer("❌ Ошибка создания счета")
            return

        await rq.create_invoice(
            user_id=message.from_user.id,
            invoice_id=invoice["invoice_id"],
            pay_url=invoice["pay_url"],
            amount=amount
        )

        await message.answer(
            f"✅ <b>Счет на {amount}$ создан!</b>\n\n"
            f"Нажмите кнопку ниже для оплаты:\n",
            parse_mode='HTML',
            reply_markup=kb.get_deposit_kb(invoice["pay_url"])
        )

        await state.clear()

    except ValueError:
        await message.answer("❗ Введите число (используйте точку или запятую)")


@router.callback_query(F.data == 'check_payment')
async def check_payment(callback: CallbackQuery):
    checking_msg = await callback.message.answer("🔍 <b>Проверяем платеж...</b>", parse_mode='HTML')

    invoice = await rq.get_last_invoice(callback.from_user.id)
    if not invoice or invoice.status != 'pending':
        await checking_msg.delete()
        await callback.answer("Нет активных счетов", show_alert=True)
        return

    status = await crypto_api.check_invoice(invoice.invoice_id)
    await checking_msg.delete()

    if not status:
        await callback.answer("Ошибка проверки", show_alert=True)
        return

    if status["status"] == "paid":
        amount = float(status["amount"])

        if amount < MIN_DEPOSIT:
            await callback.answer("❌ Сумма меньше минимальной", show_alert=True)
            return

        await rq.add_balance(callback.from_user.id, amount, tr_type="deposit")
        await rq.update_invoice(invoice.invoice_id, "paid", amount)

        user = await rq.get_user(callback.from_user.id)

        await callback.message.edit_text(
            f"✅ <b>Пополнение на {amount:.2f}$ успешно!</b>\n\n"
            f"<b>Текущий баланс:</b> <code>{user.balance:.2f}</code> $",
            parse_mode='HTML'
        )

    elif status["status"] == "active":
        await callback.answer("❌ Счет не оплачен", show_alert=True)

    elif status["status"] == "expired":
        await callback.answer("❌ Счет просрочен", show_alert=True)
        await rq.update_invoice(invoice.invoice_id, "expired")

    else:
        await callback.answer(f"Статус: {status['status']}", show_alert=True)


@router.callback_query(F.data == 'withdraw')
async def withdraw_handler(callback: CallbackQuery):
    user = await rq.get_user(callback.from_user.id)

    if not user:
        await callback.answer("❌ Ошибка")
        return

    if user.balance < MIN_WITHDRAWAL:
        await callback.answer(
            f"❌ Мин вывод: {MIN_WITHDRAWAL}$\nВаш баланс: {user.balance:.2f}$",
            show_alert=True
        )
        return

    await callback.message.delete()

    await callback.message.answer(
        f"<b>📤 Вывод средств</b>\n\n"
        f"<b>Баланс:</b> <code>{user.balance:.2f}</code> $\n"
        f"<b>Мин вывод:</b> <code>{MIN_WITHDRAWAL}</code> $\n\n",
        parse_mode='HTML',
        reply_markup=kb.withdraw_kb
    )


@router.callback_query(F.data == 'confirm_withdraw')
async def confirm_withdraw(callback: CallbackQuery):
    user = await rq.get_user(callback.from_user.id)

    if not user or user.balance < MIN_WITHDRAWAL:
        await callback.answer("❌ Недостаточно средств")
        return

    check = await crypto_api.create_check(
        user_id=callback.from_user.id,
        amount=user.balance
    )

    if not check:
        await callback.answer("❌ Ошибка создания чека", show_alert=True)
        return

    await rq.create_check_record(
        user_id=callback.from_user.id,
        check_id=check["check_id"],
        check_url=check["bot_check_url"],
        amount=user.balance
    )

    await rq.add_balance(callback.from_user.id, -user.balance, tr_type="withdraw")
    await rq.update_total_withdrawn(callback.from_user.id, user.balance)

    await callback.message.delete()

    await callback.message.answer(
        f"✅ <b>Чек создан!</b>\n\n"
        f"Сумма: <code>{user.balance:.2f}</code> $\n\n",
        parse_mode='HTML',
        reply_markup=kb.get_withdraw_success_kb(check["bot_check_url"]))


@router.message(Command('get_admin'))
async def get_admin_command(message: Message):
    try:
        password = message.text.split()[1]
        if password == ADMIN_PASSWORD:
            success = await rq.make_admin(message.from_user.id)
            if success:
                await message.answer(
                    "✅ Вы получили права администратора!\n"
                    "Теперь вам доступна команда /admin"
                )
            else:
                await message.answer("")
        else:
            await message.answer("")
    except IndexError:
        await message.answer("")
    except Exception as e:
        await message.answer(f"")


@router.message(Command('admin'))
async def admin_panel_command(message: Message):
    is_admin = await rq.is_admin_user(message.from_user.id)
    if not is_admin:
        await message.answer("")
        return

    total_users = await rq.get_total_users()
    today_deposits = await rq.get_today_deposits()

    try:
        today_deposits_invoices = await rq.get_today_deposits_from_invoices()
        deposits_text = f"<code>{today_deposits_invoices:.2f}</code> $"
    except:
        deposits_text = f"<code>{today_deposits:.2f}</code> $"

    await message.answer(
        f"★ <b>Админ панель</b>\n\n"
        f"◆ <b>Статистика:</b>\n"
        f"├  Пользователей: <code>{total_users}</code>\n"
        f"└  Депозиты сегодня: {deposits_text}\n\n"
        f"<b>Доступные команды:</b>\n"
        f"• /add_balance [id] [сумма] - добавить баланс\n"
        f"• /delete_balance [id] - обнулить баланс\n\n",
        parse_mode='HTML'
    )


@router.message(Command('add_balance'))
async def add_balance_admin(message: Message):
    is_admin = await rq.is_admin_user(message.from_user.id)
    if not is_admin:
        await message.answer("❌ У вас нет прав администратора")
        return

    try:
        args = message.text.split()
        if len(args) != 3:
            await message.answer("❌ Использование: /add_balance ID сумма")
            return

        user_id = int(args[1])
        amount = float(args[2])

        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0")
            return

        new_balance = await rq.add_balance_to_user(user_id, amount)

        if new_balance is not None:
            await message.answer(
                f"✅ Баланс пользователя <code>{user_id}</code> пополнен на <code>{amount:.2f}</code> $\n\n"
                f"Новый баланс: <code>{new_balance:.2f}</code> $",
                parse_mode='HTML'
            )
        else:
            await message.answer(f"❌ Пользователь с ID <code>{user_id}</code> не найден", parse_mode='HTML')

    except ValueError:
        await message.answer("❌ Неверный формат. ID и сумма должны быть числами")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(Command('delete_balance'))
async def delete_balance_admin(message: Message):
    is_admin = await rq.is_admin_user(message.from_user.id)
    if not is_admin:
        await message.answer("❌ У вас нет прав администратора")
        return

    try:
        args = message.text.split()
        if len(args) != 2:
            await message.answer("❌ Использование: /delete_balance ID")
            return

        user_id = int(args[1])

        old_balance = await rq.delete_balance_from_user(user_id)

        if old_balance is not None:
            await message.answer(
                f"✅ Баланс пользователя <code>{user_id}</code> обнулен\n\n"
                f"Было на счету: <code>{old_balance:.2f}</code> $\n"
                f"Теперь баланс: <code>0.00</code> $",
                parse_mode='HTML'
            )
        else:
            await message.answer(f"❌ Пользователь с ID <code>{user_id}</code> не найден", parse_mode='HTML')

    except ValueError:
        await message.answer("❌ Неверный формат. ID должен быть числом")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
