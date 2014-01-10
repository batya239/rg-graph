#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import graph_state


gs_builder = graph_state.PropertiesConfig.create(PropertyKey(name="fields",
                                    is_directed=True,
                                    externalizer=Fields.externalizer()))

print gs_builder.graph_state_from_str("e11|ee|")