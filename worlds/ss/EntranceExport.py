import yaml
from entrances.ExitGraph import AP_EXIT_GRAPH
from Entrances import GAME_ENTRANCE_TABLE

from logic.requirements.Skyloft import SKYLOFT_REQUIREMENTS
from logic.requirements.Sky import SKY_REQUIREMENTS
from logic.requirements.Faron import FARON_REQUIREMENTS
from logic.requirements.Eldin import ELDIN_REQUIREMENTS
from logic.requirements.Lanayru import LANAYRU_REQUIREMENTS

from logic.requirements.Skyview import SKYVIEW_REQUIREMENTS
from logic.requirements.Earth_Temple import EARTH_TEMPLE_REQUIREMENTS
from logic.requirements.Lanayru_Mining_Facility import LANAYRU_MINING_FACILITY_REQUIREMENTS
from logic.requirements.Ancient_Cistern import ANCIENT_CISTERN_REQUIREMENTS
from logic.requirements.Sandship import SANDSHIP_REQUIREMENTS
from logic.requirements.Fire_Sanctuary import FIRE_SANCTUARY_REQUIREMENTS
from logic.requirements.Sky_Keep import SKY_KEEP_REQUIREMENTS

ALL_REQUIREMENTS = (
    SKYLOFT_REQUIREMENTS
    | SKY_REQUIREMENTS
    | FARON_REQUIREMENTS
    | ELDIN_REQUIREMENTS
    | LANAYRU_REQUIREMENTS
    | SKYVIEW_REQUIREMENTS
    | EARTH_TEMPLE_REQUIREMENTS
    | LANAYRU_MINING_FACILITY_REQUIREMENTS
    | ANCIENT_CISTERN_REQUIREMENTS
    | SANDSHIP_REQUIREMENTS
    | FIRE_SANCTUARY_REQUIREMENTS
    | SKY_KEEP_REQUIREMENTS
)

