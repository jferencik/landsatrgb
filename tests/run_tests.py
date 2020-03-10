import unittest
import solution
import subprocess

class RunTest(unittest.TestCase):

    def setUp(self) -> None:
        self.script = solution.__file__
        self.command = f'{self.script}'

    def execute(self, **args):
        iargs = ' '.join(map(str, args)) or ''
        icommand = f'{self.command} {iargs}'
        print(icommand)
        stdout = subprocess.call(icommand)
        return 0

    def test_default(self):
        assert self.execute() == 0


if __name__ == '__main__':
    unittest.main()