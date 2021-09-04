from economy import Economy

economy = Economy(
    id="MILD_MILD_WEST",
    numeric_id=6,
    # as of May 2015 the following cargos must have fixed positions if used by an economy:
    # passengers: 0, mail: 2, goods 5, food 11
    # keep the rest of the cargos alphabetised
    # bump the min. compatible version if this list changes
    cargos=[
        "passengers",
        "alcohol",
        "mail",
        "acid",
        "carbon_black",
        "carbon_steel",
        "cement",
        "coal",
        "coal_tar",
        "coke",
        "engineering_supplies",
        "food",
        "farm_supplies",
        "fertiliser",
        "fish",
        "fruits",
        "iron_ore",
        "kaolin",
        "limestone",
        "livestock",
        "logs",
        "lumber",
        "manganese",
        "milk",
        "oil",
        "petrol",
        "pig_iron",
        "pyrite_ore",  # replace with zinc concentrate
        "quicklime",
        "sand",
        "scrap_metal",
        "slag",
        "steel_sections",
        "steel_sheet",
        "steel_wire_rod",
        "tin",
        "tinplate",
        "vegetables",
        "vehicles",
        "zinc",
    ],
    cargoflow_graph_tuning={
        "group_edges_subgraphs": [],
        "ranking_subgraphs": [
            # ("same", ["port", "goods"]),
            # ("sink", ["T_town_industries", "N_force_rank"]),
        ],
        "clusters": [
            # {"nodes": [], "rank": "", "color": ""},
        ],
    },
)
