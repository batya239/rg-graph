.. GraphState documentation master file, created by
   sphinx-quickstart on Tue Oct 21 17:05:08 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to GraphState and Graphine documentation!
=================================================

**GraphState** and **Graphine** are graph manipulation libraries. The key feature of these libraries is usage of generalization
of graph representation offered by B. G. Nickel et al. In this approach graph is represented in some unique 'canonical' form
that depends only on its combinatorial type. The uniqueness of graph representation gives an efficient way for isomorphism finding,
searching for subgraphs and other graph manipulation tasks. Though offered libraries were originally designed for Feynman graphs,
they might be useful for more general graph problems.

Properties and its configuration
================================

To define edge and node properties behaviour (name, (de)serialization process, directed or undirected (for edge properties only))
:class:`PropertiesConfig` and :class:`PropertyKey` is used. :class:`PropertyKey` defines single type of properties and :class:`PropertiesConfig`
defines all properties that are contained in graph. Additionally :class:`PropertiesConfig` serves as factory object to create edges, nodes
and :class:`GraphState` objects.

.. autoclass:: graph_state.PropertiesConfig
   :members:
.. autoclass:: graph_state.PropertyKey
   :members:
.. autoclass:: graph_state.PropertyExternalizer
   :members:

Edges and nodes
===============

Graph edges and nodes represented using following classes: :class:`Edge` and :class:`Node`.
Note that you must not use constructor to create instances of this classes. All instances must be produced
using factory methods of :class:`PropertiesConfig` instance. Edges and nodes are immutable objects and to 'change' them
:func:`copy` method can be used.

.. autoclass:: graph_state.Edge
   :members:
.. autoclass:: graph_state.Node
   :members:


:class:`graph_state.GraphState`
===================

:class:`graph_state.GraphState` represents graph state (or structure). It can be used to determine isomorphisms of graph, to low-level access
to edges, graph (de)serialization. In other cases it's useful to use :class:`Graph` objects because it provides additional possibilities.

.. autoclass:: graph_state.GraphState
   :members:

:mod:`operations_lib` module
============================

:mod:`operations_lib` provides operations on low-level data structures (list of edges or :class:`graph_state.GraphState`).
Usually all operations are produced only using :class:`graphine.Graph` objects, but if there is no way to escape low-level data structures or
in case of decreasing of :class:`Graph` performance, these functions can be used.

.. automodule:: graph_state.operations_lib
   :members:

Graphine overview
=================

:class:`graphine.Graph` class is main representation for graph. Full access to graph structure and operations on graph can be
done using this class (use :class:`graph_state.GraphState` only for graph serialization/deserializaion tasks).
Several frequently used methods of this class (for ex.: :meth:`Graph.edges`, :attr:`Graph.loops_count`) are cacheable
in hard reference map hidden in :class:`Graph` backend.

.. autoclass:: graphine.Graph
   :members:

:mod:`graphine.filters` module
===============================

.. automodule:: graphine.filters
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

