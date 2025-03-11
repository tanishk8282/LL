#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CC Checker Telegram Bot by @HACKERBOYYTK

import logging
import os
import random
import re
import string
import time
from datetime import datetime

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment variables
TOKEN = os.environ.get("BOT_TOKEN", "8129685312:AAHRsV0JW4WpMVYPg3KnS2sLh0RrNRTGuY0")

# Bot owner/admin information
ADMIN_ID = int(os.environ.get("ADMIN_ID", "5708896577"))
BOT_USERNAME = os.environ.get("BOT_USERNAME", "@HACKERBOYYTK")

# Conversation states
MAIN_MENU, CC_CHECK, BIN_GEN, ADD_USER, ADD_GROUP = range(5)

# Database simulation (in a real scenario, you would use a proper database)
authorized_users = {ADMIN_ID: {"name": "Admin", "expiry": "Unlimited"}}
authorized_groups = {}

# CC Check API endpoints (replace with actual APIs in production)
API_ENDPOINTS = {
    "kill": "https://api.example.com/cc/kill",
    "b3": "https://api.example.com/cc/b3",
    "vbv": "https://api.example.com/cc/vbv",
    "cvv": "https://api.example.com/cc/cvv",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and display main menu."""
    user = update.effective_user
    user_id = user.id
    
    # Check if user is authorized
    if user_id not in authorized_users and update.effective_chat.type == "private":
        await update.message.reply_text(
            f"⚠️ Unauthorized access. Please contact @{BOT_USERNAME} to get access."
        )
        return ConversationHandler.END
    
    # Check if group is authorized
    if update.effective_chat.type in ["group", "supergroup"]:
        group_id = update.effective_chat.id
        if group_id not in authorized_groups:
            await update.message.reply_text(
                f"⚠️ This group is not authorized to use this bot. Please contact @{BOT_USERNAME} to get access."
            )
            return ConversationHandler.END
    
    keyboard = [
        [
            InlineKeyboardButton("💳 CC Checker", callback_data="cc_check"),
            InlineKeyboardButton("🔢 BIN Generator", callback_data="bin_gen"),
        ],
        [
            InlineKeyboardButton("👤 Add User", callback_data="add_user"),
            InlineKeyboardButton("👥 Add Group", callback_data="add_group"),
        ],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    watermark = f"📌 @HACKERBOYYTK | {datetime.now().strftime('%Y-%m-%d')}"
    
    await update.message.reply_text(
        f"Welcome to CC Checker Bot!\n\n"
        f"Select an option from the menu below.\n\n{watermark}",
        reply_markup=reply_markup,
    )
    
    return MAIN_MENU

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check if user is authorized (for private chats)
    if query.message.chat.type == "private" and user_id not in authorized_users:
        await query.message.reply_text(
            f"⚠️ Unauthorized access. Please contact @{BOT_USERNAME} to get access."
        )
        return ConversationHandler.END
    
    if query.data == "main_menu":
        return await start(update, context)
    
    elif query.data == "cc_check":
        keyboard = [
            [
                InlineKeyboardButton("⚡ Kill", callback_data="check_kill"),
                InlineKeyboardButton("🔵 B3", callback_data="check_b3"),
            ],
            [
                InlineKeyboardButton("🟢 VBV", callback_data="check_vbv"),
                InlineKeyboardButton("🟠 CVV", callback_data="check_cvv"),
            ],
            [
                InlineKeyboardButton("📋 Tips", callback_data="cc_tips"),
                InlineKeyboardButton("🔙 Back", callback_data="main_menu"),
            ],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        watermark = f"📌 @HACKERBOYYTK | {datetime.now().strftime('%Y-%m-%d')}"
        
        await query.message.edit_text(
            f"💳 CC Checker\n\n"
            f"Select the check type:\n\n{watermark}",
            reply_markup=reply_markup,
        )
        
        return CC_CHECK
    
    elif query.data == "bin_gen":
        keyboard = [
            [
                InlineKeyboardButton("Visa", callback_data="gen_visa"),
                InlineKeyboardButton("Mastercard", callback_data="gen_mastercard"),
            ],
            [
                InlineKeyboardButton("Amex", callback_data="gen_amex"),
                InlineKeyboardButton("Discover", callback_data="gen_discover"),
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        watermark = f"📌 @HACKERBOYYTK | {datetime.now().strftime('%Y-%m-%d')}"
        
        await query.message.edit_text(
            f"🔢 BIN Generator\n\n"
            f"Select a card type to generate:\n\n{watermark}",
            reply_markup=reply_markup,
        )
        
        return BIN_GEN
    
    elif query.data == "add_user" and user_id == ADMIN_ID:
        await query.message.edit_text(
            "👤 Add User\n\n"
            "Please send the user ID and expiry in the format:\n"
            "`user_id days`\n\n"
            "Example: `123456789 30` (for 30 days access)"
        )
        return ADD_USER
    
    elif query.data == "add_group" and user_id == ADMIN_ID:
        await query.message.edit_text(
            "👥 Add Group\n\n"
            "Please send the group ID and expiry in the format:\n"
            "`group_id days`\n\n"
            "Example: `-100123456789 30` (for 30 days access)"
        )
        return ADD_GROUP
    
    elif query.data == "about":
        watermark = f"📌 @HACKERBOYYTK | {datetime.now().strftime('%Y-%m-%d')}"
        
        await query.message.edit_text(
            f"ℹ️ About CC Checker Bot\n\n"
            f"This bot is created by @HACKERBOYYTK\n\n"
            f"Features:\n"
            f"• CC Checking (Kill, B3, VBV, CVV)\n"
            f"• BIN Generation\n"
            f"• User & Group Management\n\n"
            f"{watermark}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]),
        )
        return MAIN_MENU
    
    # CC Check handlers
    elif query.data.startswith("check_"):
        check_type = query.data.split("_")[1]
        await query.message.edit_text(
            f"💳 CC Checker - {check_type.upper()}\n\n"
            f"Please enter your credit card details in the format:\n"
            f"`xxxxxxxxxxxxxxxx|MM|YYYY|CVV`\n\n"
            f"Example: `4111111111111111|01|2025|123`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="cc_check")]]),
        )
        context.user_data["check_type"] = check_type
        return CC_CHECK
    
    elif query.data == "cc_tips":
        await query.message.edit_text(
            "📋 CC Checker Tips\n\n"
            "1. Make sure to use valid format: `CARD|MM|YYYY|CVV`\n"
            "2. Kill check verifies if the card is alive\n"
            "3. B3 check validates the billing address\n"
            "4. VBV check determines 3D Secure status\n"
            "5. CVV check validates the security code\n\n"
            "Note: This tool is for educational purposes only.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="cc_check")]]),
        )
        return CC_CHECK
    
    # BIN Generator handlers
    elif query.data.startswith("gen_"):
        card_type = query.data.split("_")[1]
        bin_numbers = generate_bin(card_type)
        
        watermark = f"📌 @HACKERBOYYTK | {datetime.now().strftime('%Y-%m-%d')}"
        
        await query.message.edit_text(
            f"🔢 Generated {card_type.title()} BINs:\n\n{bin_numbers}\n\n{watermark}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="bin_gen")]]),
        )
        return BIN_GEN
    
    # Unauthorized admin action
    elif query.data in ["add_user", "add_group"] and user_id != ADMIN_ID:
        await query.message.edit_text(
            "⚠️ You are not authorized to perform this action.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]),
        )
        return MAIN_MENU
    
    return MAIN_MENU

async def check_cc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the CC check based on user input."""
    if "check_type" not in context.user_data:
        await update.message.reply_text(
            "⚠️ Something went wrong. Please start over.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]]),
        )
        return MAIN_MENU
    
    check_type = context.user_data["check_type"]
    cc_data = update.message.text.strip()
    
    # Validate CC format
    cc_pattern = r'^\d{13,19}\|(?:0[1-9]|1[0-2])\|20\d{2}\|\d{3,4}$'
    if not re.match(cc_pattern, cc_data):
        await update.message.reply_text(
            "⚠️ Invalid format. Please use: `CARD|MM|YYYY|CVV`\n"
            "Example: `4111111111111111|01|2025|123`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="cc_check")]]),
        )
        return CC_CHECK
    
    # Simulate checking process
    await update.message.reply_text(f"🔍 Processing {check_type.upper()} check...")
    
    # Simulate API call and processing time
    time.sleep(2)
    
    # Simulate check result (in real scenario, this would call the actual API)
    card, month, year, cvv = cc_data.split("|")
    bin_info = get_bin_info(card[:6])
    
    # Random result for demonstration
    result_options = ["APPROVED", "DECLINED"]
    result = random.choice(result_options)
    
    response_text = f"💳 CC Check Result ({check_type.upper()})\n\n"
    response_text += f"Card: {card[:6]}xxxxxx{card[-4:]}\n"
    response_text += f"Expiry: {month}/{year}\n"
    response_text += f"Type: {bin_info['type']}\n"
    response_text += f"Brand: {bin_info['brand']}\n"
    response_text += f"Bank: {bin_info['bank']}\n"
    response_text += f"Country: {bin_info['country']}\n\n"
    response_text += f"Result: {result}\n"
    
    if result == "APPROVED":
        response_text += "✅ This card passed the check.\n"
    else:
        response_text += "❌ This card failed the check.\n"
    
    watermark = f"📌 @HACKERBOYYTK | {datetime.now().strftime('%Y-%m-%d')}"
    response_text += f"\n{watermark}"
    
    await update.message.reply_text(
        response_text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="cc_check")]]),
    )
    
    return CC_CHECK

