from pprint import pprint
import time
from web3.auto import w3
from autobahn import xbr

xbr.setProvider(w3)

# FIXME: event_filter.get_all_entries() should (also) allow to get the events

def _process_block(block):
    event_filter = xbr.xbrToken.events.Transfer().createFilter(fromBlock=block, toBlock=block)
    result = w3.eth.getLogs(event_filter.filter_params)
    if result:
        for evt in result:
            receipt = w3.eth.getTransactionReceipt(evt['transactionHash'])
            args = xbr.xbrToken.events.Transfer().processReceipt(receipt)
            args = args[0].args
            print('event: {} XBR token transferred from {} to {}'.format(args.value, args['from'], args.to))
    else:
        print('no events of interest to us in block {}'.format(block))

last_processed = -1

while True:
    current = w3.eth.getBlock('latest')

    while last_processed < current.number:
        last_processed += 1
        print('processing block: {}'.format(last_processed))
        _process_block(last_processed)

    time.sleep(1)
