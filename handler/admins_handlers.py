from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, callback_query
from aiogram.types.callback_query import CallbackQuery
from keyboards.main_menu import menu_kb, role_for_admins_kb, close_kb, access_kb, role_for_senior_kb
from lexicon.lexicon import LEXICON
from config_data.config import Config, load_config
from services.services import is_admin, is_user_id, is_moderator, is_senior_moderator
from database.users import game_users
from database.conection import connection
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot


config: Config = load_config()


router = Router()


class SetPlayerRole(StatesGroup):
    choosing_id = State()
    choosing_role = State()
    access_set_role = State()


@router.message(Command('set_role'))
async def process_set_role(message: Message, state: FSMContext):
    if is_admin(message.from_user.id) or is_senior_moderator(message.from_user.id):
        if not game_users[message.from_user.id]['in_play']:
            await message.answer(text='Пожалуйста впишите id пользователья (чтобы выставить его роль он должен хоть раз запустить бота)', reply_markup=close_kb)
            await state.set_state(SetPlayerRole.choosing_id)
        else:
            await message.answer(text='Вы в игре')
    else:
        await message.answer(text=LEXICON['other_message'])


@router.message(F.text, SetPlayerRole.choosing_id)
async def process_choosing_id(message: Message, state: FSMContext):
    if is_user_id(message.text):
        if is_admin(int(message.text)):
            await message.answer(text='Вы не можете понизить админа')
        else:
            if is_admin(message.from_user.id):
                await state.update_data(user_id=int(message.text))
                await message.answer(text='Пожалуйста выберите роль:', reply_markup=role_for_admins_kb)
                await state.set_state(SetPlayerRole.choosing_role)
            elif is_senior_moderator(message.from_user.id):
                await state.update_data(user_id=int(message.text))
                await message.answer(text='Пожалуйста выберите роль:', reply_markup=role_for_senior_kb)
                await state.set_state(SetPlayerRole.choosing_role)
            else:
                await message.answer(text='У вас недостаточно прав')
    else:
        await message.answer(text='Вы вписали id в неправильном формате или он еще не запускал бота. Попробуйте еще раз:')


@router.callback_query(F.data == 'close_set_role')
async def process_close_set_role(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text='Главное меню: ', reply_markup=menu_kb)
    await state.clear()


@router.callback_query(F.data.startswith('role_'), SetPlayerRole.choosing_role)
async def process_set_role_player(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    with connection.cursor() as cursor:
        your_role = f'SELECT * FROM users WHERE id = {call.from_user.id}'
        cursor.execute(your_role)
        user = cursor.fetchall()
    await call.message.answer(text=f"Вы хотите выставить человеку: {user_data['user_id']} роль: {LEXICON[call.data]}", reply_markup=access_kb)
    await state.update_data(role=int(call.data[5]))
    await state.set_state(SetPlayerRole.access_set_role)


@router.callback_query(F.data == 'access_set_role', SetPlayerRole.access_set_role)
async def process_access_role(call: CallbackQuery, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    try:
        with connection.cursor() as cursor:
            set_role = f"UPDATE users SET role = {user_data['role']} WHERE id = {user_data['user_id']};"
            cursor.execute(set_role)
            connection.commit()

        game_users[user_data['user_id']]['role'] = user_data['role']

        await call.message.answer(text='Подтверждено')
        await bot.send_message(chat_id=user_data['user_id'], text=("У вас установлена роль: " + LEXICON[f"role_{user_data['role']}"]))

    except Exception as es:
        await call.message.answer(text=f'Ошибка: {es}. Пожалуйста перешлите это письмо в тех. поддержку')






