from lview import *
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import *
import json, time, math
import urllib3, json, urllib, ssl
from evade import checkEvade
from commons.timer import Timer
import random
from API.summoner import *

lview_script_info = {
    "script": "[T3 Vex]",
    "author": "tefan#0922",
    "description": "for vex",
    "target_champ": "vex",
}

combo_key = 57
combo_switch_key = 56

use_q_in_combo = True
use_w_in_combo = True
use_e_in_combo = True
use_r_in_combo = True

QECombo = False
EQCombo = False


q = {"Range": 1200}
q_speed1 = 600
q_speed2 = 3600
w = {"Range": 475}
e = {"Range": 800}
e_speed = 1300
rmin = {"Range": 2000}
rmax = {"Range": 3000}
r_speed = 1600

def lview_load_cfg(cfg):
    global combo_key,use_q_in_combo, use_e_in_combo, use_w_in_combo, use_r_in_combo, combo_switch_key
    combo_key = cfg.get_int("combo_key", 57)
    combo_switch_key = cfg.get_int("combo_switch_key", 56)
    use_q_in_combo = cfg.get_bool("use_q_in_combo", True)
    use_w_in_combo = cfg.get_bool("use_w_in_combo", True)
    use_e_in_combo = cfg.get_bool("use_e_in_combo", True)
    use_r_in_combo = cfg.get_bool("use_r_in_combo", True)

