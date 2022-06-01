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


E_Gap_Close, E_Anti_Melee, E_Force_Evade, Q_Harass, Q_Kill_Minion, R_Enabled, E_Enabled, W_Enabled, Q_Enabled, E_Safe_KS = True, True, True, True, True, True, True, True, True, True
Q_Range = 1100 # 1200 
W_Range = 1100 # 1200 
E_Range = 475
R_Min = 1000
R_Max = 3000


mana_q = [28,31,34,37,40]
mana_w = 50
mana_e = 90
mana_r = 100

combo_key = 57
laneclear_key =47

lview_script_info = {
    "script": "Ezreal",
	"author": "tefan#7872",
	"description": "For Ezreal",
	"target_champ": "ezreal"
}

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def getPlayerStats():
    response = urllib.request.urlopen("https://127.0.0.1:2999/liveclientdata/activeplayer").read()
    stats = json.loads(response)
    return stats



def QDamage(game, target):
    # Calculate raw W damage on target
    q_lvl = game.player.Q.level
    if q_lvl == 0:
        return 0
    ap = getPlayerStats()["championStats"]["abilityPower"]
    ad = getPlayerStats()["championStats"]["attackDamage"]
    min_dmg = [20, 45, 70, 95, 120]
    missing_hp = (target.max_health - target.health)
    missing_hp_pct = (missing_hp / target.max_health) * 100
    increased_pct = 0.15 * missing_hp_pct
    if increased_pct > 1:
        increased_pct = 1
    q_damage = (1 + increased_pct) * (min_dmg[q_lvl - 1] + 1.30 * ad + 0.15 * ap)

    # Reduce damage based on target's magic resist
    mr = target.magic_resist
    if mr >= 0:
        dmg_multiplier = 100 / (100 + mr)
    else:
        dmg_multiplier = 2 - 100 / (100 - mr)
    q_damage *= dmg_multiplier
    return q_damage

def WDamage(game, target):
    # Calculate raw W damage on target
    w_lvl = game.player.W.level
    if w_lvl == 0:
        return 0
    ap = getPlayerStats()["championStats"]["abilityPower"]
    ad = getPlayerStats()["championStats"]["attackDamage"]
    min_dmg = [80, 135, 190, 245, 300]
    missing_hp = (target.max_health - target.health)
    missing_hp_pct = (missing_hp / target.max_health) * 100
    increased_pct = 0.15 * missing_hp_pct
    if increased_pct > 1:
        increased_pct = 1
    w_damage = (1 + increased_pct) * (min_dmg[w_lvl - 1] + 0.60 * ad + 0.70 * ap)

    # Reduce damage based on target's magic resist
    mr = target.magic_resist
    if mr >= 0:
        dmg_multiplier = 100 / (100 + mr)
    else:
        dmg_multiplier = 2 - 100 / (100 - mr)
    w_damage *= dmg_multiplier
    return w_damage

def EDamage(game, target):
    # Calculate raw E damage on target
    e_lvl = game.player.E.level
    if e_lvl == 0:
        return 0
    ap = getPlayerStats()["championStats"]["abilityPower"]
    ad = getPlayerStats()["championStats"]["attackDamage"]
    min_dmg = [80, 130, 180, 230, 280]
    missing_hp = (target.max_health - target.health)
    missing_hp_pct = (missing_hp / target.max_health) * 100
    increased_pct = 0.15 * missing_hp_pct
    if increased_pct > 1:
        increased_pct = 1
    e_damage = (1 + increased_pct) * (min_dmg[e_lvl - 1] + 0.50 * ad + 0.75 * ap)

    # Reduce damage based on target's magic resist
    mr = target.magic_resist
    if mr >= 0:
        dmg_multiplier = 100 / (100 + mr)
    else:
        dmg_multiplier = 2 - 100 / (100 - mr)
    e_damage *= dmg_multiplier
    return e_damage



