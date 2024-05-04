import logging
import numpy as np

from tictactoe_twg.TicTacToeTWGGame import TicTacToeTWGGame
from othello.OthelloPlayers import RandomPlayer
from MCTS import MCTS
from tictactoe_twg.pytorch.NNet import NNetWrapper as NNet
from telegram import Update, ReplyKeyboardMarkup, ForceReply
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, CallbackQueryHandler

from utils import *

from collections import defaultdict

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

ENTRY, PLAYER_MOVE = range(2)

class TicTacToeTWGBot():
    def __init__(self, token):
        self.user_storage = dict()
        self.app = ApplicationBuilder().token(token).build()
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('play', self.init_game)],
            states={
                ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.run_game)],
                PLAYER_MOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_human_input)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            allow_reentry=True
        )
        start_handler = CommandHandler('start', self.start)

        self.app.add_handler(start_handler)
        self.app.add_handler(conversation_handler)

    async def init_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Send a message when the '/play' command is issued."""
        await update.message.reply_text('Welcome! Lets play TicTacToe on torus with gravity! Loading the game.')
        user_id = update.message.from_user.id
        game = TicTacToeTWGGame()
        self.user_storage[user_id] = dict(
            game = game,
            # ai_player = RandomPlayer(game).play
            ai_player = self.init_ai(game),
            display = game.display_tg,
            board = game.getInitBoard(),
            curPlayer = 1
        )
        logger.info(f'initalized for user {update.message.from_user.username}')
        await update.message.reply_text('Game loaded. Type anything to continue. Type /cancel if you want to end the game')
        return ENTRY

    async def run_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the game routing."""
        user_data = self.get_user_data(update)
        if len(user_data) == 0:
            await update.message.reply_text('Sorry, sosmething went wrong :(')
            return ConversationHandler.END
        string_board = np.array2string(user_data['display'](user_data['board']))
        await update.message.reply_text(string_board)
        valids = user_data['game'].getValidMoves(user_data['game'].getCanonicalForm(user_data['board'], user_data['curPlayer']), user_data['curPlayer'])
        moves = []
        for i in range(len(valids)):
            if valids[i]:
                row, col = i%user_data['game'].rows, int(i/user_data['game'].rows)
                moves.append(f'{row} {col}')
        moves = '; '.join(moves)
        game_status = user_data['game'].getGameEnded(user_data['board'], 1) 
        if game_status == 0:
            if user_data['curPlayer'] == 1:
                await update.message.reply_text(f'Make a move, available moves: {moves}', reply_markup=ForceReply(selective=True))
                return PLAYER_MOVE
            else:
                await self.process_ai(update, context, user_data)
        else:
            if game_status == 1:
                await update.message.reply_text('You won!')
            else:
                await update.message.reply_text('Humanity is doomed! Game over! ')
            return ConversationHandler.END
        return ConversationHandler.END
        
    async def process_ai(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_data) -> int:
        """Handle the ai's moves."""
        action = user_data['ai_player'](user_data['game'].getCanonicalForm(user_data['board'], user_data['curPlayer']))
        valids = user_data['game'].getValidMoves(user_data['game'].getCanonicalForm(user_data['board'], user_data['curPlayer']), user_data['curPlayer'])
        if valids[action] == 0:
            logger.error(f'Action {action} is not valid!')
            logger.debug(f'valids = {valids}')
            assert valids[action] > 0
        user_data['board'], user_data['curPlayer'] = user_data['game'].getNextState(user_data['board'], user_data['curPlayer'], action)
        await update.message.reply_text('My move!')
        await self.run_game(update, context)

    async def process_human_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_data = self.get_user_data(update)
        if len(user_data) == 0:
            await update.message.reply_text('Sorry, sosmething went wrong :(')
            return ConversationHandler.END
        user_input = update.message.text
        valids = user_data['game'].getValidMoves(user_data['game'].getCanonicalForm(user_data['board'], user_data['curPlayer']), user_data['curPlayer'])
        try:
            row, col = [int(x) for x in user_input.split(' ')] #x: row, y: col
            action = user_data['game'].rows * col + row if row != -1 else user_data['game'].rows * user_data['game'].cols
            assert valids[action] == 1
        except:
            logger.error(f'Action is not valid!')
            logger.debug(f'valids = {valids}')
            await update.message.reply_text('Action is invalid! Make another', reply_markup=ForceReply(selective=True))
            return PLAYER_MOVE
        
        user_data['board'], user_data['curPlayer'] = user_data['game'].getNextState(user_data['board'], user_data['curPlayer'], action)
        await self.run_game(update, context)

    async def cancel(self, update: Update, context: CallbackContext) -> int:
        """Allow the user to cancel the conversation."""
        await update.message.reply_text('Game cancelled.')
        return ConversationHandler.END
    
    async def start(self, update: Update, context: CallbackContext):
        await update.message.reply_text('Hello! You can play tictactoe on torus with gravity with me if you type /play.')
    
    def get_user_data(self, update):
        user_id = update.message.from_user.id
        if self.user_storage[user_id]:
            # logger.info(self.user_storage[user_id])
            return self.user_storage[user_id]
        else:
            logger.error('Something went wrong! No such user in memory!')
            return dict()

    @staticmethod
    def init_ai(game):
        n1 = NNet(game)
        n1.load_checkpoint('./pretrained_models/tictactoe_twg/pytorch','best.pth.tar')
        args1 = dotdict({'numMCTSSims': 42, 'cpuct':1.0})
        mcts1 = MCTS(game, n1, args1)
        n1p = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))
        return n1p

    def run(self):
        """Run the bot."""
        self.app.run_polling()


if __name__ == '__main__':
    TOKEN = 'TOKEN'
    game_bot = TicTacToeTWGBot(TOKEN)
    game_bot.run()
    