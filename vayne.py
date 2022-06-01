
from lview import *
from commons.items import *
from commons.targeting import *
from commons.utils import *
import json, time, math
from commons.targit import *

lview_script_info = {
    "script": "Tefans Vayne",
    "author": "Tefan",
    "description": "Vayne",
    "target_champ": "vayne",
}

lastQ = 0
lastE = 0

combo_key = 57
harass_key = 46

use_q_in_combo = True
use_e_in_combo = True
use_r_in_combo = True

e_interrupt = True

anti_gap_q = True
anti_gap_e = True

use_q_on_evade = False

draw_q_range = False
draw_e_range = False
q_range = 300
MaxRCountForUse = 0

e_range = 475

q = {"Range": 325}
e = {"Speed": 999, "Range": 650, "delay": 0.75, "radius": 120}


use_q_with_harass = True
use_e_with_harass = False


def lview_load_cfg(cfg):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range
    global combo_key, harass_key
    global anti_gap_q, anti_gap_e, use_q_on_evade
    global e_range
    global randomize_q_pos
    global MaxRCountForUse, e_interrupt
    global use_q_with_harass, use_e_with_harass
    combo_key = cfg.get_int("combo_key", 57)
    harass_key = cfg.get_int("harass_key", 46)

    use_q_in_combo = cfg.get_bool("use_q_in_combo", True)
    e_interrupt = cfg.get_bool('e_interrupt', e_interrupt)
    use_e_in_combo = cfg.get_bool("use_e_in_combo", True)
    use_r_in_combo = cfg.get_bool("use_r_in_combo", True)

    use_q_with_harass = cfg.get_bool("use_q_with_harass", True)
    use_e_with_harass = cfg.get_bool("use_e_with_harass", False)

    randomize_q_pos = cfg.get_bool("use_q_for_gapcloser", True)

    anti_gap_q = cfg.get_bool("anti_gap_q", True)
    anti_gap_e = cfg.get_bool("anti_gap_e", True)

    use_q_on_evade = cfg.get_bool("use_q_on_evade", False)

    e_range = cfg.get_int("e_range", 475)

    draw_q_range = cfg.get_bool("draw_q_range", False)
    draw_e_range = cfg.get_bool("draw_e_range", False)

    MaxRCountForUse = cfg.get_int("MaxRCountForUse", MaxRCountForUse)


