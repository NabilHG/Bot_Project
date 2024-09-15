from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold 
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

router = Router()
class ProccesBuyForm(StatesGroup):
    amount = State()

@router.message(Command(commands=["vender"]))
async def ask_to_buy_handler(message: Message, state: FSMContext):
    print("Handler 'vender' activado")
    response = message.text.lower()
    print(f"Respuesta del usuario: {response}")
    if response in "vender":
        # Preguntar la cantidad a invertir
        await message.answer("¿Qué cantidad deseas vender?")
        await state.set_state(ProccesBuyForm.amount)


@router.message(ProccesBuyForm.amount)
async def process_name(message: Message, state: FSMContext):
    print("OYE5")
    try:
        capital = float(message.text)
        if capital > 0:
            pass
    except ValueError:
        await message.answer("Por favor, ingresa una cantidad válida de capital.")
        return  # No avanzamos de estado