def RDamage(game, target):
    # Calculate raw R damage on target
    r_lvl = game.player.R.level
    if r_lvl == 0:
        return 0
    ap = getPlayerStats()["championStats"]["abilityPower"]
    ad = getPlayerStats()["championStats"]["attackDamage"]
    min_dmg = [350,500,650]
    missing_hp = (target.max_health - target.health)
    missing_hp_pct = (missing_hp / target.max_health) * 100
    increased_pct = 0.15 * missing_hp_pct
    if increased_pct > 1:
        increased_pct = 1
    r_damage = (1 + increased_pct) * (min_dmg[r_lvl - 1] + 0.90 * ap + 1.00 * ad)

    # Reduce damage based on target's magic resist
    mr = target.magic_resist
    if mr >= 0:
        dmg_multiplier = 100 / (100 + mr)
    else:
        dmg_multiplier = 2 - 100 / (100 - mr)
    r_damage *= dmg_multiplier
    return r_damage

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

def lasthit_q(game):
    Q = getSkill(game, "Q")
    before_cpos = game.get_cursor()

    minion = GetBestMinionsInRange(game, Q_Range)

    if minion is None:
        return

    if minion and IsReady(game, Q) and game.player.mana > mana_q[game.player.Q.level-1]:
        if QDamage(game, minion) > minion.health:
            Q.move_and_trigger(game.world_to_screen(minion.pos))


    
#hi zoodle

def combo_q(game):
    Q = getSkill(game, "Q")
    before_cpos = game.get_cursor()

    if not IsReady(game, Q):
        return
    
    if Q_Enabled:
        target = GetBestTargetsInRange(game, Q_Range)

        if target is None:
            return
        
        if ValidTarget(target):
            q_travel_time = Q_Range / 2000
            predicted_pos = predict_pos(target, q_travel_time)
            predicted_target = Fake_target(target.name, predicted_pos, target.gameplay_radius)
            if game.player.pos.distance(predicted_target.pos) <= Q_Range and not IsCollisioned(game, predicted_target):
                Q.move_and_trigger(game.world_to_screen(predicted_target.pos))
                
                 
    
def combo_w(game):
    Q = getSkill(game, "Q")
    W = getSkill(game, "W")
    before_cpos = game.get_cursor()

    if not IsReady(game, Q):
        return
    
    if not IsReady(game, W):
        return
    
    if W_Enabled:
        target = GetBestTargetsInRange(game, W_Range)

        if target is None:
            return

        if ValidTarget(target):
            w_travel_time = W_Range / 1700
            predicted_pos = predict_pos(target, w_travel_time)
            predicted_target = Fake_target(target.name, predicted_pos, target.gameplay_radius)
            if game.player.pos.distance(predicted_target.pos) <= W_Range and not IsCollisioned(game, predicted_target):
                W.move_and_trigger(game.world_to_screen(predicted_target.pos))
                
                 

def point_under_turret(game, pos: Vec3):

    for turret in game.turrets:
        if turret.is_ally_to(game.player):
            continue
        try:
            if pos.distance(turret.pos) <= 915:
                return True
        except:
            pass
    
    return False

def point_has_minion(game, pos: Vec3):
    for minion in game.minions:
        if minion.is_ally_to(game.player):
            continue
        try:
            if pos.distance(minion.pos) < 250:
                return True
        except:
            pass
    
    return False

def point_has_enemy_champ(game, pos: Vec3):

    for champ in game.champs:
        if champ.is_ally_to(game.player):
            continue
        try:
            if pos.distance(champ.pos) < E_Range+100:
                return True
        except:
            pass
        
    return False

def point_has_enemy_champ2(game, pos: Vec3):

    for champ in game.champs:
        if champ.is_ally_to(game.player):
            continue
        try:
            if pos.distance(champ.pos) < 350:
                return True
        except:
            pass
        
    return False

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

def getCountMelee1(game, dist):
    meelecount1 = 0
    for champ in game.champs:
        if (
            champ
            and champ.is_visible
            and champ.is_enemy_to(game.player)
            and champ.isTargetable
            and champ.is_alive
            and game.is_point_on_screen(champ.pos)
            and game.distance(game.player, champ) < dist
        ):
            meelecount1 = meelecount1 + 1
            if int(meelecount1) > 0:
                return True
            else:
                return False

