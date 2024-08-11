from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import os
import json
import aiohttp
import yfinance as yf
import pandas as pd
import asyncio

router = Router()


@router.message(Command(commands=["update"]))
async def backtest_handler(message: Message):
    print("upload_companies")