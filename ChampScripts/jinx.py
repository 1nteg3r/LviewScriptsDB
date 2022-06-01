from lview import *
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import *

lview_script_info = {
    "script": "Jinx",
    "author": "occo/tefan",
    "description": "Jinx",
    "target_champ": "jinx",
}

def buffs(target):
    for buff in t.buffs:
        if 'snare' in buff.name.lower():
            return True
        elif 'stun' in buff.name.lower():
            return True
        elif 'suppress' in buff.name.lower():
            return True
        elif 'root' in buff.name.lower():
            return True
        elif 'taunt' in buff.name.lower():
            return True
        elif 'sleep' in buff.name.lower():
            return True
        elif 'knockup' in buff.name.lower():
            return True
        elif 'binding' in buff.name.lower():
            return True
        elif 'slow' in buff.name.lower() and target.movement_speed < 200:
            return True
    return False

def is_immobile1(target):
    for buff in target.buffs:
        if 'zoeleepstun' in buff.name.lower ():
            return True
        elif 'veigareventhorizonstun' in buff.name.lower ():
            return True
        elif 'snare' in buff.name.lower ():
            return True
        elif 'stun' in buff.name.lower ():
            return True
        elif 'SonaR' in buff.name.lower ():
            return True
        elif 'root' in buff.name.lower ():
            return True
        elif 'taunt' in buff.name.lower ():
            return True
        elif 'sleep' in buff.name.lower ():
            return True
        elif 'knockup' in buff.name.lower ():
            return True
        elif 'binding' in buff.name.lower ():
            return True
        elif 'morganaq' in buff.name.lower ():
            return True
        elif 'jhinw' in buff.name.lower ():
            return True
        elif 'LuxLightBindingMis' in buff.name.lower ():
            return True
        elif 'ryzewroot' in buff.name.lower ():
            return True
        elif 'megaadhevisesnare' in buff.name.lower ():
            return True
        elif 'MorganaQ' in buff.name.lower ():
            return True
        elif 'exhaust' in buff.name.lower ():
            return True
    return False

FishStacks = 0
isFishBones = True

combo_key = 57
harass_key = 46
laneclear_key = 47
flee_key = 30


E_mele = True

Base_ult = True
recalls = {}

use_q_in_combo = True
use_w_in_combo = True
use_e_in_combo = True
use_r_in_combo = True

steal_kill_with_w = False
steal_kill_with_r = False

draw_q_range = False
draw_w_range = False
draw_e_range = False
draw_r_range = False

laneclear_with_q = True

w = {"Range": 1400}
e = {"Range": 900}

mana_w = [50,60,70,80,90]

def lview_load_cfg(cfg):
    global combo_key, harass_key, laneclear_key, flee_key
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global steal_kill_with_w, steal_kill_with_r
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global laneclear_with_q, E_mele, Base_ult

    combo_key = cfg.get_int("combo_key", 57)
    harass_key = cfg.get_int("harass_key", 45)
    laneclear_key = cfg.get_int("laneclear_key", 47)

    use_q_in_combo = cfg.get_bool("use_q_in_combo", True)
    use_w_in_combo = cfg.get_bool("use_w_in_combo", True)
    use_e_in_combo = cfg.get_bool("use_e_in_combo", True)
    use_r_in_combo = cfg.get_bool("use_r_in_combo", True)
    E_mele = cfg.get_bool("E_mele", True)

    draw_q_range = cfg.get_bool("draw_q_range", False)
    draw_w_range = cfg.get_bool("draw_w_range", False)
    draw_e_range = cfg.get_bool("draw_e_range", False)
    draw_r_range = cfg.get_bool("draw_r_range", False)

    steal_kill_with_w = cfg.get_bool("steal_kill_with_w", False)
    steal_kill_with_r = cfg.get_bool("steal_kill_with_r", False)
    Base_ult = cfg.get_bool("Base_ult", True)


def lview_save_cfg(cfg):
    global combo_key, harass_key, laneclear_key, flee_key
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global steal_kill_with_w, steal_kill_with_r
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global laneclear_with_q, E_mele, Base_ult

    cfg.set_int("combo_key", combo_key)
    cfg.set_int("harass_key", harass_key)
    cfg.set_int("laneclear_key", laneclear_key)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_w_in_combo", use_w_in_combo)
    cfg.set_bool("use_e_in_combo", use_e_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)
    cfg.set_bool("E_mele", E_mele)

    cfg.set_bool("draw_q_range", draw_q_range)
    cfg.set_bool("draw_w_range", draw_w_range)
    cfg.set_bool("draw_e_range", draw_e_range)
    cfg.set_bool("draw_r_range", draw_r_range)

    cfg.set_bool("steal_kill_with_w", steal_kill_with_w)
    cfg.set_bool("steal_kill_with_r", steal_kill_with_r)
    cfg.set_bool("Base_ult", Base_ult)


