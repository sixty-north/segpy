from segpy.revisions import SegYRevision

# Do not use _TEMPLATE directly. Prefer to use TEMPLATE defined below which is
# stripped of line endings.
_TEMPLATE = """
C 1 CLIENT { client             } COMPANY { company           } CREW NO {crew  }
C 2 LINE { line   } AREA { area               } MAP ID { map_id                }
C 3 REEL NO {reelnum} DAY-START OF REEL {d} YEAR {yr} OBSERVER {observer       }
C 4 INSTRUMENT: MFG { mfg    } MODEL { model  } SERIAL NO { serial             }
C 5 DATA TRACES/RECORD {dtpr} AUXILIARY TRACES/RECORD {atpr } CDP FOLD {cdpfold}
C 6 SAMPLE INTERVAL {intvl} SAMPLES/TRACE {spt} BITS/IN {bi} BYTES/SAMPLE {bps }
C 7 RECORDING FORMAT {rfmt} FORMAT THIS REEL {ftr } MEASUREMENT SYSTEM {measmnt}
C 8 SAMPLE CODE: FLOATING PT {f} FIXED PT {x} FIXED PT-GAIN {g} CORRELATED {cor}
C 9 GAIN  TYPE: FIXED {i} BINARY {b} FLOATING POINT {c} OTHER {other           }
C10 FILTERS: ALIAS {a }HZ  NOTCH {n }HZ  BAND {b1}-{b2 }HZ  SLOPE {s}-{s2}DB/OCT
C11 SOURCE: TYPE {type    } NUMBER/POINT {npt } POINT INTERVAL {point_interval }
C12     PATTERN: {source_pattern         } LENGTH {lent} WIDTH {width          }
C13 SWEEP: START {ss}HZ  END {se}HZ  LENGTH {lms}MS  CHANNEL NO {q} TYPE {cd   }
C14 TAPER: START LENGTH {tsl }MS  END LENGTH {tel }MS  TYPE {taper_type        }
C15 SPREAD: OFFSET {off } MAX DISTANCE {md  } GROUP INTERVAL {group_interval   }
C16 GEOPHONES: PER GROUP {p} SPACING {y} FREQUENCY {r} MFG {gmfg  } MODEL {gmod}
C17     PATTERN: {geophone_pattern      } LENGTH {glen} WIDTH {geophone_width  }
C18 TRACES SORTED BY: RECORD {u} CDP {v} OTHER { sort_other                    }
C19 AMPLITUDE RECOVERY: NONE {ar} SPHERICAL DIV {sd } AGC {} OTHER {ar_other   }
C20 MAP PROJECTION {map_projection  } ZONE ID {zid} COORDINATE UNITS {co_units }
C21 PROCESSING: { processing1                                                  }
C22 PROCESSING: { processing2                                                  }
C23 { unassigned1                                                              }
C24 { unassigned2                                                              }
C25 { unassigned3                                                              }
C26 { unassigned4                                                              }
C27 { unassigned5                                                              }
C28 { unassigned6                                                              }
C29 { unassigned7                                                              }
C30 { unassigned8                                                              }
C31 { unassigned9                                                              }
C32 { unassigned10                                                             }
C33 { unassigned11                                                             }
C34 { unassigned12                                                             }
C35 { unassigned13                                                             }
C36 { unassigned14                                                             }
C37 { unassigned15                                                             }
C38 { unassigned16                                                             }
C39 { unassigned17                                                             }
C40 { end_marker                                                               }
"""

TEMPLATE = ''.join(_TEMPLATE.splitlines(keepends=False)[1:])

END_TEXTUAL_HEADER = 'END TEXTUAL HEADER'
END_EBCDIC = 'END EBCDIC'

END_MARKERS = {SegYRevision.REVISION_0: END_EBCDIC,
               SegYRevision.REVISION_1: END_TEXTUAL_HEADER}