def lview_save_cfg(cfg):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range
    global combo_key, harass_key
    global anti_gap_q, anti_gap_e, use_q_on_evade
    global e_range, e_interrupt
    global randomize_q_pos
    global MaxRCountForUse
    global use_q_with_harass, use_e_with_harass

    cfg.set_int("combo_key", combo_key)
    cfg.set_int("harass_key", harass_key)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool('e_interrupt', e_interrupt)
    cfg.set_bool("use_e_in_combo", use_e_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    cfg.set_bool("use_q_with_harass", use_q_with_harass)
    cfg.set_bool("use_e_with_harass", use_e_with_harass)

    cfg.set_bool("use_q_for_gapcloser", randomize_q_pos)

    cfg.set_bool("anti_gap_q", anti_gap_q)
    cfg.set_bool("anti_gap_e", anti_gap_e)

    cfg.set_bool("use_q_on_evade", use_q_on_evade)

    cfg.set_int("e_range", e_range)

    cfg.set_bool("draw_q_range", draw_q_range)
    cfg.set_bool("draw_e_range", draw_e_range)

    cfg.set_int("MaxRCountForUse", MaxRCountForUse)


def lview_draw_settings(game, ui):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range
    global combo_key, harass_key
    global anti_gap_q, anti_gap_e, use_q_on_evade
    global e_range
    global randomize_q_pos
    global MaxRCountForUse, e_interrupt
    global use_q_with_harass, use_e_with_harass


    combo_key = ui.keyselect("Combo key", combo_key)


    ui.text("Tefans Vayne 1.0 beta \nmade with <3 by Tefan#7872")
    

    if ui.treenode("Setting [Q]"):
        use_q_in_combo = ui.checkbox("Use Q in Combo", use_q_in_combo)
        use_q_with_harass = ui.checkbox("Use Q with Harass", use_q_with_harass)
        use_q_on_evade = ui.checkbox("Use Q on Evade", use_q_on_evade)
        anti_gap_q = ui.checkbox("[Q] Anti-Gap closer", anti_gap_q)
        ui.treepop()

    if ui.treenode("Setting [E]"):
        e_interrupt = ui.checkbox('Auto E Wall stun + Auto Interrupt The following spells: \n alzaharnethergrasp, \n caitlynaceinthehole, \n crowstorm, \n destiny, \n drainChannel, \n galioIdolofdurand, \n infiniteduress, \n karthusfallenone, \n katarinar, \n lucianr, \n meditate, \n missfortunebullettime, \n pantheonrjump, \n pantheonrfall, \n reapthewhirlwind, \n shenstandunited, \n urgotswap2, \n velkozr, \n xerathlocusofpower2 ', e_interrupt)
        ui.separator()
        use_e_with_harass = ui.checkbox("Use E with Harass", use_e_with_harass)
        ui.text(" E KS -> ON")
        ui.treepop()

    if ui.treenode("Setting [R]"):
        use_r_in_combo = ui.checkbox("Use R in Combo", use_r_in_combo)
        MaxRCountForUse = ui.sliderint ("Max targets use for R", int(MaxRCountForUse), 1, 5)
        ui.treepop()




def CheckWallStun(game, unit, PredictedE):
    global e_range
    PredictedPos = unit.pos
    Direction = PredictedPos.sub(game.player.pos)
    if PredictedE == True:
        # Time = (mesafe(unit.pos, game.player.pos) / 2000) + 0.25
        PredictedPos = unit.pos
        Direction = PredictedPos.sub(game.player.pos)
    for i in range(1, 11):
        ESpot = PredictedPos.add(Direction.normalize().scale(40 * i))
        # game.draw_line(game.world_to_screen(unit.pos), game.world_to_screen(ESpot), 1, Color.GREEN )
        if SRinWall(game, ESpot):
            return ESpot
    return None



def Evade(game):
    global lastQ
    q_spell = getSkill(game, 'Q')


    for missile in game.missiles:
        end_pos = missile.end_pos.clone ()
        start_pos = missile.start_pos.clone ()
        curr_pos = missile.pos.clone ()
        bounding = game.player.gameplay_radius
        spell = get_missile_parent_spell (missile.name)
        if is_skillshot (missile.name) and game.point_on_line(
                game.world_to_screen(start_pos),
                game.world_to_screen(end_pos),
                game.world_to_screen(game.player.pos),
                bounding) and game.is_point_on_screen(curr_pos):
                    pos = getEvadePos (game, game.player.pos, bounding, missile, spell)
                    if pos and lastQ + 1 < game.time :
                        q_spell.move_and_trigger(game.world_to_screen(pos))
                        
                        lastQ = game.time


RTargetCount = 0


def getCountR(game, dist):
    global RTargetCount, MaxRCountForUse
    RTargetCount = 0
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
            RTargetCount = RTargetCount + 1
    if int(RTargetCount) >= MaxRCountForUse:
        return True
    else:
        return False


def EDamage(game, target):

    total_atk = game.player.base_atk + game.player.bonus_atk
    return total_atk
def DrawDMG(game, player):
    color = Color.RED
    player = game.player
    for champ in game.champs:
        if (
            champ.is_alive
            and champ.is_visible
            and champ.is_enemy_to(player)
            and game.is_point_on_screen(champ.pos)
        ):
            if EDamage(game, champ) >= champ.health:
                p = game.hp_bar_pos(champ)
                color.a = 5.0
                game.draw_rect(
                    Vec4(p.x - 47, p.y - 27, p.x + 61, p.y - 12), color, 0, 5
                )
def getVayneAttack2(game):

    for missile in game.missiles:
            # print(missile.name)
            if (missile.name == "vaynebasicattack2" 
            or missile.name == "vaynebasicattack"
            or missile.name == "zyrapseedmis"
            or missile.name == "vaynecritattack"
            or missile.name == "vayneultattack"
            ) :
                return True
    return False

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
    
def Combo(game):
    global lastQ, lastE
    global e_range
    q_spell = getSkill(game, "Q")
    e_spell = getSkill(game, "E")
    r_spell = getSkill(game, "R")

    isPressE = False
    g_time = game.time
    target = GetBestTargetsInRange(game,e["Range"]+300)

    #------------------- Q ---------------
    if (
        use_q_in_combo
        and IsReady(game, q_spell)
        and game.player.mana >= 30
        and not getBuff(game.player, "vaynetumblebonus")
    ):
        if target  :

                if (game.player.pos.distance(target.pos)<700):
                    
                            for buff in target.buffs:
                                if game.player.lvl >= 2:
                                        if buff.name == "VayneSilveredDebuff" :
                                                if buff.countAlt > 0 and getVayneAttack2(game):
                                                    
                                                        for point in range(0, 360, 20):
                                                            bestPoint = None
                                                            lowestDistance = 10000
                                                            highestDistance = 0
                                                            point_temp = math.radians(point)
                                                            pX, pY, pZ = q_range * math.cos(point_temp) + game.player.pos.x, game.player.pos.y,q_range * math.sin(point_temp) + game.player.pos.z + 240
                                                            if Vec3(pX, pY, pZ).distance(target.pos) > highestDistance:
                                                                if  not point_under_turret(game, Vec3(pX, pY, pZ)):
                                                                    highestDistance = Vec3(pX, pY, pZ).distance(target.pos)
                                                                    bestPoint = Vec3(pX, pY, pZ)  
                                                        if bestPoint is not None:
                                                            q_spell.move_and_trigger(game.world_to_screen(bestPoint))
                                                            lastQ = game.time
                                                            

                elif game.player.lvl <= 2:
                        q_spell.trigger (False)
                        
    #----------------  E ----------------
    if (
        use_e_in_combo
        and lastE + 1 < g_time
        and IsReady(game, e_spell)
        and game.player.mana >= 90
    ):
        target = GetBestTargetsInRange(game, e["Range"])
        if target:
            for buff in target.buffs:
                if buff.name == "VayneSilveredDebuff":
                    if buff.countAlt > 1 :


                        if EDamage(game,target)>= target.health:

                            e_spell.move_and_trigger (game.world_to_screen (target.pos))
            if CheckWallStun(game, target, True):
                lastE = game.time
                e_spell.move_and_trigger(game.world_to_screen(target.pos))
    if use_r_in_combo and IsReady(game,r_spell) and game.player.mana>=80:
        if getCountR(game,e["Range"]+300):
            r_spell.trigger (False)
def Harass(game):
    global use_q_with_harass, use_e_with_harass
    global lastQ, lastE
    q_spell = getSkill(game, "Q")
    e_spell = getSkill(game, "E")

    if (
        use_q_with_harass
        and IsReady(game, q_spell)
        and game.player.mana > 30
        and not getBuff(game.player, "vaynetumblebonus")
    ):
        target = GetBestTargetsInRange(game,e["Range"]+300)
        if target:
            
            q_spell.trigger(False)
            
    if (
        use_e_with_harass
        and IsReady(game, e_spell)
        and game.player.mana > 90
    ):
        target = GetBestTargetsInRange(game,e["Range"]+300)
        if target:
            if CheckWallStun(game, target, True):
                
                e_spell.move_and_trigger(game.world_to_screen(target.pos))

def is_interruptible(unit) -> bool:
    return any(buff.name.lower() in ['absolutezero',
    'alzaharnethergrasp',
    'caitlynaceinthehole',
    'crowstorm',
    'destiny',
    'drainChannel',
    'galioIdolofdurand',
    'infiniteduress',
    'karthusfallenone',
    'katarinar',
    'lucianr',
    'meditate',
    'missfortunebullettime',
    'pantheonrjump',
    'pantheonrfall',
    'reapthewhirlwind',
    'shenstandunited',
    'urgotswap2',
    'velkozr',
    'xerathlocusofpower2'] for buff in unit.buffs)

def cast_e(game, target_pos):
    e_spell = getSkill(game, "E")

    return e_spell.move_and_trigger(game.world_to_screen(target_pos))

def point_has_enemy_champ(game, pos: Vec3):

    for champ in game.champs:
        if champ.is_ally_to(game.player):
            continue
        try:
            if pos.distance(champ.pos) < 200:
                return True
        except:
            pass
        
    return False

def e_interrupt_handler(game, target):
    player = game.player
    e_spell = getSkill(game, "E")

    if not IsReady(game,e_spell):
        return False

    if target:
        distance = target.pos.distance(player.pos)
        if distance < e_range + player.gameplay_radius + target.gameplay_radius and is_interruptible(target):
            return cast_e(game, target.pos)

    return False


def AntiGap(game):
    global anti_gap_q, anti_gap_e
    global lastQ, lastE
    q_spell = getSkill(game, "Q")
    e_spell = getSkill(game, "E")
    target = GetBestTargetsInRange(game, 375)
    before_cpos = game.get_cursor()
    highestDistance = 0
    bestPoint = None
    if target and target.atkRange < 375:
        if not IsReady(game, q_spell):
                return
        for point in range(0, 360, 20):
            point_temp = math.radians(point)
            pX, pY, pZ = q_range * math.cos(point_temp) + game.player.pos.x, game.player.pos.y, q_range * math.sin(point_temp) + game.player.pos.z
                    
            if Vec3(pX, pY, pZ).distance(target.pos) > highestDistance:
                if not point_has_enemy_champ(game, Vec3(pX, pY, pZ)) and not point_under_turret(game, Vec3(pX, pY, pZ)):
                    highestDistance = Vec3(pX, pY, pZ).distance(target.pos)
                    bestPoint = Vec3(pX, pY, pZ)
                if not getBuff(game.player, "vaynetumblebonus") and IsReady(game, q_spell) and bestPoint is not None:
                    game.move_cursor(game.world_to_screen(bestPoint))
                    q_spell.trigger(False)
                    
                    game.move_cursor(before_cpos)


def lview_update(game, ui):
    global draw_q_range, draw_e_range,lastQ
    global combo_key, harass_key
    self = game.player

    if self.is_alive and game.is_point_on_screen(self.pos):
        
        
        if anti_gap_e and anti_gap_q:
            AntiGap(game)
        if game.was_key_pressed(combo_key):
            Combo(game)
        target = GetBestTargetsInRange(game, e_range)
        if target is None:
            return
        if e_interrupt and e_interrupt_handler(game, target) and game.player.mana >= 90:
            return
        if game.was_key_pressed(harass_key):
             Harass(game)

        
