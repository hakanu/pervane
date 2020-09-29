import unittest
import serve
import argparse


class ServeTest(unittest.TestCase):
    def test_str2bool(self):
        self.assertTrue(serve._str2bool('True'))
        self.assertTrue(serve._str2bool('TRUE'))
        self.assertTrue(serve._str2bool('true'))
        self.assertTrue(serve._str2bool('T'))
        self.assertTrue(serve._str2bool('t'))
        self.assertTrue(serve._str2bool('trUe'))
        self.assertTrue(serve._str2bool('1'))
        self.assertTrue(serve._str2bool('Yes'))
        self.assertTrue(serve._str2bool('YES'))
        self.assertTrue(serve._str2bool('yes'))
        self.assertTrue(serve._str2bool('yeS'))
        self.assertTrue(serve._str2bool('Y'))
        self.assertTrue(serve._str2bool('y'))
        self.assertFalse(serve._str2bool('False'))
        self.assertFalse(serve._str2bool('FALSE'))
        self.assertFalse(serve._str2bool('false'))
        self.assertFalse(serve._str2bool('F'))
        self.assertFalse(serve._str2bool('f'))
        self.assertFalse(serve._str2bool('faLse'))
        self.assertFalse(serve._str2bool('0'))
        self.assertFalse(serve._str2bool('No'))
        self.assertFalse(serve._str2bool('NO'))
        self.assertFalse(serve._str2bool('no'))
        self.assertFalse(serve._str2bool('nO'))
        self.assertFalse(serve._str2bool('N'))
        self.assertFalse(serve._str2bool('n'))
        with self.assertRaises(argparse.ArgumentTypeError):
            serve._str2bool('')
        with self.assertRaises(argparse.ArgumentTypeError):
            serve._str2bool('asd')
        with self.assertRaises(TypeError):
            serve._str2bool(True)
        with self.assertRaises(TypeError):
            serve._str2bool(False)
        with self.assertRaises(TypeError):
            serve._str2bool(1)
        with self.assertRaises(TypeError):
            serve._str2bool(0)

    def test_is_filename_allowed(self):
        self.assertTrue(serve._is_filename_allowed('a.txt'))
        self.assertTrue(serve._is_filename_allowed('a.TXT'))
        self.assertTrue(serve._is_filename_allowed('a.txT'))
        self.assertTrue(serve._is_filename_allowed('b.pdf'))
        self.assertTrue(serve._is_filename_allowed('c.png'))
        self.assertTrue(serve._is_filename_allowed('d.jpg'))
        self.assertTrue(serve._is_filename_allowed('e.jpeg'))
        self.assertTrue(serve._is_filename_allowed('f.gif'))
        self.assertTrue(serve._is_filename_allowed('çöşığüé§âİ.gif'))
        self.assertTrue(serve._is_filename_allowed('asd.qwe.jpeg'))
        self.assertFalse(serve._is_filename_allowed('zxc.gİf'))
        self.assertFalse(serve._is_filename_allowed(''))
        self.assertFalse(serve._is_filename_allowed('asd'))
        self.assertFalse(serve._is_filename_allowed('.'))
        self.assertFalse(serve._is_filename_allowed('.txt'))
        self.assertFalse(serve._is_filename_allowed('/\\:*?<>|.txt'))
        self.assertFalse(serve._is_filename_allowed('q. '))
        self.assertFalse(serve._is_filename_allowed(' . '))
        self.assertFalse(serve._is_filename_allowed(' .pdf'))
        self.assertFalse(serve._is_filename_allowed('a. jpg'))
        self.assertFalse(serve._is_filename_allowed('qwe.docx'))
        with self.assertRaises(TypeError):
            serve._is_filename_allowed(1)
        with self.assertRaises(TypeError):
            serve._is_filename_allowed(False)

if __name__ == '__main__':
    unittest.main()
