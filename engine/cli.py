# Executable CLI version

import time
from datetime import timedelta
from engine.structs import Transaction
from engine.game import Game
from engine.settings import *

current_tx: Transaction | None = None
reward_requested: int | None = None
loop_end = False
game = Game()


def transaction(args_: list[str]):
    global current_tx
    if len(args_) < 1:
        if current_tx is None:
            print('No pending transaction. Get a new one with "transaction new"')
        else:
            print(current_tx.printable())
    elif args_[0] in ('new', 'get'):
        if current_tx is not None:
            print(f'Transaction {current_tx.tx_id} is still waiting for your decision')
        else:
            current_tx = game.new_tx()
            print(f'New transaction obtained! View it with "transaction"')
    elif args_[0] in ('count', 'stats'):
        accepted_ = len(game.block.transactions)
        rejected_ = len(game.rejected_tx)
        message = f'You have processed {accepted_ + rejected_} transactions so far ({accepted_} accepted, {rejected_} rejected)'
        if current_tx is not None:
            message += f'. Also, one more is waiting for your decision'
        print(message)
    else:
        print(f'Unknown subcommand "{args_[0]}"')

def utxo(args_: list[str]):
    if len(args_) < 1:
        print('You need to provide transaction ID')
    else:
        tx_id = args_[0]
        sources = game.source_lookup(tx_id)
        if len(sources) == 0:
            print(f'Transaction {tx_id} not found')
        else:
            for src in sources:
                print(src.printable())

def accept():
    global current_tx
    if current_tx is None:
        print('Nothing to accept. Get a new transaction with "transaction new"')
    else:
        game.accept(current_tx)
        print(f'Transaction {current_tx.tx_id} accepted')
        current_tx = None

def reject():
    global current_tx
    if current_tx is None:
        print('Nothing to reject. Get a new transaction with "transaction new"')
    else:
        game.reject(current_tx)
        print(f'Transaction {current_tx.tx_id} rejected')
        current_tx = None

def reward():
    if current_tx is not None:
        print(f'Transaction {current_tx.tx_id} is still waiting for your decision')
    elif len(game.block.transactions) < REQUIRED_TX:
        print(f'You have only {len(game.block.transactions)} out of {REQUIRED_TX} required accepted transactions.')
    else:
        global reward_requested
        reward_requested = game.block.reward(include_wrong=True)
        _btc = reward_requested / 100_000_000
        print(f'You have requested a reward of {_btc} BTC (3.125 for mining + sum of transaction fees)')

def nonce_find():
    nonce = 0
    if reward_requested is None:
        print(f'You have not requested a reward yet. Do it with "reward"')
    else:
        print(f'Time to find the nonce value. The block\'s hash has to start with {ZEROS_REQUIRED} zeros')
        print(f'Keep pressing ENTER to test values, type "exit" to exit')
        try:
            while True:
                _inp = input()
                if _inp.lower() in ('exit', 'quit', 'end', 'leave', 'x'):
                    return
                block_hash = game.block.hash(nonce)
                print(f'Block hash for nonce={nonce}: {block_hash}')
                nonce += 1
        except KeyboardInterrupt:
            return


def close(args_: list[str]):
    global loop_end
    if reward_requested is None:
        print(f'You have not requested a reward yet. Do it with "reward"')
    elif len(args_) < 1:
        print(f'You need to provide the nonce value, such that this block\'s hash starts with {ZEROS_REQUIRED} zeros')
    else:
        try:
            nonce = int(args_[0])
        except ValueError:
            print('Nonce has to be a number')
            return
        if nonce >= 2 ** 32:
            print('Nonce needs to take up at most 4 bytes')
            return
        block_hash = game.block.hash(nonce)
        if not block_hash.startswith('0' * ZEROS_REQUIRED):
            print(f'With that nonce, the block hash is {block_hash}, so does not start with {ZEROS_REQUIRED} zeros')
            return
        print(f'Success! Your own block {block_hash} is ready to go!')
        loop_end = True


start_time = time.time()
while not loop_end:
    print(PROMPT)
    inp = input().strip('/').split()
    if len(inp) == 0:
        continue
    command, args = inp[0].lower(), inp[1:]
    if command in ('transaction', 'tx'):
        transaction(args)
    elif command in ('utxo', 'utxos', 'input'):
        utxo(args)
    elif command == 'accept':
        accept()
    elif command == 'reject':
        reject()
    elif command in ('reward', 'prize', 'payout'):
        reward()
    elif command == 'nonce':
        nonce_find()
    elif command in ('close', 'end', 'sign'):
        close(args)
    else:
        print(f'Unknown command "{command}"')
print('---')
print('Press ENTER to publish (you can\'t turn back anymore)... ')
input()

elapsed = time.time() - start_time
elapsed_delta = timedelta(seconds=elapsed)
tx_num = len(game.block.transactions) + len(game.rejected_tx)
summary = game.result_summary()
real_reward = game.block.reward(include_wrong=False)
reward_diff = reward_requested - real_reward
btc = real_reward / 100_000_000
btc_diff = reward_diff / 100_000_000

print('Congratulations! You have published your block! Time for some results:')
print('---')
print(f'You processed {tx_num} transactions in {elapsed_delta}')
print(f'\t...that is {elapsed / tx_num:.2f} seconds per transaction!')
print('---')
print(f'Transaction decisions - {summary[True]} correct and {summary[False]} incorrect:')
for r in game.results:
    print('...' + r.printable())
print('---')
print(f'You got a reward of {btc} BTC (3.125 for mining + sum of transaction fees)')
if btc_diff > 0:
    print(f'\t...although you requested {btc_diff} BTC more (a bit greedy, aren\'t we?)')
elif btc_diff < 0:
    print(f'\t...although you requested {abs(btc_diff)} BTC less (don\'t be so modest)')
else:
    print('\t...and this is exactly how much you requested. Perfect!')
