from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .keyboards import generate_start_keyboard, profile
from .database.data import add_user, get_user, update_user

router = Router()

GREETING = """
Hey there! 👋💸

Welcome to the world of $BLAZE! 🚀✨
Ready to boost your earnings and unlock new opportunities? 🌟 Here’s how:

    1. Invite Your Friends 👥
    2. Complete Exciting Tasks 🎯
    3. Earn Big 💰

Join us now and start your journey to financial success with $BLAZE! 🚀🌟
"""

class UserState(StatesGroup):
    username = State()
    amount = State()
    user_id = State()
    invited_friends = State()
    invited_friends_usernames = State()
    support_query = State()
    feedback = State()

@router.message(CommandStart())
async def start_command(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username if message.from_user.username else first_name

    user = get_user(user_id)

    if user is None:
        add_user(user_id, username, first_name)

        if len(message.text.split()) > 1:
            referrer_id = message.text.split()[1].split('_')[1]
            referrer = get_user(referrer_id)
            if referrer:
                update_user(referrer_id, 
                            invited_friends=referrer['invited_friends'] + 1, 
                            amount=referrer['amount'] + 150, 
                            invited_friends_usernames=referrer['invited_friends_usernames'] + [username])

    image_url = 'https://i.ibb.co/GTK5Cwm/hello.png'
    start_keyboard = generate_start_keyboard(user_id)

    await message.answer_photo(
        photo=image_url,
        caption=GREETING,
        reply_markup=start_keyboard
    )
    
    
    
@router.message(Command('profile'))
async def profile_command(message: Message, state: FSMContext):
    user_id = message.from_user.id

    user = get_user(user_id)

    if user:
        name, amount, invited_friends, invited_friends_usernames = user['name'], user['amount'], user['invited_friends'], user['invited_friends_usernames']
        friends_usernames_str = "\n".join(invited_friends_usernames) if invited_friends_usernames else "None"

        await message.answer(
            f"💎Your Profile Infoℹ️:\n\n🆔Your ID: {user_id}\n\n👤Your name: {name}\n\n🔥Coins: {amount} $BLZ\n\n👥Invited Friends: {invited_friends}\n\n📜Invited Friends' Usernames: {friends_usernames_str}\n\nInvite Friends and get 🔥150 $BLAZE per invited friend",
            reply_markup=profile
        )
    else:
        await message.answer("Profile not found. Please start with /start")

@router.callback_query(lambda c: c.data == 'invite')
async def handle_invite(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    referral_link = f"https://t.me/earnblazebot?start=invite_{user_id}"
    await callback_query.message.answer(f"Hey there! 🤙 Ready to blaze a trail in the world of crypto? 🔥 Join us and start earning more with every step you take! 🚀💰\n {referral_link}")

    await callback_query.answer()
