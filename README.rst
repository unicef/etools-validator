Validation
==========

Validation is a library that provides an improved.

Installation
------------

.. code-block:: bash
   pip install unicef-validation

Add `validation` to `INSTALLED_APPS` in `settings.py`

.. code-block:: python
   INSTALLED_APPS = [
       ...
       'validation',
   ]

Use `validation` in views

.. code-block:: python
   from validation.mixins import ValidatorViewMixin

   class ExampleView(ValidatorViewMixin, ListCreateAPIView):
       ...
