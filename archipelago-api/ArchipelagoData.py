def get_players_from_data(data):
    players = []
    # name, team, slot
    for player_name, (team, slot) in data["connect_names"].items():
        players.append({"name": player_name, "team": team, "slot": slot})

    # checks
    for (team, slot), checks in data["location_checks"].items():
        for player in players:
            if not player["team"] == team or not player["slot"] == slot:
                continue

            player["checks"] = list(checks)
            break

    # game_state
    for (team, slot), game_state in data["client_game_state"].items():
        for player in players:
            if not player["team"] == team or not player["slot"] == slot:
                continue

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
            if not player["team"] == team or not player["slot"] == slot:
                continue

            player["last_activity"] = round(last_activity)
            break

    return players
