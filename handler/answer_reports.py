from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, callback_query
from aiogram.types.callback_query import CallbackQuery
from keyboards.main_menu import menu_kb, team_kb, access_payment_kb
from lexicon.lexicon import LEXICON
from config_data.config import Config, load_config
from services.services import is_admin, is_senior_moderator, is_moderator
from database.users import game_users
from database.teams import teams
import pymysql.cursors
from mysql.connector import connect, Error
from database.conection import connection
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot


config: Config = load_config()


router = Router()


class AnsReport(StatesGroup):
    text_answer = State()


@router.message(Command('ans_report'))
async def process_ans_report(message: Message, state: FSMContext):
    if is_admin(message.from_user.id) or is_senior_moderator(message.from_user.id) or is_moderator(message.from_user.id):
        if not game_users[message.from_user.id]['in_play']:
            try:
                with connection.cursor() as cursor:
                    select_query = "SELECT * FROM `reports`;"
                    cursor.execute(select_query)
                    rows = cursor.fetchall()

                if len(rows) <= 0:
                    await message.answer(text='Жалоб в данный момент нет')

                else:
                    await message.answer(text=rows[0]['text'])
                    await state.set_state(AnsReport.text_answer)

            except Exception as es:
                await message.answer(text=f'Ошибка: {es}. Пожалуйста перешлите это письмо в тех. поддержку')

        else:
            await message.answer(text='Вы в игре!')

    else:
        await message.answer(text=LEXICON['other_message'])


@router.message(F.text, AnsReport.text_answer)
async def process_text_report(message: Message, state: FSMContext, bot: Bot):
    try:
        with connection.cursor() as cursor:
            select_query = "SELECT * FROM `reports`;"
            cursor.execute(select_query)
            rows = cursor.fetchall()

        await bot.send_message(chat_id=rows[0]['user_id'], text=message.text)
        with connection.cursor() as cursor:
            del_report = f"DELETE FROM reports WHERE user_id={rows[0]['user_id']};"
            cursor.execute(del_report)
            connection.commit()

        await message.answer(text='Жалоба обработана, чтобы продолжить команда: /ans_report')
        await state.clear()

    except Exception as es:
        await message.answer(text=f'Ошибка: {es}. Пожалуйста перешлите это письмо в тех. поддержку')
