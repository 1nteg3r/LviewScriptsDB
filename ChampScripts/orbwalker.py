import time
import json
import random
import urllib3
import json
import urllib
import ssl

from winstealer import *
from evade import *
from commons.items import *
from commons.skills import *
from commons.utils import *
from commons.targeting import *
from commons.timer import Timer
from API.summoner import *

winstealer_script_info = {
    "script": "tefan's Orbwalker",
    "author": "tefan",
    "description": "Life's orbwalker but optimized by tefan",
}


ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Globalsdm

lasthit_key = 45
harass_key = 46
orbwalk_key = 57
laneclear_key = 47

draw_killable_minion = False
draw_killable_minion_fade = False

click_speed = 0
ping = 0

lowArmor = False
lowHealth = False
lowMr = False
autoPriority = True

attacked = False
resetted = False

attackTimer = Timer()
moveTimer = Timer()
humanizer = Timer()
last = 0
atk_speed = 0


def winstealer_load_cfg(cfg):
    global orbwalk_key, lasthit_key, harass_key, laneclear_key
    global click_speed, ping, lowArmor, lowHealth, lowMr, autoPriority
    global draw_killable_minion, draw_killable_minion_fade

    lasthit_key = cfg.get_int("lasthit_key", 46)
    harass_key = cfg.get_int("harass_key", 45)
    orbwalk_key = cfg.get_int("key_orbwalk", 57)
    laneclear_key = cfg.get_int("laneclear_key", 47)
    draw_killable_minion = cfg.get_bool("draw_killable_minion", False)
    draw_killable_minion_fade = cfg.get_bool(
        "draw_killable_minion_fade", False)
    click_speed = cfg.get_int("click_speed", 7)
    ping = cfg.get_int("ping", 20)

    autoPriority = cfg.get_bool("autoPriority", True)
    lowArmor = cfg.get_bool("lowArmor", False)
    lowHealth = cfg.get_bool("lowHealth", False)
    lowMr = cfg.get_bool("lowMr", False)


def winstealer_save_cfg(cfg):
    global orbwalk_key, harass_key, lasthit_key, laneclear_key
    global click_speed, ping
    global draw_killable_minion, draw_killable_minion_fade
    global lowArmor, lowHealth, lowMr, autoPriority

    cfg.set_int("lasthit_key", lasthit_key)
    cfg.set_int("harass_key", harass_key)
    cfg.set_int("laneclear_key", laneclear_key)
    cfg.set_int("key_orbwalk", orbwalk_key)
    cfg.set_bool("draw_killable_minion", draw_killable_minion)
    cfg.set_bool("draw_killable_minion_fade", draw_killable_minion_fade)
    cfg.set_float("click_speed", click_speed)
    cfg.set_float("ping", ping)

    cfg.set_bool("autoPriority", autoPriority)
    cfg.set_bool("lowArmor", lowArmor)
    cfg.set_bool("lowHealth", lowHealth)
    cfg.set_bool("lowMr", lowMr)


def winstealer_draw_settings(game, ui):
    global orbwalk_key, harass_key, lasthit_key, laneclear_key
    global click_speed, ping
    global draw_killable_minion, draw_killable_minion_fade
    global lowArmor, lowHealth, lowMr, autoPriority
    ui.text("v 1.0")
    if ui.treenode("Key settings"):
        lasthit_key = ui.keyselect("Last hit key", lasthit_key)
        harass_key = ui.keyselect("Harass key", harass_key)
        laneclear_key = ui.keyselect("Laneclear key", laneclear_key)
        orbwalk_key = ui.keyselect("Combo key", orbwalk_key)
        ui.treepop()

    autoPriority = ui.checkbox("Auto Priority", autoPriority)
    lowArmor = ui.checkbox("Target Lowest Armor", lowArmor)
    lowHealth = ui.checkbox("Target Lowest Health", lowHealth)
    lowMr = ui.checkbox("Target Lowest Magic resist", lowMr)

    ui.text("----------------------------------------------------------")
    click_speed = ui.sliderint("Click speed", int(click_speed), 0, 1000)
    ping = ui.sliderint("Your Ping", int(ping), 0, 100)
    draw_killable_minion = ui.checkbox(
        "Draw killable minions", draw_killable_minion)
    draw_killable_minion_fade = ui.checkbox(
        "Draw killable minions fade effect", draw_killable_minion_fade
    )

def last_hit_minions(game, atk_range=0):
    target = None
    if atk_range == 0:
        atk_range = game.player.atkRange + game.player.gameplay_radius + 25
    for minion in game.minions:
        if (
            not minion.is_alive
            or not minion.is_visible
            or not minion.isTargetable
            or minion.is_ally_to(game.player)
            or game.player.pos.distance(minion.pos) >= atk_range
        ):
            continue
        if is_last_hitable(game, game.player, minion):
            target = minion
    return target
    

def reset_auto(game, player):
    global resetted
    if not resetted:
        for buff in game.player.buffs:
            if buff.name == "LucianPassiveBuff":
                return True
            if buff.name == "vaynetumblebonus":
                return True
    return False
