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
:class:`PropertiesConfig` and :class:`PropertyKey` used. :class:`PropertyKey` defines single type of properties and :class:`PropertiesConfig`
defines all properties are contained in graph. Additionally :class:`PropertiesConfig` serves as factory object to create edges, nodes
 and :class:`GraphState` objects.

.. autoclass:: graph_state.PropertyConfig
   :members:
.. autoclass:: graph_state.PropertyKey
   :members:
.. autoclass:: graph_state.PropertyExternalizer
   :members:

Edges and nodes
===============

Graph edges and nodes represented using following classes: :class:`Edge` and :class:`Node`.
Note that you must not to use constructor to create instances of this classes. All instances must be produced
using factory methods of :class:`PropertiesConfig` instance. Edges and nodes are immutable object and to 'change' its
:func:`copy` method can be used.

.. autoclass:: graph_state.Edge
   :members:
.. autoclass:: graph_state.Node
   :members:

:mod:`operations_lib` module
============================

:mode:`operations_lib` provides operations on low-level data structures (list of edges or :class:`GraphState`).
Usually all operations are produced only using :class:`Graph` objects but if there is no way to escape low-level data structures or
decreasing of :class:`Graph` performance are occurred then this functions can be used.

.. automodule:: graph_state.operations_lib
   :members:

Graphine overview
=================

:class:`Graph` class is main representation for graph. All access to graph structure and producing operations on graph may be
done using this class (use :class:`GraphState` only for graph serialization/deserializaion tasks).
Several frequently used methods of this class (for ex.: :meth:`Graph.edges`, :attr:`Graph.loops_count`) are cacheable
in hard reference map hidden in :class:`Graph` backend.

.. autoclass:: graphine.Graph
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

