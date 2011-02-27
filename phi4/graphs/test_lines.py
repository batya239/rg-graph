#!/usr/bin/python
# -*- coding:utf8

from lines import Line


class TestLine:
#    def setUp(self):
    def test_emptyinit(self):
        try:
           line=Line()
        except ValueError:
           assert True
        else:
           assert False
    def test_emptyinit2(self):
        try:
           line=Line(type=0)
        except ValueError:
           assert True
        else:
           assert False

    def test_init(self):
        line=Line(type=1,momenta=None,start=2,end=3,modifiers=[])
        assert line.type == 1
        assert line.momenta == None
        assert line.start == 2
        assert line.end == 3
        assert line.modifiers == list()

    def test_init2(self):
        line=Line(type=3,momenta=None,start=4,end=6,modifiers=[],additional_field="test")
        assert line.type == 3
        assert line.momenta == None
        assert line.start == 4
        assert line.end == 6
        assert line.modifiers == list()
        assert line.additional_field == "test"

