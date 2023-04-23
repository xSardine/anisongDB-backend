import json
import utils

"""
A script to add/edit/remove line ups
"""

song_DATABASE_PATH = "../app/data/song_database.json"
artist_DATABASE_PATH = "../app/data/artist_database.json"

with open(song_DATABASE_PATH, encoding="utf-8") as json_file:
    song_database = json.load(json_file)
with open(artist_DATABASE_PATH, encoding="utf-8") as json_file:
    artist_database = json.load(json_file)


def add_member_group_links(group_id, group_members, line_up_id):
    """add new group link to new line up vocalist

    Parameters
    ----------
    group_id : int
        group id
    group_members : list
        list of members in the new line up
    line_up_id : int
        line up id

    Returns
    -------
    None
    """
    for member in group_members:
        print(
            f"adding link {member['role_type']} '{group_id},{line_up_id}' to {artist_database[member['id']]['name']}"
        )
        artist_database[member["id"]]["groups"].append(
            {"id": group_id, "line_up_id": line_up_id, "role_type": member["role_type"]}
        )
        artist_database[member["id"]][f"is_{member['role_type']}"] = True


def remove_member_group_links(group_id, line_up_id):
    """
    remove group link from old line up

    Parameters
    ----------
    group_id : int
        group id
    line_up_id : int
        line up id

    Returns
    -------
    None
    """

    group = artist_database[group_id]
    for member in group["line_ups"][line_up_id]["members"]:
        for j, groupT in enumerate(artist_database[member["id"]]["groups"]):
            if groupT["id"] == group_id and groupT["line_up_id"] == line_up_id:
                print(
                    f"removed link '{group_id},{line_up_id}' from {artist_database[member['id']]['name']}"
                )
                artist_database[member["id"]]["groups"].pop(j)


def update_new_line_up_in_song_database(group_id, line_up_id, update_songs, mode):
    """
    Update the song database with the new line up

    Parameters
    ----------
    group_id : int
        group id
    line_up_id : int
        line up id
    update_songs : list
        list of songs to update
    mode : str
        mode of update (edit, addAll, addSub)
    """

    if mode not in ["edit", "addAll", "addSub"]:
        print("CHOOSE A CORRECT MODE")
        exit(1)

    print("\nUpdated Song:")
    if mode == "addAll":
        for anime_ann_id in song_database:
            anime = song_database[anime_ann_id]
            for song in anime["songs"]:
                for artist in (
                    song["vocalists"]
                    + song["backing_vocalists"]
                    + song["performers"]
                    + song["composers"]
                    + song["arrangers"]
                ):
                    if artist["id"] == group_id:
                        print(song["song_name"])
                        artist["line_up_id"] = line_up_id
        print()
        return

    if mode == "addSub":
        for update_song in update_songs:
            flag_song = False
            for anime_ann_id in song_database:
                anime = song_database[anime_ann_id]
                for song in anime["songs"]:
                    if utils.check_same_song(song, update_song):
                        flag_artist = False
                        for artist in (
                            song["vocalists"]
                            + song["backing_vocalists"]
                            + song["performers"]
                            + song["composers"]
                            + song["arrangers"]
                        ):
                            if group_id == artist["id"]:
                                flag_song = True
                                flag_artist = True
                                artist["line_up_id"] = line_up_id
                                print(song["song_name"])
                        if not flag_artist:
                            print(f"{update_song} FOUND BUT NOT THE RIGHT ARTIST")
            if not flag_song:
                print(f"{update_song} NOT FOUND")

    print()


