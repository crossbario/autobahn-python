from pprint import pprint
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('xbr')

pprint(datas)

hiddenimports = [
    'Crypto.Cipher',
    'Crypto.Signature',
    'Crypto.Hash',
    'Crypto.PublicKey',
    'Crypto.Protocol',
    'Crypto.IO',
    'Crypto.Random',
    'Crypto.Util',
    'Crypto.IO',
]