def combo_e(game):
    Q = getSkill(game, "Q")
    W = getSkill(game, "W")
    E = getSkill(game, "E")
    before_cpos = game.get_cursor()
    q2Targets = GetBestTargetsInRange(game, Q_Range*2)
    bestPoint = None
    lowestDistance = 10000
    highestDistance = 0

    if not IsReady(game, E):
        return

    if GetEnemyCount(game, Q_Range*2) == 0:
        return
        
    if GetEnemyCount(game, Q_Range*2) > 2:
        return
        
    if q2Targets is None:
        return
        
    if game.player.pos.distance(q2Targets.pos) <= Q_Range - 200:
        return
        
    Target_Killable = False
    totalDamage = 0

    if q2Targets and getBuff(q2Targets, "ezrealwattach"):
        totalDamage = QDamage(game, q2Targets) + WDamage(game, q2Targets) + EDamage(game,q2Targets)
        
    if  IsReady(game, W) and game.player.mana > mana_w:
        totalDamage = QDamage(game, q2Targets) + WDamage(game, q2Targets) + EDamage(game,q2Targets)
        
    totalDamage = QDamage(game, q2Targets) + EDamage(game,q2Targets)

    if totalDamage > q2Targets.health:
        Target_Killable = True

    for point in range(0, 360, 20):
        point_temp = math.radians(point)
        pX, pY, pZ = E_Range * math.cos(point_temp) + game.player.pos.x, game.player.pos.y, E_Range * math.sin(point_temp) + game.player.pos.z

        if Vec3(pX, pY, pZ).distance(q2Targets.pos) < lowestDistance:

            if not point_has_minion(game, Vec3(pX, pY, pZ)) and not point_has_enemy_champ(game, Vec3(pX, pY, pZ))  and not point_under_turret(game, Vec3(pX, pY, pZ)) and not IsDanger(game, Vec3(pX, pY, pZ)):
                lowestDistance = Vec3(pX, pY, pZ).distance(q2Targets.pos)
                bestPoint = Vec3(pX, pY, pZ)  

    if IsReady(game, Q) and game.player.mana > mana_q[game.player.Q.level-1] and IsReady(game, E) and game.player.mana > mana_e and bestPoint is not None and Target_Killable:
       game.move_cursor(game.world_to_screen(bestPoint))
       E.trigger(False)
       game.move_cursor(before_cpos)
         
                  

    if E_Gap_Close:
        if not IsReady(game, E):
            return
        targets_gap_range = GetBestTargetsInRange(game, E_Range)
        if targets_gap_range and getCountMelee1(game, E_Range) and game.player.mana > mana_e and IsReady(game, E):
            if targets_gap_range.isDashing:
                for point in range(0, 360, 20):
                    point_temp = math.radians(point)
                    pX, pY, pZ = E_Range * math.cos(point_temp) + game.player.pos.x, game.player.pos.y, E_Range * math.sin(point_temp) + game.player.pos.z
                    
                    if Vec3(pX, pY, pZ).distance(targets_gap_range.pos) > highestDistance:
                            if not point_has_enemy_champ(game, Vec3(pX, pY, pZ))  and not point_under_turret(game, Vec3(pX, pY, pZ)) and not IsDanger(game, Vec3(pX, pY, pZ)):
                                highestDistance = Vec3(pX, pY, pZ).distance(targets_gap_range.pos)
                                bestPoint = Vec3(pX, pY, pZ)
                
                if IsReady(game, Q) and game.player.mana > mana_q[game.player.Q.level-1] and IsReady(game, E) and game.player.mana > mana_e and bestPoint is not None:
                    game.move_cursor(game.world_to_screen(bestPoint))
                    E.trigger(False)
                    game.move_cursor(before_cpos)


    
    


        
def combo_r(game):
    R = getSkill(game, "R")
    before_cpos = game.get_cursor()

    if not IsReady(game, R):
        return

    if R_Enabled and IsReady(game, R):
        target = GetBestTargetsInRange(game, R_Max)
        if target is None:
            return
        W_Attached = False
        Target_Killable = False
        if getBuff(target, "ezrealwattach"):
            W_Attached = True
        if W_Attached:
            if RDamage(game, target) + WDamage(game,target) > target.health:
                Target_Killable = True
        if RDamage(game,target) > target.health:
            Target_Killable = True
        if ValidTarget(target) and IsReady(game, R) and game.player.mana > 100:
            r_travel_time = R_Max / 2000
            predicted_pos = predict_pos(target, r_travel_time)
            
            predicted_target = Fake_target(target.name, predicted_pos, target.gameplay_radius)
            if game.player.pos.distance(predicted_target.pos) > R_Min and Target_Killable:
                R.move_and_trigger(game.world_to_screen(predicted_target.pos))

