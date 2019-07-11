.. eecalpy documentation master file, created by
   sphinx-quickstart on Sat Jul  6 22:02:31 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to eecalpy's documentation!
===================================

The *Electrical Engineering Calculations for Python* (→ *eecalpy* 😉)
module is a tool for simple to complex electrical calculations, with a
special focus on handling tolerances.

.. code:: python

   from eecalpy import *
   print(R(1e3))

why not working?

.. code::

   a = 12k
   R_12 = 30k

   a + R_12 ?

.. important::

   this is not what it looks like

try to run

Installation
============

Subdir
------

Introduction
============

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
