import streamlit as st
import beam_bearing_module as bbm

from handcalcs.decorator import handcalc
calc_renderer = handcalc()


# For Later Versions - a 20mm subtraction of bearing width to account for the chamfer that is generally done around corners at connection to simplify CNC
# - the ignoring of remaining column material around the connection when the remaining material is not thick enough to rely on it being there after transport
# - would really like to add a report print function for easy documentation
# - in far future, would like to be able to load in a building from ETABS or similar, have it parse thru member sizes, loads, etc, then either the user adjusts
# bearing lengths or the software determines them to pass the bearing check at a certain percentage. After all of this, I want to print all of this information
# as a table that can be included in design drawings.


st.set_page_config(layout="wide")

st.title("Timber Beam Bearing Calculator")

st.sidebar.subheader("Beam 1 Parameters")
beam1_width = st.sidebar.number_input("Beam 1 Width (in)", value = 6)
beam1_depth = st.sidebar.number_input("Beam 1 Depth (in)", value = 10)
beam1_dead_load = st.sidebar.number_input("Beam 1 Dead Load (lbs)", value = 1000)
beam1_live_load = st.sidebar.number_input("Beam 1 Live Load (lbs)", value = 1000)

st.sidebar.subheader("Beam 2 Parameters")
beam2_width = st.sidebar.number_input("Beam 2 Width (in)", value = 8)
beam2_depth = st.sidebar.number_input("Beam 2 Depth (in)", value = 12)
beam2_dead_load = st.sidebar.number_input("Beam 2 Dead Load (lbs)", value = 2000)
beam2_live_load = st.sidebar.number_input("Beam 2 Live Load (lbs)", value = 3000)

st.sidebar.subheader("Column Parameters")
column_width = st.sidebar.number_input("Column Width (in)", value = 8)
column_depth = st.sidebar.number_input("Column Depth (in)", value = 10)

st.sidebar.subheader("Design Parameters")
F_c_perp = st.sidebar.number_input("F_c_perp (psi)", value = 430)


FRR = st.sidebar.selectbox(
    "Fire Design Requirement",
    ("0 hour", "1 hour", "2 hour")
)

beam1_route_length = st.slider(label="Beam 1 Routing Length (in)", key = 0, min_value = float(2.25), max_value = float(column_depth), step=float(0.125))
beam2_route_length = st.slider(label="Beam 2 Routing Length (in)", key = 1, min_value = float(2.25), max_value = float(column_depth), step=float(0.125))

if FRR == "0 hour":
    char_depth = 0
elif FRR == "1 hour":
    char_depth = 1.8
elif FRR == "2 hour":
    char_depth = 3.2


BearingNode = bbm.BearingNode(beam1_width,
    beam1_depth,
    beam1_dead_load,
    beam1_live_load,
    beam1_route_length,
    beam2_width,
    beam2_depth,
    beam2_dead_load,
    beam2_live_load,
    beam2_route_length,
    column_width,
    column_depth,
    F_c_perp,
    char_depth
    )


b1_nonfire, b2_nonfire, b1_fire, b2_fire, loads = BearingNode.call_calculation()

ratios = []

ratios.append(round(loads[0]/b1_nonfire[0],3))

if b1_fire[0] == 0:
    ratios.append(100000)
else:
    ratios.append(round(loads[1]/b1_fire[0],3))
    
ratios.append(round(loads[2]/b2_nonfire[0],3))

if b2_fire[0] == 0:
    ratios.append(100000)
else:
    ratios.append(round(loads[3]/b2_fire[0],3))

# NONFIRE CASE
# bx_nonfire = capacity, bearing width, routing length
# loads = b1_f, b1_u, b2_f, b2_u


from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection

col1, col2 = st.columns(2)

column_outline = Rectangle([0, 0], column_width, column_depth, angle=0, facecolor='peachpuff', edgecolor='black')
beam1_outline = Rectangle([column_width/2-beam1_width/2, column_depth-beam1_route_length], beam1_width, column_depth*0.8, angle=0, facecolor='green', edgecolor='black')
beam2_outline = Rectangle([column_width/2-beam2_width/2, beam2_route_length], beam2_width, -column_depth*0.8, angle=0, facecolor='blue', edgecolor='black')
column_outline2 = Rectangle([0, 0], column_width, column_depth, angle=0, facecolor='peachpuff', edgecolor='black', fill=False, ls='--')