def lview_save_cfg(cfg):
    global combo_key,use_q_in_combo, use_e_in_combo, use_w_in_combo, use_r_in_combo, combo_switch_key
    cfg.set_int("combo_key", combo_key)
    cfg.set_int("combo_switch_key", combo_switch_key)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_w_in_combo", use_w_in_combo)
    cfg.set_bool("use_e_in_combo", use_e_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

def lview_draw_settings(game, ui):
    global combo_key,use_q_in_combo, use_e_in_combo, use_w_in_combo, use_r_in_combo,combo_switch_key
    ui.text("[Vex]")

    combo_key = ui.keyselect("Combo key", combo_key)
    ui.text("Made with <3 by tefan#0922")
    
    if ui.treenode("[Combo Settings]"):
        ui.text(" Press [Alt] key to switch between combo modes ")
        use_q_in_combo = ui.checkbox("Use Q in combo", use_q_in_combo)
        use_w_in_combo = ui.checkbox("Use W in combo", use_w_in_combo)
        use_e_in_combo = ui.checkbox("Use E in combo", use_e_in_combo)
        use_r_in_combo = ui.checkbox("Use R in combo", use_r_in_combo)
        ui.treepop()

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def getPlayerStats():
    response = urllib.request.urlopen("https://127.0.0.1:2999/liveclientdata/activeplayer").read()
    stats = json.loads(response)
    return stats

def r_recast_damage(game, target):
    # Calculate raw R damage on target
    r_lvl = game.player.R.level
    if r_lvl == 0:
        return 0
    ap = getPlayerStats()["championStats"]["abilityPower"]
    ad = getPlayerStats()["championStats"]["attackDamage"]
    min_dmg = [150,250,350]
    missing_hp = (target.max_health - target.health)
    missing_hp_pct = (missing_hp / target.max_health) * 100
    increased_pct = 0.015 * missing_hp_pct
    if increased_pct > 1:
        increased_pct = 1
    r_damage = (1 + increased_pct) * (min_dmg[r_lvl - 1] + 0.50 * ap )
    # Reduce damage based on target's magic resist
    mr = target.magic_resist
    if mr >= 0:
        dmg_multiplier = 100 / (100 + mr)
    else:
        dmg_multiplier = 2 - 100 / (100 - mr)
    r_damage *= dmg_multiplier
    return r_damage

def r_initial_damage(game, target):
    # Calculate raw R damage on target
    r_lvl = game.player.R.level
    if r_lvl == 0:
        return 0
    ap = getPlayerStats()["championStats"]["abilityPower"]
    ad = getPlayerStats()["championStats"]["attackDamage"]
    min_dmg = [75,125,175]
    missing_hp = (target.max_health - target.health)
    missing_hp_pct = (missing_hp / target.max_health) * 100
    increased_pct = 0.015 * missing_hp_pct
    if increased_pct > 1:
        increased_pct = 1
    r1_damage = (1 + increased_pct) * (min_dmg[r_lvl - 1] + 0.20 * ap )
    # Reduce damage based on target's magic resist
    mr = target.magic_resist
    if mr >= 0:
        dmg_multiplier = 100 / (100 + mr)
    else:
        dmg_multiplier = 2 - 100 / (100 - mr)
    r1_damage *= dmg_multiplier
    return r1_damage

def q_damage(game, target):
    # Calculate raw Q damage on target
    q_lvl = game.player.Q.level
    if q_lvl == 0:
        return 0
    ap = getPlayerStats()["championStats"]["abilityPower"]
    ad = getPlayerStats()["championStats"]["attackDamage"]
    min_dmg = [60,110,160,210,260]
    missing_hp = (target.max_health - target.health)
    missing_hp_pct = (missing_hp / target.max_health) * 100
    increased_pct = 0.015 * missing_hp_pct
    if increased_pct > 1:
        increased_pct = 1
    q_damage = (1 + increased_pct) * (min_dmg[q_lvl - 1] + 0.60 * ap )
    # Reduce damage based on target's magic resist
    mr = target.magic_resist
    if mr >= 0:
        dmg_multiplier = 100 / (100 + mr)
    else:
        dmg_multiplier = 2 - 100 / (100 - mr)
    q_damage *= dmg_multiplier
    return q_damage

def w_damage(game, target):
    # Calculate raw W damage on target
    w_lvl = game.player.W.level
    if w_lvl == 0:
        return 0
    ap = getPlayerStats()["championStats"]["abilityPower"]
    ad = getPlayerStats()["championStats"]["attackDamage"]
    min_dmg = [80,120,160,200,240]
    missing_hp = (target.max_health - target.health)
    missing_hp_pct = (missing_hp / target.max_health) * 100
    increased_pct = 0.015 * missing_hp_pct
    if increased_pct > 1:
        increased_pct = 1
    w_damage = (1 + increased_pct) * (min_dmg[w_lvl - 1] + 0.30 * ap )
    # Reduce damage based on target's magic resist
    mr = target.magic_resist
    if mr >= 0:
        dmg_multiplier = 100 / (100 + mr)
    else:
        dmg_multiplier = 2 - 100 / (100 - mr)
    w_damage *= dmg_multiplier
    return w_damage

def e_damage(game, target):
    # Calculate raw E damage on target
    e_lvl = game.player.E.level
    if e_lvl == 0:
        return 0
    ap = getPlayerStats()["championStats"]["abilityPower"]
    ad = getPlayerStats()["championStats"]["attackDamage"]
    min_dmg = [50,70,90,110,130]
    min_bonus = [0.40,0.45,0.50,0.55,0.60]
    missing_hp = (target.max_health - target.health)
    missing_hp_pct = (missing_hp / target.max_health) * 100
    increased_pct = 0.015 * missing_hp_pct
    if increased_pct > 1:
        increased_pct = 1
    e_damage = (1 + increased_pct) * (min_dmg[e_lvl - 1] + min_bonus[e_lvl - 1] * ap )
    # Reduce damage based on target's magic resist
    mr = target.magic_resist
    if mr >= 0:
        dmg_multiplier = 100 / (100 + mr)
    else:
        dmg_multiplier = 2 - 100 / (100 - mr)
    e_damage *= dmg_multiplier
    return e_damage

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

def EQ1Combo(game):
    Q = getSkill(game, "Q")
    E = getSkill(game, "E")
    before_cpos = game.get_cursor()

    if use_e_in_combo and IsReady(game, E):
        target = GetBestTargetsInRange(game, e['Range'])
        if ValidTarget(target):
            e_travel_time = e['Range'] / e_speed
            predicted_pos = predict_pos(target, e_travel_time)
            predicted_target = Fake_target(target.name, predicted_pos, target.gameplay_radius)
            if game.player.pos.distance(predicted_target.pos) <= e['Range']:
                game.move_cursor(game.world_to_screen(predicted_target.pos))
                time.sleep(0.01)
                E.trigger(False)
                time.sleep(0.01)
                game.move_cursor(before_cpos)
    
    if use_q_in_combo and IsReady(game, Q):
        target = GetBestTargetsInRange(game, q["Range"])
        if ValidTarget(target):
            q_travel_time = q['Range'] / q_speed2
            predicted_pos = predict_pos(target, q_travel_time)
            predicted_target = Fake_target(target.name, predicted_pos, target.gameplay_radius)
            if game.player.pos.distance(predicted_target.pos) <= q['Range']:
                game.move_cursor(game.world_to_screen(predicted_target.pos))
                time.sleep(0.01)
                Q.trigger(False)
                time.sleep(0.01)
                game.move_cursor(before_cpos)

def QE1Combo(game):
    Q = getSkill(game, "Q")
    E = getSkill(game, "E")
    before_cpos = game.get_cursor()    
    if use_q_in_combo and IsReady(game, Q):
        target = GetBestTargetsInRange(game, q["Range"])
        if ValidTarget(target):
            q_travel_time = q['Range'] / q_speed2
            predicted_pos = predict_pos(target, q_travel_time)
            predicted_target = Fake_target(target.name, predicted_pos, target.gameplay_radius)
            if game.player.pos.distance(predicted_target.pos) <= q['Range']:
                game.move_cursor(game.world_to_screen(predicted_target.pos))
                time.sleep(0.01)
                Q.trigger(False)
                time.sleep(0.01)
                game.move_cursor(before_cpos)
    
    if use_e_in_combo and IsReady(game, E):
        target = GetBestTargetsInRange(game, e['Range'])
        if ValidTarget(target):
            e_travel_time = e['Range'] / e_speed
            predicted_pos = predict_pos(target, e_travel_time)
            predicted_target = Fake_target(target.name, predicted_pos, target.gameplay_radius)
            if game.player.pos.distance(predicted_target.pos) <= e['Range']:
                game.move_cursor(game.world_to_screen(predicted_target.pos))
                time.sleep(0.01)
                E.trigger(False)
                time.sleep(0.01)
                game.move_cursor(before_cpos)

def WCombo(game):
    W = getSkill(game, "W")
    before_cpos = game.get_cursor() 
    if use_w_in_combo and IsReady(game, W):
        target = GetBestTargetsInRange(game, w["Range"])
        if ValidTarget(target):
            if game.player.pos.distance(target.pos) <= w['Range']:
                W.trigger(False)

def RCombo(game):
    Q = getSkill(game, "Q")
    W = getSkill(game, "W")
    E = getSkill(game, "E")
    R = getSkill(game, "R")
    before_cpos = game.get_cursor()
    total_damage = 0
    target = GetBestTargetsInRange(game)

    if use_r_in_combo and IsReady(game, R):
        target = GetBestTargetsInRange(game, rmin["Range"])
        if ValidTarget(target):
            r_travel_time = rmax["Range"] / r_speed
            predicted_pos = predict_pos(target, r_travel_time)
            predicted_target = Fake_target(target.name, predicted_pos, target.gameplay_radius)
            if game.player.pos.distance(predicted_target.pos) <= rmax["Range"] and target.health < r_recast_damage(game, target):
                game.move_cursor(game.world_to_screen(predicted_target.pos))
                time.sleep(0.01)
                R.trigger(False)
                time.sleep(0.01)
                game.move_cursor(before_cpos)

def lview_update(game, ui):
    self = game.player
    global EQCombo



    if self.is_alive and self.is_visible and not game.isChatOpen:
        if game.was_key_pressed(combo_switch_key):
            EQCombo = ~EQCombo
        if EQCombo:
            pos = game.player.pos
            game.draw_text(game.world_to_screen(pos).add(Vec2(-15,20)), "E->Q", Color.PURPLE)
            if game.is_key_down(combo_key):
                EQ1Combo(game)
        else:
            pos = game.player.pos
            game.draw_text(game.world_to_screen(pos).add(Vec2(-15,20)), "Q->E", Color.PURPLE)
            if game.is_key_down(combo_key):
                QE1Combo(game)
        if use_w_in_combo and game.is_key_down(combo_key):
            WCombo(game)
        if use_r_in_combo and game.is_key_down(combo_key):
            RCombo(game)
