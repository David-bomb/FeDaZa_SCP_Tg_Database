import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

TOKEN = "5120267238:AAGm7_j0JuyOygEBvu_BUIPQGMGCrUY_3rE"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


class Scp(StatesGroup):
    scp = State()


@dp.message_handler(commands=['start'])  # Просто приветствие
async def send_welcome(msg: types.Message):
    await msg.reply(f'Привет, меня зовут ScpArchive. Приятно познакомиться, {msg.from_user.first_name}!')


@dp.message_handler(commands=['help'])
async def helper(msg: types.Message):
    await msg.reply('''Пока что у меня мало функций, но я уже могу кидать ссылку на статью об обьекте, если
    вы отпрвите команду /browse %название объекта%, где название объекта пишется как scp-001''')


@dp.message_handler(commands=['browse'])  # TODO Это скорее демонстративная команда, мы не будем отправлять ссылки,
async def browse(msg: types.Message):  # TODO а будем отправлять инфу в сообщениях, описание, картинка и тд.
    argument = msg.get_args()
    if argument:
        try:
            await msg.reply(f'Вот, я искал и нашёл что вы хотели: http://scpfoundation.net/{argument}')
        except Exception:
            await msg.reply('Я всё обыскал, нигде не нашёл того, чего вы хотели')
    else:
        await msg.reply('Я не думаю что я смогу найти нужный объект, если вы не укажете его название')

    '''await msg.reply(f'Чтобы обратиться к архиву фонда, введи название обьекта согласно примеру: scp-001')
    await Scp.scp.set()'''


'''@dp.message_handler(state=Scp.scp, content_types=types.ContentTypes.TEXT)
async def browsing(message: types.Message, state: FSMContext):
    await state.update_data(name_user=message.text.lower())
    user_data = await state.get_data()
    await state.finish()
    await bot.send_message(user_data)'''


@dp.message_handler(content_types=['text'])  # Шаблон приема обычного сообщения
async def get_text_messages(msg: types.Message):
    if msg.text.lower() == 'привет' or msg.text.lower() == 'здравствуй' or msg.text.lower() == 'приветствую':
        await msg.answer(f'Привет, {msg.from_user.first_name}')
    else:
        await msg.answer('Не понимаю, что это значит.')


if __name__ == '__main__':
    executor.start_polling(dp)