if column_width >= beam1_width:
    b1_nf_rect_x_pos = column_width/2-beam1_width/2
else:
    b1_nf_rect_x_pos = 0

if column_width >= beam2_width:
    b2_nf_rect_x_pos = column_width/2-beam2_width/2
else:
    b2_nf_rect_x_pos = 0

b1_nf_bearing_area = Rectangle([b1_nf_rect_x_pos, column_depth-b1_nonfire[2]],b1_nonfire[1],b1_nonfire[2], angle=0, facecolor='magenta', edgecolor='red')
b2_nf_bearing_area = Rectangle([b2_nf_rect_x_pos, 0],b2_nonfire[1],b2_nonfire[2], angle=0, facecolor='magenta', edgecolor='red')

fig = Figure()
nf = fig.gca()

nf.add_patch(column_outline)
nf.add_patch(beam1_outline)
nf.add_patch(beam2_outline)
nf.add_patch(b1_nf_bearing_area)
nf.add_patch(b2_nf_bearing_area)
nf.add_patch(column_outline2)

nf.set_xlim(-column_width, column_width * 2)
nf.set_ylim(-column_depth, column_depth * 2)
nf.set_aspect('equal')

nf.text(-column_width*0.6,column_depth*1.9, ('Non-fire Case'), fontsize = 5, ha = 'center')
nf.text(column_width/2, column_depth*1.75, ("Beam 1 Effective Bearing Area = " + str(round(b1_nonfire[1],3)) + " inch wide x " + str(round(b1_nonfire[2],3)) + " inch long."), fontsize = 5, ha = 'center')
nf.text(column_width/2, -column_depth*0.8, ("Beam 2 Effective Bearing Area = " + str(round(b2_nonfire[1],3)) + " inch wide x " + str(round(b2_nonfire[2],3)) + " inch long."), fontsize = 5, ha = 'center')

with col1:
    if beam1_route_length + beam2_route_length > column_depth:
        st.write('Your beam routing is overlapping. Please reduce one side.')

    if ratios[0] > 1:
        st.write("Non-fire capacity is " + str(b1_nonfire[0]) + " lbs. Demand is " + str(loads[0]) + " lbs. Ratio = " + str(ratios[0]) + ". FAIL!")
    else:
        st.write("Non-fire capacity is " + str(b1_nonfire[0]) + " lbs. Demand is " + str(loads[0]) + " lbs. Ratio = " + str(ratios[0]) + ". PASS!")
    if ratios[2] > 1:
        st.write("Non-fire capacity is " + str(b2_nonfire[0]) + " lbs. Demand is " + str(loads[2]) + " lbs. Ratio = " + str(ratios[2]) + ". FAIL!")
    else:
        st.write("Non-fire capacity is " + str(b2_nonfire[0]) + " lbs. Demand is " + str(loads[2]) + " lbs. Ratio = " + str(ratios[2]) + ". PASS!")
    fig


# FIRE CASE

if column_width - char_depth*2 >= beam1_width:
    b1_f_rect_x_pos = column_width/2-beam1_width/2
else:
    b1_f_rect_x_pos = char_depth

if column_width - char_depth*2 >= beam2_width:
    b2_f_rect_x_pos = column_width/2-beam2_width/2
else:
    b2_f_rect_x_pos = char_depth


#repeated code here because it doesn't let you put the same shape on two figures
column_outline = Rectangle([0, 0], column_width, column_depth, angle=0, facecolor='peachpuff', edgecolor='black')
beam1_outline = Rectangle([column_width/2-beam1_width/2, column_depth-beam1_route_length], beam1_width, column_depth*0.8, angle=0, facecolor='green', edgecolor='black')
beam2_outline = Rectangle([column_width/2-beam2_width/2, beam2_route_length], beam2_width, -column_depth*0.8, angle=0, facecolor='blue', edgecolor='black')
column_outline2 = Rectangle([0, 0], column_width, column_depth, angle=0, facecolor='peachpuff', edgecolor='black', fill=False, ls='--')

