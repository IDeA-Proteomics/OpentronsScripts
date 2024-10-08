from opentrons import protocol_api

metadata = {"apiLevel": "2.20"}

def add_parameters(parameters):
    parameters.add_int(
        variable_name="buffer_volume",
        display_name="Buffer Volume",
        description="Amount of buffer to resuspend",
        minimum=30,
        maximum=200,
        default=100
    )
    parameters.add_bool(
        variable_name="second_proj",
        display_name="Two sets",
        description="Second set on bottom of plate",
        default=True
    )

def run(protocol: protocol_api.ProtocolContext):

    vol = protocol.params.buffer_volume

    source_plate = protocol.load_labware(
        load_name="nest_96_wellplate_100ul_pcr_full_skirt",
        location=5,
        label="Fractionation Plate"
        )
    
    reservoir = protocol.load_labware(
        load_name= "usascientific_12_reservoir_22ml",
        location=4,
        label="Reservior with Buffer A in A"
    )
                                        
        
    tiprack_20 = protocol.load_labware(
        load_name="opentrons_96_tiprack_20ul",
        location=11
        )
    tiprack_300 = protocol.load_labware(
        load_name="opentrons_96_tiprack_300ul",
        location=10
        )
    tiprack_300.set_offset(0.8, 1.0, 0)
    p20 = protocol.load_instrument(
        instrument_name="p20_single_gen2",
        mount="left",
        tip_racks=[tiprack_20]
        )
    p300 = protocol.load_instrument(
        instrument_name="p300_multi_gen2",
        mount="right",
        tip_racks=[tiprack_300]
        )
    p300.configure_nozzle_layout(
        style=protocol_api.SINGLE,
        start="A1",
        tip_racks=[tiprack_300]
    )

    wells = source_plate.wells_by_name()
    well_map = {
        'B1' : ['D7', 'A3'],
        'B2' : ['D8', 'A4'],
        'B3' : ['D9', 'A5'],
        'B4' : ['D10', 'A6'],
        'B5' : ['D11'],
        'B6' : ['D12'],
        'B7' : ['C7'],
        'B8' : ['C8'],
        'B9' : ['C9'],
        'B10' : ['C10'],
        'B11' : ['C11'],
        'B12' : ['C12'],
        'C1' : ['A7', 'D1'],
        'C2' : ['A8', 'D2'],
        'C3' : ['A9', 'D3'],
        'C4' : ['A10', 'D4'],
        'C5' : ['A11', 'D5'],
        'C6' : ['A12', 'D6'],
    }
    well_map_2 = {
        'F1' : ['H7', 'E3'],
        'F2' : ['H8', 'E4'],
        'F3' : ['H9', 'E5'],
        'F4' : ['H10', 'E6'],
        'F5' : ['H11'],
        'F6' : ['H12'],
        'F7' : ['G7'],
        'F8' : ['G8'],
        'F9' : ['G9'],
        'F10' : ['G10'],
        'F11' : ['G11'],
        'F12' : ['G12'],
        'G1' : ['E7', 'H1'],
        'G2' : ['E8', 'H2'],
        'G3' : ['E9', 'H3'],
        'G4' : ['E10', 'H4'],
        'G5' : ['E11', 'H5'],
        'G6' : ['E12', 'H6'],
    }

    if protocol.params.second_proj == True:
        well_map = well_map | well_map_2

    target_wells = list(well_map.keys())
    for swell in target_wells:
        p300.pick_up_tip()
        p300.transfer(vol, reservoir['A1'], wells[swell], mix_after=(5, vol), new_tip='never')
        for owell in well_map[swell]:
            p300.transfer(vol, wells[swell], wells[owell], mix_after=(5, vol), new_tip='never')
            p300.transfer(vol, wells[owell], wells[swell], new_tip='never')
        p300.drop_tip()