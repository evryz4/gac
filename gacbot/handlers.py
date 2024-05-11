from aiogram import Router, Bot, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

from sqlitewithoutsql import Sqltype, Database

import os

from config import *
from wallet import *

dbfile = f'{'\\'.join(__file__.split('\\')[:-2])}\\data.db'
db = Database(dbfile)
db.new_table('accs', accname=Sqltype.STR, userid=Sqltype.INT)

chainfile = f'{'\\'.join(__file__.split('\\')[:-2])}\\chain.json'
gac = Coin(file=chainfile)

maxemission = 150000

if not os.path.exists(chainfile):
    gac.setemission(amount=maxemission)

router = Router()

bot = Bot(TOKEN)

def getaccs(idkeys: bool = False):
    ret = {}
    data = db.get_table('accs')
    for row in data:
        if idkeys:
            ret[data[row]['userid']] = data[row]['accname']
        else:
            ret[data[row]['accname']] = data[row]['userid']
    
    return ret

@router.message(Command('start'))
async def start_handler(msg: Message):
    await msg.reply('Привет! Giving Anonymity Bot это криптокошелёк для Giving Anonymity Coin [GAC]. Напиши /help чтобы увидить список команд')

@router.message(Command('help'))
async def help_handler(msg: Message):
    await msg.reply('Вот список команд:\n/createacc [имя без пробелов] - создать аккаунт в боте (изменить имя нельзя, 1 аккаунт в gac на телеграм аккаунт)\n/profile - ваш профиль в боте\n/send [имя получателя] [кол-во] [комментарий (необязательно)] - перевести gac другому пользователю\n/emission - просмотреть размер эмиссии (уже выпущенных монет) и то, сколько еще осталось выпустить\n/chain - просмотреть блокчейн')

@router.message(Command('createacc'))
async def createacc_handler(msg: Message):
    if msg.text.split()[1] == 'EMISSION':
        await msg.reply('Решил обмануть бота? He получится)')
    data = db.get_table('accs')
    for row in data:
        if msg.text.split()[1] == data[row]['accname'] or msg.from_user.id == data[row]['userid']:
            await msg.reply('Аккаунт c таким айди/именем уже существует.')
            return
    db.insert('accs', msg.text.split()[1], msg.from_user.id)
    await msg.reply('Аккаунт успешно создан')

@router.message(Command('send'))
async def send_handler(msg: Message):
    if msg.from_user.id in getaccs(True):
        if msg.text.split()[1] in getaccs():
            comment = None
            if len(msg.text.split()) > 3:
                comment = ' '.join(msg.text.split()[3:])
            if gac.transfer(fromh=getaccs(True)[msg.from_user.id], to=msg.text.split()[1], amount=int(msg.text.split()[2]), comment=comment):
                await msg.reply('Успешно переведено!')
                if comment is None:
                    await bot.send_message(getaccs()[msg.text.split()[1]], f'{getaccs(True)[msg.from_user.id]} перевёл вам {msg.text.split()[2]} GAC!')
                else:
                    await bot.send_message(getaccs()[msg.text.split()[1]], f'{getaccs(True)[msg.from_user.id]} перевёл вам {msg.text.split()[2]} GAC! Комментарий к платежу: {comment}')
        else:
            await msg.reply('Не существует аккаунта с таким именем!')
    else:
        await msg.reply('У вас нет аккаунта в боте!')

@router.message(Command('profile'))
async def profile_handler(msg: Message):
    if msg.from_user.id in getaccs(True):
        name = getaccs(True)[msg.from_user.id]
        await msg.reply(f'Ваш аккаунт:\nИмя пользователя: {name}\nБаланс: {gac.getholders()[name]}')
    else:
        await msg.reply('У вас нет аккаунта в боте!')

@router.message(Command('emission'))
async def emission_handler(msg: Message):
    emission = maxemission - gac.getholders()['EMISSION']
    await msg.reply(f'Уже выпущено {emission}/{maxemission} GAC')

@router.message(Command('chain'))
async def chain_handler(msg: Message):
    await msg.reply(str(gac), )
    await bot.send_document(msg.from_user.id, FSInputFile(chainfile, 'chain.json'))