b1_f_bearing_area = Rectangle([b1_f_rect_x_pos, column_depth-beam1_route_length],b1_fire[1],b1_fire[2], angle=0, facecolor='magenta', edgecolor='black')
b2_f_bearing_area = Rectangle([b2_f_rect_x_pos, char_depth],b2_fire[1],b2_fire[2], angle=0, facecolor='magenta', edgecolor='black')

column_char_outline = Rectangle([char_depth,char_depth], column_width - char_depth*2, column_depth-char_depth*2, angle=0, edgecolor='red', fill = False)

fig = Figure()
f = fig.gca()

f.add_patch(column_outline)
f.add_patch(beam1_outline)
f.add_patch(beam2_outline)
f.add_patch(column_outline2)

f.add_patch(b1_f_bearing_area)
f.add_patch(b2_f_bearing_area)

f.add_patch(column_char_outline)

f.set_xlim(-column_width, column_width * 2)
f.set_ylim(-column_depth, column_depth * 2)
f.set_aspect('equal')

f.text(-column_width*0.6,column_depth*1.9, (FRR + ' Fire Case'), fontsize = 5, ha = 'center')
f.text(column_width/2, column_depth*1.75, ("Beam 1 Effective Bearing Area = " + str(round(b1_fire[1],3)) + " inch wide x " + str(round(b1_fire[2],3)) + " inch long."), fontsize = 5, ha = 'center')
f.text(column_width/2, -column_depth*0.8, ("Beam 2 Effective Bearing Area = " + str(round(b2_fire[1],3)) + " inch wide x " + str(round(b2_fire[2],3)) + " inch long."), fontsize = 5, ha = 'center')


with col2:
    if ratios[1] == 100000:
        st.write("After " + FRR + " fire, beam 1 has no bearing material remaining. Increase bearing length.")
    elif ratios[1] > 1:
        st.write(FRR + " fire capacity is " + str(b1_fire[0]) + " lbs. Demand is " + str(loads[1]) + " lbs. Ratio = " + str(ratios[1]) + ". FAIL!")
    else:
        st.write(FRR + " fire capacity is " + str(b1_fire[0]) + " lbs. Demand is " + str(loads[1]) + " lbs. Ratio = " + str(ratios[1]) + ". PASS!")
    if ratios[3] == 100000:
        st.write("After " + FRR + " fire, beam 2 has no bearing material remaining. Increase bearing length.")
    elif ratios[3] > 1:
        st.write(FRR + " fire capacity is " + str(b2_fire[0]) + " lbs. Demand is " + str(loads[3]) + " lbs. Ratio = " + str(ratios[3]) + ". FAIL!")
    else:
        st.write(FRR + " fire capacity is " + str(b2_fire[0]) + " lbs. Demand is " + str(loads[3]) + " lbs. Ratio = " + str(ratios[3]) + ". PASS!")
    fig



@handcalc()
def handcalc(F_c_perp:float, bearingwidth_nonfire:float, bearinglength_nonfire:float, bearingwidth_fire:float, bearinglength_fire:float, load_factored:float, load_unfactored:float, C_M=1, C_t=1, C_b=1, K_F=1.67, phi=0.9):        
    F_c_perp_prime = F_c_perp * C_M * C_t * C_b * K_F * phi

    Areqd_nonfire = load_factored/F_c_perp_prime

    bearingarea_nonfire = bearingwidth_nonfire * bearinglength_nonfire

    ratio_nonfire = Areqd_nonfire/bearingarea_nonfire

    Areqd_fire = load_unfactored/F_c_perp_prime

    bearingarea_fire = bearingwidth_fire * bearinglength_fire

    ratio_fire = Areqd_fire/bearingarea_fire

    return locals()

sample_b1_nonfire_w = b1_nonfire[1]
sample_b1_nonfire_l = b1_nonfire[2]
sample_b1_fire_w = b1_fire[1]
sample_b1_fire_l = b1_fire[2]
sample_f_loads = loads[0]
sample_u_loads = loads[1]



latex_code, result = handcalc(F_c_perp, sample_b1_nonfire_w, sample_b1_nonfire_l, sample_b1_fire_w, sample_b1_fire_l, sample_f_loads, sample_u_loads)

calc_expander_a = st.expander(label="Beam 1 Sample Calculation")

with calc_expander_a:
    st.latex(latex_code)





