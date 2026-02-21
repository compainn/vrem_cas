from app.database.models import async_session, User
from app.database.models import Invoice
from sqlalchemy import select, func, and_
from datetime import datetime, date
from app.utils.posts_on_channel import (post_dice_on_channel,
                                        post_basket_on_channel,
                                        post_football_on_channel,
                                        post_darts_on_channel,
                                        post_bowling_on_channel)
import app.keyboard as kb


async def set_user(tg_id, username, referrer_id=None):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            user = User(tg_id=tg_id, username=username)

            if referrer_id and referrer_id != tg_id:
                referrer = await session.scalar(select(User).where(User.tg_id == referrer_id))
                if referrer:
                    user.referrer_id = referrer_id
                    referrer.referrals_count += 1

            session.add(user)
            await session.commit()


async def get_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user


async def get_days_with_us(created_at):
    now = datetime.now()
    time_passed = now - created_at
    days = time_passed.days
    if days < 1:
        days = 1
    return days


async def add_balance(tg_id: int, amount: float, tr_type: str = "other"):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            user = User(tg_id=tg_id)
            session.add(user)
            await session.commit()

        user.balance += amount

        if tr_type == "deposit" and amount > 0:
            user.total_deposited += amount
        elif tr_type == "bet" and amount < 0:
            user.games_played = (user.games_played or 0) + 1
            user.total_wagered = (user.total_wagered or 0) + abs(amount)
        elif tr_type == "referral" and amount > 0:
            user.referral_balance += amount

        await session.commit()


async def add_referral_earnings(referrer_id: int, amount: float):
    if not referrer_id:
        return

    async with async_session() as session:
        referrer = await session.scalar(select(User).where(User.tg_id == referrer_id))
        if referrer:
            commission = amount * 0.1
            referrer.referral_balance += commission
            await session.commit()


async def process_bet_result(user_id: int, amount: float, is_win: bool):
    if not is_win:
        return

    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        if user and user.referrer_id:
            await add_referral_earnings(user.referrer_id, amount)


