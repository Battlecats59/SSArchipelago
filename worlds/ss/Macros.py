from BaseClasses import CollectionState

############ MACRO NAMING ############
#  has item:        "has_"           #
#  defeat enemies:  "can_defeat_"    #
#  defeat bosses:   "can_beat_"      #
#  beat dungeon:    "can_beat_"      #
#  access region:   "can_access_"    #
#  reach area:      "can_reach_"     #
#  get past area:   "can_pass_"      #
# -------------- misc -------------- #
#  "can_afford_"                     #
#  "can_obtain_"                     #
#  "can_reach_dungeon_entrance_in_"  #
######################################


# Items
def has_practice_sword(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Sword", player, 1)


def has_goddess_sword(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Sword", player, 2)


def has_goddess_longsword(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Sword", player, 3)


def has_goddess_white_sword(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Sword", player, 4)


def has_master_sword(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Sword", player, 5)


def has_true_master_sword(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Sword", player, 6)


def has_beetle(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Beetle", player, 1)


def has_hook_beetle(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Beetle", player, 2)

def has_quick_beetle(state: CollectionState, player: int) -> bool:
    return (
        (state.has("Progressive Beetle", player, 3) & state._ss_option_gondo_upgrades(player))
        | (can_upgrade_to_quick_beetle(state, player) & ~state._ss_option_gondo_upgrades(player))
    )

def has_tough_beetle(state: CollectionState, player: int) -> bool:
    return (
        (state.has("Progressive Beetle", player, 4) & state._ss_option_gondo_upgrades(player))
        | (can_upgrade_to_tough_beetle(state, player) & ~state._ss_option_gondo_upgrades(player))
    )

def has_bow(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Bow", player, 1)


def has_slingshot(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Slingshot", player, 1)


def has_bug_net(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Bug Net", player, 1)


def has_digging_mitts(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Mitts", player, 1)


def has_mogma_mitts(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Mitts", player, 2)


def has_pouch(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Pouch", player, 1)


def has_medium_wallet(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Wallet", player, 1)


def has_big_wallet(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Wallet", player, 2)


def has_giant_wallet(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Wallet", player, 3)


def has_tycoon_wallet(state: CollectionState, player: int) -> bool:
    return state.has("Progressive Wallet", player, 4)


def has_one_extra_wallet(state: CollectionState, player: int) -> bool:
    return state.has("Extra Wallet", player, 1)


def has_two_extra_wallets(state: CollectionState, player: int) -> bool:
    return state.has("Extra Wallet", player, 2)


def has_three_extra_wallets(state: CollectionState, player: int) -> bool:
    return state.has("Extra Wallet", player, 3)


def has_song_of_the_hero(state: CollectionState, player: int) -> bool:
    return (
        state.has("Faron Song of the Hero Part", player)
        & state.has("Eldin Song of the Hero Part", player)
        & state.has("Lanayru Song of the Hero Part", player)
    )


def has_bottle(state: CollectionState, player: int) -> bool:
    return has_pouch(state, player) & state.has("Empty Bottle", player)


def has_completed_triforce(state: CollectionState, player: int) -> bool:
    return (
        state.has("Triforce of Courage", player)
        & state.has("Triforce of Power", player)
        & state.has("Triforce of Wisdom", player)
    )


# Misc
def upgraded_skyward_strike(state: CollectionState, player: int) -> bool:
    return has_true_master_sword(state, player) | (
        state._ss_option_upgraded_skyward_strike(player)
        & has_goddess_sword(state, player)
    )


def unlocked_endurance_potion(state: CollectionState, player: int) -> bool:
    return can_raise_lmf(state, player)


def damaging_item(state: CollectionState, player: int) -> bool:
    return (
        has_practice_sword(state, player)
        | has_bow(state, player)
        | state.has("Bomb Bag", player)
    )


def projectile_item(state: CollectionState, player: int) -> bool:
    return (
        has_slingshot(state, player)
        | has_beetle(state, player)
        | has_bow(state, player)
    )


def distance_activator(state: CollectionState, player: int) -> bool:
    return projectile_item(state, player) | state.has("Clawshots", player)


def can_cut_trees(state: CollectionState, player: int) -> bool:
    return has_practice_sword(state, player) | state.has("Bomb Bag", player)


def can_unlock_combination_lock(state: CollectionState, player: int) -> bool:
    return (
        has_practice_sword(state, player)
        | has_bow(state, player)
        | state.has("Whip", player)
        | state.has("Clawshots", player)
    )


def can_hit_timeshift_stone(state: CollectionState, player: int) -> bool:
    return (
        distance_activator(state, player)
        | has_practice_sword(state, player)
        | state.has("Whip", player)
        | state.has("Bomb Bag", player)
    )

def can_upgrade_to_quick_beetle(state: CollectionState, player: int) -> bool:
    return(
        has_hook_beetle(state, player)
        & can_access_deep_woods(state, player) # Larvae farming
        & (
            lanayru_mine_ancient_flower_farming(state, player)
            | lanayru_desert_ancient_flower_farming(state, player)
            | lanayru_desert_ancient_flower_farming_near_main_node(state, player)
            | pirate_stronghold_ancient_flower_farming(state, player)
            | lanayru_gorge_ancient_flower_farming(state, player)
        ) # Ancient flower farming
        & clean_cut_minigame(state, player) # Gold Skull farming
    )

def can_upgrade_to_tough_beetle(state: CollectionState, player: int) -> bool:
    return(
        can_upgrade_to_quick_beetle(state, player)
        & can_reach_most_of_faron_woods(state, player) # Amber relic farming
        & (
            lanayru_mine_ancient_flower_farming(state, player)
            | lanayru_desert_ancient_flower_farming(state, player)
            | lanayru_desert_ancient_flower_farming_near_main_node(state, player)
            | pirate_stronghold_ancient_flower_farming(state, player)
            | lanayru_gorge_ancient_flower_farming(state, player)
        ) # Ancient flower farming
        & clean_cut_minigame(state, player) # Plume/Blue feather farming
    )


# Can Defeat
def can_defeat_bokoblins(state: CollectionState, player: int) -> bool:
    return damaging_item(state, player)


def can_defeat_moblins(state: CollectionState, player: int) -> bool:
    return damaging_item(state, player)


def can_defeat_keeses(state: CollectionState, player: int) -> bool:
    return (
        damaging_item(state, player)
        | has_slingshot(state, player)
        | has_beetle(state, player)
        | state.has("Whip", player)
        | state.has("Clawshots", player)
    )


def can_defeat_lezalfos(state: CollectionState, player: int) -> bool:
    return has_practice_sword(state, player) | state.has("Bomb Bag", player)


def can_defeat_ampilus(state: CollectionState, player: int) -> bool:
    return damaging_item(state, player)


def can_defeat_moldarachs(state: CollectionState, player: int) -> bool:
    return state.has("Gust Bellows", player) & has_practice_sword(state, player)


def can_defeat_armos(state: CollectionState, player: int) -> bool:
    return state.has("Gust Bellows", player) & has_practice_sword(state, player)


def can_defeat_beamos(state: CollectionState, player: int) -> bool:
    return has_practice_sword(state, player) | has_bow(state, player)


def can_defeat_cursed_bokoblins(state: CollectionState, player: int) -> bool:
    return has_practice_sword(state, player) | state.has("Bomb Bag", player)


def can_defeat_stalfos(state: CollectionState, player: int) -> bool:
    return has_practice_sword(state, player)


def can_defeat_stalmaster(state: CollectionState, player: int) -> bool:
    return has_practice_sword(state, player)


# Crystals
def can_access_batreauxs_house(state: CollectionState, player: int) -> bool:
    return can_access_skyloft_village(state, player)


def can_obtain_5_loose_crystals(state: CollectionState, player: int) -> bool:
    return can_access_central_skyloft(state, player)


def can_obtain_10_loose_crystals(state: CollectionState, player: int) -> bool:
    return (
        can_access_central_skyloft(state, player)
        & can_access_sky(state, player)
        & (
            can_cut_trees(state, player)  # 2 crystals past waterfall cave
            | state.has("Clawshots", player)  # Zelda's room, atop waterfall
            | has_beetle(state, player)
        )  # Sparring hall, beedle's island
    )


def can_obtain_15_loose_crystals(state: CollectionState, player: int) -> bool:
    return (
        can_access_central_skyloft(state, player)
        & can_access_sky(state, player)
        & (can_cut_trees(state, player) | has_beetle(state, player))
        & state.has("Clawshots", player)
        & has_beetle(state, player)
    )


def five_gratitude_crystals(state: CollectionState, player: int) -> bool:
    return can_obtain_5_loose_crystals(state, player) | state.has(
        "Gratitude Crystal Pack", player, 1
    )


def ten_gratitude_crystals(state: CollectionState, player: int) -> bool:
    return (
        can_obtain_10_loose_crystals(state, player)
        | (
            can_obtain_5_loose_crystals(state, player)
            & state.has("Gratitude Crystal Pack", player, 1)
        )
        | state.has("Gratitude Crystal Pack", player)
    )


def thirty_gratitude_crystals(state: CollectionState, player: int) -> bool:
    return (
        (
            can_obtain_15_loose_crystals(state, player)
            & state.has("Gratitude Crystal Pack", player, 3)
        )
        | (
            can_obtain_10_loose_crystals(state, player)
            & state.has("Gratitude Crystal Pack", player, 4)
        )
        | (
            can_obtain_5_loose_crystals(state, player)
            & state.has("Gratitude Crystal Pack", player, 5)
        )
        | state.has("Gratitude Crystal Pack", player, 6)
    )


def forty_gratitude_crystals(state: CollectionState, player: int) -> bool:
    return (
        (
            can_obtain_15_loose_crystals(state, player)
            & state.has("Gratitude Crystal Pack", player, 5)
        )
        | (
            can_obtain_10_loose_crystals(state, player)
            & state.has("Gratitude Crystal Pack", player, 6)
        )
        | (
            can_obtain_5_loose_crystals(state, player)
            & state.has("Gratitude Crystal Pack", player, 7)
        )
        | state.has("Gratitude Crystal Pack", player, 8)
    )


def fifty_gratitude_crystals(state: CollectionState, player: int) -> bool:
    return (
        (
            can_obtain_15_loose_crystals(state, player)
            & state.has("Gratitude Crystal Pack", player, 7)
        )
        | (
            can_obtain_10_loose_crystals(state, player)
            & state.has("Gratitude Crystal Pack", player, 8)
        )
        | (
            can_obtain_5_loose_crystals(state, player)
            & state.has("Gratitude Crystal Pack", player, 9)
        )
        | state.has("Gratitude Crystal Pack", player, 10)
    )


def seventy_gratitude_crystals(state: CollectionState, player: int) -> bool:
    return (
        (
            can_obtain_15_loose_crystals(state, player)
            & state.has("Gratitude Crystal Pack", player, 11)
        )
        | (
            can_obtain_10_loose_crystals(state, player)
            & state.has("Gratitude Crystal Pack", player, 12)
        )
        | (
            can_obtain_5_loose_crystals(state, player)
            & state.has("Gratitude Crystal Pack", player, 13)
        )
    )


def eighty_gratitude_crystals(state: CollectionState, player: int) -> bool:
    return can_obtain_15_loose_crystals(state, player) & state.has(
        "Gratitude Crystal Pack", player, 13
    )


# Rupees
def can_access_beedles_shop(state: CollectionState, player: int) -> bool:
    return distance_activator(state, player)


def can_afford_300_rupees(state: CollectionState, player: int) -> bool:
    return can_medium_rupee_farm(state, player)


def can_afford_600_rupees(state: CollectionState, player: int) -> bool:
    return can_high_rupee_farm(state, player) & (
        has_big_wallet(state, player) | has_one_extra_wallet(state, player)
    )


def can_afford_800_rupees(state: CollectionState, player: int) -> bool:
    return can_high_rupee_farm(state, player) & (
        has_big_wallet(state, player)
        | has_two_extra_wallets(state, player)
        | (has_medium_wallet(state, player) & has_one_extra_wallet(state, player))
    )


def can_afford_1000_rupees(state: CollectionState, player: int) -> bool:
    return can_high_rupee_farm(state, player) & (
        has_big_wallet(state, player)
        | has_three_extra_wallets(state, player)
        | (has_medium_wallet(state, player) & has_two_extra_wallets(state, player))
    )


def can_afford_1200_rupees(state: CollectionState, player: int) -> bool:
    return can_high_rupee_farm(state, player) & (
        has_giant_wallet(state, player)
        | has_three_extra_wallets(state, player)
        | (has_big_wallet(state, player) & has_one_extra_wallet(state, player))
        | (has_medium_wallet(state, player) & has_three_extra_wallets(state, player))
    )


def can_afford_1600_rupees(state: CollectionState, player: int) -> bool:
    return can_high_rupee_farm(state, player) & (
        has_giant_wallet(state, player)
        | (has_big_wallet(state, player) & has_two_extra_wallets(state, player))
    )


def can_medium_rupee_farm(state: CollectionState, player: int) -> bool:
    return (
        clean_cut_minigame(state, player) & can_access_skyloft_village(state, player)
    ) | can_high_rupee_farm(state, player)


def can_high_rupee_farm(state: CollectionState, player: int) -> bool:
    return fun_fun_minigame(state, player) | thrill_digger_minigame(state, player)


def clean_cut_minigame(state: CollectionState, player: int) -> bool:
    return can_access_sky(state, player) & has_practice_sword(state, player)


def fun_fun_minigame(state: CollectionState, player: int) -> bool:
    return can_access_sky(state, player) & can_retrieve_party_wheel(state, player)


def thrill_digger_minigame(state: CollectionState, player: int) -> bool:
    return can_reach_second_part_of_eldin_volcano(state, player) & has_digging_mitts(
        state, player
    )


### SKY REGION
# Skyloft
def can_access_upper_skyloft(state: CollectionState, player: int) -> bool:
    return True


def can_access_central_skyloft(state: CollectionState, player: int) -> bool:
    return True


def can_access_skyloft_village(state: CollectionState, player: int) -> bool:
    return True


def can_reach_dungeon_entrance_on_skyloft(state: CollectionState, player: int) -> bool:
    return (
        can_access_central_skyloft(state, player)
        & state.has("Stone of Trials", player)
        & state.has("Clawshots", player)
    )


def can_open_trial_gate_on_skyloft(state: CollectionState, player: int) -> bool:
    return (
        can_access_central_skyloft(state, player)
        & has_song_of_the_hero(state, player)
        & state.has("Goddess's Harp", player)
    )


# Sky
def can_access_sky(state: CollectionState, player: int) -> bool:
    return True


def can_save_orielle(state: CollectionState, player: int) -> bool:
    return has_bottle(state, player)


# Thunderhead
def can_access_thunderhead(state: CollectionState, player: int) -> bool:
    return (
        state._ss_option_thunderhead_ballad(player)
        & state.has("Ballad of the Goddess", player)
    ) | state._ss_option_thunderhead_open(player)


### Faron
# Sealed Grounds
def can_access_sealed_grounds(state: CollectionState, player: int) -> bool:
    return can_access_sky(state, player) & state.has("Emerald Tablet", player)


def can_reach_sealed_temple(state: CollectionState, player: int) -> bool:
    return can_access_sealed_grounds(state, player)


def can_raise_gate_of_time(state: CollectionState, player: int) -> bool:
    return state.has("Goddess's Harp", player)


# Past
def can_reach_past(state: CollectionState, player: int) -> bool:
    return (
        can_reach_sealed_temple(state, player)
        & can_raise_gate_of_time(state, player)
        & state._ss_sword_requirement_met(player)
        & (state._ss_can_beat_required_dungeons(player) | state._ss_option_unrequired_dungeons(player))
    )


def can_access_hylias_realm(state: CollectionState, player: int) -> bool:
    return can_reach_past(state, player) & (
        state._ss_option_no_triforce(player) | has_completed_triforce(state, player)
    )


def can_reach_and_defeat_demise(state: CollectionState, player: int) -> bool:
    return can_access_hylias_realm(state, player)


# Faron Woods
def can_access_faron_woods(state: CollectionState, player: int) -> bool:
    return can_reach_sealed_temple(state, player)


def can_reach_most_of_faron_woods(state: CollectionState, player: int) -> bool:
    return (
        can_access_faron_woods(state, player)
        & (
            can_cut_trees(state, player)
            | state.has("Clawshots", player)
        )
    )


def can_reach_oolo(state: CollectionState, player: int) -> bool:
    return (
        (
            can_access_faron_woods(state, player)
            | can_access_flooded_faron_woods(state, player)
        )
        & can_reach_most_of_faron_woods(state, player)
        & state.has("Bomb Bag", player)
    )


def can_reach_great_tree(state: CollectionState, player: int) -> bool:
    return can_reach_most_of_faron_woods(state, player) & state.has(
        "Water Dragon's Scale", player
    )


def can_reach_top_of_great_tree(state: CollectionState, player: int) -> bool:
    return (
        can_reach_most_of_faron_woods(state, player) & state.has("Clawshots", player)
    ) | (can_reach_great_tree(state, player) & state.has("Gust Bellows", player))


def can_talk_to_yerbal(state: CollectionState, player: int) -> bool:
    return can_reach_top_of_great_tree(state, player) & (
        has_slingshot(state, player) | has_beetle(state, player)
    )


def can_open_trial_gate_in_faron_woods(state: CollectionState, player: int) -> bool:
    return (
        can_reach_most_of_faron_woods(state, player)
        & state.has("Farore's Courage", player)
        & state.has("Goddess's Harp", player)
    )


def goddess_cube_on_east_great_tree_with_clawshot_target(
    state: CollectionState, player: int
) -> bool:
    return (
        can_reach_most_of_faron_woods(state, player)
        & (
            state.has("Clawshots", player) | can_reach_top_of_great_tree(state, player)
        )
        & has_goddess_sword(state, player)
    )


def goddess_cube_on_east_great_tree_with_rope(
    state: CollectionState, player: int
) -> bool:
    return can_reach_top_of_great_tree(state, player) & has_goddess_sword(
        state, player
    )


def goddess_cube_on_west_great_tree_near_exit(
    state: CollectionState, player: int
) -> bool:
    return can_reach_top_of_great_tree(state, player) & has_goddess_sword(
        state, player
    )


# Deep Woods
def can_access_deep_woods(state: CollectionState, player: int) -> bool:
    return can_reach_most_of_faron_woods(state, player) & (
        distance_activator(state, player) | state.has("Bomb Bag", player)
    )


def can_reach_deep_woods_after_beehive(state: CollectionState, player: int) -> bool:
    return can_access_deep_woods(state, player) & (
        distance_activator(state, player)
        | has_goddess_sword(state, player)
        | state.has("Bomb Bag", player)
    )


def can_reach_dungeon_entrance_in_deep_woods(
    state: CollectionState, player: int
) -> bool:
    return can_reach_deep_woods_after_beehive(state, player) & distance_activator(
        state, player
    )


def initial_goddess_cube(state: CollectionState, player: int) -> bool:
    return can_reach_deep_woods_after_beehive(state, player) & has_goddess_sword(
        state, player
    )


def goddess_cube_in_deep_woods(state: CollectionState, player: int) -> bool:
    return can_reach_deep_woods_after_beehive(state, player) & has_goddess_sword(
        state, player
    )


def goddess_cube_on_top_on_skyview(state: CollectionState, player: int) -> bool:
    return (
        can_reach_dungeon_entrance_in_deep_woods(state, player)
        & state.has("Clawshots", player)
        & has_goddess_sword(state, player)
    )


# Lake Floria
def can_access_lake_floria(state: CollectionState, player: int) -> bool:
    return (
        can_reach_most_of_faron_woods(state, player)
        & state.has("Water Dragon's Scale", player)
        & (
            (can_talk_to_yerbal(state, player) & has_goddess_sword(state, player))
            | (
                can_talk_to_yerbal(state, player)
                & state._ss_option_lake_floria_yerbal(player)
            )
            | state._ss_option_lake_floria_open(player)
        )
    )


def can_reach_floria_waterfall(state: CollectionState, player: int) -> bool:
    return can_access_lake_floria(state, player)


def can_reach_dungeon_entrance_in_lake_floria(
    state: CollectionState, player: int
) -> bool:
    return can_reach_floria_waterfall(state, player) & state.has(
        "Water Dragon's Scale", player
    )


def goddess_cube_in_lake_floria(state: CollectionState, player: int) -> bool:
    return can_access_lake_floria(state, player) & has_goddess_sword(state, player)


def goddess_cube_in_floria_waterfall(state: CollectionState, player: int) -> bool:
    return (
        can_reach_floria_waterfall(state, player)
        & state.has("Clawshots", player)
        & has_goddess_sword(state, player)
    )


# Flooded Faron Woods
def can_access_flooded_faron_woods(state: CollectionState, player: int) -> bool:
    return can_reach_top_of_great_tree(state, player)


### Eldin
# Eldin Volcano
def can_access_eldin_volcano(state: CollectionState, player: int) -> bool:
    return can_access_sky(state, player) & state.has("Ruby Tablet", player)


def can_reach_second_part_of_eldin_volcano(state: CollectionState, player: int) -> bool:
    return can_access_eldin_volcano(state, player) & (
        can_reach_second_part_of_mogma_turf(state, player)
        | (state.has("Bomb Bag", player) | has_hook_beetle(state, player))
    )


def can_survive_eldin_hot_cave(state: CollectionState, player: int) -> bool:
    return state.has(
        "Fireshield Earrings", player
    ) | state._ss_option_damage_multiplier_under_12(player)


def can_open_trial_gate_in_eldin_volcano(state: CollectionState, player: int) -> bool:
    return (
        can_reach_second_part_of_eldin_volcano(state, player)
        & state.has("Din's Power", player)
        & state.has("Goddess's Harp", player)
    )


def can_reach_dungeon_entrance_in_eldin_volcano(
    state: CollectionState, player: int
) -> bool:
    return can_reach_second_part_of_eldin_volcano(state, player) & state.has(
        "Key Piece", player, 5
    )


def goddess_cube_at_eldin_entrance(state: CollectionState, player: int) -> bool:
    return can_access_eldin_volcano(state, player) & has_goddess_sword(state, player)


def goddess_cube_near_mogma_turf_entrance(state: CollectionState, player: int) -> bool:
    return (
        can_access_eldin_volcano(state, player)
        | (can_access_bokoblin_base(state, player) & has_mogma_mitts(state, player))
    ) & has_goddess_sword(state, player)


def goddess_cube_on_sand_slide(state: CollectionState, player: int) -> bool:
    return (
        can_reach_second_part_of_eldin_volcano(state, player)
        & can_survive_eldin_hot_cave(state, player)
        & has_goddess_sword(state, player)
    )


def goddess_cube_east_of_earth_temple_entrance(
    state: CollectionState, player: int
) -> bool:
    return (
        can_reach_second_part_of_eldin_volcano(state, player)
        | (
            can_access_bokoblin_base(state, player)
            & has_mogma_mitts(state, player)
            & state.has("Clawshots", player)
            & (
                state.has("Bomb Bag", player)
                | (
                    can_bypass_boko_base_watchtower(state, player)
                    & state.has("Whip", player)
                )
            )
        )
    ) & has_goddess_sword(state, player)


def goddess_cube_west_of_earth_temple_entrance(
    state: CollectionState, player: int
) -> bool:
    return (
        (
            can_reach_second_part_of_eldin_volcano(state, player)
            & has_digging_mitts(state, player)
        )
        | (
            can_access_bokoblin_base(state, player)
            & has_mogma_mitts(state, player)
            & state.has("Clawshots", player)
            & (
                state.has("Bomb Bag", player)
                | can_bypass_boko_base_watchtower(state, player)
                & state.has("Whip", player)
            )
        )
    ) & has_goddess_sword(state, player)


# Mogma Turf
def can_access_mogma_turf(state: CollectionState, player: int) -> bool:
    return can_access_eldin_volcano(state, player)


def can_reach_second_part_of_mogma_turf(state: CollectionState, player: int) -> bool:
    return can_access_mogma_turf(state, player) & has_digging_mitts(state, player)


def goddess_cube_in_mogma_turf(state: CollectionState, player: int) -> bool:
    return can_access_mogma_turf(state, player) & has_goddess_sword(state, player)


# Volcano Summit
def can_access_volcano_summit(state: CollectionState, player: int) -> bool:
    return can_reach_second_part_of_eldin_volcano(state, player) & state.has(
        "Fireshield Earrings", player
    )


def can_pass_volcano_summit_first_frog(state: CollectionState, player: int) -> bool:
    return can_access_volcano_summit(state, player) & has_bottle(state, player)


def can_pass_volcano_summit_second_frog(state: CollectionState, player: int) -> bool:
    return can_pass_volcano_summit_first_frog(state, player) & state.has(
        "Clawshots", player
    )


def can_reach_dungeon_entrance_in_volcano_summit(
    state: CollectionState, player: int
) -> bool:
    return can_pass_volcano_summit_second_frog(state, player)


def goddess_cube_inside_volcano_summit(state: CollectionState, player: int) -> bool:
    return (
        can_access_volcano_summit(state, player)
        & (
            upgraded_skyward_strike(state, player)
            | (
                can_access_bokoblin_base(state, player)
                & has_mogma_mitts(state, player)
                & state.has("Clawshots", player)
                & state.has("Bomb Bag", player)
                & state.has("Fireshield Earrings", player)
            )
        )
        & has_goddess_sword(state, player)
    )


def goddess_cube_in_summit_waterfall(state: CollectionState, player: int) -> bool:
    return can_access_volcano_summit(state, player) & has_goddess_sword(state, player)


def goddess_cube_near_fire_sanctuary_entrance(
    state: CollectionState, player: int
) -> bool:
    return (
        can_pass_volcano_summit_second_frog(state, player)
        & state.has("Clawshots", player)
        & has_goddess_sword(state, player)
    )


# Boko Base
def can_access_bokoblin_base(state: CollectionState, player: int) -> bool:
    return can_access_eldin_volcano(state, player)


def can_bypass_boko_base_watchtower(state: CollectionState, player: int) -> bool:
    return (
        state.has("Bomb Bag", player)
        | has_slingshot(state, player)
        | has_bow(state, player)
    )


### LANAYRU


# Lanayru Mine
def can_access_lanayru_mine(state: CollectionState, player: int) -> bool:
    return state.has("Amber Tablet", player)


def can_reach_second_part_of_lanayru_mine(state: CollectionState, player: int) -> bool:
    return (
        can_access_lanayru_mine(state, player)
        & can_hit_timeshift_stone(state, player)
        & (
            state.has("Bomb Bag", player)
            | has_hook_beetle(state, player)
            | False  # (unlocked_endurance_potion(state, player) & has_bottle(state, player))
        )  # Line above is recursive, AP doesn't like that :c
    )


def goddess_cube_at_lanayru_mine_entrance(state: CollectionState, player: int) -> bool:
    return can_access_lanayru_mine(state, player) & has_goddess_sword(state, player)


# Lanayru Desert
def can_access_lanayru_desert(state: CollectionState, player: int) -> bool:
    return can_reach_second_part_of_lanayru_mine(state, player) | (
        can_access_lanayru_mine(state, player) & state.has("Clawshots", player)
    )


def can_retrieve_party_wheel(state: CollectionState, player: int) -> bool:
    return (
        can_access_lanayru_desert(state, player)
        & state.has("Scrapper", player)
        & state.has("Bomb Bag", player)
    )


def can_reach_temple_of_time(state: CollectionState, player: int) -> bool:
    return can_access_lanayru_desert(state, player) & (
        state.has("Clawshots", player) | has_hook_beetle(state, player)
    )


def can_reach_second_part_of_lanayru_desert(
    state: CollectionState, player: int
) -> bool:
    return can_access_lanayru_desert(state, player) & (
        state.has("Clawshots", player)
        | can_reach_temple_of_time(state, player)
        | state._ss_option_lmf_open(player)
    )


def can_activate_nodes(state: CollectionState, player: int) -> bool:
    return (
        can_reach_second_part_of_lanayru_desert(state, player)
        & state.has("Bomb Bag", player)
        & has_practice_sword(state, player)
        & can_defeat_ampilus(state, player)
        & has_hook_beetle(state, player)
    )


def can_raise_lmf(state: CollectionState, player: int) -> bool:
    return can_access_lanayru_desert(state, player) & (
        state._ss_option_lmf_open(player)
        | (
            state._ss_option_lmf_main_node(player)
            & can_reach_second_part_of_lanayru_desert(state, player)
        )
        | can_activate_nodes(state, player)
    )


def can_open_trial_gate_in_lanayru_desert(state: CollectionState, player: int) -> bool:
    return (
        can_reach_second_part_of_lanayru_desert(state, player)
        & state.has("Nayru's Wisdom", player)
        & state.has("Goddess's Harp", player)
    )


def can_reach_dungeon_entrance_in_lanayru_desert(
    state: CollectionState, player: int
) -> bool:
    return can_raise_lmf(state, player)


def goddess_cube_near_caged_robot(state: CollectionState, player: int) -> bool:
    return (
        can_access_lanayru_desert(state, player)
        & state.has("Clawshots", player)
        & has_goddess_sword(state, player)
    )


def goddess_cube_in_secret_passageway(state: CollectionState, player: int) -> bool:
    return (
        can_reach_second_part_of_lanayru_desert(state, player)
        & state.has("Clawshots", player)
        & state.has("Bomb Bag", player)
        & has_goddess_sword(state, player)
    )


def goddess_cube_in_sand_oasis(state: CollectionState, player: int) -> bool:
    return can_reach_temple_of_time(state, player) & has_goddess_sword(state, player)


def goddess_cube_at_ride_near_temple_of_time(
    state: CollectionState, player: int
) -> bool:
    return can_reach_temple_of_time(state, player) & has_goddess_sword(state, player)


# Lanayru Caves
def can_access_lanayru_caves(state: CollectionState, player: int) -> bool:
    return can_access_lanayru_mine(state, player) & state.has("Clawshots", player)


# Lanayru Gorge
def can_access_lanayru_gorge(state: CollectionState, player: int) -> bool:
    return can_access_lanayru_caves(state, player)


def goddess_cube_in_lanayru_gorge(state: CollectionState, player: int) -> bool:
    return (
        can_access_lanayru_gorge(state, player)
        & can_hit_timeshift_stone(state, player)
        & has_goddess_sword(state, player)
    )


# Lanayru Sand Sea
def can_access_lanayru_sand_sea(state: CollectionState, player: int) -> bool:
    return (
        can_access_lanayru_caves(state, player)
        & state.has("Lanayru Caves Small Key", player)
        & state.has("Clawshots", player)
    )


def can_reach_dungeon_entrance_in_lanayru_sand_sea(
    state: CollectionState, player: int
) -> bool:
    return (
        can_access_lanayru_sand_sea(state, player)
        & state.has("Sea Chart", player)
        & has_practice_sword(state, player)
    )


def goddess_cube_in_ancient_harbour(state: CollectionState, player: int) -> bool:
    return (
        can_access_lanayru_sand_sea(state, player)
        & state.has("Clawshots", player)
        & has_goddess_sword(state, player)
    )


def goddess_cube_in_skippers_retreat(state: CollectionState, player: int) -> bool:
    return (
        can_access_lanayru_sand_sea(state, player)
        & (state.has("Bomb Bag", player) | has_hook_beetle(state, player))
        & state.has("Clawshots", player)
        & has_goddess_sword(state, player)
    )


def goddess_cube_in_pirate_stronghold(state: CollectionState, player: int) -> bool:
    return (
        can_access_lanayru_sand_sea(state, player)
        & can_defeat_beamos(state, player)
        & can_defeat_armos(state, player)
        & has_goddess_sword(state, player)
    )


# Ancient Flowers
def lanayru_mine_ancient_flower_farming(state: CollectionState, player: int) -> bool:
    return can_access_lanayru_mine(state, player) & can_hit_timeshift_stone(
        state, player
    )


def lanayru_desert_ancient_flower_farming(state: CollectionState, player: int) -> bool:
    return can_access_lanayru_desert(state, player) & state.has("Bomb Bag", player)


def lanayru_desert_ancient_flower_farming_near_main_node(
    state: CollectionState, player: int
) -> bool:
    return can_reach_second_part_of_lanayru_desert(state, player) & (
        has_hook_beetle(state, player) | state.has("Bomb Bag", player)
    )


def pirate_stronghold_ancient_flower_farming(
    state: CollectionState, player: int
) -> bool:
    return can_access_lanayru_sand_sea(state, player)


def lanayru_gorge_ancient_flower_farming(state: CollectionState, player: int) -> bool:
    return (
        can_access_lanayru_gorge(state, player)
        & state.has("Gust Bellows", player)
        & can_hit_timeshift_stone(state, player)
    )


### DUNGEONS

# Skyview


def can_reach_SV_second_room(state: CollectionState, player: int) -> bool:
    return (
        state.can_reach_region("Skyview", player)
        & can_cut_trees(state, player)
        & (
            state.has("Water Dragon's Scale", player)  # Skyview 2
            | state.has("Bomb Bag", player)  # Bomb the barricade
            | (
                distance_activator(state, player) & has_practice_sword(state, player)
            )  # One eye room
        )
    )


def can_reach_SV_main_room(state: CollectionState, player: int) -> bool:
    return (
        can_reach_SV_second_room(state, player)
        & state.has("Skyview Small Key", player)
        & (
            distance_activator(state, player)
            | has_goddess_sword(state, player)  # Only have to raise water level once
            | state.has(
                "Whip", player
            )  # Whip & goddess sword can hit vines in left room
        )
    )


def can_reach_SV_boss_door(state: CollectionState, player: int) -> bool:
    return (
        can_reach_SV_second_room(state, player)
        & state.has("Skyview Small Key", player, 2)
        & (
            has_practice_sword(state, player) | state.has("Bomb Bag", player)
        )  # Staldra fight
        & (
            has_goddess_sword(state, player)  # Hanging Skulltula
            | has_beetle(state, player)  # Break web with beetle | bow
            | has_bow(state, player)  # Knock away with skyward strike | bombs
            | state.has("Water Dragon's Scale", player)  # Doesn't exist in skyview 2
            | state.has("Bomb Bag", player)
        )
        & (
            upgraded_skyward_strike(state, player)
            | has_hook_beetle(state, player)
            | has_bow(state, player)  # Archers in last room in skyview 2
        )
    )


def can_beat_ghirahim_1(state: CollectionState, player: int) -> bool:
    return (
        can_reach_SV_boss_door(state, player)
        & state.has("Skyview Boss Key", player)
        & has_practice_sword(state, player)
    )


def can_beat_SV(state: CollectionState, player: int) -> bool:
    return can_beat_ghirahim_1(state, player) & has_goddess_sword(state, player)


def goddess_cube_in_skyview_spring(state: CollectionState, player: int) -> bool:
    return can_beat_ghirahim_1(state, player) & has_goddess_sword(state, player)


# Earth Temple
def can_lower_ET_drawbridge(state: CollectionState, player: int) -> bool:
    return has_bow(state, player) | has_beetle(state, player)


def can_dislodge_ET_boulder(state: CollectionState, player: int) -> bool:
    return (
        has_slingshot(state, player)
        | has_bow(state, player)
        | upgraded_skyward_strike(state, player)
        | state.has("Clawshots", player)
        | (has_beetle(state, player) & can_defeat_lezalfos(state, player))
    )


def can_reach_ET_main_room(state: CollectionState, player: int) -> bool:
    return (
        state.can_reach_region("Earth Temple", player)
        & can_lower_ET_drawbridge(state, player)
        & can_dislodge_ET_boulder(state, player)
    )


def can_pass_ET_boulder_section(state: CollectionState, player: int) -> bool:
    return (
        can_reach_ET_main_room(state, player)
        & has_beetle(state, player)
        & (has_hook_beetle(state, player) | state.has("Bomb Bag", player))
    )


def can_reach_ET_boss_door(state: CollectionState, player: int) -> bool:
    return can_pass_ET_boulder_section(state, player) & (
        has_hook_beetle(state, player)
        | (has_digging_mitts(state, player) & state.has("Bomb Bag", player))
    )


def can_beat_scaldera(state: CollectionState, player: int) -> bool:
    return (
        can_reach_ET_boss_door(state, player)
        & state.has("Earth Temple Boss Key", player)
        & state.has("Bomb Bag", player)
        & has_practice_sword(state, player)
    )


def can_beat_ET(state: CollectionState, player: int) -> bool:
    return can_beat_scaldera(state, player) & has_goddess_sword(state, player)


# Lanayru Mining Facility
def can_reach_LMF_second_room(state: CollectionState, player: int) -> bool:
    return state.can_reach_region(
        "Lanayru Mining Facility", player
    ) & has_hook_beetle(state, player)


def can_reach_LMF_key_locked_room_in_past(state: CollectionState, player: int) -> bool:
    return (
        can_reach_LMF_second_room(state, player)
        & state.has("Lanayru Mining Facility Small Key", player)
        & has_hook_beetle(state, player)
    )


def can_reach_LMF_hub_room(state: CollectionState, player: int) -> bool:
    return can_reach_LMF_second_room(state, player)


def can_reach_LMF_hub_room_west(state: CollectionState, player: int) -> bool:
    return (
        can_reach_LMF_second_room(state, player)
        & state.has("Gust Bellows", player)
        & can_defeat_beamos(state, player)
        & can_defeat_armos(state, player)
        & (
            has_goddess_sword(state, player)
            | has_slingshot(state, player)
            | has_bow(state, player)
            | state.has("Whip", player)  # to hit timeshift stone
        )
    )


def can_reach_LMF_boss_door(state: CollectionState, player: int) -> bool:
    return can_reach_LMF_hub_room_west(state, player) & state.has(
        "Gust Bellows", player
    )


def can_pass_LMF_boss_key_room(state: CollectionState, player: int) -> bool:
    return (
        can_reach_LMF_boss_door(state, player)
        & state.has("Gust Bellows", player)
        & state.has("Bomb Bag", player)  # Bombs uncover statues
        & can_defeat_beamos(state, player)
        & can_defeat_armos(state, player)
        & (
            has_practice_sword(state, player) | distance_activator(state, player)
        )  # Hit crystals
    )


def can_beat_moldarach(state: CollectionState, player: int) -> bool:
    return (
        can_reach_LMF_boss_door(state, player)
        & state.has("Lanayru Mining Facility Boss Key", player)
        & can_defeat_moldarachs(state, player)
    )


def can_beat_LMF(state: CollectionState, player: int) -> bool:
    return can_beat_moldarach(state, player) & (
        has_beetle(state, player) | has_bow(state, player)
    )  # To hit the timeshift stone


# Ancient Cistern
def can_enter_AC_statue(state: CollectionState, player: int) -> bool:
    return state.can_reach_region("Ancient Cistern", player) & (
        state.has("Ancient Cistern Small Key", player, 2)
        | can_lower_AC_statue(state, player)
    )


def can_lower_AC_statue(state: CollectionState, player: int) -> bool:
    return can_reach_AC_vines(state, player) & state.has("Whip", player)


def can_pass_AC_waterfall(state: CollectionState, player: int) -> bool:
    return (
        state.can_reach_region("Ancient Cistern", player)
        & state.has("Water Dragon's Scale", player)
        & state.has("Whip", player)
    )


def can_reach_AC_boko_key_door(state: CollectionState, player: int) -> bool:
    return (
        can_pass_AC_waterfall(state, player)
        & state.has("Whip", player)
        & state.has("Water Dragon's Scale", player)
        & (has_beetle(state, player) | has_bow(state, player))
    )


def can_reach_AC_vines(state: CollectionState, player: int) -> bool:
    return state.can_reach_region("Ancient Cistern", player) & (
        (state.has("Clawshots", player) & state.has("Whip", player))
        | (
            can_reach_AC_boko_key_door(state, player)
            & state.has("Ancient Cistern Small Key", player, 2)
        )
    )


def can_reach_AC_thread(state: CollectionState, player: int) -> bool:
    return can_lower_AC_statue(state, player) & (
        state.has("Clawshots", player) | has_hook_beetle(state, player)
    )


def can_reach_AC_boss_door(state: CollectionState, player: int) -> bool:
    return (  # This means can reach the very TOP of the dungeon after the boss key is put in
        can_enter_AC_statue(state, player)
        & state.has("Whip", player)  # Whip valves
        & state.has("Ancient Cistern Boss Key", player)
    )


def can_beat_koloktos(state: CollectionState, player: int) -> bool:
    return (
        can_reach_AC_boss_door(state, player)
        & state.has("Whip", player)
        & (
            has_practice_sword(state, player)
            | has_bow(state, player)
            | state.has("Bomb Bag", player)
        )
    )


def can_beat_AC(state: CollectionState, player: int) -> bool:
    return can_beat_koloktos(state, player) & has_goddess_sword(state, player)


# Sandship
def can_change_SSH_temporality(state: CollectionState, player: int) -> bool:
    return (
        state.can_reach_region("Sandship", player)
        & has_bow(state, player)
        & (
            has_practice_sword(state, player)
            | state.has("Sandship Small Key", player, 2)
        )
    )


def can_reach_SSH_4_door_corridor(state: CollectionState, player: int) -> bool:
    return state.can_reach_region("Sandship", player) & (
        can_change_SSH_temporality(state, player)
        | has_goddess_sword(state, player)
        | has_bow(state, player)
        | has_slingshot(state, player)
        | state.has("Bomb Bag", player)
    )


def can_reach_SSH_brig(state: CollectionState, player: int) -> bool:
    return (
        can_change_SSH_temporality(state, player)
        & has_practice_sword(state, player)
        & has_bow(state, player)
        & state.has("Whip", player)
    )


def can_reach_SSH_boss_door(state: CollectionState, player: int) -> bool:
    return can_change_SSH_temporality(state, player)


def can_beat_tentalus(state: CollectionState, player: int) -> bool:
    return (
        can_reach_SSH_boss_door(state, player)
        & state.has("Sandship Boss Key", player)
        & has_bow(state, player)
    )


def can_beat_SSH(state: CollectionState, player: int) -> bool:
    return can_beat_tentalus(state, player) & has_goddess_sword(state, player)


# Fire Sanctuary
def can_reach_FS_first_magmanos_room(state: CollectionState, player: int) -> bool:
    return (
        state.can_reach_region("Fire Sanctuary", player)
        & state.has("Fire Sanctuary Small Key", player)
        & (distance_activator(state, player) | state.has("Bomb Bag", player))
    )


def can_reach_FS_water_pod_room(state: CollectionState, player: int) -> bool:
    return (
        can_reach_FS_first_magmanos_room(state, player)
        & can_defeat_lezalfos(state, player)
        & has_hook_beetle(state, player)
        & state.has("Fire Sanctuary Small Key", player, 2)
    )


def can_reach_FS_second_bridge(state: CollectionState, player: int) -> bool:
    return (
        can_reach_FS_water_pod_room(state, player)
        & has_practice_sword(state, player)
        & has_mogma_mitts(state, player)
        & state.has("Gust Bellows", player)
    )


def can_reach_FS_plats_room(state: CollectionState, player: int) -> bool:
    return (
        can_reach_FS_water_pod_room(state, player)
        & has_practice_sword(state, player)
        & has_mogma_mitts(state, player)
        & state.has("Fire Sanctuary Small Key", player, 3)
        & (
            distance_activator(state, player) | state.has("Bomb Bag", player)
        )  # for water pod
    )


def can_reach_FS_boss_door(state: CollectionState, player: int) -> bool:
    return can_reach_FS_plats_room(state, player) & has_mogma_mitts(state, player)


def can_reach_top_of_FS_staircase(state: CollectionState, player: int) -> bool:
    return (
        can_reach_FS_boss_door(state, player)
        & can_defeat_lezalfos(state, player)
        & state.has("Clawshots", player)
    )


def can_beat_ghirahim_2(state: CollectionState, player: int) -> bool:
    return (
        can_reach_FS_boss_door(state, player)
        & state.has("Fire Sanctuary Boss Key", player)
        & has_practice_sword(state, player)
    )


def can_beat_FS(state: CollectionState, player: int) -> bool:
    return can_beat_ghirahim_2(state, player) & has_goddess_sword(state, player)


# Sky Keep
def can_pass_SK_sv_room(state: CollectionState, player: int) -> bool:
    return (
        state.can_reach_region("Sky Keep", player)
        & (has_beetle(state, player) | has_bow(state, player))
        & state.has("Whip", player)
        & state.has("Clawshots", player)
        & (
            state.has("Bomb Bag", player)
            | has_hook_beetle(state, player)
            | has_bow(state, player)
        )
        & state.has("Gust Bellows", player)
    )


def can_pass_SK_lmf_room(state: CollectionState, player: int) -> bool:
    return (
        can_pass_SK_sv_room(state, player)
        & has_bow(state, player)
        & state.has("Gust Bellows", player)
    )


def can_pass_SK_et_room(state: CollectionState, player: int) -> bool:
    return (
        can_pass_SK_lmf_room(state, player)
        & has_mogma_mitts(state, player)
        & has_hook_beetle(state, player)
        & state.has("Bomb Bag", player)
        & upgraded_skyward_strike(state, player)
    )


def can_pass_SK_mini_boss_room(state: CollectionState, player: int) -> bool:
    return (
        (can_pass_SK_et_room(state, player) | can_pass_SK_fs_room(state, player))
        & has_practice_sword(state, player)
        & state.has("Clawshots", player)
    )


def can_pass_SK_ac_room(state: CollectionState, player: int) -> bool:
    return can_pass_SK_lmf_room(state, player)


def can_get_triforce_of_courage(state: CollectionState, player: int) -> bool:
    return (
        can_pass_SK_ac_room(state, player)
        & state.has("Sky Keep Small Key", player)
        & can_defeat_moblins(state, player)
        & can_defeat_bokoblins(state, player)
        & can_defeat_stalfos(state, player)
        & has_bow(state, player)
        & can_defeat_cursed_bokoblins(state, player)
        & can_defeat_stalmaster(state, player)
    )


def can_pass_SK_fs_room(state: CollectionState, player: int) -> bool:
    return (
        can_pass_SK_ac_room(state, player)
        & has_beetle(state, player)
        & state.has("Clawshots", player)
    )


def can_get_triforce_of_power(state: CollectionState, player: int) -> bool:
    return can_pass_SK_fs_room(state, player)


def can_pass_SK_ssh_room(state: CollectionState, player: int) -> bool:
    return (
        can_pass_SK_fs_room(state, player)
        & has_bow(state, player)
        & state.has("Clawshots", player)
    )


def can_get_triforce_of_wisdom(state: CollectionState, player: int) -> bool:
    return can_pass_SK_ssh_room(state, player)


def can_beat_SK(state: CollectionState, player: int) -> bool:
    return (
        state.can_reach_region("Sky Keep", player)
        & can_get_triforce_of_courage(state, player)
        & can_get_triforce_of_power(state, player)
        & can_get_triforce_of_wisdom(state, player)
    )


# Silent Realms
def can_access_skyloft_silent_realm(state: CollectionState, player: int) -> bool:
    return state.can_reach_region("Skyloft Silent Realm", player)


def can_access_faron_silent_realm(state: CollectionState, player: int) -> bool:
    return state.can_reach_region("Faron Silent Realm", player)


def can_access_eldin_silent_realm(state: CollectionState, player: int) -> bool:
    return state.can_reach_region("Eldin Silent Realm", player)


def can_access_lanayru_silent_realm(state: CollectionState, player: int) -> bool:
    return state.can_reach_region("Lanayru Silent Realm", player)
