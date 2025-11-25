"""
Entry point for running the Yandex Tracker Telegram Bot
"""

from main_bot import bot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Main entry point"""
    print("Starting the Yandex Tracker Telegram Bot...")
    print("Bot is running. Press Ctrl+C to stop.")
    
    try:
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        print("\nStopping the bot...")
    except Exception as e:
        logging.error(f"Error running bot: {e}")

if __name__ == '__main__':
    main()