async def add_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process adding a new authorized user."""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text(
            "⚠️ You are not authorized to perform this action.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]]),
        )
        return MAIN_MENU
    
    try:
        data = update.message.text.strip().split()
        new_user_id = int(data[0])
        days = int(data[1])
        
        # Calculate expiry date
        if days == 0:
            expiry = "Unlimited"
        else:
            expiry_date = datetime.now().replace(hour=23, minute=59, second=59)
            expiry_date = expiry_date.replace(day=expiry_date.day + days)
            expiry = expiry_date.strftime("%Y-%m-%d")
        
        # Add user to database
        authorized_users[new_user_id] = {"name": f"User_{new_user_id}", "expiry": expiry}
        
        await update.message.reply_text(
            f"✅ User {new_user_id} has been added successfully!\n"
            f"Expiry: {expiry}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]]),
        )
    except (ValueError, IndexError):
        await update.message.reply_text(
            "⚠️ Invalid format. Please use: `user_id days`\n"
            "Example: `123456789 30` (for 30 days access)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]]),
        )
    
    return MAIN_MENU

async def add_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process adding a new authorized group."""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text(
            "⚠️ You are not authorized to perform this action.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]]),
        )
        return MAIN_MENU
    
    try:
        data = update.message.text.strip().split()
        group_id = int(data[0])
        days = int(data[1])
        
        # Calculate expiry date
        if days == 0:
            expiry = "Unlimited"
        else:
            expiry_date = datetime.now().replace(hour=23, minute=59, second=59)
            expiry_date = expiry_date.replace(day=expiry_date.day + days)
            expiry = expiry_date.strftime("%Y-%m-%d")
        
        # Add group to database
        authorized_groups[group_id] = {"name": f"Group_{group_id}", "expiry": expiry}
        
        await update.message.reply_text(
            f"✅ Group {group_id} has been added successfully!\n"
            f"Expiry: {expiry}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]]),
        )
    except (ValueError, IndexError):
        await update.message.reply_text(
            "⚠️ Invalid format. Please use: `group_id days`\n"
            "Example: `-100123456789 30` (for 30 days access)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]]),
        )
    
    return MAIN_MENU