TEMPLATE_FIELD_NAMES = {'client': 'client',
                        'company': 'company',
                        'crew': 'crew_number',
                        'line': 'line',
                        'area': 'area',
                        'map_id': 'map_id',
                        'reelnum': 'reel_number',
                        'd': 'day_start_of_reel',
                        'yr': 'year',
                        'observer': 'observer',
                        'mfg': 'instrument_manufacturer',
                        'model': 'instrument_model',
                        'serial': 'instrument_serial',
                        'dtpr': 'data_traces_per_record',
                        'atpr': 'auxiliary_traces_per_record',
                        'cdpfold': 'cdp_fold',
                        'intvl': 'sample_interval',
                        'spt': 'samples_per_trace',
                        'bi': 'bits_per_inch',
                        'bps': 'bytes_per_sample',
                        'rfmt': 'recording_format',
                        'ftr': 'format_this_reel',
                        'measmnt': 'measurement_system',
                        'f': 'sample_code_floating_point',
                        'x': 'sample_code_fixed_point',
                        'g': 'sample_code_fixed_point_gain',
                        'cor': 'sample_code_correlated',
                        'i': 'gain_type_fixed',
                        'b': 'gain_type_binary',
                        'c': 'gain_type_fixed_point_gain',
                        'other': 'gain_type_other',
                        'a': 'filters_alias_hz',
                        'n': 'filters_notch_hz',
                        'b1': 'filters_band_lower_hz',
                        'b2': 'filters_band_upper_hz',
                        's': 'filters_slope_lower_db_per_oct',
                        's2': 'filters_slope_upper_db_per_oct',
                        'type': 'source_type',
                        'npt': 'source_number_per_point',
                        'point_interval': 'source_point_interval',
                        'source_pattern': 'source_pattern',
                        'lent': 'source_length',
                        'width': 'source_width',
                        'ss': 'sweep_start_hz',
                        'se': 'sweep_end_hz',
                        'lms': 'sweep_length_ms',
                        'q': 'sweep_channel_number',
                        'cd': 'sweep_type',
                        'tsl': 'taper_start_length_ms',
                        'tel': 'taper_end_length_ms',
                        'taper_type': 'taper_type',
                        'off': 'spread_offset',
                        'md': 'spread_max_distance',
                        'group_interval': 'spread_group_interval',
                        'p': 'geophones_per_group',
                        'y': 'geophone_spacing',
                        'r': 'geophone_frequency',
                        'gmfg': 'geophone_manufacturer',
                        'gmod': 'geophone_model',
                        'geophone_pattern': 'geophone_pattern',
                        'glen': 'geophone_length',
                        'geophone_width': 'geophone_width',
                        'u': 'traces_sorted_by_record',
                        'v': 'traces_sorted_by_cdp',
                        'sort_other': 'traces_sorted_by_other',
                        'ar': 'amplitude_recovery_none',
                        'sd': 'amplitude_recovery_spherical_div',
                        '': 'amplitude_recovery_agc',
                        'ar_other': 'amplitude_recovery_other',
                        'map_projection': 'map_projection',
                        'zid': 'zone_id',
                        'co_units': 'coordinate_units',
                        'processing1': 'processing1',
                        'processing2': 'processing2',
                        'unassigned1': 'unassigned1',
                        'unassigned2': 'unassigned2',
                        'unassigned3': 'unassigned3',
                        'unassigned4': 'unassigned4',
                        'unassigned5': 'unassigned5',
                        'unassigned6': 'unassigned6',
                        'unassigned7': 'unassigned7',
                        'unassigned8': 'unassigned8',
                        'unassigned9': 'unassigned9',
                        'unassigned10': 'unassigned10',
                        'unassigned11': 'unassigned11',
                        'unassigned12': 'unassigned12',
                        'unassigned13': 'unassigned13',
                        'unassigned14': 'unassigned14',
                        'unassigned15': 'unassigned15',
                        'unassigned16': 'unassigned16',
                        'unassigned17': 'unassigned17',
                        'end_marker':   'end_marker'
                        }

INV_TEMPLATE_FIELD_NAMES = dict((v, k) for k, v in TEMPLATE_FIELD_NAMES.items())
