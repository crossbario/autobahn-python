
# coding: utf-8

# In[ ]:


DBPATH = '../../crossbar/.xbrdb-transactions'

import os

print(os.listdir(DBPATH))


# In[ ]:


import zlmdb
from cfxdb.xbr import Schema

db = zlmdb.Database(DBPATH, maxsize=2**30, readonly=False)

schema = Schema.attach(db)

print(schema.token_transfers)
print(schema.payment_channels)


# In[ ]:


from binascii import b2a_hex

with db.begin() as txn:
    for token_transfer in schema.token_transfers.select(txn, return_values=True, return_keys=False, limit=20):
        print(b2a_hex(token_transfer.from_address), b2a_hex(token_transfer.to_address))


# # Counting

# Here is how you count all XBR token transfers:

# In[ ]:


with db.begin() as txn:
    cnt = schema.token_transfers.count(txn)

print('total token transfers:', cnt)


# The database is updated by CrossbarFX as it is watching the blockchain and insert new records into the database as they arrive:

# In[ ]:


import time

t = 10
while t > 0:
    with db.begin() as txn:
        cnt = schema.token_transfers.count(txn)
    print('total token transfers:', cnt)
    time.sleep(1)
    t -= 1


# # Payment Channels
# 
# Here is how to access payment channels stored and operated on within a XBR market maker:

# In[ ]:


with db.begin() as txn:
    for channel in schema.payment_channels.select(txn, return_values=True, return_keys=False, limit=20):
        print('consumer={}.. delegate={}.. amount={} state={}'.format(
            channel.sender.hex()[:8], channel.delegate.hex()[:8], channel.amount, channel.state))

