import pickle
import zlib
import glob
import zipfile
import hashlib
import json
from pathlib import Path

OUTPUT_PATH = "./output"  # must not end with a '/'


def print_save_data(save_data, depth=0):
    for key, value in save_data.items():
        if type(value) == dict:
            print("  " * depth, key, ":")
            print_save_data(save_data[key], depth + 1)
        else:
            print("  " * depth, key, value)


def get_hash_from_json(data: dict) -> str:
    return hashlib.sha256(json.dumps(data).encode("utf8")).hexdigest()


def get_apsave_file_path():
    # TODO add ways to input the output_path/apsave path
    apsave_files = glob.glob(f"{OUTPUT_PATH}/*.apsave")
    if len(apsave_files) == 0:
        raise Exception(
            f"no .apsave file found in the output path directory {OUTPUT_PATH}"
        )
    # TODO add choosing the latest edited apsave file as default behavior while giving a warning
    if len(apsave_files) > 1:
        raise Exception(
            f"more than one .apsave file found in the output path directory {OUTPUT_PATH}"
        )

    return apsave_files[0]


def get_zip_file_path():
    # TODO add ways to input the output_path/zip path
    zip_files = glob.glob(f"{OUTPUT_PATH}/*.zip")
    if len(zip_files) == 0:
        raise Exception(
            f"no .zip file found in the output path directory {OUTPUT_PATH}"
        )
    # TODO add choosing the latest edited zip file as default behavior while giving a warning
    if len(zip_files) > 1:
        raise Exception(
            f"more than one .zip file found in the output path directory {OUTPUT_PATH}"
        )

    return zip_files[0]


def load_apsave(apsave_file_path: str, players) -> list:
    if not Path(apsave_file_path).exists:
        return players

    with open(apsave_file_path, "rb") as f:
        save_data = pickle.loads(zlib.decompress(f.read()))
    return get_players_from_apsave_data(save_data, players)


def load_archipelago_file(zip_file_path: str):
    with zipfile.ZipFile(zip_file_path) as zf:
        for file in zf.namelist():
            if file.endswith(".archipelago"):
                data = zf.read(file)
                break
    data = pickle.loads(zlib.decompress(data[1:]))

    datapackages: dict[str, dict] = {}
    for game_name, game in data["datapackage"].items():
        datapackage = {
            "item_name_to_id": game["item_name_to_id"],
            "location_name_to_id": game["location_name_to_id"],
            "game": game_name,
        }
        datapackage["hash"] = get_hash_from_json(datapackage)
        datapackages[game_name] = datapackage
    return get_players_from_archipelago_data(data), datapackages


class ArchipelagoData:
    def __init__(self):
        players, datapackages = load_archipelago_file(get_zip_file_path())
        self.players = load_apsave(get_apsave_file_path(), players)
        self.datapackages = datapackages


def get_players_from_archipelago_data(data):
    players = []
    # name, team, slot
    for player_name, (team, slot) in data["connect_names"].items():
        players.append({"name": player_name, "team": team, "slot": slot})

    # game and location_number
    for key, slot_info in data["slot_info"].items():
        for player in players:
            if player["name"] == slot_info.name:
                player["game"] = slot_info.game
                player["location_number"] = len(data["locations"][key])
                break

    return players


def get_players_from_apsave_data(data, players):
    # checks
    for (team, slot), checks in data["location_checks"].items():
        for player in players:
            if player["team"] == team and player["slot"] == slot:
                player["checks"] = list(checks)
                break

    # game_state
    for (team, slot), game_state in data["client_game_state"].items():
        for player in players:
            if player["team"] == team and player["slot"] == slot:
                player["game_state"] = {
                    0: "Disconnected",
                    5: "Connected",
                    10: "ready",
                    20: "Playing",
                    30: "Goal Completed",
                }[game_state]
                break

    # last activity
    for (team, slot), last_activity in data["client_activity_timers"]:
        for player in players:
            if player["team"] == team and player["slot"] == slot:
                player["last_activity"] = round(last_activity)
                break

    # hints
    for (team, slot), hints in data["hints"].items():
        for player in players:
            if player["team"] == team and player["slot"] == slot:
                player["hints"] = [
                    {
                        "receiving_player": hint.receiving_player,
                        "finding_player": hint.finding_player,
                        "location": hint.location,
                        "item": hint.item,
                        "found": hint.found,
                        "item_flags": hint.item_flags,
                        "status": int(hint.status),
                        "entrance": hint.entrance,
                    }
                    for hint in hints
                ]
                break

    return players