class Entrances():
    def __init__(self):
        with open("./entrances/Entrances.yaml", "r") as f:
            self.entrances = yaml.safe_load(f)
        if self.entrances is None:
            self.entrances = {}
        with open("./entrances/GameEntrances.yaml", "r") as f:
            self.game_entrances = yaml.safe_load(f)
        with open("./entrances/entrance_templates/entrances_py_template", "r") as f:
            self.entrances_py = f.read() + "\n\n\n"
        self.non_updated = []

    def exporter(self):
        for reg in AP_EXIT_GRAPH.keys():
            assert reg in ALL_REQUIREMENTS, f"Region {reg} not found in logic"
        for reg in ALL_REQUIREMENTS.keys():
            assert reg in AP_EXIT_GRAPH, f"Region {reg} not found in the exit graph"

        for reg, data in ALL_REQUIREMENTS.items():
            for ex in data["exits"].keys():
                assert ex in AP_EXIT_GRAPH[reg], f"Exit {ex} not found in exit graph"
                if f"{reg} - {ex}" in self.entrances:
                    entrance_data = self.entrances[f"{reg} - {ex}"]
                    print(f"{reg} - {ex} already exists")
                    ## Check that the entrance is valid
                    if "ss_exit_name" not in entrance_data:
                        if entrance_data["group"] == 2:
                            entrance_data["ss_exit_name"] = None
                        else:
                            entrance_data["ss_exit_name"] = input(f"Existing exit   {reg} ({ex})   needs an in-game name:\n")
                    else:
                        if entrance_data["group"] == 1:
                            exit_name = entrance_data["ss_exit_name"]
                            if exit_name == "None":
                                pass
                            else:
                                assert exit_name in self.game_entrances, f"Exit {exit_name} not in game entrance data"
                                game_exit = self.game_entrances[exit_name]
                                assert game_exit["type"] == "exit", f"Exit {exit_name} not a valid game exit"
                                if "stage" in game_exit and "room" in game_exit and "index" in game_exit:
                                    entrance_data["exit_stage"] = game_exit["stage"]
                                    entrance_data["exit_room"] = game_exit["room"]
                                    entrance_data["exit_index"] = game_exit["index"]
                                else:
                                    print(f"Exit {exit_name} does not have all required info")
                                    self.non_updated.append(f"[EXIT] {exit_name}")
                    if "ss_entrance_name" not in entrance_data:
                        if entrance_data["group"] == 2:
                            entrance_data["ss_entrance_name"] = None
                        else:
                            entrance_data["ss_entrance_name"] = input(f"Existing entrance   {entrance_data["connecting_region"]} ({entrance_data["connecting_entrance"]})   needs an in-game name:\n")
                    else:
                        if entrance_data["group"] == 1:
                            entrance_name = entrance_data["ss_entrance_name"]
                            if entrance_name == "None":
                                entrance_data["can_start_at"] = False
                            else:
                                assert entrance_name in self.game_entrances, f"Entrance {entrance_name} not in game entrance data"
                                game_entrance = self.game_entrances[entrance_name]
                                assert game_entrance["type"] == "entrance", f"Entrance {entrance_name} not a valid game Entrance"
                                if "stage" in game_entrance and "room" in game_entrance and "entrance" in game_entrance and "layer" in game_entrance and "tod" in game_entrance and "province" in game_entrance:
                                    entrance_data["entrance_province"] = game_entrance["province"]
                                    entrance_data["entrance_stage"] = game_entrance["stage"]
                                    entrance_data["entrance_room"] = game_entrance["room"]
                                    entrance_data["entrance_index"] = game_entrance["entrance"]
                                    entrance_data["entrance_layer"] = game_entrance["layer"]
                                    entrance_data["entrance_tod"] = game_entrance["tod"]
                                    if "can-start-at" in game_entrance:
                                        entrance_data["can_start_at"] = game_entrance["can-start-at"]
                                    else:
                                        entrance_data["can_start_at"] = True
                                else:
                                    print(f"Entrance {entrance_name} does not have all required info")
                                    self.non_updated.append(f"[ENTRANCE] {entrance_name}")
                                    entrance_data["can_start_at"] = False
                        else:
                            entrance_data["can_start_at"] = False
                    if entrance_data["group"] in [2, 4, 5, 6, 8, 9, 10]:
                        if entrance_data["can_shuffle"]:
                            print(f"Exit {reg} ({ex}) in un-shuffleable group {entrance_data["group"]} is set to shuffle")
                            if input("Change? (y/n)").lower() == "y":
                                entrance_data["can_shuffle"] = False
                    if entrance_data["group"] in [3, 7]:
                        if not entrance_data["can_shuffle"]:
                            print(f"Exit {reg} ({ex}) in shuffleable group {entrance_data["group"]} is set to NOT shuffle")
                            if input("Change? (y/n)").lower() == "y":
                                entrance_data["can_shuffle"] = True
                    if entrance_data["can_shuffle"] == -1:
                        print(f"Exit {reg} ({ex}) [direction={entrance_data["direction"]}] can_shuffle set to -1")
                        if input("Change? (y/n)").lower() == "y":
                            if input("Can Shuffle? (1 = True / 0 = False)") == 1:
                                entrance_data["can_shuffle"] = True
                            else:
                                entrance_data["can_shuffle"] = False
                    continue
                con_reg_data = AP_EXIT_GRAPH[reg][ex]
                if isinstance(con_reg_data, tuple):
                    con_reg = con_reg_data[0]
                else:
                    con_reg = con_reg_data
                con_ent = None
                for ent, ent_target_reg in AP_EXIT_GRAPH[con_reg].items():
                    if isinstance(ent_target_reg, str) and reg == ent_target_reg:
                        con_ent = ent
                    elif isinstance(ent_target_reg, tuple) and reg == ent_target_reg[0] and ex == ent_target_reg[1]:
                        con_ent = ent
                if con_ent is None:
                    group = int(input(f"[GROUP?] {reg}  ({ex}) ---> {con_reg} (No Entrance) (ONE WAY)"))
                    direction = 1
                else:
                    group = int(input(f"[GROUP?] {reg} ({ex}) ---> {con_reg} ({con_ent})"))
                    direction = 2
                if group == 1:
                    can_shuffle = int(input(f"Can shuffle?"))
                    if can_shuffle == 1:
                        can_shuffle = True
                    elif can_shuffle == 0:
                        can_shuffle = False
                else:
                    can_shuffle = False
                
                self.entrances[f"{reg} - {ex}"] = {
                    "exit_region": reg,
                    "exit_name": ex,
                    "connecting_region": con_reg,
                    "connecting_entrance": con_ent,
                    "direction": direction,
                    "group": group,
                    "can_shuffle": can_shuffle,
                }

                entrance_data = self.entrances[f"{reg} - {ex}"]
                if "ss_exit_name" not in entrance_data:
                    if entrance_data["group"] == 2:
                        entrance_data["ss_exit_name"] = None
                    else:
                        entrance_data["ss_exit_name"] = input(f"Existing exit   {reg} ({ex})   needs an in-game name:\n")
                else:
                    if entrance_data["group"] == 1:
                        exit_name = entrance_data["ss_exit_name"]
                        if exit_name == "None":
                            pass
                        else:
                            assert exit_name in self.game_entrances, f"Exit {exit_name} not in game entrance data"
                            game_exit = self.game_entrances[exit_name]
                            assert game_exit["type"] == "exit", f"Exit {exit_name} not a valid game exit"
                            if "stage" in game_exit and "room" in game_exit and "index" in game_exit:
                                entrance_data["exit_stage"] = game_exit["stage"]
                                entrance_data["exit_room"] = game_exit["room"]
                                entrance_data["exit_index"] = game_exit["index"]
                            else:
                                print(f"Exit {exit_name} does not have all required info")
                                self.non_updated.append(f"[EXIT] {exit_name}")
                if "ss_entrance_name" not in entrance_data:
                    if entrance_data["group"] == 2:
                        entrance_data["ss_entrance_name"] = None
                    else:
                        entrance_data["ss_entrance_name"] = input(f"Existing entrance   {entrance_data["connecting_region"]} ({entrance_data["connecting_entrance"]})   needs an in-game name:\n")
                else:
                    if entrance_data["group"] == 1:
                        entrance_name = entrance_data["ss_entrance_name"]
                        if entrance_name == "None":
                            entrance_data["can_start_at"] = False
                        else:
                            assert entrance_name in self.game_entrances, f"Entrance {entrance_name} not in game entrance data"
                            game_entrance = self.game_entrances[entrance_name]
                            assert game_entrance["type"] == "entrance", f"Entrance {entrance_name} not a valid game Entrance"
                            if "stage" in game_entrance and "room" in game_entrance and "entrance" in game_entrance and "layer" in game_entrance and "tod" in game_entrance and "province" in game_entrance:
                                entrance_data["entrance_province"] = game_entrance["province"]
                                entrance_data["entrance_stage"] = game_entrance["stage"]
                                entrance_data["entrance_room"] = game_entrance["room"]
                                entrance_data["entrance_index"] = game_entrance["entrance"]
                                entrance_data["entrance_layer"] = game_entrance["layer"]
                                entrance_data["entrance_tod"] = game_entrance["tod"]
                                if "can-start-at" in game_entrance:
                                    entrance_data["can_start_at"] = game_entrance["can-start-at"]
                                else:
                                    entrance_data["can_start_at"] = True
                            else:
                                print(f"Entrance {entrance_name} does not have all required info")
                                self.non_updated.append(f"[ENTRANCE] {entrance_name}")
                                entrance_data["can_start_at"] = False
                    else:
                        entrance_data["can_start_at"] = False
                if entrance_data["group"] in [2, 4, 5, 6, 8, 9, 10]:
                    if entrance_data["can_shuffle"]:
                        print(f"Exit {reg} ({ex}) in un-shuffleable group {entrance_data["group"]} is set to shuffle")
                        if input("Change? (y/n)").lower() == "y":
                            entrance_data["can_shuffle"] = False
                if entrance_data["group"] in [3, 7]:
                    if not entrance_data["can_shuffle"]:
                        print(f"Exit {reg} ({ex}) in shuffleable group {entrance_data["group"]} is set to NOT shuffle")
                        if input("Change? (y/n)").lower() == "y":
                            entrance_data["can_shuffle"] = True
                if entrance_data["can_shuffle"] == -1:
                    print(f"Exit {reg} ({ex}) [direction={entrance_data["direction"]}] can_shuffle set to -1")
                    if input("Change? (y/n)").lower() == "y":
                        if input("Can Shuffle? (1 = True / 0 = False)") == 1:
                            entrance_data["can_shuffle"] = True
                        else:
                            entrance_data["can_shuffle"] = False

                if direction == 2:
                    self.entrances[f"{con_reg} - {con_ent}"] = {
                        "exit_region": con_reg,
                        "exit_name": con_ent,
                        "connecting_region": reg,
                        "connecting_entrance": ex,
                        "direction": direction,
                        "group": group,
                        "can_shuffle": can_shuffle,
                    }

                    entrance_data = self.entrances[f"{con_reg} - {con_ent}"]

                    if "ss_exit_name" not in entrance_data:
                        if entrance_data["group"] == 2:
                            entrance_data["ss_exit_name"] = None
                        else:
                            entrance_data["ss_exit_name"] = input(f"Existing exit   {con_reg} ({con_ent})   needs an in-game name:\n")
                    else:
                        if entrance_data["group"] == 1:
                            exit_name = entrance_data["ss_exit_name"]
                            if exit_name == "None":
                                pass
                            else:
                                assert exit_name in self.game_entrances, f"Exit {exit_name} not in game entrance data"
                                game_exit = self.game_entrances[exit_name]
                                assert game_exit["type"] == "exit", f"Exit {exit_name} not a valid game exit"
                                if "stage" in game_exit and "room" in game_exit and "index" in game_exit:
                                    entrance_data["exit_stage"] = game_exit["stage"]
                                    entrance_data["exit_room"] = game_exit["room"]
                                    entrance_data["exit_index"] = game_exit["index"]
                                else:
                                    print(f"Exit {exit_name} does not have all required info")
                                    self.non_updated.append(f"[EXIT] {exit_name}")
                    if "ss_entrance_name" not in entrance_data:
                        if entrance_data["group"] == 2:
                            entrance_data["ss_entrance_name"] = None
                        else:
                            entrance_data["ss_entrance_name"] = input(f"Existing entrance   {entrance_data["connecting_region"]} ({entrance_data["connecting_entrance"]})   needs an in-game name:\n")
                    else:
                        if entrance_data["group"] == 1:
                            entrance_name = entrance_data["ss_entrance_name"]
                            if entrance_name == "None":
                                entrance_data["can_start_at"] = False
                            else:
                                assert entrance_name in self.game_entrances, f"Entrance {entrance_name} not in game entrance data"
                                game_entrance = self.game_entrances[entrance_name]
                                assert game_entrance["type"] == "entrance", f"Entrance {entrance_name} not a valid game Entrance"
                                if "stage" in game_entrance and "room" in game_entrance and "entrance" in game_entrance and "layer" in game_entrance and "tod" in game_entrance and "province" in game_entrance:
                                    entrance_data["entrance_province"] = game_entrance["province"]
                                    entrance_data["entrance_stage"] = game_entrance["stage"]
                                    entrance_data["entrance_room"] = game_entrance["room"]
                                    entrance_data["entrance_index"] = game_entrance["entrance"]
                                    entrance_data["entrance_layer"] = game_entrance["layer"]
                                    entrance_data["entrance_tod"] = game_entrance["tod"]
                                    if "can-start-at" in game_entrance:
                                        entrance_data["can_start_at"] = game_entrance["can-start-at"]
                                    else:
                                        entrance_data["can_start_at"] = True
                                else:
                                    print(f"Entrance {entrance_name} does not have all required info")
                                    self.non_updated.append(f"[ENTRANCE] {entrance_name}")
                                    entrance_data["can_start_at"] = False
                        else:
                            entrance_data["can_start_at"] = False
                    if entrance_data["group"] in [2, 4, 5, 6, 8, 9, 10]:
                        if entrance_data["can_shuffle"]:
                            print(f"Exit {con_reg} ({con_ent}) in un-shuffleable group {entrance_data["group"]} is set to shuffle")
                            if input("Change? (y/n)").lower() == "y":
                                entrance_data["can_shuffle"] = False
                    if entrance_data["group"] in [3, 7]:
                        if not entrance_data["can_shuffle"]:
                            print(f"Exit {con_reg} ({con_ent}) in shuffleable group {entrance_data["group"]} is set to NOT shuffle")
                            if input("Change? (y/n)").lower() == "y":
                                entrance_data["can_shuffle"] = True
                    if entrance_data["can_shuffle"] == -1:
                        print(f"Exit {con_reg} ({con_ent}) [direction={entrance_data["direction"]}] can_shuffle set to -1")
                        if input("Change? (y/n)").lower() == "y":
                            if input("Can Shuffle? (1 = True / 0 = False)") == 1:
                                entrance_data["can_shuffle"] = True
                            else:
                                entrance_data["can_shuffle"] = False

        with open("./entrances/Entrances.yaml", "w") as f:
            yaml.safe_dump(self.entrances, f, indent=2)
    
        print(self.non_updated)

    def py_exporter(self):
        with open("./entrances/entrance_templates/ap_entrance_class", "r") as f:
            self.entrances_py += f.read()
            self.entrances_py += "\n\n"
        self.entrances_py += "EXIT_GRAPH = [\n"

        for reg, regdata in ALL_REQUIREMENTS.items():
            for ex in regdata["exits"].keys():
                data = self.entrances[f"{reg} - {ex}"]
                self.entrances_py += f'    SSAPEntrance(\n'
                self.entrances_py += f'        "{data["exit_region"]}",\n'
                self.entrances_py += f'        "{data["exit_name"]}",\n'
                self.entrances_py += f'        "{data["connecting_region"]}",\n'
                if data["connecting_entrance"]:
                    self.entrances_py += f'        "{data["connecting_entrance"]}",\n'
                else:
                    self.entrances_py += f'        {None},\n'
                self.entrances_py += f'        {data["direction"]}, {data["can_shuffle"]}, {data["group"]},\n'
                if data["ss_exit_name"] is None:
                    self.entrances_py += f'        None,\n'
                else:
                    self.entrances_py += f'        "{data["ss_exit_name"]}",\n'
                if data["ss_entrance_name"] is None:
                    self.entrances_py += f'        None,\n'
                else:
                    self.entrances_py += f'        "{data["ss_entrance_name"]}",\n'
                self.entrances_py += f'        {data["can_start_at"]},\n'
                if "exit_stage" in data and "entrance_stage" in data:
                    self.entrances_py += f'        "{data["exit_stage"]}", {data["exit_room"]}, {data["exit_index"]},\n'
                    self.entrances_py += f'        "{data["entrance_stage"]}", {data["entrance_room"]}, {data["entrance_index"]}, {data["entrance_layer"]}, {data["entrance_tod"]},\n'
                self.entrances_py += f'    ),\n'
        self.entrances_py += "]\n\n\n"

        with open("./entrances/entrance_templates/game_entrance_class", "r") as f:
            self.entrances_py += f.read() + "\n\n"
        self.entrances_py += "GAME_ENTRANCE_TABLE = [\n"

        for ent, data in self.game_entrances.items():
            if data["type"] == "exit":
                continue
            if "can-start-at" in data:
                if data["can-start-at"] == False:
                    continue
            if len([gment for gment in GAME_ENTRANCE_TABLE if gment.name == ent]) == 1:
                existing_ent = [gment for gment in GAME_ENTRANCE_TABLE if gment.name == ent].pop()
                ent_name = existing_ent.name
                ent_statue_name = existing_ent.statue_name
                ent_province = existing_ent.province
                ent_stage = existing_ent.stage
                ent_room = existing_ent.room
                ent_layer = existing_ent.layer
                ent_entrance = existing_ent.entrance
                ent_tod = existing_ent.tod
                ent_type = existing_ent.type
                ent_apregion = existing_ent.apregion
                ent_flag_space = existing_ent.flag_space
                ent_flag = existing_ent.flag
                ent_vanilla_statue = existing_ent.vanilla_statue
            else:
                ent_name = ent
                ent_province = data["province"]
                ent_stage = data["stage"]
                ent_room = data["room"]
                ent_layer = data["layer"]
                ent_entrance = data["entrance"]
                ent_tod = data["tod"]
                if "subtype" in data:
                    if data["subtype"] == "bird-statue-entrance":
                        ent_type = "Statue"
                        ent_statue_name = data["statue-name"]
                        ent_flag_space = data["flag-space"]
                        ent_flag = data["flag"]
                        if "vanilla-start-statue" in data:
                            ent_vanilla_statue = True
                        else:
                            ent_vanilla_statue = False
                elif ent_name == "Skyloft - Knight Academy - Start Entrance":
                    ent_type = "Vanilla"
                    ent_statue_name = "Link's Room"
                else:
                    ent_type = "Entrance"
                    ent_statue_name = None
                    
                ent_apregion = input(f"AP region for entrance: {ent}")

            self.entrances_py += f'    SSGameEntrance(\n'
            self.entrances_py += f'        "{ent_name}",\n'
            if ent_statue_name:
                self.entrances_py += f'        "{ent_statue_name}",\n'
            else:
                self.entrances_py += f'        None,\n'
            self.entrances_py += f'        "{ent_province}",\n'
            self.entrances_py += f'        "{ent_stage}", {ent_room}, {ent_layer}, {ent_entrance}, {ent_tod},\n'
            self.entrances_py += f'        "{ent_type}", "{ent_apregion}",\n'
            if ent_type == "Statue":
                self.entrances_py += f'        "{ent_flag_space}", {ent_flag}, {ent_vanilla_statue},\n'
            self.entrances_py += f'    ),\n'

        self.entrances_py += "]\n"

        with open("Entrances.py", "w") as f:
            f.write(self.entrances_py)


Ent = Entrances()

Ent.exporter()
Ent.py_exporter()