def remove_line_up(group_id, line_up_id, fall_back_line_up):
    """
    Remove a line up from a group

    Parameters
    ----------
    group_id : int
        group id from which to remove line up
    line_up_id : int
        line up id to remove
    fall_back_line_up : int
        line up id to fall back to

    Returns
    -------
    None
    """

    # song - artist links
    print()

    for anime_ann_id in song_database:
        anime = song_database[anime_ann_id]
        for song in anime["songs"]:
            for artist in (
                song["vocalists"]
                + song["backing_vocalists"]
                + song["performers"]
                + song["composers"]
                + song["arrangers"]
            ):
                if artist["id"] != group_id:
                    continue
                # Update song - artist links for removed line up
                if artist["line_up_id"] == line_up_id:
                    print(
                        f"{song['song_name']} : {artist['line_up_id']} → {fall_back_line_up}"
                    )
                    artist["line_up_id"] = fall_back_line_up
                # Update song - artist links for above line ups that got shifted
                elif artist["line_up_id"] > line_up_id:
                    print(
                        f"{song['song_name']} : {artist['line_up_id']} → {artist['line_up_id']-1}"
                    )
                    artist["line_up_id"] -= 1

    print()
    # Remove artist - group links for line up
    for member in artist_database[group_id]["line_ups"][line_up_id]["members"]:
        for i, group in enumerate(artist_database[member["id"]]["groups"]):
            if group["id"] == group_id and group["line_up_id"] == line_up_id:
                print(
                    f"Removing artist - group link for {artist_database[member['id']]['name']}, {line_up_id}"
                )
                artist_database[member["id"]]["groups"].pop(i)

    print()
    # Update artist - group links for above line-up that got shifted
    for line_up in artist_database[group_id]["line_ups"][line_up_id:]:
        for member in line_up["members"]:
            for group in artist_database[member["id"]]["groups"]:
                if group["id"] == group_id and group["line_up_id"] > line_up_id:
                    # TODO : problem with relation types
                    print(
                        f"Updating link for {artist_database[member['id']]['name']}: {group['line_up_id']}→{group['line_up_id']-1}"
                    )
                    group["line_up_id"] -= 1

    print()
    # Update line-up for topGroup containing the affected group
    for artist_id in artist_database:
        artist = artist_database[artist_id]
        for line_up in artist["line_ups"]:
            for member in line_up["members"]:
                if member["id"] != group_id:
                    continue
                # Update group - member links for removed line up
                if member["line_up_id"] == line_up_id:
                    print(
                        f"{artist['name']} : {member['line_up_id']} → {fall_back_line_up}"
                    )
                    member["line_up_id"] = fall_back_line_up
                # Update group - member links for above line ups that got shifted
                elif member["line_up_id"] > line_up_id:
                    # TODO : problem with relation types
                    print(
                        f"{artist['name']} : {member['line_up_id']} → {member['line_up_id']-1}"
                    )
                    member["line_up_id"] -= 1

    artist_database[group_id]["line_ups"].pop(line_up_id)