def lview_draw_settings(game, ui):
    global combo_key, harass_key, laneclear_key, flee_key
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global steal_kill_with_w, steal_kill_with_r
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global laneclear_with_q, E_mele, Base_ult

    combo_key = ui.keyselect("Combo key", combo_key)
    harass_key = ui.keyselect("Harass key", harass_key)
    if ui.treenode("Setting [Q]"):
        use_q_in_combo = ui.checkbox("Use Q in Combo mode:(out of basic Q range)", use_q_in_combo)
        laneclear_with_q = ui.checkbox("Check not to use rockets when laneclearing", laneclear_with_q)
        ui.treepop()
    if ui.treenode("Setting [W]"):
        use_w_in_combo = ui.checkbox("Use W in Combo", use_w_in_combo)
        ui.treepop()
    if ui.treenode("Setting [E]"):
        use_e_in_combo = ui.checkbox("Use E on CC / Try and Gapclose", use_e_in_combo)
        E_mele = ui.checkbox('E anti-mele', E_mele)
        ui.treepop()
    if ui.treenode("Setting [R]"):
        use_r_in_combo = ui.checkbox("Use R in Combo", use_r_in_combo)
        Base_ult = ui.checkbox('Base Ult -> BETA AF', Base_ult)
        ui.treepop()
    ui.separator()



qDamages = [20, 40, 55]
rDamages = [200, 320, 440]


def CalcRDmg(game, unit):
    global qDamages
    damage = 0
    distance = game.player.pos.distance(unit.pos)
    mathdist = math.floor(math.floor(distance) / 100)
    level = game.player.R.level
    baseq = rDamages[level - 1] + 0.15 + game.player.bonus_atk
    qmissheal = qDamages[level - 1] / 100 * (unit.max_health - unit.health)
    if distance < 100:
        damage = baseq + qmissheal
    elif distance >= 1500:
        damage = baseq + 10 + qmissheal
    else:
        damage = ((((mathdist * 6) + 10) / 100) * baseq) + baseq + qmissheal
    return rDamages[level - 1] 


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


lastQ = 0
lastW = 0
lastE = 0
lastR = 0

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

def minigun(game):
    if getBuff(game.player, "jinxqramp"):
        return True


def Combo(game):
    global lastQ, lastW, lastE, lastR
    q_spell = getSkill(game, "Q")
    w_spell = getSkill(game, "W")
    e_spell = getSkill(game, "E")
    r_spell = getSkill(game, "R")
    before_cpos = game.get_cursor()
#q swap has logic
    if (
        use_q_in_combo 
        and IsReady(game, q_spell)
    ):
        target = GetBestTargetsInRange(game, (game.player.Q.level * 25) + 75 + 635)
        if ValidTarget(target):
            if game.player.pos.distance(target.pos) > 600 and getBuff(game.player, "jinxqicon")and getBuff(game.player, "jinxqicon").countAlt > 0 and game.player.mana > 20:
                q_spell.trigger(False)  
            elif getBuff(game.player, "JinxQ") and getBuff(game.player, "JinxQ").countAlt > 0 and game.player.pos.distance(target.pos) <= 599:
                q_spell.trigger(False)

    if (
        use_w_in_combo
        and game.player.mana > mana_w[game.player.W.level-1]
        and IsReady(game, w_spell)
        and lastW + 1 < game.time
    ):
        target = GetBestTargetsInRange(game, 1415)
        if ValidTarget(target) and not IsCollisioned(
            game, target
        ):  # and game.player.pos.distance(target.pos) > (game.player.Q.level*25) + 75 + 600:
            distance = game.player.pos.distance(target.pos)
            w_travel_time = distance / 3300
            predicted_pos = predict_pos(target, w_travel_time)
            predicted_target = Fake_target(target.name, predicted_pos, target.gameplay_radius)
            if game.player.pos.distance(predicted_target.pos) > game.player.atkRange and not IsCollisioned(game, predicted_target):
                w_spell.move_and_trigger(game.world_to_screen(predicted_target.pos))

    if (
        use_e_in_combo
        and IsReady(game, e_spell)
        and game.player.mana > 90
        and lastE + 1 < game.time
    ):
        target = GetBestTargetsInRange(game, 900)
        if ValidTarget(target) and is_immobile1(target):
            e_spell.move_and_trigger(game.world_to_screen(target.pos))
            lastE = game.time
        elif ValidTarget(target):
            distance = game.player.pos.distance(target.pos)
            e_travel_time = distance / 3300
            predicted_pos = predict_pos(target, e_travel_time)
            predicted_target = Fake_target(target.name, predicted_pos, target.gameplay_radius)
            if game.player.pos.distance(predicted_target.pos) <= game.player.atkRange:
                e_spell.move_and_trigger(game.world_to_screen(predicted_target.pos))
    if (
        use_r_in_combo
        and IsReady(game, r_spell)
        and game.player.mana > 100
        and lastR + 1 < game.time
    ):
        target = GetBestTargetsInRange(game, 4000)
        if ValidTarget(target):
            distance = game.player.pos.distance(target.pos)
            r_travel_time = distance / 4000
            predicted_pos = predict_pos(target, r_travel_time)
            predicted_target = Fake_target(target.name, predicted_pos, target.gameplay_radius)
            if game.player.pos.distance(predicted_target.pos) > 900 and CalcRDmg(game, target) >= target.health:
                r_spell.move_and_trigger(game.world_to_screen(predicted_target.pos))

