import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from download import download_all_pdfs, check_files_exist

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hi! I'm a PDF downloader bot.\n\n"
        "Commands:\n"
        "/download - Download PDF documents\n"
        "/status - Check if files exist"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check if PDF files exist."""
    file_status = check_files_exist()
    
    message = "📁 **File Status:**\n\n"
    
    if file_status['document_2023.pdf']:
        message += "✅ document_2023.pdf - Available\n"
    else:
        message += "❌ document_2023.pdf - Not found\n"
    
    if file_status['document_2024.pdf']:
        message += "✅ document_2024.pdf - Available\n"
    else:
        message += "❌ document_2024.pdf - Not found\n"
    
    if file_status['both_exist']:
        message += "\n🎉 All files are ready!"
    else:
        message += "\n📥 Use /download to get missing files"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download PDF documents."""
    # Check current status first
    file_status = check_files_exist()
    
    if file_status['both_exist']:
        await update.message.reply_text(
            "✅ Both documents already exist!\n\n"
            "📁 Available files:\n"
            "• document_2023.pdf\n"
            "• document_2024.pdf"
        )
        return
    
    # Send initial message
    status_message = await update.message.reply_text("📥 Starting download process...")
    
    try:
        # Perform downloads
        results = download_all_pdfs()
        
        # Prepare response message
        message = "📥 **Download Results:**\n\n"
        
        for filename, status in results.items():
            if status == "downloaded":
                message += f"✅ {filename} - Successfully downloaded\n"
            elif status == "already_exists":
                message += f"📁 {filename} - Already exists\n"
            elif status.startswith("error"):
                message += f"❌ {filename} - {status}\n"
        
        # Check final status
        final_status = check_files_exist()
        if final_status['both_exist']:
            message += "\n🎉 All documents are now available!"
        else:
            message += "\n⚠️ Some downloads may have failed. Check logs for details."
        
        await status_message.edit_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        await status_message.edit_text(
            f"❌ Download failed with error:\n`{str(e)}`\n\n"
            "Please check your environment variables and try again.",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by Updates."""
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def main() -> None:
    """Start the bot."""
    # Get bot token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("download", download))
    application.add_handler(CommandHandler("status", status))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Run the bot until the user presses Ctrl-C
    print("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
