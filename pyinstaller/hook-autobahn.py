from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("autobahn")

# Most of the following are found automatically by PyInstaller - but some are not!
# To be on the safe side, we list _all_ modules here, which needs to be kept in
# sync manually
[
    "autobahn",
    "autobahn.asyncio",
    "autobahn.asyncio.test",
    "autobahn.nvx",
    "autobahn.nvx.test",
    "autobahn.rawsocket",
    "autobahn.rawsocket.test",
    "autobahn.test",
    "autobahn.twisted",
    "autobahn.twisted.test",
    "autobahn.twisted.testing",
    "autobahn.wamp",
    "autobahn.wamp.flatbuffers",
    "autobahn.wamp.gen",
    "autobahn.wamp.gen.schema",
    "autobahn.wamp.gen.wamp",
    "autobahn.wamp.gen.wamp.proto",
    "autobahn.wamp.test",
    "autobahn.websocket",
    "autobahn.websocket.test",
]
