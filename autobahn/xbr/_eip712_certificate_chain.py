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

from typing import List, Tuple, Dict, Any, Union

from autobahn.xbr._eip712_delegate_certificate import EIP712DelegateCertificate
from autobahn.xbr._eip712_authority_certificate import EIP712AuthorityCertificate


def parse_certificate_chain(certificates: List[Tuple[Dict[str, Any], str]]) \
        -> List[Union[EIP712DelegateCertificate, EIP712AuthorityCertificate]]:
    """

    :param certificates:
    :return:
    """
    # parse the whole certificate chain
    cert_chain = []
    for cert_hash, cert_data, cert_sig in certificates:
        if cert_data['primaryType'] == 'EIP712DelegateCertificate':
            cert = EIP712DelegateCertificate.parse(cert_data)
        elif cert_data['primaryType'] == 'EIP712AuthorityCertificate':
            cert = EIP712AuthorityCertificate.parse(cert_data)
        else:
            assert False, 'should not arrive here'
        cert_chain.append(cert)

    # FIXME: proper adaptive implementation of certificate chain rules checking
    # if False:
    #     assert len(cert_chain) == 3
    #
    #     # Certificate Chain Rules (CCR):
    #     #
    #     # 1. **CCR-1**: The `chainId` and `verifyingContract` must match for all certificates to what we expect, and `validFrom` before current block number on the respective chain.
    #     # 2. **CCR-2**: The `realm` must match for all certificates to the respective realm.
    #     # 3. **CCR-3**: The type of the first certificate in the chain must be a `EIP712DelegateCertificate`, and all subsequent certificates must be of type `EIP712AuthorityCertificate`.
    #     # 4. **CCR-4**: The last certificate must be self-signed (`issuer` equals `subject`), it is a root CA certificate.
    #     # 5. **CCR-5**: The intermediate certificate's `issuer` must be equal to the `subject` of the previous certificate.
    #     # 6. **CCR-6**: The root certificate must be `validFrom` before the intermediate certificate
    #     # 7. **CCR-7**: The `capabilities` of intermediate certificate must be a subset of the root cert
    #     # 8. **CCR-8**: The intermediate certificate's `subject` must be the delegate certificate `delegate`
    #     # 9. **CCR-9**: The intermediate certificate must be `validFrom` before the delegate certificate
    #     # 10. **CCR-10**: The root certificate's signature must be valid and signed by the root certificate's `issuer`.
    #     # 11. **CCR-11**: The intermediate certificate's signature must be valid and signed by the intermediate certificate's `issuer`.
    #     # 12. **CCR-12**: The delegate certificate's signature must be valid and signed by the `delegate`.
    #
    #     # CCR-1
    #     chainId = 1
    #     verifyingContract = a2b_hex('0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57'[2:])
    #     for cert in cert_chain:
    #         assert cert.chainId == chainId
    #         assert cert.verifyingContract == verifyingContract
    #
    #     # CCR-2
    #     realm = a2b_hex('0xA6e693CC4A2b4F1400391a728D26369D9b82ef96'[2:])
    #     for cert in cert_chain[1:]:
    #         assert cert.realm == realm
    #
    #     # CCR-3
    #     assert isinstance(cert_chain[0], EIP712DelegateCertificate)
    #     for i in [1, len(cert_chain) - 1]:
    #         assert isinstance(cert_chain[i], EIP712AuthorityCertificate)
    #
    #     # CCR-4
    #     assert cert_chain[2].subject == cert_chain[2].issuer
    #
    #     # CCR-5
    #     assert cert_chain[1].issuer == cert_chain[2].subject
    #
    #     # CCR-6
    #     assert cert_chain[2].validFrom <= cert_chain[1].validFrom
    #
    #     # CCR-7
    #     assert cert_chain[2].capabilities == cert_chain[2].capabilities | cert_chain[1].capabilities
    #
    #     # CCR-8
    #     assert cert_chain[1].subject == cert_chain[0].delegate
    #
    #     # CCR-9
    #     assert cert_chain[1].validFrom <= cert_chain[0].validFrom
    #
    #     # CCR-10
    #     _issuer = cert_chain[2].recover(a2b_hex(cert_sigs[2]))
    #     assert _issuer == cert_chain[2].issuer
    #
    #     # CCR-11
    #     _issuer = cert_chain[1].recover(a2b_hex(cert_sigs[1]))
    #     assert _issuer == cert_chain[1].issuer
    #
    #     # CCR-12
    #     _issuer = cert_chain[0].recover(a2b_hex(cert_sigs[0]))
    #     assert _issuer == cert_chain[0].delegate

    return cert_chain
