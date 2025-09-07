from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

from database.db_manager import db_manager
from database.models import SubscriptionStatus
from utils.keyboards import get_main_menu_keyboard
from utils.texts import get_text
from config import config

router = Router()

@router.callback_query(F.data == "premium")
async def premium_menu(callback: CallbackQuery, language: str = "uk"):
    """Show premium subscription menu"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Check current subscription status
    user = await db_manager.get_user(user_id)
    is_premium = user and user.subscription_status == SubscriptionStatus.PREMIUM
    
    if is_premium:
        await show_premium_dashboard(callback, user, language)
    else:
        await show_premium_offer(callback, language)

async def show_premium_offer(callback: CallbackQuery, language: str):
    """Show premium subscription offer"""
    premium_text = get_text("premium_benefits", language).format(price=config.PREMIUM_PRICE)
    premium_text = get_text("premium_benefits", language).format(price=config.get('PREMIUM_PRICE', 99))
    
    # Add detailed benefits
    benefits_list = [
        get_text("unlimited_ai_chats", language, default="Необмежені чати з ШІ"),
        get_text("priority_support", language, default="Пріоритетна підтримка"),
        get_text("advanced_analytics", language, default="Розширена аналітика настрою"),
        get_text("direct_psychologist", language, default="Прямий зв'язок з психологами"),
        get_text("personalized_recommendations", language, default="Персоналізовані рекомендації"),
        get_text("voice_assistant_unlimited", language, default="Необмежений голосовий асистент"),
        get_text("crisis_priority", language, default="Пріоритет у кризових ситуаціях"),
        get_text("exclusive_content", language, default="Ексклюзивний контент")
    ]
    
    premium_text += f"\n\n✨ **{get_text('premium_features', language, default='Преміум функції')}:**\n"
    for benefit in benefits_list:
        premium_text += f"• {benefit}\n"
    
    # Add trial offer
    premium_text += f"\n🎁 **{get_text('trial_offer', language, default='Спеціальна пропозиція')}:**\n"
    premium_text += get_text("trial_description", language, 
                           default="Перші 7 днів безкоштовно! Скасувати можна в будь-який час.")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("start_trial", language, default="🎁 Почати безкоштовний період"),
                callback_data="start_trial"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("subscribe_premium", language),
                callback_data="subscribe_premium"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("learn_more", language, default="Дізнатися більше"),
                callback_data="premium_details"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_menu", language),
                callback_data="main_menu"
            )
        ]
    ])
    
    await callback.message.edit_text(
        premium_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def show_premium_dashboard(callback: CallbackQuery, user, language: str):
    """Show premium user dashboard"""
    dashboard_text = f"💎 **{get_text('premium_dashboard', language, default='Преміум панель')}**\n\n"
    dashboard_text += f"✅ {get_text('premium_active', language, default='Преміум підписка активна')}\n\n"
    
    # Show subscription details
    if user.subscription_expires:
        expires_date = user.subscription_expires.strftime('%d.%m.%Y')
        dashboard_text += f"📅 {get_text('expires_on', language, default='Діє до')}: {expires_date}\n\n"
    
    # Show usage statistics
    try:
        async with db_manager.pool.acquire() as conn:
            stats = await conn.fetchrow('''
                SELECT 
                    COUNT(*) FILTER (WHERE timestamp >= NOW() - INTERVAL '30 days') as monthly_chats,
                    COUNT(*) FILTER (WHERE is_voice = true AND timestamp >= NOW() - INTERVAL '30 days') as monthly_voice
                FROM ai_chats 
                WHERE user_id = $1
            ''', user.user_id)
            
            if stats:
                dashboard_text += f"📊 **{get_text('monthly_usage', language, default='Використання за місяць')}:**\n"
                dashboard_text += f"💬 {get_text('ai_chats', language, default='ШІ чати')}: {stats['monthly_chats']}\n"
                dashboard_text += f"🎙 {get_text('voice_sessions', language, default='Голосові сесії')}: {stats['monthly_voice']}\n\n"
    except Exception:
        pass
    
    dashboard_text += f"🎯 **{get_text('premium_features_available', language, default='Доступні функції')}:**\n"
    dashboard_text += f"• {get_text('unlimited_access', language, default='Необмежений доступ до всіх функцій')}\n"
    dashboard_text += f"• {get_text('priority_support_active', language, default='Пріоритетна підтримка активна')}\n"
    dashboard_text += f"• {get_text('advanced_analytics_active', language, default='Розширена аналітика доступна')}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("manage_subscription", language, default="Керувати підпискою"),
                callback_data="manage_subscription"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("premium_support", language, default="Преміум підтримка"),
                callback_data="premium_support"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("referral_program", language, default="Реферальна програма"),
                callback_data="referral_program"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_menu", language),
                callback_data="main_menu"
            )
        ]
    ])
    
    await callback.message.edit_text(
        dashboard_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "start_trial")
async def start_trial(callback: CallbackQuery, language: str = "uk"):
    """Start premium trial"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    try:
        # Check if user already had trial
        user = await db_manager.get_user(user_id)
        if user and user.subscription_status != SubscriptionStatus.FREE:
            await callback.message.edit_text(
                get_text("trial_already_used", language, default="Ви вже використовували безкоштовний період"),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=get_text("subscribe_premium", language),
                            callback_data="subscribe_premium"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_text("back_to_menu", language),
                            callback_data="main_menu"
                        )
                    ]
                ])
            )
            return
        
        # Activate trial
        trial_expires = datetime.now() + timedelta(days=7)
        
        async with db_manager.pool.acquire() as conn:
            await conn.execute('''
                UPDATE users SET 
                    subscription_status = $1,
                    subscription_expires = $2
                WHERE user_id = $3
            ''', SubscriptionStatus.TRIAL.value, trial_expires, user_id)
        
        trial_text = f"🎉 **{get_text('trial_activated', language, default='Безкоштовний період активовано!')}**\n\n"
        trial_text += f"✅ {get_text('trial_duration', language, default='Тривалість: 7 днів')}\n"
        trial_text += f"📅 {get_text('trial_expires', language, default='Закінчується')}: {trial_expires.strftime('%d.%m.%Y')}\n\n"
        trial_text += f"💎 {get_text('trial_benefits', language, default='Тепер у вас є доступ до всіх преміум функцій!')}\n\n"
        trial_text += get_text("trial_reminder", language, 
                             default="Пам'ятайте: підписку можна скасувати в будь-який час до закінчення пробного періоду.")
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("explore_premium", language, default="Дослідити преміум функції"),
                    callback_data="premium_tour"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("back_to_menu", language),
                    callback_data="main_menu"
                )
            ]
        ])
        
        await callback.message.edit_text(
            trial_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("trial_error", language, default="Помилка активації пробного періоду"),
            reply_markup=get_main_menu_keyboard(language)
        )

