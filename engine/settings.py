REQUIRED_TX = 2
MESSAGES = {
    'none': 'This transaction is correct',
    'script_failed': 'In this transaction, script verification fails',
    'negative_fee': 'In this transaction, sum of outputs is larger that sum of inputs',
    'invalid_input': 'This transaction uses non-existent funds',
    'already_spent': 'This transaction uses funds which had already been spent',
}
PROMPT = '~ CryptoMiner ~'
ZEROS_REQUIRED = 2
SCRIPT_LENGTH = 3  # Relative script length. 2 will be extremely short, 10 will be extremely long.