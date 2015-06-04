#!/usr/bin/env python3

from segpy.reader import create_reader
from segpy.trace_header import TraceHeaderRev1
from segpy.types import Int16
from segpy.writer import write_segy
from segpy.header import are_equal, field


class CustomTraceHeader(TraceHeaderRev1):

        unassigned_1 = field(
            Int16, offset=233, default=0, documentation="Unassigned 1")

        unassigned_2 = field(
            Int16, offset=235, default=0, documentation="Unassigned 2")

        unassigned_3 = field(
            Int16, offset=237, default=0, documentation="Unassigned 3")

        unassigned_4 = field(
            Int16, offset=239, default=0, documentation="Unassigned 4")


in_filename = "data/rth.segy"
out_filename = "data/rth_out2.segy"

in_file = open(in_filename, 'rb')

with open(out_filename, 'wb') as out_file:
    segy_reader_in = create_reader(in_file, trace_header_format=CustomTraceHeader)
    write_segy(out_file, segy_reader_in, trace_header_format=CustomTraceHeader)

out_file = open(out_filename, 'rb')
segy_reader_out = create_reader(in_file, trace_header_format=CustomTraceHeader)

for trace_index in segy_reader_in.trace_indexes():
    trace_offset = segy_reader_in._trace_offset_catalog[trace_index]
    print(trace_index, hex(trace_offset))
    head0 = segy_reader_in.trace_header(trace_index)
    head1 = segy_reader_out.trace_header(trace_index)
    assert are_equal(head0, head1), "Error {}".format(trace_index)

    data0 = segy_reader_in.trace_samples(trace_index)
    data1 = segy_reader_out.trace_samples(trace_index)
    assert data0==data1