@router.callback_query(F.data == "subscribe_premium")
async def subscribe_premium(callback: CallbackQuery, language: str = "uk"):
    """Handle premium subscription"""
    await callback.answer()
    
    # In a real implementation, this would integrate with payment systems
    subscription_text = f"💳 **{get_text('subscription_payment', language, default='Оплата підписки')}**\n\n"
    subscription_text += f"💰 {get_text('monthly_price', language, default='Вартість')}: {config.PREMIUM_PRICE} грн/місяць\n\n"
    subscription_text += f"💰 {get_text('monthly_price', language, default='Вартість')}: {config.get('PREMIUM_PRICE', 99)} грн/місяць\n\n"
    subscription_text += get_text("payment_methods", language,
                                default="Доступні способи оплати:\n• Банківська картка\n• Google Pay\n• Apple Pay\n• Приват24")
    
    subscription_text += f"\n\n⚠️ {get_text('payment_notice', language, default='УВАГА')}: "
    subscription_text += get_text("payment_development", language,
                                default="Система оплати знаходиться в розробці. Зв'яжіться з підтримкою для активації преміум підписки.")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("contact_support", language, default="Зв'язатися з підтримкою"),
                callback_data="premium_support"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("start_trial", language, default="Спробувати безкоштовно"),
                callback_data="start_trial"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_premium", language, default="Назад до преміум"),
                callback_data="premium"
            )
        ]
    ])
    
    await callback.message.edit_text(
        subscription_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "premium_details")
