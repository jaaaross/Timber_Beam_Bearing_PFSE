import beam_bearing_module as bbm
import math

def test_calc_F_c_perp_prime():
    F_c_perp = 430

    assert math.isclose(bbm.calc_F_c_perp_prime(F_c_perp), 646.29)


def test_calc_loads():
    b1_DL = 1
    b1_LL = 1
    b2_DL = 1
    b2_LL = 1
        
    loads = bbm.calc_loads(b1_DL, b1_LL, b2_DL, b2_LL)
    
    assert math.isclose(loads[0], 2.8)


# Checking six cases to test if the program is calculating bearing areas properly.
# 1. Beam is less wide than column
# 2. Beam is same width as column
# 3. Beam is more wide than column

# 4. Original beam is less wide than column after charring (bearing width not affected)
# 5. Original beam is same width as column after charring (bearing width not affected)
# 6. Original beam is more wide than column after column (bearing width reduced)

def test_calc_nonfire_solution():
    #Case 1
    bw1 = 5
    cw1 = 10
    Fcp1 = 430 # 646.29
    rl1 = 3

    case1 = bbm.calc_nonfire_solution(bw1, cw1, Fcp1, rl1)

    assert math.isclose(case1[0], 9694)

    #Case 2
    bw2 = 5
    cw2 = 5
    Fcp2 = 430 # 646.29
    rl2 = 4

    case2 = bbm.calc_nonfire_solution(bw2, cw2, Fcp2, rl2)

    assert math.isclose(case2[0], 12926)

    #Case 3
    bw3 = 10
    cw3 = 6
    Fcp3 = 430 # 646.29
    rl3 = 3

    case3 = bbm.calc_nonfire_solution(bw3, cw3, Fcp3, rl3)

    assert math.isclose(case3[0], 11633)

    #Case 4
    bw4 = 5
    cw4 = 10
    Fcp4 = 430 # 646.29
    rl4 = 3
    cd4 = 1.8

    case4 = bbm.calc_fire_solution(bw4, cw4, Fcp4, rl4, cd4)

    assert math.isclose(case4[0], 3878)

    #Case 5
    bw5 = 5
    cw5 = 8.6
    Fcp5 = 430 # 646.29
    rl5 = 3
    cd5 = 1.8

    case5 = bbm.calc_fire_solution(bw5, cw5, Fcp5, rl5, cd5)

    assert math.isclose(case5[0], 3878)

    #Case 6
    bw6 = 5
    cw6 = 6
    Fcp6 = 430 # 646.29
    rl6 = 3
    cd6 = 1.8

    case6 = bbm.calc_fire_solution(bw6, cw6, Fcp6, rl6, cd6)

    assert math.isclose(case6[0], 1861)

