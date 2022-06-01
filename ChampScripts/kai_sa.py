from lview import *
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import *
import json, time, math
import urllib3, json, urllib, ssl
##
from evade import checkEvade
from commons.timer import Timer
import random
from API.summoner import *
import math

lview_script_info = {
    "script": "[T3 KAI'SA]",
    "author": "tefan",
    "description": "for Kaisa",
    "target_champ": "kaisa",
}

R_Enabled, E_Enabled, W_Enabled, Q_Enabled = True, True, True, True
Q_Range = 599
W_Range = 2690
R_Min = 1000
R_Max = 3000
R_Under_HP = 35
R_Target_HP = 25
R_Radius = 525

lastE = 0

last_positions = []
last_pos_id = []

def is_immobile(target):
	for buff in target.buffs:

		if 'absolutezero' in buff.name.lower():
			return True
		elif 'alzaharnethergrasp' in buff.name.lower():
			return True
		elif 'caitlynaceinthehole' in buff.name.lower():
			return True
		elif 'crowstorm' in buff.name.lower():
			return True
		elif 'destiny' in buff.name.lower():
			return True
		elif 'drainChannel' in buff.name.lower():
			return True
		elif 'galioIdolofdurand' in buff.name.lower():
			return True
		elif 'infiniteduress' in buff.name.lower():
			return True
		elif 'karthusfallenone' in buff.name.lower():
			return True
		elif 'katarinar' in buff.name.lower():
			return True
	return False

def lview_load_cfg(cfg):
    global combo_key
    combo_key = cfg.get_int("combo_key", 57)
    cfg.get_bool("Q", Q_Enabled)
    cfg.get_bool("W", W_Enabled)
    cfg.get_bool("E", E_Enabled)
    cfg.get_bool("R_Target_HP", R_Target_HP)
    cfg.get_bool("R", R_Enabled)
    cfg.get_int("R_Under_HP", R_Under_HP)

def lview_save_cfg(cfg):
    cfg.set_int("combo_key", combo_key)
    cfg.get_bool("Q", Q_Enabled)
    cfg.get_bool("W", W_Enabled)
    cfg.get_bool("E", E_Enabled)
    cfg.get_bool("R_Target_HP", R_Target_HP)
    cfg.get_bool("R", R_Enabled)
    cfg.get_int("R_Under_HP", R_Under_HP)

def lview_draw_settings(game, ui):

	global Q_Enabled, W_Enabled, E_Enabled, R_Enabled, R_Min, R_Max, R_Target_HP, R_Under_HP

	ui.text("[T3 Sniper Kai'sa]")
	if ui.treenode("[Q] Icathian Rain"):
		Q_Enabled = ui.checkbox('Enabled [Q]', Q_Enabled)
		ui.treepop()
	if ui.treenode("[W] Void Seeker"):
		W_Enabled = ui.checkbox('Enabled [W]', W_Enabled)
		ui.treepop()
	if ui.treenode("[E] Supercharge"):
		E_Enabled = ui.checkbox('Enabled [E]', E_Enabled)
		ui.treepop()
	if ui.treenode("[R] Killer Instinct"):
		R_Enabled = ui.checkbox('Enabled [R]', R_Enabled)
		R_Target_HP = ui.sliderint('Target < HP %', int(R_Target_HP), 0, 100)
		R_Under_HP = ui.sliderint('Player < HP % to use R',  int(R_Under_HP),   0, 100)
	ui.treepop()

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



def QCombo(game):
    Q = getSkill(game, "Q")
    before_cpos = game.get_cursor()




    if Q_Enabled and IsReady(game, Q):
        target = GetBestTargetsInRange(game, Q_Range)

        if target and game.player.mana > 55:
            if game.player.pos.distance(target.pos) <= Q_Range:
                Q.move_and_trigger(game.world_to_screen(target.pos))

def WCombo(game):

    W = getSkill(game, "W")
    before_cpos = game.get_cursor()
    if W_Enabled and IsReady(game, W) and game.player.mana > 70:
        target = GetBestTargetsInRange (game, W_Range)

        if ValidTarget (target):
            w_travel_time = W_Range / 1750
            predicted_pos = predict_pos (target, w_travel_time)
            predicted_target = Fake_target (target.name, predicted_pos, target.gameplay_radius)
            if not game.is_point_on_screen(predicted_target.pos):
                W.move_and_trigger(game.world_to_minimap (predicted_target.pos))
            elif game.player.pos.distance(predicted_target.pos) > game.player.atkRange and not IsCollisioned(game, target):
                W.move_and_trigger (game.world_to_screen (predicted_target.pos))
            

def Evade(game):
    E = getSkill(game, "E")
    if E_Enabled and IsReady(game, E):
        
        for missile in game.missiles: #checks if missile is coming at your pos
            end_pos = missile.end_pos.clone()
            start_pos = missile.start_pos.clone()
            curr_pos = missile.pos.clone()
            br = game.player.gameplay_radius
            if not game.player.is_alive or missile.is_ally_to(game.player):
                continue
            if not is_skillshot(missile.name):
                continue
            spell = get_missile_parent_spell(missile.name)
            if not spell:
                continue
            if (
                game.point_on_line(
                game.world_to_screen(start_pos),
                game.world_to_screen(end_pos),
                game.world_to_screen(game.player.pos),
                br,
            )
            and game.is_point_on_screen(curr_pos)
        ):
             if IsReady(game, E) and spell.danger > 0 : 
                 E.trigger(False) 

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

def Rcombo(game):
    R = getSkill(game, "R")
    Q = getSkill(game, "Q")
    E = getSkill(game, "E")
    before_cpos = game.get_cursor()
    if R_Enabled and IsReady(game, R) and IsReady(game, Q) :
        highestDistance = 0
        bestPoint = None
        target = GetBestTargetsInRange(game, R_Max)
        
        if target:
            hp = int(game.player.health / game.player.max_health * 100)
            target_hp = int(target.health / target.max_health * 100)
            isTagged = False
            kitePos = GetKitePosition(game, target)
            if target and getBuff(target, "kaisapassivemarker"):
                isTagged = True
                if target and target_hp <= R_Target_HP and hp != R_Under_HP and isTagged:
                    for point in range(0, 360, 20):
                        point_temp = math.radians(point)
                        pX, pY, pZ = R_Radius * math.cos(point_temp) + target.pos.x, target.pos.y, R_Radius * math.sin(point_temp) + target.pos.z

                        if Vec3(pX, pY, pZ).distance(target.pos) > highestDistance:
                                if not IsDanger(game,Vec3(pX, pY, pZ )) and not point_under_turret(game, Vec3(pX, pY, pZ)):
                                    highestDistance = Vec3(pX, pY, pZ).distance(target.pos)
                                    bestPoint = Vec3(pX, pY, pZ)
            
                    if IsReady(game, R) and game.player.mana > 100 and bestPoint is not None:
                        if game.is_point_on_screen(bestPoint):
                            R.move_and_trigger(game.world_to_screen(bestPoint))
                        elif not game.is_point_on_screen(bestPoint):
                            R.move_and_trigger(game.world_to_minimap(bestPoint))
                        if IsReady(game, E) :
                            E.trigger(False)


def lview_update(game, ui):
    self = game.player

    if self.is_alive and self.is_visible and not game.isChatOpen and game.is_point_on_screen(self.pos) :
        if game.was_key_pressed(combo_key):
            Evade(game)
            WCombo(game)
            QCombo(game)
            Rcombo(game)
