from opentrons import protocol_api, types

metadata = {"apiLevel": "2.20"}

def add_parameters(parameters):
    parameters.add_csv_file(
        variable_name="project_list",
        display_name="Project List",
        description="List of Projects, start position, number of samples, and amount",
    )

def run(protocol: protocol_api.ProtocolContext):

    data = protocol.params.project_list.parse_as_csv()
    lines = [row for row in data[1:]]
    slots = [x for x in [4, 5, 6, 8, 9]]

    reservoir = protocol.load_labware(
        load_name="idea_12_reservoir_22000ul",
        location = 1
    )

    source_plate = protocol.load_labware(
        load_name="nest_96_wellplate_2ml_deep",
        location=7
        )
    
    plates = []
    for i in range(len(lines)):
        plates.append(
            protocol.load_labware(
                load_name="nest_96_wellplate_100ul_pcr_full_skirt",
                location=slots[i],
                label=lines[i][0]
            )
        )
    tiprack_20 = protocol.load_labware(
        load_name="opentrons_96_tiprack_20ul",
        location=11
        )
    tiprack_300 = protocol.load_labware(
        load_name="opentrons_96_tiprack_300ul",
        location=10
        )
    # tiprack_300.set_offset(0.8, 1.0, 0)
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


    ###  Get list of wells in row by row format   
    source_wells_by_row = []
    dest_wells_by_row = [] 
    for row in source_plate.rows():
        source_wells_by_row += row
    for row in plates[i].rows():
        dest_wells_by_row += row

    
    for i in range(len(lines)):

        first_well_name = lines[i][1]
        num_samples = int(lines[i][2])
        amount = float(lines[i][3])

        ###  Load BufferA into wells as specified in CSV

        first_well_index = source_wells_by_row.index(source_plate.wells_by_name()[first_well_name])

        source_wells = source_wells_by_row[first_well_index:first_well_index + num_samples]

        for well in source_wells:

            bottom = well.bottom()
            offset = 2.5
            offset_depth = 6

            p300.pick_up_tip()
            p300.aspirate(amount, reservoir['A1'])
            p300.dispense(amount, bottom)

            p300.aspirate(amount, bottom)
            p300.dispense(amount, bottom.move(types.Point(offset, offset, offset_depth)))

            p300.aspirate(amount, bottom)
            p300.dispense(amount, bottom.move(types.Point(offset, -offset, offset_depth)))

            p300.aspirate(amount, bottom)
            p300.dispense(amount, bottom.move(types.Point(-offset, -offset, offset_depth)))

            p300.aspirate(amount, bottom)
            p300.dispense(amount, bottom.move(types.Point(-offset, offset, offset_depth)))

            p300.mix(5, amount, bottom)
            p300.blow_out(bottom.move(types.Point(0, 0, 5)))
            p300.drop_tip()


    protocol.pause("Shake the plate!")



    
    for i in range(len(lines)):

        first_well_name = lines[i][1]
        num_samples = int(lines[i][2])
        amount = float(lines[i][3])
        pool = True if lines[i][4] == 'Y' else False

        
        

        first_well_index = source_wells_by_row.index(source_plate.wells_by_name()[first_well_name])

        source_wells = source_wells_by_row[first_well_index:first_well_index + num_samples]
        dest_wells = dest_wells_by_row[:num_samples]

        p300.pick_up_tip()
        p300.transfer(amount, source_wells, dest_wells, new_tip='never')
        p300.drop_tip()

        if pool:
            pool_amount = 100 / num_samples
            pip = p20 if pool_amount <=20 else p300
            pip.pick_up_tip()
            pip.transfer(pool_amount, dest_wells, plates[i]['H12'], new_tip='never')
            pip.drop_tip()

    
