from lview import *
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import *
import json, time, math

lview_script_info = {
    "script": "Samira",
    "author": "tefan",
    "description": "4 Samira",
    "target_champ": "samira",
}

combo_key = 57
harass_key = 45
laneclear_key = 47

use_q_in_combo = True
use_w_in_combo = True
use_e_in_combo = True
use_r_in_combo = True

lane_clear_with_q = False
lane_clear_with_q2 = False

steal_kill_with_q = False
steal_kill_with_e = False

draw_q_range = False
draw_w_range = False
draw_e_range = False
draw_r_range = False

use_w_on_evade = False
use_e_on_evade = False

LastR = 0

q = {"Range": 900.0, "MinRange": 325.0, "Mana": 30}
w = {"Range": 325.0, "Mana": 60}
e = {"Range": 550.0, "Mana": 40}
r = {"Range": 550.0}

def lview_load_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global combo_key, harass_key, laneclear_key
    global lane_clear_with_q, lane_clear_with_q2
    global use_w_on_evade, use_e_on_evade
    global steal_kill_with_q, steal_kill_with_e
    combo_key = cfg.get_int("combo_key", 57)
    harass_key = cfg.get_int("harass_key", 45)
    laneclear_key = cfg.get_int("laneclear_key", 47)

    use_q_in_combo = cfg.get_bool("use_q_in_combo", True)
    use_w_in_combo = cfg.get_bool("use_w_in_combo", True)
    use_e_in_combo = cfg.get_bool("use_e_in_combo", True)
    use_r_in_combo = cfg.get_bool("use_r_in_combo", True)

    use_w_on_evade = cfg.get_bool("use_w_on_evade", False)
    use_e_on_evade = cfg.get_bool("use_e_on_evade", False)

    steal_kill_with_q = cfg.get_bool("steal_kill_with_q", False)
    steal_kill_with_e = cfg.get_bool("steal_kill_with_e", False)

    lane_clear_with_q = cfg.get_bool("lane_clear_with_q", False)
    lane_clear_with_q2 = cfg.get_bool("lane_clear_with_q2", False)


