###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from autobahn.xbr import HAS_XBR

if HAS_XBR:
    import unittest
    import binascii
    from autobahn.xbr import generate_seedphrase, check_seedphrase, account_from_seedphrase

    _SEEDPHRASE = "myth like bonus scare over problem client lizard pioneer submit female collect"
    _INVALID_SEEDPHRASE = "9 nn \0 kk$"

    _EXPECTED = [
        ('0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1', '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'),
        ('0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0', '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'),
        ('0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b', '0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c'),
        ('0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d', '0x646f1ce2fdad0e6deeeb5c7e8e5543bdde65e86029e2fd9fc169899c440a7913'),
        ('0xd03ea8624C8C5987235048901fB614fDcA89b117', '0xadd53f9a7e588d003326d1cbf9e4a43c061aadd9bc938c843a79e7b4fd2ad743'),
        ('0x95cED938F7991cd0dFcb48F0a06a40FA1aF46EBC', '0x395df67f0c2d2d9fe1ad08d1bc8b6627011959b79c53d7dd6a3536a33ab8a4fd'),
        ('0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9', '0xe485d098507f54e7733a205420dfddbe58db035fa577fc294ebd14db90767a52'),
        ('0x28a8746e75304c0780E011BEd21C72cD78cd535E', '0xa453611d9419d0e56f499079478fd72c37b251a94bfde4d19872c44cf65386e3'),
        ('0xACa94ef8bD5ffEE41947b4585a84BdA5a3d3DA6E', '0x829e924fdf021ba3dbbc4225edfece9aca04b929d6e75613329ca6f1d31c0bb4'),
        ('0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e', '0xb0057716d5917badaf911b193b12b910811c1497b5bada8d7711f758981c3773'),
        ('0x610Bb1573d1046FCb8A70Bbbd395754cD57C2b60', '0x77c5495fbb039eed474fc940f29955ed0531693cc9212911efd35dff0373153f'),
        ('0x855FA758c77D68a04990E992aA4dcdeF899F654A', '0xd99b5b29e6da2528bf458b26237a6cf8655a3e3276c1cdc0de1f98cefee81c01'),
        ('0xfA2435Eacf10Ca62ae6787ba2fB044f8733Ee843', '0x9b9c613a36396172eab2d34d72331c8ca83a358781883a535d2941f66db07b24'),
        ('0x64E078A8Aa15A41B85890265648e965De686bAE6', '0x0874049f95d55fb76916262dc70571701b5c4cc5900c0691af75f1a8a52c8268'),
        ('0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598', '0x21d7212f3b4e5332fd465877b64926e3532653e2798a11255a46f533852dfe46'),
        ('0xf408f04F9b7691f7174FA2bb73ad6d45fD5d3CBe', '0x47b65307d0d654fd4f786b908c04af8fface7710fc998b37d219de19c39ee58c'),
        ('0x66FC63C2572bF3ADD0Fe5d44b97c2E614E35e9a3', '0x66109972a14d82dbdb6894e61f74708f26128814b3359b64f8b66565679f7299'),
        ('0xF0D5BC18421fa04D0a2A2ef540ba5A9f04014BE3', '0x2eac15546def97adc6d69ca6e28eec831189baa2533e7910755d15403a0749e8'),
        ('0x325A621DeA613BCFb5B1A69a7aCED0ea4AfBD73A', '0x2e114163041d2fb8d45f9251db259a68ee6bdbfd6d10fe1ae87c5c4bcd6ba491'),
        ('0x3fD652C93dFA333979ad762Cf581Df89BaBa6795', '0xae9a2e131e9b359b198fa280de53ddbe2247730b881faae7af08e567e58915bd'),
    ]

    class TestEthereumMnemonic(unittest.TestCase):

        def test_check_valid_seedphrase(self):
            self.assertTrue(check_seedphrase(_SEEDPHRASE))

        def test_check_invalid_seedphrase(self):
            self.assertFalse(check_seedphrase(_INVALID_SEEDPHRASE))

        def test_generate_seedphrase(self):
            for strength in [128, 160, 192, 224, 256]:
                seedphrase = generate_seedphrase(strength)

                self.assertEqual(type(seedphrase), str)
                for word in seedphrase.split():
                    self.assertTrue(type(word) == str)
                self.assertTrue(check_seedphrase(seedphrase))

        def test_derive_wallet(self):
            for i, (public_adr, private_key) in enumerate(_EXPECTED):
                account = account_from_seedphrase(_SEEDPHRASE, i)
                private_key = binascii.a2b_hex(private_key[2:])

                self.assertEqual(account.address, public_adr)
                self.assertEqual(account.key, private_key)
