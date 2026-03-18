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

    return players
