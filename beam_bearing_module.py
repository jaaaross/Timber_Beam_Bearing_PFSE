from dataclasses import dataclass
import beam_bearing_module as bbm

from handcalcs.decorator import handcalc
calc_renderer = handcalc()

@dataclass
class BearingNode:
    b1_w: float
    b1_d: float
    b1_DL: float
    b1_LL: float
    b1_rl: float
    b2_w: float
    b2_d: float
    b2_DL: float
    b2_LL: float
    b2_rl: float
    c_w: float
    c_d: float
    F_c_perp: float
    char_depth: float


    def call_calculation(self):
        b1_nonfire = calc_nonfire_solution(self.b1_w, self.c_w, self.F_c_perp, self.b1_rl)
        b2_nonfire = calc_nonfire_solution(self.b2_w, self.c_w, self.F_c_perp, self.b2_rl)
        
        b1_fire = calc_fire_solution(self.b1_w, self.c_w, self.F_c_perp, self.b1_rl, self.char_depth)
        b2_fire = calc_fire_solution(self.b2_w, self.c_w, self.F_c_perp, self.b2_rl, self.char_depth)
        
        loads = calc_loads(self.b1_DL, self.b1_LL, self.b2_DL, self.b2_LL)

        return b1_nonfire, b2_nonfire, b1_fire, b2_fire, loads


def calc_loads(b1_DL:float, b1_LL:float, b2_DL:float, b2_LL:float) -> float:
    b1_factored = 1.2 * b1_DL + 1.6 * b1_LL
    b1_unfactored = b1_DL + b1_LL

    b2_factored = 1.2 * b2_DL + 1.6 * b2_LL
    b2_unfactored = b2_DL + b2_LL
    
    return b1_factored, b1_unfactored, b2_factored, b2_unfactored


def calc_F_c_perp_prime(F_c_perp:float, C_M=1, C_t=1, C_b=1, K_F=1.67, phi=0.9) -> float:        
    F_c_perp_prime = F_c_perp * C_M * C_t * C_b * K_F * phi
        
    return F_c_perp_prime
    

def calc_nonfire_solution(beam_width:float, column_width:float, F_c_perp:float, routing_length:float) -> float:
    F_c_perp_prime = calc_F_c_perp_prime(F_c_perp)

    if column_width >= beam_width:
        bearing_width = beam_width
    else:
        bearing_width = column_width
        
    nonfire_capacity = F_c_perp_prime * bearing_width * routing_length

    return round(nonfire_capacity,0), bearing_width, routing_length


def calc_fire_solution(beam_width:float, column_width:float, F_c_perp: float, routing_length:float, char_depth:float) -> float:
    F_c_perp_prime = calc_F_c_perp_prime(F_c_perp)

    charred_column_width = column_width - char_depth * 2

    if charred_column_width >= beam_width:
        charred_bearing_width = beam_width
    else:
        charred_bearing_width = charred_column_width
    
    if  routing_length <= char_depth:
        charred_routing_length = 0
    else:
        charred_routing_length = routing_length - char_depth

    fire_capacity = F_c_perp_prime * charred_bearing_width * charred_routing_length

    return round(fire_capacity,0), charred_bearing_width, charred_routing_length

