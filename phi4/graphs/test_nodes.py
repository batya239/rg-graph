#!/usr/bin/python
# -*- coding:utf8

from nodes import Node


class TestNode:

#     def test_emptyinit(self):
#         try:
#            node=Node()
#         except ValueError:
#            assert True
#         else:
#            assert False

#     def test_emptyinit2(self):
#         try:
#            node=Node(type=0)
#         except ValueError:
#            assert True
#         else:
#            assert False

    def test_init(self):
        node=Node(type=1,lines_dict={},modifiers=[])
        assert node.type == 1
        assert node.lines_dict == dict()
        assert node.modifiers == list()

    def test_init2(self):
        node=Node(type=2,lines_dict={},modifiers=['mod1'],additional_field="test")
        assert node.type == 2
        assert node.lines_dict == dict()
        assert node.modifiers == ['mod1']
        assert node.additional_field == "test"
#     def test_Lines(self):
#         node=Node(type=1,lines_dict={2:None,4:None,1:None},modifiers=[])
#         nlines=list(node.Lines())
#         nlines.sort()
#         assert nlines == [1,2,4]
