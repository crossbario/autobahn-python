import unittest2 as unittest
from autobahn.websocket.types import ConnectionAccept, ConnectionDeny


class ConnectionAcceptTests(unittest.TestCase):
    """
    Tests for autobahn.websocket.types.ConnectionAccept.
    """

    def test_subprotocol_type_assertions(self):
        """
        subprotocol must be a unicode string.
        """
        with self.assertRaises(AssertionError):
            ConnectionAccept(subprotocol=b'non-unicode types are invalid')

        unicode_subprotocol = u'unicode is valid'
        accepted_conn = ConnectionAccept(subprotocol=unicode_subprotocol)
        self.assertEqual(accepted_conn.subprotocol, unicode_subprotocol)

    def test_headers_type_assertions(self):
        """
        headers must be a dictionary with unicode keys, and values that are
        unicode, lists, or tuples.
        """
        with self.assertRaises(AssertionError):
            ConnectionAccept(headers='non-dictionary types are invalid')

        invalid_keys_dict = {b'this key is invalid': u'this value is valid'}
        invalid_values_dict = {u'this key is valid': b'this value is invalid'}

        with self.assertRaises(AssertionError):
            ConnectionAccept(headers=invalid_keys_dict)

        with self.assertRaises(AssertionError):
            ConnectionAccept(headers=invalid_values_dict)

        valid_dicts = [{u'valid key': u'unicode is valid'},
                       {u'valid key': []},  # lists are valid
                       {u'valid key': ()}]  # tuples are valid
        for valid_dict in valid_dicts:
            accepted_conn = ConnectionAccept(headers=valid_dict)
            self.assertEqual(accepted_conn.headers, valid_dict)


class ConnectionDenyTests(unittest.TestCase):
    """
    Tests for autobahn.websocket.types.ConnectionDeny.x
    """

    VALID_CODE = 123

    def test_code_type_assertions(self):
        """
        code must be an int.
        """
        with self.assertRaises(AssertionError):
            ConnectionDeny(code='invalid code')

        denied_connection = ConnectionDeny(self.VALID_CODE)
        self.assertEqual(denied_connection.code, self.VALID_CODE)

    def test_reason_type_assertions(self):
        """
        reason must be a unicode string.
        """

        with self.assertRaises(AssertionError):
            ConnectionDeny(code=self.VALID_CODE, reason=b'invalid reason')

        valid_reason = u'valid reason'
        denied_connection = ConnectionDeny(self.VALID_CODE,
                                           reason=valid_reason)
        self.assertEqual(denied_connection.reason, valid_reason)