def Harass(game):
    global lastQ, lastW, lastE, lastR
    q_spell = getSkill(game, "Q")
    w_spell = getSkill(game, "W")
    e_spell = getSkill(game, "E")
    r_spell = getSkill(game, "R")
    before_cpos = game.get_cursor()

    if (
        use_q_in_combo
        and IsReady(game, q_spell)
    ):
        target = GetBestTargetsInRange(game, (game.player.Q.level * 25) + 75 + 635)
        if ValidTarget(target):
            if getBuff(game.player, "jinxqicon")and getBuff(game.player, "jinxqicon").countAlt > 0 and game.player.mana > 20:
                q_spell.trigger(False)  


def Laneclear(game):
    global lastQ
    q_spell = getSkill(game, "Q")

    if getBuff(game.player, "Q") and getBuff(game.player, "Q").countAlt > 0:
        q_spell.trigger(True)

def antimelee(game):
    E = getSkill(game, "E")
    self =game.player
    target = GetBestTargetsInRange(game, 200)
    if ValidTarget(target) and IsReady(game, E) and self.mana > 90:
        E.move_and_trigger(game.world_to_screen(self.pos))

def getEnemyBase(game):
    redBase = Vec3(14355.25, 171.0, 14386.00)
    blueBase = Vec3(414.0, 183.0, 420.0)
    base = None
    for turret in game.turrets:
        if turret.is_enemy_to(game.player) and turret.has_tags(
            UnitTag.Unit_Structure_Turret_Shrine
        ):
            if turret.pos.distance(redBase) <= 600:
                base = redBase
            else:
                base = blueBase
    return base

supportedChampions = {
    "Jinx": [
        {
            "name": "JinxR",
            "missileName": "JinxR",
            "range": 25000,
            "speed": 1700,
            "maxSpeed": 2500,
            "delay": 0.6,
            "width": 112.5,
            "radius": 225,
            "slot": "R",
            "block": ["hero"],
            "damage": [200, 400, 550],
        },
    ],
}
def calcTravelTimeToBase(game, unit, spell):
    player = supportedChampions.get(game.player.name.capitalize())
    base = getEnemyBase(game)
    dist = unit.pos.distance(base)
    speed = player[0]["speed"]
    delay = player[0]["delay"] + 0.1
    if speed == math.inf and delay != 0:
        return delay
    # if dist > player[0]["range"]:
    #     return 0
    # if speed == 0:
    #     return delay
    if game.player.name == "jinx" and dist > 1350:
        accelerationrate = 0.3
        acceldifference = dist - 1350
        if acceldifference > 150:
            acceldifference = 150
        difference = dist - 1700
        speed = (
            1350 * speed
            + acceldifference * (speed + accelerationrate * acceldifference)
            + difference * 2700
        ) / dist
    # if player[0]["maxSpeed"]:
    #     return (dist - speed) / player[0]["maxSpeed"] + delay + 1
    time = dist / speed + delay

    return time

def lview_update(game, ui):
    self = game.player

    if self.is_alive and game.is_point_on_screen(self.pos) and not game.isChatOpen:

        if game.is_key_down(combo_key):
            Combo(game)
        if game.is_key_down(laneclear_key):
            Laneclear(game)
        if game.is_key_down(harass_key):
            Harass(game)
        if E_mele:
            antimelee(game)
        if Base_ult:
            base = getEnemyBase(game)
        # game.draw_line(
        #     game.world_to_screen(game.player.pos),
        #     game.world_to_screen(cp),
        #     1,
        #     Color.GREEN,
        # )
        for champ in game.champs:
            if champ.is_alive and champ.is_enemy_to(game.player):
                buff = getBuff(champ, "recall")
                if buff:
                    r_spell = getSkill(game, "R")
                    if IsReady(game, r_spell) and game.player.mana > 100:
                        recallTime = int(buff.end_time - game.time)
                        hitTime = calcTravelTimeToBase(game, champ, r_spell)
                        if (
                            hitTime - recallTime >= 0.05
                            and CalcRDmg(game, champ)
                            >= champ.health + (champ.health_regen * 10) + champ.armour
                        ):

                            r_spell.move_and_trigger(game.world_to_minimap(base))
                            pos = game.player.pos
                            game.draw_text(game.world_to_screen(pos).add(Vec2(-25,20)), "BASEULT", Color.GREEN)


        