async def delete_balance(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            user = User(tg_id=tg_id)
            session.add(user)
            await session.commit()

        user.balance = 0.0
        await session.commit()


async def update_total_withdrawn(user_id: int, amount: float):
    async with async_session() as session:
        from sqlalchemy import select
        from app.database.models import User

        user = await session.scalar(select(User).where(User.tg_id == user_id))
        if user:
            user.total_withdrawn = (user.total_withdrawn or 0) + amount
            await session.commit()


async def hide_user_nickname(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.hide_username = True
            await session.commit()
            return True
        return False


async def show_user_nickname(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.hide_username = False
            await session.commit()
            return True
        return False


async def play_dice_game(bot, user_id, username, amount, bet_type, hide_nickname=False, message=None):
    await add_balance(user_id, -amount, tr_type="bet")
    result = await post_dice_on_channel(bot, user_id, username, amount, bet_type, hide_nickname)

    if message:
        await message.edit_text("👌")
        await message.answer("Ваша ставка", reply_markup=kb.create_bet_button(result["post_link"]))

    if result["is_win"]:
        win_amount = result["win_amount"]
        await add_balance(user_id, win_amount, tr_type="win")
        await process_bet_result(user_id, win_amount, True)

    return result


async def play_basket_game(bot, user_id, username, amount, bet_type, hide_nickname=False, message=None):
    await add_balance(user_id, -amount, tr_type="bet")
    result = await post_basket_on_channel(bot, user_id, username, amount, bet_type, hide_nickname)

    if message:
        await message.edit_text("👌")
        await message.answer("Ваша ставка", reply_markup=kb.create_bet_button(result["post_link"]))

    if result["is_win"]:
        win_amount = result["win_amount"]
        await add_balance(user_id, win_amount, tr_type="win")
        await process_bet_result(user_id, win_amount, True)

    return result


async def play_football_game(bot, user_id, username, amount, bet_type, hide_nickname=False, message=None):
    await add_balance(user_id, -amount, tr_type="bet")
    result = await post_football_on_channel(bot, user_id, username, amount, bet_type, hide_nickname)

    if message:
        await message.edit_text("👌")
        await message.answer("Ваша ставка", reply_markup=kb.create_bet_button(result["post_link"]))

    if result["is_win"]:
        win_amount = result["win_amount"]
        await add_balance(user_id, win_amount, tr_type="win")
        await process_bet_result(user_id, win_amount, True)

    return result


async def play_darts_game(bot, user_id, username, amount, bet_type, hide_nickname=False, message=None):
    await add_balance(user_id, -amount, tr_type="bet")
    result = await post_darts_on_channel(bot, user_id, username, amount, bet_type, hide_nickname)

    if message:
        await message.edit_text("👌")
        await message.answer("Ваша ставка", reply_markup=kb.create_bet_button(result["post_link"]))

    if result["is_win"]:
        win_amount = result["win_amount"]
        await add_balance(user_id, win_amount, tr_type="win")
        await process_bet_result(user_id, win_amount, True)

    return result


async def play_bowling_game(bot, user_id, username, amount, bet_type, hide_nickname=False, message=None):
    await add_balance(user_id, -amount, tr_type="bet")
    result = await post_bowling_on_channel(bot, user_id, username, amount, bet_type, hide_nickname)

    if message:
        await message.edit_text("👌")
        await message.answer("Ваша ставка", reply_markup=kb.create_bet_button(result["post_link"]))

    if result.get("is_draw", False):
        return_amount = result["win_amount"]
        await add_balance(user_id, return_amount, tr_type="draw_return")
    elif result["is_win"]:
        win_amount = result["win_amount"]
        await add_balance(user_id, win_amount, tr_type="win")
        await process_bet_result(user_id, win_amount, True)

    return result


async def create_invoice(user_id: int, invoice_id: str, pay_url: str, amount: float = None):
    async with async_session() as session:
        from app.database.models import Invoice
        invoice = Invoice(
            user_id=user_id,
            invoice_id=invoice_id,
            pay_url=pay_url,
            amount=amount,
            status='pending'
        )
        session.add(invoice)
        await session.commit()
        return invoice


async def create_check_record(user_id: int, check_id: str, check_url: str, amount: float):
    async with async_session() as session:
        from app.database.models import CheckRecord
        check = CheckRecord(
            user_id=user_id,
            check_id=check_id,
            check_url=check_url,
            amount=amount,
            status='active'
        )
        session.add(check)
        await session.commit()
        return check


async def get_last_invoice(user_id: int):
    async with async_session() as session:
        from app.database.models import Invoice
        from sqlalchemy import select
        result = await session.execute(
            select(Invoice)
            .where(Invoice.user_id == user_id)
            .order_by(Invoice.id.desc())
        )
        return result.scalar()


async def update_invoice(invoice_id: str, status: str, amount: float = None):
    async with async_session() as session:
        from app.database.models import Invoice
        from sqlalchemy import update
        await session.execute(
            update(Invoice)
            .where(Invoice.invoice_id == invoice_id)
            .values(status=status, amount=amount)
        )
        await session.commit()


async def get_total_users():
    async with async_session() as session:
        result = await session.execute(select(func.count(User.id)))
        return result.scalar()


async def get_today_deposits():
    async with async_session() as session:
        result = await session.execute(
            select(func.sum(User.total_deposited))
        )
        total = result.scalar()
        return total if total else 0.0


async def get_today_deposits_from_invoices():
    try:
        async with async_session() as session:
            today = date.today()
            result = await session.execute(
                select(func.sum(Invoice.amount)).where(
                    and_(
                        Invoice.status == 'paid',
                        func.date(Invoice.created_at) == today
                    )
                )
            )
            total = result.scalar()
            return total if total else 0.0
    except:
        return 0.0


async def is_admin_user(tg_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        user = result.scalar_one_or_none()
        if user and user.is_admin:
            return True
        return False


async def make_admin(tg_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.is_admin = True
            await session.commit()
            return True
        return False


async def add_balance_to_user(user_id: int, amount: float):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.tg_id == user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            old_balance = user.balance
            user.balance += amount
            user.total_deposited += amount
            await session.commit()
            return old_balance + amount
        return None


async def delete_balance_from_user(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.tg_id == user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            old_balance = user.balance
            user.balance = 0.0
            await session.commit()
            return old_balance
        return None


async def get_referral_info(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return {
                "referral_balance": user.referral_balance,
                "referrals_count": user.referrals_count,
                "referral_link": f"https://t.me/{(await get_bot_username())}?start={tg_id}"
            }
        return None


async def withdraw_referral_balance(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user and user.referral_balance > 0:
            amount = user.referral_balance
            user.balance += amount
            user.referral_balance = 0
            await session.commit()
            return amount
        return 0


async def get_bot_username():
    from config import BOT_USERNAME
    return BOT_USERNAME
