import unittest
import solution
import subprocess
import os

class RunTest(unittest.TestCase):
    working_folder = os.environ.get('working_folder', None)

    def setUp(self):
        self.script = solution.__file__
        self.command = f'{self.script}'
        assert self.working_folder is not None, f'invalid working_folder={self.working_folder}'
        assert os.path.exists(self.working_folder), f'working_folder={self.working_folder} does nto exist'


    def execute(self, *args):
        iargs = ' '.join(map(str, args)) or ''
        icommand = f'python3 {self.command} {iargs}'
        p = subprocess.Popen(icommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return p.returncode, out, err


    def test_noargs(self):
        assert self.execute()[0] > 0


    def test_help(self):
        assert self.execute('-h')[0] == 0

    def test_default(self):

        rc, out, err = self.execute('-wf', self.working_folder)
        assert rc == 0

if __name__ == '__main__':
    unittest.main()