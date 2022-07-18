###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
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

from binascii import a2b_hex
from typing import List, Tuple, Dict, Any, Union

from autobahn.xbr._eip712_delegate_certificate import EIP712DelegateCertificate
from autobahn.xbr._eip712_authority_certificate import EIP712AuthorityCertificate


def parse_certificate_chain(certificates: List[Tuple[Dict[str, Any], str]]) \
        -> List[Union[EIP712DelegateCertificate, EIP712AuthorityCertificate]]:
    """

    :param certificates:
    :return:
    """
    # CC0:
    # parse the whole certificate chain
    cert_chain = []
    cert_sigs = []
    for cert_data, cert_sig in certificates:
        if cert_data['primaryType'] == 'EIP712DelegateCertificate':
            cert = EIP712DelegateCertificate.parse(cert_data['message'])
        elif cert_data['primaryType'] == 'EIP712AuthorityCertificate':
            cert = EIP712AuthorityCertificate.parse(cert_data['message'])
        else:
            assert False, 'should not arrive here'
        cert_chain.append(cert)
        cert_sigs.append(cert_sig)

    # FIXME: allow length 2 and length > 3
    assert len(cert_chain) == 3

    # CC1:
    # check certificate types - the first must be a EIP712DelegateCertificate, and all
    # subsequent certificates must be of type EIP712AuthorityCertificate
    assert isinstance(cert_chain[0], EIP712DelegateCertificate)
    for i in [1, len(cert_chain) - 1]:
        assert isinstance(cert_chain[i], EIP712AuthorityCertificate)

    # CC2:
    # last certificate must be self-signed - it is a root CA certificate
    assert cert_chain[2].subject == cert_chain[2].issuer

    # CC3.1:
    # intermediate certificate's issuer must be the root CA certificate subject
    assert cert_chain[1].issuer == cert_chain[2].subject

    # CC3.2:
    # and root certificate must be valid before the intermediate certificate
    assert cert_chain[2].validFrom <= cert_chain[1].validFrom

    # CC3.3:
    # and capabilities of intermediate certificate must be a subset of the root cert
    assert cert_chain[2].capabilities == cert_chain[2].capabilities | cert_chain[1].capabilities

    # CC4.1:
    # intermediate certificate's subject must be the delegate certificate delegate
    assert cert_chain[1].subject == cert_chain[0].delegate

    # CC4.2:
    # and intermediate certificate must be valid before the delegate certificate
    assert cert_chain[1].validFrom <= cert_chain[0].validFrom

    # CC5:
    # verify signature on root certificate
    _issuer = cert_chain[2].recover(a2b_hex(cert_sigs[2]))
    assert _issuer == cert_chain[2].issuer

    # CC6:
    # verify signature on intermediate certificate
    _issuer = cert_chain[1].recover(a2b_hex(cert_sigs[1]))
    assert _issuer == cert_chain[1].issuer

    # CC7:
    # verify signature on delegate certificate
    _issuer = cert_chain[0].recover(a2b_hex(cert_sigs[0]))
    assert _issuer == cert_chain[0].delegate

    return cert_chain
