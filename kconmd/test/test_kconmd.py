import logging
import threading
import tempfile
import os

import pkg_resources
import pytest

from kconmd import kconMD
from kconmd.server import kconMD_client, kconMD_server


@pytest.fixture()
def cleandir():
    folder = tempfile.mkdtemp(prefix='testfiles-', dir='.')
    logging.info(f'Folder: {folder}:')
    os.chdir(folder)


@pytest.mark.usefixtures("cleandir")
class Test_all:
    @pytest.fixture(scope="class")
    def kconmd(self):
        xyzfilename = 'test.xyz'
        pbfilename = 'test.pb'
        forcefilename = 'force'

        for filename in (xyzfilename, pbfilename):
            with open(filename, 'wb') as f:
                f.write(pkg_resources.resource_string(__name__, filename))
        return kconMD(pbfilename, xyzfilename, forcefilename)

    def test_kconmd(self, kconmd):
        kconmd.printforce()
        self._printresult(kconmd)

    def test_server(self, kconmd):
        server = kconMD_server(kconmd)
        cilent = kconMD_client()
        t = threading.Thread(target=server.response, name='server')
        t.start()
        cilent.printforce()
        t.join()
        self._printresult(kconmd)

    @classmethod
    def _printresult(cls, kconmd):
        with open(kconmd.outputfilename) as f:
            logging.info("Force:")
            print(f.read())
