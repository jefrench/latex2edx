'''
Test cross-reference and Table of Contents generating modules from
`latex2edx/main.py`
'''
import os
import re
import unittest
from lxml import etree
from path import path  # needs path.py

import latex2edx as l2e
from latex2edx.main import latex2edx
from latex2edx.test.util import make_temp_directory


class TestToC(unittest.TestCase):
    '''
    This class inherits the `unittest.TestCase` class and contains the methods
    `test_toc1` and `test_toc2` that test the proper functionality of the
    latex2edx `label`, `ref`, `toclabel`, and `tocref` commands.
    `test_toc3` tests the output tocindex.html file for the case when
    verticals are referenced.
    '''

    def test_toc1(self):
        '''
        Test the output of `latex2edx example11_toc_test.tex` for proper label
        and reference tags, as well as figure numbering.
        '''
        testdir = path(l2e.__file__).parent / 'testtex'
        tfn = testdir / 'example11_toc_test.tex'
        print "file %s" % tfn
        with make_temp_directory() as tmdir:
            nfn = '%s/%s' % (tmdir, tfn.basename())
            os.system('cp %s/* %s' % (testdir, tmdir))
            os.chdir(tmdir)
            l2eout = latex2edx(nfn, output_dir=tmdir)
            l2eout.convert()

            xhfn = nfn[:-4] + '.xhtml'
            xml = etree.fromstring(open(xhfn).read())
            toclabels = xml.findall('.//toclabel')
            self.assertEqual(toclabels[0].text, 'chap:intro')
            self.assertEqual(toclabels[1].text, 'mo:explore')
            tocref = xml.find('.//tocref')
            self.assertEqual(tocref.text, 'mo:explore')
            labels = xml.findall('.//label')
            self.assertEqual(labels[0].text, 'fig:single')
            self.assertEqual(labels[1].text, 'fig:multi')
            captions = xml.findall('.//div[@class="caption"]/b')
            self.assertEqual(captions[0].text, 'Figure 1')
            self.assertEqual(captions[1].text, 'Figure 2')
            chaps = xml.findall('.//chapter')
            self.assertIsNone(chaps[0].get('refnum'))
            self.assertEqual(chaps[1].get('refnum'), '1')
            equation = xml.find('.//td[@class="equation"]')
            self.assertEqual(re.findall(r'\\label\{(.*?)\}', equation.text,
                                        re.S)[0], 'eq:pythagorean')
            tocfn = '%s/tabs/tocindex.html' % tmdir
            toc = etree.fromstring(open(tocfn).read().replace('<br>', '<br/>'))
            toctitle = toc.find('.//h1')
            self.assertEqual(toctitle.text, 'Table of Contents')
            # Check the measurable outcome table headers
            # table>tbody>tr>th>a>strong
            toctabs = toc.findall('.//table')
            self.assertEqual(toctabs[0][0][0][0][0][0].text, '0')
            self.assertEqual(toctabs[1][0][0][0][0][0].text, 'MO1')
            self.assertEqual(toctabs[2][0][0][0][0][0].text, 'MO2')
            # table>tbody>tr>th>span
            self.assertIn('Explore the edX platform',
                          toctabs[1][0][0][0][1].text)
            self.assertIn('Answer an edX question',
                          toctabs[2][0][0][0][1].text)
            # check example 'Learn' link
            self.assertEqual(toctabs[1][0][1][0][0].text, 'Learn')
            self.assertIn('Example text', toctabs[1][0][1][0][1][0][0].text)
            # check example 'Assess' link
            self.assertEqual(toctabs[0][0][1][0][2].text, 'Assess')
            self.assertIn('Example problem', toctabs[0][0][1][0][3][0][0].text)
            self.assertIn('Example problem', toctabs[1][0][1][0][3][0][0].text)
            self.assertIn('Example problem', toctabs[2][0][1][0][3][0][0].text)
            # tocbod = toc.find('.//body')
            self.assertEqual(toc[1][8].tag, 'br')
            self.assertIn('Module 1', toc[1][9][0].text)

    def test_toc2(self):
        '''
        Test the output of `latex2edx --popups example11_toc_test.tex` for
        proper equation numbering and button links to the static tocindex.html
        file.
        '''
        testdir = path(l2e.__file__).parent / 'testtex'
        tfn = testdir / 'example11_toc_test.tex'
        print "file %s" % tfn
        with make_temp_directory() as tmdir:
            nfn = '%s/%s' % (tmdir, tfn.basename())
            os.system('cp %s/* %s' % (testdir, tmdir))
            os.chdir(tmdir)
            l2eout = latex2edx(nfn, output_dir=tmdir, popup_flag=True)
            l2eout.convert()

            cfn = path(tmdir) / 'html/text-L1.xml'
            data = open(cfn).read()
            xml = etree.fromstring(data)
            # Check the first equation
            eqn = xml.find('.//table[@class="equation"]')
            self.assertEqual(eqn[0][0].text,
                             '[mathjax] \\frac{d}{dx} e^ x = e^ x[/mathjax]')
            # Check the reference link text
            href = xml.findall('.//a[@href]')
            self.assertEqual(href[0].text, '0')  # Non-numbered chapter
            self.assertEqual(href[1].text, '1.2')  # Numbered equation 2
            self.assertEqual(href[2].text, '1.3')  # Numbered equation 3
            # Check for popup format
            self.assertEqual(href[1].get('href'), 'javascript: void(0)')
            self.assertEqual(href[2].get('href'), 'javascript: void(0)')
            # Check for taglist in problem
            cfn = path(tmdir) / 'problem/p0.xml'
            data = open(cfn).read()
            xml = etree.fromstring(data)
            taglist = xml.find('.//p[@id="taglist"]')
            self.assertEqual(taglist.get('tags'),
                             'mo:explore,mo:problem,chap:intro')

    def test_toc3(self):
        '''
        Test the output of `latex2edx example17_toc_vert.tex` for proper
        generation of a tocindex.html file based on the contents of a vertical.
        '''
        testdir = path(l2e.__file__).parent / 'testtex'
        tfn = testdir / 'example17_toc_vert.tex'
        print "file %s" % tfn
        with make_temp_directory() as tmdir:
            nfn = '%s/%s' % (tmdir, tfn.basename())
            os.system('cp %s/* %s' % (testdir, tmdir))
            os.chdir(tmdir)
            l2eout = latex2edx(nfn, output_dir=tmdir)
            l2eout.convert()

            tocfn = '%s/tabs/tocindex.html' % tmdir
            toc = etree.fromstring(open(tocfn).read().replace('<br>', '<br/>'))
            toctitle = toc.find('.//h1')
            self.assertEqual(toctitle.text, 'Table of Contents')
            toctabs = toc.findall('.//table')
            self.assertEqual(toctabs[0][0][0][0][0][0].text, 'MO1.1')
            self.assertEqual(toctabs[1][0][0][0][0][0].text, 'MO1.2')
            self.assertIn('Follow a Lesson',
                          toctabs[0][0][0][0][1].text)
            self.assertEqual(toctabs[0][0][1][0][0].text, 'Learn')
            self.assertIn('Example text', toctabs[0][0][1][0][1][0][0].text)
            self.assertIn('Answer a problem set',
                          toctabs[1][0][0][0][1].text)
            self.assertEqual(toctabs[1][0][1][0][2].text, 'Assess')
            self.assertIn('Problem Set 1', toctabs[1][0][1][0][3][0][0].text)

if __name__ == '__main__':
    unittest.main()
