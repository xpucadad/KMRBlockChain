import logging
import unittest
from unittest import mock

import hashes
import test_utils
#from time import sleep

import accounts
from accounts import Account
from wallets import Wallet

class WalletsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_newWallet(self):
        # Create a wallet
        wallet = Wallet()

        # Create 2 accounts with Names
        a1_name = 'account 1'
        a1 = wallet.createNewAccount(a1_name)
        a1_raw_address = a1.getAddress()
        a1_b58_address = a1.getB58Address()
        a2_name = 'account 2'
        a2 = wallet.createNewAccount(a2_name)
        a2_raw_address = a2.getAddress()
        a2_b58_address = a2.getB58Address()

        # Retrieve the accounts by address and compare to the originals
        t1n = wallet.findNamedAccount(a1_name)
        self.assertTrue(a1.equals(t1n))
        t1a = wallet.findAccount(a1_raw_address)
        self.assertTrue(a1.equals(t1a))
        t1b = wallet.findAccount(a1_b58_address)
        self.assertTrue(a1.equals(t1b))

        t2n = wallet.findNamedAccount(a2_name)
        self.assertTrue(a2.equals(t2n))
        t2a = wallet.findAccount(a2_raw_address)
        self.assertTrue(a2.equals(t2a))
        t2b = wallet.findAccount(a2_b58_address)
        self.assertTrue(a2.equals(t2b))
        test_wallet_1 = 'test_newWallet_w1.dat'

        logging.debug("Writing to %s %s", test_wallet_1, wallet)
        wallet.saveToFile(test_wallet_1)
        w2 = Wallet()
        w2.loadFromFile(test_wallet_1)
        logging.debug("Read from %s %s", test_wallet_1, w2)

        t1n = w2.findNamedAccount(a1_name)
        self.assertTrue(a1.equals(t1n))
        t1a = w2.findAccount(a1_raw_address)
        self.assertTrue(a1.equals(t1a))
        t1b = w2.findAccount(a1_b58_address)
        self.assertTrue(a1.equals(t1b))

        t2n = w2.findNamedAccount(a2_name)
        self.assertTrue(a2.equals(t2n))
        t2a = w2.findAccount(a2_raw_address)
        self.assertTrue(a2.equals(t2a))
        t2b = w2.findAccount(a2_b58_address)
        self.assertTrue(a2.equals(t2b))

    def test_badB58Address(self):
        wallet = Wallet()
        account = wallet.createNewAccount('')
        logging.debug("test bad b58 new account %s", account)
        b58_address = account.getB58Address()
        if b58_address == 'A':
            new_10 = 'a'
        else:
            new_10 = 'A'
        bad_address = b58_address[0:10] + new_10 + b58_address[11:]
        logging.debug("test bad b58 corrupted address %s", bad_address)
        try:
            retrieved = wallet.findAccount(bad_address)
        except ResourceWarning as inst:
            logging.debug("Got expected resource warning for %s", inst.args)
            failed = True
        else:
            failed = False

        self.assertTrue(failed, "Bad address did not fail in find")

        # Now pass a bad type to the decode to check that
        try:
            retrieved = wallet.findAccount(1)
        except ResourceWarning as inst:
            logging.debug("Got expected resource warning for %s", inst.args)
            failed = True
        else:
            failed = False
        self.assertTrue(failed, "Incorrect address type did not fail in find")

def suite():
    suite = unittest.TestSuite()
    suite.addTest(WalletsTestCase('test_newWallet'))
    suite.addTest(WalletsTestCase('test_badB58Address'))
    return suite

if __name__ == '__main__':
    log_file = 'test_wallets.log'
    test_utils.setup_logging(log_file)

    logging.info('Log started in file %s', log_file)
    runner = unittest.TextTestRunner(verbosity = 2)
    test_suite = suite()
    runner.run(test_suite)
    logging.info('Log ended')
