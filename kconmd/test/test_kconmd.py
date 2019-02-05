import unittest
import logging

import pkg_resources

from kconmd import kconMD


class Test_all(unittest.TestCase):
    def test_fragment(self):
        xyzfilename = 'test.xyz'
        pbfilename = 'test.pb'
        forcefilename = 'force'

        for filename in (xyzfilename, pbfilename):
            with open(filename, 'wb') as f:
                f.write(pkg_resources.resource_string(__name__, filename))
        kconMD(pbfilename, xyzfilename, forcefilename, cell=[
            31.219299, 31.219299, 31.219299]).printforce()

        with open(forcefilename) as f:
            logging.info("Force:")
            print(f.read())


if __name__ == '__main__':
    unittest.main()
