from aiogram import Router, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.config import TORTOISE_ORM, FIRST_ADMIN, SECOND_ADMIN
from bot.db import models
from tortoise import Tortoise

router = Router()

class ProccesDeleteForm(StatesGroup):
    phone = State()
    confirm = State()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Sí")],
        [KeyboardButton(text="No")],
    ],
    resize_keyboard=True
)

async def delete_user(message, state):
    data = await state.get_data()
    user = data.get("user")

    await models.User.filter(id=user.id).delete()
    await message.answer(f"✅ Usuario correctamente <b>eliminado</b>.", reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML')


@router.message(Command(commands=["rechazar"]), ProccesDeleteForm.phone)
async def cancel_sell_handler(message: Message, state: FSMContext):
    await message.answer("Operación cancelada.")
    await state.clear()  # Limpiar el estado para cancelar la operación
    
@router.message(Command(commands=["eliminar"]))
async def analysis_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    print(user_id, )
    if user_id not in [int(FIRST_ADMIN)]:
        print("d")
        return
    await message.answer("Para eliminar a un usuario, debes de introducir su <b>teléfono</b>.", parse_mode='HTML')
    await message.answer("Teléfono:")
    await state.set_state(ProccesDeleteForm.phone)

@router.message(ProccesDeleteForm.phone)
async def phone_to_delete(message: Message, state: FSMContext):
    phone = message.text

    await Tortoise.init(TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)
    try:
        user = await models.User.filter(phone=phone).first()  
    except Exception as e:
        print(f"Error fetching data: {e}")
        return
    user_data = (
        f"Nombre: <b>{user.name}</b>\n"
        f"Teléfono: <b>{user.phone}</b>\n"
    )
    await message.answer(f"¿Estás seguro de <b>eliminar</b> al siguiente usuario?\{user_data}", reply_markup=keyboard, parse_mode='HTML')
    await state.update_data(user=user)
    await state.set_state(ProccesDeleteForm.confirm)



@router.message(ProccesDeleteForm.confirm)
async def confim_to_sell(message: Message, state: FSMContext):
    response = message.text.lower()
    print(response)
    if response in ["si", "sí"]:
        await delete_user(message, state)
        await state.clear()  # Limpiar el estado después de completar la compra
    else:
        await message.answer("Operación cancelada.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()