def process():
    user_input, group_id = utils.ask_artist(
        "Please input the group to which you want to add a line up\n",
        song_database,
        artist_database,
    )
    group = artist_database[group_id]

    if not group["line_ups"]:
        print(
            f"No Line Up found for {group['name']}, automatically adding to every songs\n"
        )

        group_members = utils.ask_line_up(
            "Please type in the members you want to add\n",
            song_database,
            artist_database,
            not_exist_ok=True,
        )

        if not group_members:
            print("There are no members to add, cancelled")
            return

        group_recap_str1 = f"group {group['name']}: {' | '.join(utils.get_example_song_for_artist(song_database, group_id)[:min(3, len(utils.get_example_song_for_artist(song_database, group_id)))])}"

        group_recap_str2 = ""
        for member in group_members:
            if member["id"] in artist_database:
                group_recap_str2 += f"{artist_database[member['id']]['name']} {member['role_type']} {member['id']} {member['line_up_id']}> {' | '.join(utils.get_example_song_for_artist(song_database, member['id'])[:min(3, len(utils.get_example_song_for_artist(song_database, member['id'])))])}\n"
            else:
                group_recap_str2 += f"NEW {member['id']}\n"

        group["line_ups"] = [{"line_up_id": 0, "members": group_members}]

        add_member_group_links(group_id, group_members, 0)

        # change line up for any group containing this group as it is now a group
        for artist_id in artist_database:
            artist = artist_database[artist_id]
            for line_up in artist["line_ups"]:
                for member in line_up["members"]:
                    if member["id"] == group_id:
                        print(f"Swapping to line up 0 in {artist['name']}")
                        member["line_up_id"] = 0

        update_new_line_up_in_song_database(group_id, 0, [], "addAll")

        validation_message = f"You will add the first line-up to every song by the {group_recap_str1}\nThe line up is composed of:\n{group_recap_str2}\nDo you validate this change ?\n"
        validation = utils.ask_validation(validation_message)
        if not validation:
            print("User Cancelled")
            return

    else:
        validation = utils.ask_validation(
            "There are already existing line up, do you want to remove one ?\n"
        )
        if validation:
            # skip user input as there's no question needed if only one line up
            if len(group["line_ups"]) == 1:
                remove_line_up(group_id, 0, -1)

            else:
                line_ups = "\n"
                for i, line_up in enumerate(group["line_ups"]):
                    line_up = [
                        artist_database[member["id"]]["name"]
                        for member in line_up["members"]
                    ]
                    line_ups += f"{i}: {', '.join(line_up)}\n"
                line_up_id = utils.ask_integer_input(
                    f"Please select the line up you want to remove:{line_ups}",
                    range(len(group["line_ups"])),
                )

                line_ups = "\n"
                tmp_line_up = group["line_ups"].copy()
                tmp_line_up.pop(line_up_id)
                for i, line_up in enumerate(tmp_line_up):
                    line_up = [
                        artist_database[member["id"]]["name"]
                        for member in line_up["members"]
                    ]
                    line_ups += f"{i}: {', '.join(line_up)}\n"
                fall_back_line_up = utils.ask_integer_input(
                    f"Please select to which line up should the song fall back to:{line_ups}",
                    range(len(group["line_ups"]) - 1),
                )

                remove_line_up(group_id, line_up_id, fall_back_line_up)

            validation_message = "Do you validate those changes ?\n"
            validation = utils.ask_validation(validation_message)
            if not validation:
                print("USER CANCELLED")
                return

        else:
            line_ups = "\n"
            for i, line_up in enumerate(group["line_ups"]):
                line_up = [
                    artist_database[member["id"]]["name"]
                    for member in line_up["members"]
                ]
                line_ups += f"{i}: {', '.join(line_up)}\n"

            line_up_id = utils.ask_integer_input(
                f"There are already line-ups linked to this group, input the one you want to update or -1 if you want to add a new one:\n{line_ups}",
                range(-1, len(group["line_ups"])),
            )

            if line_up_id != -1:
                print("Updating a line up\n")

                group_members = utils.update_line_up(
                    group,
                    line_up_id,
                    song_database,
                    artist_database,
                )

                if not group_members:
                    print("There are no members to add, cancelled")
                    return

                group_recap_str1 = f"group {group['name']}: {' | '.join(utils.get_example_song_for_artist(song_database, group_id)[:min(3, len(utils.get_example_song_for_artist(song_database, group_id)))])}"

                group_recap_str2 = ""
                for member in group_members:
                    if member["id"] in artist_database:
                        group_recap_str2 += f"{artist_database[member['id']]['name']} {member}> {' | '.join(utils.get_example_song_for_artist(song_database, member['id'])[:min(3, len(utils.get_example_song_for_artist(song_database, member['id'])))])}\n"
                    else:
                        group_recap_str2 += f"NEW {member['id']}\n"

                remove_member_group_links(group_id, line_up_id)

                add_member_group_links(group_id, group_members, line_up_id)

                print(
                    "Select the songs you want to update, if already linked: removed if not already linked: added to line up\n"
                )
                linked_songs = utils.ask_song_ids()

                update_new_line_up_in_song_database(
                    group_id, line_up_id, linked_songs, "addSub"
                )

                group["line_ups"][line_up_id] = {
                    "line_up_id": line_up_id,
                    "members": group_members,
                }

                validation_message = f"You will update line-up n°{line_up_id} of the {group_recap_str1}\nThis line up will be composed of:\n{group_recap_str2}\nDo you validate this change ?\n"
                validation = utils.ask_validation(validation_message)
                if not validation:
                    print("USER CANCELLED")
                    return

            else:
                print("Creating a new line up\n")

                group_members = utils.ask_line_up(
                    "Please type in the members you want to add\n",
                    song_database,
                    artist_database,
                    not_exist_ok=True,
                )

                if not group_members:
                    print("There are no members to add, cancelled")
                    return

                group_recap_str1 = f"group {group['name']}: {' | '.join(utils.get_example_song_for_artist(song_database, group_id)[:min(3, len(utils.get_example_song_for_artist(song_database, group_id)))])}"

                group_recap_str2 = ""
                for member in group_members:
                    if member["id"] in artist_database:
                        group_recap_str2 += f"{artist_database[member['id']]['name']} {member}> {' | '.join(utils.get_example_song_for_artist(song_database, member['id'])[:min(3, len(utils.get_example_song_for_artist(song_database, member['id'])))])}\n"
                    else:
                        group_recap_str2 += f"NEW {member['id']}\n"

                line_up_id = len(group["line_ups"])

                linked_songs = utils.ask_song_ids()

                if not linked_songs:
                    validation_message = "There are no songs to link to this line up, are you sure you want to continue ?\n"
                    validation = utils.ask_validation(validation_message)
                    if not validation:
                        print("USER CANCELLED")
                        return

                add_member_group_links(group_id, group_members, line_up_id)

                group["line_ups"].append(
                    {"line_up_id": line_up_id, "members": group_members}
                )

                update_new_line_up_in_song_database(
                    group_id, line_up_id, linked_songs, "addSub"
                )

                validation_message = f"You will add a new line-up (n°{line_up_id}) to the {group_recap_str1}\non the songs {linked_songs}\nThis line up will be composed of:\n{group_recap_str2}\nDo you validate this change ?\n"
                validation = utils.ask_validation(validation_message)
                if not validation:
                    print("USER CANCELLED")
                    return

    with open(song_DATABASE_PATH, "w", encoding="utf-8") as outfile:
        json.dump(song_database, outfile, indent=4)
    with open(artist_DATABASE_PATH, "w", encoding="utf-8") as outfile:
        json.dump(artist_database, outfile, indent=4)


"""
enter the "group", and the "member" of the line up to add/update
if there are not any line up yet, will add automatically to line up 0, and link every song by this artist
if there are line up already, will ask you to either edit existing one or create a new one:
    - edit existing one will swap old line up with new line up, and if linked_songs will also add/remove song linked depending of their current state
    - add a new one will create a new line up and link any song in linked_songs
"""

process()

# remove old groups on update
