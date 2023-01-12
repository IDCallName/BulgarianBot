import telegram
import telegram.ext

import mysql.connector as mysql


#
#  BOT STARTUP
#

BOT_TOKEN = 'CENSORED'

updater = telegram.ext.Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

#
#  CONNECTING TO MYSQL SERVER
#

try:
    hostname: str = "tabeltabel.mysql.pythonanywhere-services.com"
    username: str = "tabeltabel"
    password: str = "cooldatabase"

    connection = mysql.connect(host=hostname, user=username, password=password, database="tabeltabel$telegram_db")

except mysql.Error as err:
    print(err)

#
#  USER CLASS
#

class User:

    # ______________________
    # Just a /start command, idk
    def __init__(self, telegramid: str):

        # creating query

        mysql_query: str = "SELECT tgid, description FROM users WHERE tgid = '%s';" % (telegramid)

        # executing query and getting result

        with connection.cursor() as cursor:
            cursor.execute(mysql_query)
            mysql_result = cursor.fetchall()

        # creating database entry if result is empty
        if (len(mysql_result) == 0):
            mysql_query: str = "INSERT INTO users (tgid) VALUES (%s)" % (telegramid)

            self.userindx = telegramid
            self.userdesc = None

            with connection.cursor() as cursor:
                cursor.execute(mysql_query)
                connection.commit()

        # setting vars if entry exists
        else:
            self.userindx: int = telegramid
            self.userdesc: str = mysql_result[0][1]


    # ______________________
    # Command for changing user data in DB
    def update(self, *args: tuple): # tuples of format (COLUMN_NAME, COLUMN_VALUE)
        # Making up query text from args
        mysql_query: str = "UPDATE users SET %s = '%s'" % (args[0][0], args[0][1])

        for i in range(1, len(args)):
            mysql_query += ", %s = '%s'" % (args[i][0], args[i][1])

        mysql_query += " WHERE tgid = %s" % (self.userindx)

        # Updating
        with connection.cursor() as cursor:
            cursor.execute(mysql_query)
            connection.commit()

#
#  COMMANDS
#

# On /start
def cmd_start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Правяраю Вас у БД")

    userid = str(update.message.from_user.id);
    user = User(userid)

    message = "Ваше імя: %s\nВаше апісанне: %s" % (user.userindx, user.userdesc)

    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# On /info
def cmd_info(update, context):
    replyTo = update.message.reply_to_message;

    message: str = '';

    # if command is not a reply
    if replyTo == None:
        message = "Калі ласка, ўвядзіце гэту каманду ў адказ на паведамленьне удзельніка чату"
    # if command is a reply
    else:
        userid = str(replyTo.from_user.id);
        user = User(userid)

        message = "Апісанне: %s" % (user.userdesc)

    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# On /setdesc
def cmd_setdesc(update, context):
    # setting some variables
    userid : str  = str(update.message.from_user.id);
    user   : User = User(userid)
    message: str  = ''

    # if user hasn't specified the description
    if len(context.args) == 0:
        message = "Каманда патребна быць у фармаце '/setdesc [АПІСАННЕ]'"

    # if user specified the description
    else:
        description: str = ' '.join(context.args)
        user.update(("description", description))

        message = "Гатова!"

    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

#
#  HANDLERS
#

from telegram.ext import CommandHandler

start_handler   = CommandHandler('start', cmd_start)
info_handler    = CommandHandler('info', cmd_info)
setdesc_handler = CommandHandler('setdesc', cmd_setdesc)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(info_handler)
dispatcher.add_handler(setdesc_handler)

#
# START POLLING
#

updater.start_polling()
