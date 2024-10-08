from opentrons import protocol_api
import math

metadata = {"apiLevel": "2.20"}

row_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

def add_parameters(parameters):
    parameters.add_int(
        variable_name="sample_count",
        display_name="Sample Count",
        description="",
        default=1,
        minimum=1,
        maximum=95
    )


def run(protocol: protocol_api.ProtocolContext):

    plate = protocol.load_labware(
        load_name="nest_96_wellplate_100ul_pcr_full_skirt",
        location=7
        )
    
    tiprack_20 = protocol.load_labware(
        load_name="opentrons_96_tiprack_20ul",
        location=11
        )
    # tiprack_300.set_offset(0.8, 1.0, 0)
    p20 = protocol.load_instrument(
        instrument_name="p20_single_gen2",
        mount="left",
        tip_racks=[tiprack_20]
        )
    
    ###  Get list of wells in row by row format   
    source_wells_by_row = []
    for row in plate.rows():
        source_wells_by_row += row

    volume = 100 / protocol.params.sample_count

    for i in range(protocol.params.sample_count):
        p20.transfer(volume, source_wells_by_row[i], plate['H12'], blow_out=True, blowout_location="destination well")