def generate_bin(card_type):
    """Generate random BIN numbers based on card type."""
    bins = []
    
    # Prefixes based on card type
    prefixes = {
        "visa": ["4"],
        "mastercard": ["51", "52", "53", "54", "55"],
        "amex": ["34", "37"],
        "discover": ["6011", "644", "645", "646", "647", "648", "649", "65"]
    }
    
    # Generate 5 random BINs
    for _ in range(5):
        prefix = random.choice(prefixes[card_type])
        remaining_digits = 6 - len(prefix)
        
        bin_number = prefix
        for _ in range(remaining_digits):
            bin_number += random.choice(string.digits)
        
        bins.append(bin_number)
    
    return "\n".join(bins)

def get_bin_info(bin_number):
    """Get information about a BIN (first 6 digits of a card)."""
    # In a real scenario, you would call a BIN lookup API
    # This is a simulation with random data
    
    card_types = ["Credit", "Debit", "Prepaid"]
    card_brands = ["Visa", "Mastercard", "American Express", "Discover"]
    banks = ["Chase", "Bank of America", "Wells Fargo", "Citibank", "Capital One"]
    countries = ["US", "UK", "CA", "AU", "DE", "FR", "JP"]
    
    return {
        "type": random.choice(card_types),
        "brand": random.choice(card_brands),
        "bank": random.choice(banks),
        "country": random.choice(countries)
    }

def main() -> None:
    """Set up and run the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()
    
    # Set up conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(button_handler),
            ],
            CC_CHECK: [
                CallbackQueryHandler(button_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, check_cc),
            ],
            BIN_GEN: [
                CallbackQueryHandler(button_handler),
            ],
            ADD_USER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_user_handler),
            ],
            ADD_GROUP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_group_handler),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    
    application.add_handler(conv_handler)
    
    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main()