def lview_draw_settings(game, ui):
    global Q_Enabled, W_Enabled, E_Enabled, R_Enabled, Q_Kill_Minion, R_Min, R_Max, Q_Harass, E_Gap_Close, E_Anti_Melee, E_Force_Evade, E_Safe_KS
    ui.text('[T3] Ezreal                                                      Version [0.2]\nDeveloped by tefan#7872')
    ui.separator()
    if ui.treenode("Explorer Core"):
        if ui.treenode("[Q] Mystic Shot"):
            Q_Enabled = ui.checkbox('Enabled [Q]', Q_Enabled)
            ui.treepop()
        if ui.treenode("[W] Essence Flux"):
            W_Enabled = ui.checkbox('Enabled [W]', W_Enabled)
            ui.treepop()
        if ui.treenode("[E] Arcane Shift"):
            E_Enabled = ui.checkbox('Smart [E]', E_Enabled)
            E_Gap_Close = ui.checkbox('[E] Anti-Gap', E_Gap_Close)
            E_Anti_Melee = ui.checkbox('[E] Anti-Melee', E_Anti_Melee)
            # E_Force_Evade = ui.checkbox('[E] Force Evade', E_Force_Evade)
            # E_Safe_KS = ui.checkbox('[E] Safe Kill Steal', E_Safe_KS)
            ui.treepop()
        if ui.treenode("[R] Trueshot Barrage"):
            R_Enabled = ui.checkbox('Enabled [R]', R_Enabled)
            R_Min = ui.sliderint('Min. [R] Range (min distance to target)', int(R_Min), 0, 1000)
            R_Max = ui.sliderint('Max. [R] Range (max distance to target)', int(R_Max), 1000, 5000)
            ui.treepop()
            
        ui.treepop()
    ui.separator()
    if ui.treenode("Farming Core"):
        if ui.treenode("[Q] Mystic Shot"):
            Q_Kill_Minion = ui.checkbox("[Q] Killable Minion", Q_Kill_Minion)
            ui.treepop()
        ui.treepop()
    ui.separator()
    # if ui.treenode("Harass Core"):
    #     if ui.treenode("[Q] Mystic Shot"):
    #         Q_Harass = ui.checkbox("[Q] Harass", Q_Harass)
    #         ui.treepop()
    #     ui.treepop()
    # ui.separator()

def lview_load_cfg(cfg):
    global Q_Enabled, W_Enabled, E_Enabled, R_Enabled, Q_Kill_Minion, R_Min, R_Max, Q_Harass, E_Gap_Close, E_Anti_Melee, E_Force_Evade, E_Safe_KS
    Q_Enabled = cfg.get_bool("Q_Enabled", True)
    W_Enabled = cfg.get_bool("W_Enabled", True)
    E_Enabled = cfg.get_bool("E_Enabled", True)
    Q_Kill_Minion = cfg.get_bool("Q_KS_MINION", True)
    E_Gap_Close = cfg.get_bool("E_Gap_Close", True)
    E_Anti_Melee = cfg.get_bool("E_Anti_Melee", True)
    E_Force_Evade = cfg.get_bool("E_Force_Evade", True)
    E_Safe_KS = cfg.get_bool("E_Safe_KS", True)
    R_Enabled = cfg.get_bool("R", True)

def lview_save_cfg(cfg):
    cfg.get_bool("Q", Q_Enabled)
    cfg.get_bool("W", W_Enabled)
    cfg.get_bool("E", E_Enabled)
    cfg.get_bool("Q_KS_MINION", Q_Kill_Minion)
    cfg.get_bool("E_Gap_Close", E_Gap_Close)
    cfg.get_bool("E_Anti_Melee", E_Anti_Melee)
    cfg.get_bool("E_Force_Evade", E_Force_Evade)
    cfg.get_bool("E_Safe_KS", E_Safe_KS)
    cfg.get_bool("R", R_Enabled)
