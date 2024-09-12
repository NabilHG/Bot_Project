# start_handler.py
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from bot.db.models import User, Wallet
from bot.config import TORTOISE_ORM
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

router = Router()

# Define los estados para la conversación
class RegisterForm(StatesGroup):
    name = State()
    phone = State()
    capital = State()
    investor_profile = State()

# Manejador para el comando /start
@router.message(Command(commands=["register"]))
async def send_welcome(message: Message, state: FSMContext):
    await Tortoise.init(TORTOISE_ORM)

    # Verifica si el usuario ya está registrado
    user_id = message.from_user.id

    try:
        await User.get(id=user_id)
        # Si llega aquí, el usuario ya existe
        await message.reply("Ya estás registrado. No es necesario volver a registrarte.")
    except DoesNotExist:
        # Si el usuario no existe, continúa con el registro
        await message.reply("¡Hola! Para registrarte, por favor responde a las siguientes preguntas.")
        await message.answer("1. ¿Cómo quieres que se dirija el bot hacia ti?")
        await state.set_state(RegisterForm.name)

# Manejador para capturar el nombre o cómo quiere que se dirija el bot
@router.message(RegisterForm.name)
async def process_name(message: Message, state: FSMContext):
    if not message.text.isalpha():
        await message.answer("Por favor, ingresa un nombre válido (solo letras).")
        return  # No avanzamos de estado
    await state.update_data(name=message.text)
    await message.answer("2. ¿Cuál es tu número de teléfono?")
    await state.set_state(RegisterForm.phone)

@router.message(RegisterForm.phone)
async def process_phone(message: Message, state: FSMContext):
    if not (message.text.isdigit() and len(message.text) == 9):        
        await message.answer("Por favor, ingresa un número de teléfono válido (sin prefijo).")
        return  # No avanzamos de estado
    await state.update_data(phone=message.text)
    await message.answer("3. ¿Cuál es tu capital inicial?")
    await state.set_state(RegisterForm.capital)

# Manejador para capturar el capital inicial
@router.message(RegisterForm.capital)
async def process_capital(message: Message, state: FSMContext):
    try:
        capital = float(message.text)
        if capital <= 0:
            await message.answer("Por favor, ingresa un capital positivo.")
            return  # No avanzamos de estado
    except ValueError:
        await message.answer("Por favor, ingresa una cantidad válida de capital.")
        return  # No avanzamos de estado
    
    await state.update_data(capital=capital)
    
    # Teclado para seleccionar el perfil de inversor
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Conservador")],
            [KeyboardButton(text="Medio")],
            [KeyboardButton(text="Atrevido")]
        ],
        resize_keyboard=True
    )

    await message.answer("4. ¿Cuál es tu perfil de inversor? (Elige una opción)", reply_markup=keyboard)
    await state.set_state(RegisterForm.investor_profile)

# Manejador para capturar el perfil de inversor
@router.message(RegisterForm.investor_profile)
async def process_investor_profile(message: Message, state: FSMContext):
    valid_profiles = {"Conservador", "Medio", "Atrevido"}
    if message.text not in valid_profiles:
        await message.answer("Por favor, elige una opción válida (Conservador, Medio o Atrevido).")
        return  # No avanzamos de estado

    await state.update_data(investor_profile=message.text)

    profile_map = {"Conservador": 1, "Medio": 2, "Atrevido": 3}
    investor_profile = profile_map[message.text]
    
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Concatenar el nombre y el apellido para usarlo como 'username'
    username = f"{first_name} {last_name}" if last_name else first_name
    data = await state.get_data()
    summary = (
        f"Nombre: {data['name']}\n"
        f"Teléfono: {data['phone']}\n"
        f"Capital Inicial: {data['capital']}\n"
        f"Perfil de Inversor: {data['investor_profile']}"
    )

    try:
        user = await User.create(
            id=message.from_user.id,
            name=data['name'],
            username=username,
            phone=data['phone'],
            investor_profile=investor_profile,
            is_admin=True
        )
        wallet = await Wallet.create(
            initial_capital = data['capital'],
            user_id = user.id
        )
        await message.answer("Usuario registrado exitosamente.")
    except Exception as e:
        await message.answer(f"Error al registrar el usuario: {e}")

    await message.answer(f"Registro completado: \n{summary}", reply_markup=types.ReplyKeyboardRemove())
    
    # Guardar los cambios en la base de datos
    try:
        await user.save()  
        await wallet.save()  
    except Exception as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")
    
    await state.clear()  # Finaliza la conversación y limpia el estado