# The buffs get updated pretty slowly so the reset_auto function currently makes us spam attack for a bit. To fix that we can 

def draw_killable_minions(game, fade_effect):
    minion = game.GetBestTarget(
        UnitTag.Unit_Minion_Lane, game.player.atkRange + game.player.gameplay_radius
    )
    if minion:
        if fade_effect:
            value = 255 - (minion.health * 2)
            game.draw_circle_world(
                minion.pos,
                minion.gameplay_radius * 2,
                100,
                1,
                Color(0.0, 1.0, 1.0 - value, 1.0),
            )

        if not fade_effect:
            game.draw_circle_world(
                minion.pos, minion.gameplay_radius * 2, 100, 2, Color.ORANGE
            )

def is_immobile(unit) -> bool:
    return any(
        buff.type == 5
        or buff.type == 11
        or buff.type == 29
        or buff.type == 24
        or buff.name == 10
        for buff in unit.buffs
    )

def is_last_hitable(game, player, enemy):
    missile_speed = player.basic_missile_speed + 1

    damageCalc.damage_type = damageType
    damageCalc.base_damage = 0

    hit_dmg = (
        damageCalc.calculate_damage(game, player, enemy)
        + items.get_onhit_physical(player, enemy)
        + items.get_onhit_magical(player, enemy)
    )

    hp = enemy.health + enemy.armour + (enemy.health_regen)
    t_until_basic_hits = game.distance(player, enemy) / missile_speed

    for missile in game.missiles:
        if missile.dest_id == enemy.id:
            src = game.get_obj_by_id(missile.src_id)
            if src:
                t_until_missile_hits = game.distance(missile, enemy) / (
                    missile.speed + 1
                )

                if t_until_missile_hits < t_until_basic_hits:
                    hp -= src.base_atk

    return hp - hit_dmg <= 0



def get_best_auto_priority(game, atk_range=0):
    armor = 999999999
    health = 999999999
    mr = 999999999
    target = None

    if atk_range == 0:
        atk_range = game.player.atkRange - 1.5 + game.player.gameplay_radius

    for champ in game.champs:

        if champ.name in clones and champ.R.name == champ.D.name:
            continue

        if (not champ.is_alive
                or not champ.is_visible
                or not champ.isTargetable
                or champ.is_ally_to(game.player)
                or game.player.pos.distance(champ.pos) >= atk_range
                ):
            continue

        if armor >= champ.armour and health >= champ.health and mr >= champ.magic_resist:
            armor = champ.armour
            health = champ.health
            mr = champ.magic_resist
            target = champ

        if is_immobile(champ):
            target = champ

        if is_last_hitable(game, game.player, champ):
            target = champ

    if target:
        return target

def castingQxer(player):
    return True in ["xeratharcanopulsechargeup" in buff.name.lower() for buff in player.buffs]

def castingRxer(player):
    return True in ["xerathrshots" in buff.name.lower() for buff in player.buffs]

def get_best_targets_low_armour(game, atk_range=0):
    num = 999999999
    target = None
    if atk_range == 0:
        atk_range = game.player.atkRange - 1.5 + game.player.gameplay_radius
    for champ in game.champs:
        if champ.name in clones and champ.R.name == champ.D.name:
            continue
        if (
            not champ.is_alive
            or not champ.is_visible
            or not champ.isTargetable
            or champ.is_ally_to(game.player)
            or game.player.pos.distance(champ.pos) >= atk_range
        ):
            continue
        if num >= champ.armour:
            num = champ.armour
            target = champ
        if is_immobile(champ):
            target = champ
        if is_last_hitable(game, game.player, champ):
            target = champ
    if target:
        return target


def get_best_targets_low_health(game, atk_range=0):
    num = 999999999
    target = None
    if atk_range == 0:
        atk_range = game.player.atkRange -1.5 + game.player.gameplay_radius
    for champ in game.champs:
        if champ.name in clones and champ.R.name == champ.D.name:
            continue
        if (
            not champ.is_alive
            or not champ.is_visible
            or not champ.isTargetable
            or champ.is_ally_to(game.player)
            or game.player.pos.distance(champ.pos) >= atk_range
        ):
            continue
        if num >= champ.health:
            num = champ.health
            target = champ
        if is_immobile(champ):
            target = champ
        if is_last_hitable(game, game.player, champ):
            target = champ
    if target:
        return target


def get_best_targets_low_mr(game, atk_range=0):
    num = 999999999
    target = None
    if atk_range == 0:
        atk_range = game.player.atkRange + game.player.gameplay_radius
    for champ in game.champs:
        if champ.name in clones and champ.R.name == champ.D.name:
            continue
        if (
            not champ.is_alive
            or not champ.is_visible
            or not champ.isTargetable
            or champ.is_ally_to(game.player)
            or game.player.pos.distance(champ.pos) >= atk_range
        ):
            continue

        if num >= champ.magic_resist:
            num = champ.magic_resist
            target = champ
        if is_immobile(champ):
            target = champ
        if is_last_hitable(game, game.player, champ):
            target = champ
    if target:
        return target