async def premium_details(callback: CallbackQuery, language: str = "uk"):
    """Show detailed premium information"""
    await callback.answer()
    
    details_text = f"💎 **{get_text('premium_detailed_info', language, default='Детальна інформація про преміум')}**\n\n"
    
    # Feature comparison
    details_text += f"📊 **{get_text('feature_comparison', language, default='Порівняння функцій')}:**\n\n"
    
    features = [
        ("ai_chats", "ШІ чати", "5/день", "Необмежено"),
        ("voice_assistant", "Голосовий асистент", "3/день", "Необмежено"),
        ("mood_analytics", "Аналітика настрою", "Базова", "Розширена"),
        ("psychologist_access", "Доступ до психологів", "Черга", "Пріоритет"),
        ("crisis_support", "Кризова підтримка", "Стандарт", "Пріоритет"),
        ("recommendations", "Рекомендації", "Загальні", "Персональні")
    ]
    
    details_text += f"| {'Функція':<20} | {'Безкоштовно':<15} | {'Преміум':<15} |\n"
    details_text += f"|{'-'*20}|{'-'*15}|{'-'*15}|\n"
    
    for feature_id, feature_name, free_limit, premium_limit in features:
        details_text += f"| {feature_name:<20} | {free_limit:<15} | {premium_limit:<15} |\n"
    
    details_text += f"\n💰 **{get_text('pricing_info', language, default='Інформація про ціни')}:**\n"
    details_text += f"• {get_text('monthly_subscription', language, default='Місячна підписка')}: {config.PREMIUM_PRICE} грн\n"
    details_text += f"• {get_text('monthly_subscription', language, default='Місячна підписка')}: {config.get('PREMIUM_PRICE', 99)} грн\n"
    details_text += f"• {get_text('first_week_free', language, default='Перший тиждень безкоштовно')}\n"
    details_text += f"• {get_text('cancel_anytime', language, default='Скасування в будь-який час')}\n"
    details_text += f"• {get_text('no_hidden_fees', language, default='Без прихованих платежів')}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("start_trial", language, default="Почати безкоштовний період"),
                callback_data="start_trial"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("subscribe_now", language, default="Підписатися зараз"),
                callback_data="subscribe_premium"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_premium", language, default="Назад до преміум"),
                callback_data="premium"
            )
        ]
    ])
    
    await callback.message.edit_text(
        details_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "referral_program")
async def referral_program(callback: CallbackQuery, language: str = "uk"):
    """Show referral program information"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = await db_manager.get_user(user_id)
    
    if not user:
        return
    
    referral_text = f"🎁 **{get_text('referral_program_title', language, default='Реферальна програма')}**\n\n"
    referral_text += f"🔗 **{get_text('your_referral_link', language, default='Ваше реферальне посилання')}:**\n"
    referral_text += f"`https://t.me/VetSupportAI_bot?start={user.referral_code}`\n\n"
    
    referral_text += f"💰 **{get_text('referral_benefits', language, default='Переваги')}:**\n"
    referral_text += f"• {get_text('friend_bonus', language, default='Ваш друг отримує 1 тиждень преміум безкоштовно')}\n"
    referral_text += f"• {get_text('your_bonus', language, default='Ви отримуєте 1 тиждень преміум за кожного друга')}\n"
    referral_text += f"• {get_text('unlimited_referrals', language, default='Необмежена кількість запрошень')}\n\n"
    
    # Show referral statistics
    try:
        async with db_manager.pool.acquire() as conn:
            referral_stats = await conn.fetchrow('''
                SELECT COUNT(*) as total_referrals,
                       COUNT(*) FILTER (WHERE bonus_awarded = true) as successful_referrals
                FROM referrals 
                WHERE referrer_id = $1
            ''', user_id)
            
            if referral_stats:
                referral_text += f"📊 **{get_text('your_statistics', language, default='Ваша статистика')}:**\n"
                referral_text += f"👥 {get_text('total_invites', language, default='Всього запрошень')}: {referral_stats['total_referrals']}\n"
                referral_text += f"✅ {get_text('successful_invites', language, default='Успішних запрошень')}: {referral_stats['successful_referrals']}\n"
                referral_text += f"🎁 {get_text('earned_days', language, default='Зароблено днів преміум')}: {referral_stats['successful_referrals'] * 7}"
    except Exception:
        pass
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("share_referral", language, default="Поділитися посиланням"),
                switch_inline_query=f"Приєднуйся до VetSupport AI! https://t.me/VetSupportAI_bot?start={user.referral_code}"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("copy_link", language, default="Копіювати посилання"),
                callback_data=f"copy_referral_{user.referral_code}"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_premium", language, default="Назад до преміум"),
                callback_data="premium"
            )
        ]
    ])
    
    await callback.message.edit_text(
        referral_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("copy_referral_"))
async def copy_referral_link(callback: CallbackQuery, language: str = "uk"):
    """Handle referral link copying"""
    await callback.answer(
        get_text("link_copied", language, default="Посилання скопійовано! Поділіться ним з друзями."),
        show_alert=True
    )