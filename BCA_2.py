

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
        maximum=23
    )

def run(protocol: protocol_api.ProtocolContext):
    count = protocol.params.sample_count
    plate = protocol.load_labware(
        load_name="corning_96_wellplate_360ul_flat",
        location=6
        )
    tubes = protocol.load_labware(
        load_name = "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
        location = 4
    )
    reservoir = protocol.load_labware(
        load_name= "usascientific_12_reservoir_22ml",
        location=1
    )
    tiprack_20 = protocol.load_labware(
            load_name="opentrons_96_tiprack_20ul",
            location=11)
    tiprack_300 = protocol.load_labware(
            load_name="opentrons_96_tiprack_300ul",
            location=10)
    p20 = protocol.load_instrument(
        instrument_name="p20_single_gen2",
        mount="left",
        tip_racks=[tiprack_20])
    p300 = protocol.load_instrument(
        instrument_name="p300_multi_gen2",
        mount="right",
        tip_racks=[tiprack_300])
    

    samples = tubes.wells()[1:count+1] ## first well holds standard

    standard_wells = [well for well in (plate.columns()[0] + plate.columns()[1])]
    blank_wells = plate.columns()[2][:2]
    sample_wells = [well for well in plate.wells() if well not in standard_wells and well not in blank_wells]

    std_stock_amts = [40, 30, 20, 15, 10, 4, 2, 0]
    
    ###  Put water in wells to make up standard

    p300.configure_nozzle_layout(
        style=protocol_api.SINGLE,
        start="A1",
        tip_racks=[tiprack_300]
    )
    p300.pick_up_tip()

    for i in range(8):
        p300.transfer(100 - std_stock_amts[i], reservoir['A1'], standard_wells[i], new_tip='never')
        p300.transfer(100 - std_stock_amts[i], reservoir['A1'], standard_wells[i+8], new_tip='never')
    
    p300.drop_tip()
    

    ### Add standards to standard wells
    p20.pick_up_tip()
    for i in range(8):
        if std_stock_amts[i] > 0:
            p20.transfer(std_stock_amts[i], tubes['A1'], standard_wells[i], new_tip='never')
            p20.transfer(std_stock_amts[i], tubes['A1'], standard_wells[i + 8], new_tip='never')
    p20.drop_tip()


    ### put 95ul water in sample wells.
    p300.configure_nozzle_layout(
        style=protocol_api.ALL,
        tip_racks=[tiprack_300]
    )

    p300.pick_up_tip()

    num_cols = math.ceil((count + 2)/8)

    for i in range(num_cols):
        p300.transfer(95, reservoir['A1'], plate.columns()[i + 2], new_tip='never')

    p300.drop_tip()

    ### 5ul of water in blank wells
    for i in range(2):
        p20.transfer(5, reservoir['A1'], blank_wells[i], new_tip='once')


    ### add sample to sample wells

    for i in range(count):
        p20.transfer(5, samples[i], sample_wells[i], new_tip='always')


    ### add BCA reagent to all wells. 

    for i in range(num_cols + 2):
        p300.transfer(100, reservoir['A2'], plate.columns()[i], new_tip='always', mix_after=(5, 200))




    