def get_player_stats():
    response = urllib.request.urlopen(
        "https://127.0.0.1:2999/liveclientdata/activeplayer").read()
    stats = json.loads(response)
    return stats

def attack(game, target, c_atk_time, b_windup_time):
    global attacked
    game.click_at(False, game.world_to_screen(target.pos))
    attacked = True
    attackTimer.SetTimer(c_atk_time)
    moveTimer.SetTimer(b_windup_time)


def orbwalk(game, target, c_atk_time, b_windup_time):
    global attacked, resetted
    if reset_auto(game, game.player) and target:
        attack(game, target, c_atk_time, b_windup_time)
        resetted = True
    elif attackTimer.Timer() and target and not getBuff(game.player, "JhinPassiveReload"):
        attack(game, target, c_atk_time, b_windup_time)
        resetted = False
    else:
        if humanizer.Timer():
            if moveTimer.Timer():
                game.press_right_click()
                attacked = False
                resetted = False
                humanizer.SetTimer(click_speed / 1000)
                


def winstealer_update(game, ui):
    global orbwalk_key, lasthit_key, laneclear_key, harass_key
    global click_speed, ping
    global draw_killable_minion, draw_killable_minion_fade
    global attackTimer, moveTimer, humanizer, attacked
    global last
    global lowArmor, lowHealth, lowMr, autoPriority

    if draw_killable_minion_fade:
        draw_killable_minions(game, True)
    elif draw_killable_minion:
        draw_killable_minions(game, False)

    if (
        game.player.is_visible
        and not game.isChatOpen
    ):
        if game.player.name == "graves":
            atk_speed = get_player_stats()["championStats"]["attackSpeed"]+1.2
        else:
            atk_speed = get_player_stats()["championStats"]["attackSpeed"]
        c_atk_time = max(1.0 / atk_speed, ping / 100)
        b_windup_time = (1.0/atk_speed) * game.player.basic_atk_windup


        # Harass
        if game.is_key_down(harass_key):
            # Auto priority
            if autoPriority:
                target = get_best_auto_priority(
                    game, game.player.atkRange + game.player.gameplay_radius)
                orbwalk(game, target, c_atk_time, b_windup_time)

            # Low Armor
            elif lowArmor:
                target = get_best_targets_low_armour(
                    game, game.player.atkRange + game.player.gameplay_radius)
                orbwalk(game, target, c_atk_time, b_windup_time)

            # Low Health
            elif lowHealth:
                target = game.GetBestTarget(
                    UnitTag.Unit_Champion,
                    game.player.atkRange + game.player.gameplay_radius,
                )
                orbwalk(game, target, c_atk_time, b_windup_time)

            # Low MR
            elif lowMr:
                target = get_best_targets_low_mr(
                    game, game.player.atkRange + game.player.gameplay_radius)
                orbwalk(game, target, c_atk_time, b_windup_time)

        # Orbwalker
        if game.is_key_down(orbwalk_key) :
            # Auto Priority
            if autoPriority:
                target = get_best_auto_priority(
                    game, game.player.atkRange + game.player.gameplay_radius)
                orbwalk(game, target, c_atk_time, b_windup_time)

            # Low Armor
            elif lowArmor:
                target = get_best_targets_low_armour(
                    game, game.player.atkRange + game.player.gameplay_radius)
                orbwalk(game, target, c_atk_time, b_windup_time)

            # Low Health
            elif lowHealth:
                target = game.GetBestTarget(
                    UnitTag.Unit_Champion,
                    game.player.atkRange + game.player.gameplay_radius,
                )
                orbwalk(game, target, c_atk_time, b_windup_time)

            # Low MR
            elif lowMr:
                target = get_best_targets_low_mr(
                    game, game.player.atkRange + game.player.gameplay_radius)
                orbwalk(game, target, c_atk_time, b_windup_time)

        # Lasthit
        if game.is_key_down(lasthit_key) :
            target = last_hit_minions(game)
            # targetLarge=Largeminion(game)
            # if attackTimer.Timer() and targetLarge:
            #     game.click_at(False, game.world_to_screen(targetLarge.pos))
            #     attackTimer.SetTimer(c_atk_time)
            #     moveTimer.SetTimer(b_windup_time)
            orbwalk(game, target, c_atk_time, b_windup_time)

        # Laneclear
        if game.is_key_down(laneclear_key) :
            target = (
                game.GetBestTarget(
                    UnitTag.Unit_Structure_Turret,
                    game.player.atkRange + game.player.gameplay_radius,
                )
                or game.GetBestTarget(
                    UnitTag.Unit_Minion_Lane,
                    game.player.atkRange + game.player.gameplay_radius,
                )
                or game.GetBestTarget(
                    UnitTag.Unit_Monster,
                    game.player.atkRange + game.player.gameplay_radius,
                )
            )
            orbwalk(game, target, c_atk_time, b_windup_time)