def close_w(game):
    
    W = getSkill(game, "W")
    before_cpos = game.get_cursor()

    if not IsReady(game, W):
        return
    
    if not W_Enabled:
        return
    
    target = GetBestTargetsInRange(game, game.player.atkRange)

    if target is None:
        return

    if ValidTarget(target) and IsReady(game, W):
        w_travel_time = game.player.atkRange / 1700
        predicted_pos = predict_pos(target, w_travel_time)
        predicted_target = Fake_target(target.name, predicted_pos, target.gameplay_radius)
        if game.player.pos.distance(predicted_target.pos) <= game.player.atkRange:
            W.move_and_trigger(game.world_to_screen(predicted_target.pos))
                
    
# def safe_ks(game):
#     Q = getSkill(game, "Q")
#     W = getSkill(game, "W")
#     E = getSkill(game, "E")
#     before_cpos = game.get_cursor()
#     bestPoint = None
#     if not IsReady(game, E):
#         return
#     if E_Safe_KS:
#         totalDamage = 0
#         lowestDistance = 10000
#         Target_Killable = False
#         target = GetBestTargetsInRange(game, game.player.atkRange + E_Range)
#         if target is None:
#             return
#         if target and getBuff(target, "ezrealwattach"):
#             totalDamage = WDamage(game, target) + EDamage(game,target)
#         totalDamage =  EDamage(game,target)
#         if totalDamage > target.health:
#             Target_Killable = True
#             for point in range(0, 360, 20):
#                 point_temp = math.radians(point)
#                 pX, pY, pZ = E_Range * math.cos(point_temp) + game.player.pos.x, game.player.pos.y, E_Range * math.sin(point_temp) + game.player.pos.z
                
#                 if Vec3(pX, pY, pZ).distance(target.pos) < lowestDistance:
#                     if not point_has_minion(game, Vec3(pX, pY, pZ)) and not point_under_turret(game, Vec3(pX, pY, pZ)) and not IsDanger(game, Vec3(pX, pY, pZ)) and not point_has_enemy_champ2(game, Vec3(pX, pY, pZ)):
#                         lowestDistance = Vec3(pX, pY, pZ).distance(target.pos)
#                         bestPoint = Vec3(pX, pY, pZ) 

#             if IsReady(game, E) and game.player.mana > mana_e and bestPoint is not None and Target_Killable:
#                 E.move_and_trigger(game.world_to_screen(bestPoint))
                 

def lview_update(game, ui):
    self = game.player
    Q = getSkill(game, "Q")
    W = getSkill(game, "W")
    E = getSkill(game, "E")
    R = getSkill(game, "R")
    before_cpos = game.get_cursor()
    highestDistance = 0
    bestPoint = None
    


    if self.is_alive and self.is_visible and not game.isChatOpen:
        if game.was_key_pressed(combo_key):
            combo_e(game)
            close_w(game)
            combo_w(game)
            combo_q(game)
            combo_r(game)
        if game.was_key_pressed(laneclear_key):
            lasthit_q(game)
        if E_Anti_Melee:
            if not IsReady(game, E):
                return
            targets_melee_range = GetBestTargetsInRange(game, 250)
            if  GetEnemyCount(game,250) > 0 and IsReady(game, E):
                for point in range(0, 360, 20):
                    point_temp = math.radians(point)
                    pX, pY, pZ = E_Range * math.cos(point_temp) + game.player.pos.x, game.player.pos.y, E_Range * math.sin(point_temp) + game.player.pos.z
                    
                    if Vec3(pX, pY, pZ).distance(targets_melee_range.pos) > highestDistance:
                            if not point_has_enemy_champ(game, Vec3(pX, pY, pZ)) and not point_has_minion(game, Vec3(pX, pY, pZ)) and not point_under_turret(game, Vec3(pX, pY, pZ)):
                                highestDistance = Vec3(pX, pY, pZ).distance(targets_melee_range.pos)
                                bestPoint = Vec3(pX, pY, pZ)
                if IsReady(game, E) and bestPoint is not None:
                    game.move_cursor(game.world_to_screen(bestPoint))
                    E.trigger(False)
                    game.move_cursor(before_cpos)
        
    