def lview_save_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global combo_key, harass_key, laneclear_key
    global lane_clear_with_q, lane_clear_with_q2
    global use_w_on_evade, use_e_on_evade
    global steal_kill_with_q, steal_kill_with_e

    cfg.set_int("combo_key", combo_key)
    cfg.set_int("harass_key", harass_key)
    cfg.set_int("laneclear_key", laneclear_key)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_w_in_combo", use_w_in_combo)
    cfg.set_bool("use_e_in_combo", use_e_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    cfg.set_bool("use_w_on_evade", use_w_on_evade)

    cfg.set_bool("steal_kill_with_q", steal_kill_with_q)
    cfg.set_bool("steal_kill_with_e", steal_kill_with_e)

    cfg.set_bool("lane_clear_with_q", lane_clear_with_q)
    cfg.set_bool("lane_clear_with_q2", lane_clear_with_q2)


def lview_draw_settings(game, ui):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global combo_key, harass_key, laneclear_key
    global lane_clear_with_q, lane_clear_with_q2
    global use_w_on_evade, use_e_on_evade
    global steal_kill_with_q, steal_kill_with_e

    ui.text("Samira")
    ui.separator()
    combo_key = ui.keyselect("Combo key", combo_key)
    laneclear_key = ui.keyselect("Laneclear key", laneclear_key)
    if ui.treenode("Setting [Q]"):
        use_q_in_combo = ui.checkbox("Use [Q] in Combo", use_q_in_combo)
        ui.treepop()

    if ui.treenode("Setting [W]"):
        use_w_in_combo = ui.checkbox("Use [W] in Combo", use_w_in_combo)
        use_w_on_evade = ui.checkbox("Use [W] on Evade", use_w_on_evade)
        ui.treepop()

    if ui.treenode("Setting [E]"):
        use_e_in_combo = ui.checkbox("Smart [E]", use_e_in_combo)
        steal_kill_with_e = ui.checkbox("Steal kill with [E]", steal_kill_with_e)
        ui.treepop()

    if ui.treenode("Setting [R]"):
        use_r_in_combo = ui.checkbox("Use [R] in Combo", use_r_in_combo)
        ui.treepop()

    if ui.treenode("Laneclear"):
        lane_clear_with_q = ui.checkbox("Laneclear with [Q]", lane_clear_with_q)
        lane_clear_with_q2 = ui.checkbox("Laneclear with [Q2]", lane_clear_with_q2)
        ui.treepop()
    ui.separator()




RTargetCount = 0


def getCountR(game, dist):
    global RTargetCount
    RTargetCount = 0
    for champ in game.champs:
        if (
            champ
            and champ.is_visible
            and champ.is_enemy_to(game.player)
            and champ.isTargetable
            and champ.is_alive
            and game.is_point_on_screen(champ.pos)
            and game.distance(game.player, champ) <= dist
        ):
            RTargetCount = RTargetCount + 1
    return RTargetCount

class Fake_target():
    def __init__(self, name, pos, gameplay_radius):
        self.name = name
        self.pos = pos
        self.gameplay_radius = gameplay_radius

def predict_pos(target, duration):
    """Predicts the target's new position after a duration"""
    target_direction = target.pos.sub(target.prev_pos).normalize()
    # In case the target wasn't moving
    if math.isnan(target_direction.x):
        target_direction.x = 0.0
    if math.isnan(target_direction.y):
        target_direction.y = 0.0
    if math.isnan(target_direction.z):
        target_direction.z = 0.0
    if target_direction.x == 0.0 and target_direction.z == 0.0:
        return target.pos
    # Target movement speed
    target_speed = target.movement_speed
    # The distance that the target will have traveled after the given duration
    distance_to_travel = target_speed * duration
    return target.pos.add(target_direction.scale(distance_to_travel))


def EDamage(game, target):
    # Calculate raw E damage on target
    e_lvl = game.player.E.level
    if e_lvl == 0:
        return 0
    ap = game.player.ap
    ad = game.player.base_atk + game.player.bonus_atk
    min_dmg = [50, 60, 70, 80, 90]
    missing_hp = (target.max_health - target.health)
    missing_hp_pct = (missing_hp / target.max_health) * 100
    increased_pct = 0.015 * missing_hp_pct
    if increased_pct > 1:
        increased_pct = 1
    e_damage = (1 + increased_pct) * (min_dmg[e_lvl - 1] + 0.20 * ad)

    # Reduce damage based on target's magic resist
    mr = target.magic_resist
    if mr >= 0:
        dmg_multiplier = 100 / (100 + mr)
    else:
        dmg_multiplier = 2 - 100 / (100 - mr)
    e_damage *= dmg_multiplier
    return e_damage

def QDamage(game, target):
    ad = game.player.base_atk + game.player.bonus_atk
    damage = 0
    if game.player.Q.level == 1:
        damage = 0 + 0.80 *ad
    elif game.player.Q.level == 2:
        damage = 5 + 0.90 *ad
    elif game.player.Q.level == 3:
        damage = 10 + 1.00 *ad
    elif game.player.Q.level == 4:
        damage = 15 + 1.10 *ad
    elif game.player.Q.level == 5:
        damage = 20 + 1.20 *ad
    return damage

def WDamage(game, target):
    ad = game.player.base_atk + game.player.bonus_atk
    damage = 0
    if game.player.W.level == 1:
        damage = 20 + 0.80 *ad
    elif game.player.W.level == 2:
        damage = 35 + 0.80 *ad
    elif game.player.W.level == 3:
        damage = 50 + 0.80 *ad
    elif game.player.W.level == 4:
        damage = 65 + 0.80 *ad
    elif game.player.W.level == 5:
        damage = 80 + 0.80 *ad
    return damage

def EKs(game):

    E = getSkill(game, "E")

    before_cpos = game.get_cursor()

    if not steal_kill_with_e:
        return

    target = GetBestTargetsInRange(game, e["Range"])

    if target is None:
        return

    if ValidTarget(target) and IsReady(game, E):
        if target.health <= EDamage(game, target):
            game.move_cursor(game.world_to_screen(target.pos))
            E.trigger(False)
            game.move_cursor(before_cpos)

def GetEnemyCount(game, dist):
    count = 0
    for champ in game.champs:
        if (
            champ
            and champ.is_visible
            and champ.is_enemy_to(game.player)
            and champ.isTargetable
            and champ.is_alive
            and game.is_point_on_screen(champ.pos)
            and game.distance(game.player, champ) <= dist
        ):
            count = count + 1
    return count




def Combo(game):
    global q, w, e, r
    global LastR
    Q = getSkill(game, "Q")
    W = getSkill(game, "W")
    E = getSkill(game, "E")
    R = getSkill(game, "R")
    before_cpos = game.get_cursor()

    if use_e_in_combo and IsReady(game, E) and game.player.mana > e["Mana"]:
        Etarget = GetBestTargetsInRange(game, e["Range"])
        Target_Killable =False
        total_damage = 0
        if Etarget is None:
            return
        total_damage1 = EDamage(game, Etarget) + QDamage(game, Etarget) + WDamage(game,Etarget)
        total_damage2 = EDamage(game, Etarget) + QDamage(game, Etarget)
        total_damage3 = EDamage(game, Etarget) + WDamage(game, Etarget)

        if Etarget and IsReady(game,E) and IsReady(game,Q) and IsReady(game,W) and Etarget.health < total_damage1:
            E.move_and_trigger(game.world_to_screen(Etarget.pos))

        elif Etarget and IsReady(game,E) and IsReady(game,Q) and Etarget.health < total_damage2:
            E.move_and_trigger(game.world_to_screen(Etarget.pos))


        elif Etarget and IsReady(game,E) and IsReady(game,W) and Etarget.health < total_damage3:
            E.move_and_trigger(game.world_to_screen(Etarget.pos))

    if use_w_in_combo and IsReady(game, W) and game.player.mana > w["Mana"]:
        target = GetBestTargetsInRange(game, w["Range"])
        if target:
            W.trigger(False)





    if use_q_in_combo and IsReady(game, Q) and game.player.mana > q["Mana"]:
        Q1target = GetBestTargetsInRange(game, q["Range"])
        if Q1target is None:
            return
        if Q1target.isMoving:
            distance = game.player.pos.distance(Q1target.pos)
            q_travel_time = distance / 2000
            predicted_pos = predict_pos(Q1target, q_travel_time)
            predicted_target = Fake_target(Q1target.name, predicted_pos, Q1target.gameplay_radius)
            if game.player.pos.distance(predicted_target.pos) <= 900 and not IsCollisioned(game, predicted_target):
                Q.move_and_trigger(game.world_to_screen(predicted_target.pos))
        elif Q1target and not IsCollisioned(game, Q1target):
            distance = game.player.pos.distance(Q1target.pos)
            q_travel_time = distance / 2000
            predicted_pos = predict_pos(Q1target, q_travel_time)
            predicted_target = Fake_target(Q1target.name, predicted_pos, Q1target.gameplay_radius)
            Q.move_and_trigger(game.world_to_screen(predicted_target.pos))
        
        Q2Target = GetBestTargetsInRange(game,q["MinRange"])
        if Q2Target is None:
            return
        if Q2Target:
            distance = game.player.pos.distance(Q2Target.pos)
            q_travel_time = distance / 2000
            predicted_pos = predict_pos(Q2Target, q_travel_time)
            predicted_target = Fake_target(Q2Target.name, predicted_pos, Q2Target.gameplay_radius)
            Q.move_and_trigger(game.world_to_screen(predicted_target.pos))


    if (
        use_r_in_combo
        and LastR + 1 < game.time
        and (
            getBuff(game.player, "SamiraPassiveCombo")
            or (getBuff(game.player, "samirarreadybuff"))
        )
        and IsReady(game, R)
    ):
        target = GetBestTargetsInRange(game, r["Range"])
        if target or GetEnemyCount(game, r["Range"])>= 1:
            LastR = game.time
            R.trigger(False)

def Laneclear(game):
    Q = getSkill(game, "Q")
    if lane_clear_with_q and IsReady(game, Q) and game.player.mana > q["Mana"]:
        minion = GetBestMinionsInRange(game, q["Range"])
        if minion and minion.health <= QDamage(game,minion):
            Q.move_and_trigger(game.world_to_screen(minion.pos))
    if lane_clear_with_q2 and IsReady(game, Q) and game.player.mana > q["Mana"]:
        minion = GetBestMinionsInRange(game, q["MinRange"])
        if minion and minion.health <= QDamage(game,minion):
            Q.move_and_trigger(game.world_to_screen(minion.pos))


def lview_update(game, ui):
    global combo_key, harass_key, laneclear_key

    self = game.player

    if self.is_alive and not game.isChatOpen:

        if game.was_key_pressed(combo_key):
            EKs(game)
            Combo(game)
        if game.was_key_pressed(laneclear_key):
            Laneclear(game)
