from aiogram import Bot
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from keyboards.main_menu import menu_kb
from database.users import game_users
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, callback_query
from aiogram.types.callback_query import CallbackQuery
from database.conection import connection


router = Router()


@router.callback_query(F.data == 'Access_Payment')
async def process_order(call: CallbackQuery, bot: Bot):
    await bot.send_invoice(chat_id=call.message.chat.id,
                           title='Купить билет',
                           description='Покупка билета ',
                           provider_token='381764678:TEST:94256',
                           currency='RUB',
                           prices=[
                               LabeledPrice(
                                   label='Билет',
                                   amount=50000
                               ),
                               LabeledPrice(
                                   label='НДС',
                                   amount=10000
                               ),
                               LabeledPrice(
                                   label='Бонус',
                                   amount=-5000
                               ),
                               LabeledPrice(
                                   label='Скидка',
                                   amount=-10000
                               )
                           ],
                           is_flexible=False,
                           payload='Ticket for quest',
                           photo_url='https://s0.rbk.ru/v6_top_pics/media/img/4/04/346843326750044.jpg',
                           max_tip_amount=10000,
                           suggested_tip_amounts=[123, 456, 789, 800]
                           )


@router.pre_checkout_query()
async def pre_checkout_q(pre_checkout_qu: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_qu.id, ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    try:
        with connection.cursor() as cursor:
            edit_payed = f'UPDATE users SET payed = 1 WHERE id = {message.from_user.id};'
            edit_team = f'UPDATE users SET team = {game_users[message.from_user.id]["pre_team"]} WHERE id = {message.from_user.id};'
            cursor.execute(edit_payed)
            connection.commit()
            cursor.execute(edit_team)
            connection.commit()

        game_users[message.from_user.id]['payed'] = True
        game_users[message.from_user.id]['team'] = game_users[message.from_user.id]['pre_team']
        await message.answer(text='Спасибо за покупку билета', reply_markup=menu_kb)


    except Exception as es:
        await message.answer(text=f'Ошибка: {es}. Перешлите это сообщение в поддержку')




