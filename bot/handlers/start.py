import base64
import re
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from bot.db.models import User, Wallet
from bot.config import TORTOISE_ORM, FIRST_ADMIN
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

router = Router()

# Define los estados para la conversación
class RegisterForm(StatesGroup):
    name = State()
    phone = State()
    capital = State()
    investor_profile = State()

async def decode_multiple_params(encoded_data):
    decoded_bytes = base64.urlsafe_b64decode(encoded_data)
    decoded_str = decoded_bytes.decode('utf-8')
    if '-' in decoded_str:
        params = decoded_str.split('-')
    else:
        params = [decoded_str]
    return params

async def trim_emojis(txt): # Expresión regular que captura emojis y otros caracteres especiales Unicode 
    emoji_pattern = re.compile( 
        "[" 
        u"\U0001F600-\U0001F64F" # Emoticonos 
        u"\U0001F300-\U0001F5FF" # Símbolos y pictogramas 
        u"\U0001F680-\U0001F6FF" # Transporte y símbolos 
        u"\U0001F700-\U0001F77F" # Alquimia 
        u"\U0001F780-\U0001F7FF" # Geometría adicional 
        u"\U0001F800-\U0001F8FF" # Componentes adicionales 
        u"\U0001F900-\U0001F9FF" # Emoticonos adicionales y más símbolos 
        u"\U0001FA00-\U0001FA6F" # Componentes adicionales 
        u"\U00002702-\U000027B0" # Diversos símbolos 
        u"\U000024C2-\U0001F251" # Otros caracteres especiales 
        "]+", flags=re.UNICODE ) 
    return emoji_pattern.sub(r'', txt)  

# Manejador para el comando /register
@router.message(Command(commands=["start"]))
async def send_welcome(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    if len(args)<2:
        await message.answer("Error.")
        return
    print(args)
    encoded_data = args[1]
    params = await decode_multiple_params(encoded_data)
    print(params)
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
        await message.answer("1. ¿Cómo quieres que me dirija hacia ti?")
        await state.update_data(params=params)
        await state.set_state(RegisterForm.name)

# Manejador para capturar el nombre o cómo quiere que se dirija el bot
@router.message(RegisterForm.name)
async def process_name(message: Message, state: FSMContext):
    print("OYE5")
    if not message.text.isalpha():
        await message.answer("Por favor, ingresa un nombre válido (solo letras).")
        return  # No avanzamos de estado
    await state.update_data(name=message.text)
    await message.answer(f"Perfecto <b>{message.text}</b> 2. ¿Cuál es tu número de teléfono?", parse_mode='HTML')
    await state.set_state(RegisterForm.phone)

@router.message(RegisterForm.phone)
async def process_phone(message: Message, state: FSMContext):
    print("OYE6")
    if not (message.text.isdigit() and len(message.text) == 9):        
        await message.answer("Por favor, ingresa un número de teléfono válido (sin prefijo).")
        return  # No avanzamos de estado
    await state.update_data(phone=message.text)
    await message.answer("3. ¿Cuál es tu capital inicial?")
    await state.set_state(RegisterForm.capital)

# Manejador para capturar el capital inicial
@router.message(RegisterForm.capital)
async def process_capital(message: Message, state: FSMContext):
    print("OYE7")
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
            [KeyboardButton(text="🏠Conservador🏠")],
            [KeyboardButton(text="⭐Medio⭐")],
            [KeyboardButton(text="🚀Atrevido🚀")]
        ],
        resize_keyboard=True
    )

    await message.answer("4. ¿Cuál es tu perfil de inversor? (Elige una opción)", reply_markup=keyboard)
    await state.set_state(RegisterForm.investor_profile)

# Manejador para capturar el perfil de inversor
@router.message(RegisterForm.investor_profile)
async def process_investor_profile(message: Message, state: FSMContext):
    print("OYE8")
    valid_profiles = {"🏠Conservador🏠", "⭐Medio⭐", "🚀Atrevido🚀"}
    if message.text not in valid_profiles:
        await message.answer("Por favor, elige una opción válida (Conservador, Medio o Atrevido).")
        return  # No avanzamos de estado

    await state.update_data(investor_profile=message.text)

    profile_map = {"Conservador": 0.2, "Medio": 0.4, "Atrevido": 0.6}
    text = await trim_emojis(message.text)
    investor_profile = profile_map[text]
    
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Concatenar el nombre y el apellido para usarlo como 'username'
    username = f"{first_name} {last_name}" if last_name else first_name
    data = await state.get_data()
    summary = (
        f"Nombre: <b>{data['name']}</b>\n"
        f"Teléfono: <b>{data['phone']}</b>\n"
        f"Capital Inicial: <b>{data['capital']}€</b>\n"
        f"Perfil de Inversor: <b>{data['investor_profile']}</b>"
    )
    params = data.get("params")
    is_lictor = False
    father_id = params[0]
    if len(params) > 1:
        is_lictor = True
        father_id = params[1]
    admin_ids = [int(FIRST_ADMIN)]
    is_admin = False
    if message.from_user.id in admin_ids:
        is_admin = True
    try:
        user = await User.create(
            id=message.from_user.id,
            name=data['name'],
            username=username,
            phone=data['phone'],
            investor_profile=investor_profile,
            is_admin=is_admin,
            belongs_to=father_id,
            is_lictor=is_lictor
        )
        wallet = await Wallet.create(
            initial_capital = data['capital'],
            current_capital = data['capital'],
            gain_capital = data['capital'],
            user_id = user.id,
            profit=0,
            max_drawdown=0,
            peak_capital=data['capital'],
            number_of_operations = 0
        )
    except Exception as e:
        await message.answer(f"Error al registrar el usuario: {e}")

    await message.answer(f"✅ Registro completado: \n{summary}", reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML')
    if user.id not in admin_ids:
        bot = message.bot
        msg = (f'✅ Nuevo usuario registrado: \n{summary}')
        if user.is_lictor:
            print("les")
            await bot.send_message(int(FIRST_ADMIN), msg, parse_mode='HTML')
        else:
            print("els")
            for admin in admin_ids:
                await bot.send_message(int(admin), msg, parse_mode='HTML')


    # Guardar los cambios en la base de datos
    try:
        await user.save()  
        await wallet.save()  
    except Exception as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")
    
    await state.clear()  # Finaliza la conversación y limpia el estado