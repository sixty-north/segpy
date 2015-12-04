``segpy.reader``
================

.. automodule:: segpy.reader

  .. autosummary::
     :nosignatures:

     .. currentmodule segy.reader

     create_reader
     SegYReader
     SegYReader3D
     SegYReader2D

  .. autofunction:: create_reader(fh, encoding=None, trace_header_format=TraceHeaderRev1, endian='>', progress=None, cache_directory=".segpy")

     .. rubric:: Examples

     Create a reader from a SEG Y file::

       with open('atlantic.segy', 'rb') as segy:
           reader = create_reader(segy)
           print("Number of traces: ", reader.num_traces())

``segpy.reader.SegYReader``
---------------------------

   .. autoclass:: SegYReader

      .. automethod:: __init__(self, fh, textual_reel_header, binary_reel_header, extended_textual_headers, trace_offset_catalog, trace_length_catalog, trace_header_format, encoding, endian='>')

      .. automethod:: trace_indexes()

      .. automethod:: num_traces()

      .. automethod:: max_num_trace_samples()

      .. automethod:: num_trace_samples(trace_index)

      .. automethod:: trace_samples(trace_index, start=None, stop=None)

         .. rubric:: Examples

         Read the first trace samples::

             first_trace_samples = segy_reader.trace_samples(0)

      .. automethod:: trace_header(trace_index, header_packer_override=None)

         .. rubric:: Examples

         Read the first trace header::

             first_trace_header = segy_reader.trace_header(0)

      .. autoattribute:: trace_header_format_class

      .. autoattribute:: dimensionality

      .. autoattribute:: textual_reel_header

      .. autoattribute:: binary_reel_header

      .. autoattribute:: extended_textual_header

      .. autoattribute:: filename

      .. autoattribute:: revision

      .. autoattribute:: bytes_per_sample

      .. autoattribute:: data_sample_format

      .. autoattribute:: data_sample_format_description

      .. autoattribute:: encoding

      .. autoattribute:: endian


``segpy.reader.SegYReader3D``
-----------------------------

   .. autoclass:: SegYReader3D(SegYReader)

      .. automethod:: __init__(fh, textual_reel_header, binary_reel_header, extended_textual_headers, trace_offset_catalog, trace_length_catalog, line_catalog, trace_header_format, encoding, endian='>')

      .. automethod:: inline_numbers()

      .. automethod:: num_inlines()

      .. automethod:: xline_numbers()

      .. automethod:: num_xlines()

      .. automethod:: inline_xline_numbers()

      .. automethod:: has_trace_index(inline_xline)

      .. automethod:: trace_index(inline_xline)


``segpy.reader.SegYReader2D``
-----------------------------

   .. autoclass:: SegYReader2D(SegYReader)

      .. automethod:: __init__(fh, textual_reel_header, binary_reel_header, extended_textual_headers, trace_offset_catalog, trace_length_catalog, cdp_catalog, trace_header_format, encoding, endian='>')

      .. automethod:: cdp_numbers()

      .. automethod:: num_cdps()

      .. automethod:: has_trace_index(cdp_number)

      .. automethod:: trace_index(cdp_number)
