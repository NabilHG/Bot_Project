from aiogram import Router, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from tortoise import Tortoise
from bot.config import TORTOISE_ORM
from bot.db import models
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class UpdateForm(StatesGroup):
    select = State()
    name = State()
    phone = State()
    investor_profile = State()
    current_capital = State()

keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Conservador")],
            [KeyboardButton(text="Medio")],
            [KeyboardButton(text="Atrevido")]
        ],
        resize_keyboard=True
    )

@router.message(Command(commands=["cancelar"]))
async def cancel_update_handler(message: Message, state: FSMContext):
    await message.answer("Operación cancelada.", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()  # Limpiar el estado para cancelar la operación

@router.message(Command(commands=["actualizar"]))
async def udpate_profile_handler(message: Message, state:FSMContext):
    await Tortoise.init(TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)

    id = message.from_user.id
    try:
        user = await models.User.filter(id=id).first()  
        wallet = await models.Wallet.filter(user_id=user.id).first()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return
    
    await state.update_data(user=user, wallet=wallet)

    investor_map = {0.2: "Conservador", 0.4: "Medio", 0.6: "Atrevido"}
    investor_profile = investor_map.get(user.investor_profile)
    msg = (
            f"<b>1</b> - Nombre: {user.name}\n"
            f"<b>2</b> - Teléfono: {user.phone}\n"
            f"<b>3</b> - Capital actual: {wallet.current_capital}\n"
            f"<b>4</b> - Perfil de inversor: {investor_profile}"
        )    
    
    await message.answer(msg, parse_mode='HTML')
    await message.answer('Escriba el número indicado para editar dicha característica.\nEn cualquier momento puede cancelar la acción con <b>/cancelar</b>',  parse_mode='HTML')
    await state.set_state(UpdateForm.select)

@router.message(UpdateForm.select)
async def select_aspect(message: Message, state: FSMContext):
    try:
        response = int(message.text)
    except Exception as e:
        await message.answer('Escriba el número indicado para editar dicha característica.')
        return

    match response:
        case 1:
            await state.set_state(UpdateForm.name)
            await message.answer('Introduce el nuevo valor:')
        case 2:
            await state.set_state(UpdateForm.phone)
            await message.answer('Introduce el nuevo valor:')
        case 3:
            await state.set_state(UpdateForm.current_capital)
            await message.answer('Introduce el nuevo valor:')
        case 4:
            await state.set_state(UpdateForm.investor_profile)
            await message.answer('Introduce el nuevo valor:', reply_markup=keyboard)
        case _:
            await message.answer('Operación cancelada.')
            await state.clear()
    

@router.message(UpdateForm.name)
async def update_name(message: Message, state: FSMContext):
    data = await state.get_data()
    user = data.get("user")
    name = message.text
    if not name.isalpha():
        await message.answer("Por favor, ingresa un nombre válido (solo letras).")
        return  # No avanzamos de estado
    user.name = name
    try:
        await user.save()  
    except Exception as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")    
    await summary_profile(message, state)



@router.message(UpdateForm.phone)
async def update_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    user = data.get("user")
    phone = message.text
    if not (message.text.isdigit() and len(message.text) == 9):        
        await message.answer("Por favor, ingresa un número de teléfono válido (sin prefijo).")
        return
    user.phone = phone
    try:
        await user.save()  
    except Exception as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")
    await summary_profile(message, state)

@router.message(UpdateForm.current_capital)
async def update_current_capital(message: Message, state: FSMContext):
    data = await state.get_data()
    wallet = data.get("wallet")
    try:
        capital = float(message.text)
        if capital <= 0:
            await message.answer("Por favor, ingresa un capital positivo.")
            return  # No avanzamos de estado
    except ValueError:
        await message.answer("Por favor, ingresa una cantidad válida de capital.")
        return  # No avanzamos de estado
    wallet.current_capital = capital
    try:
        await wallet.save()  
    except Exception as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")
    await summary_profile(message, state)

@router.message(UpdateForm.investor_profile)
async def update_investor_profile(message: Message, state: FSMContext):
    data = await state.get_data()
    user = data.get("user")
    valid_profiles = {"Conservador", "Medio", "Atrevido"}
    if message.text not in valid_profiles:
        await message.answer("Por favor, elige una opción válida (Conservador, Medio o Atrevido).")
        return  # No avanzamos de estado
    profile_map = {"Conservador": 0.2, "Medio": 0.4, "Atrevido": 0.6}
    investor_profile = profile_map[message.text]
    await state.update_data(investor_profile=investor_profile)
    user.investor_profile = investor_profile
    try:
        await user.save()  
    except Exception as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")
    await message.answer("Información actualizada", reply_markup=types.ReplyKeyboardRemove())
    await summary_profile(message, state)

async def summary_profile(message: Message, state: FSMContext):
    data = await state.get_data()
    user = data.get("user")
    wallet = data.get("wallet")
    investor_map = {0.2: "Conservador", 0.4: "Medio", 0.6: "Atrevido"}
    investor_profile = investor_map.get(user.investor_profile)

    msg = (
            "✅ Perfil actualizado\n"
            f"Nombre: <b>{user.name}</b>\n"
            f"Teléfono: <b>{user.phone}</b>\n"
            f"Capital actual: <b>{wallet.current_capital}€</b>\n"
            f"Perfil de inversor: <b>{investor_profile}</b>"
        ) 
    
    await message.answer(msg, parse_mode='HTML')
    await state.clear()
    return
