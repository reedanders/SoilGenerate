from data import filter_data, calc_pop

from pulp import *
import pandas

area_msq = 4046.86
prob = LpProblem("GrowthOpt", LpMaximize)

# Import variables with Pandas and create

df, count = filter_data()

variable_names = ['x_{}'.format(index) for index in range(count)]
variable_dict = {name: dict(sci_name=None, cn=None, sun=None, root_depth=None) for name in variable_names}

df_index = 0
for throwaway, row in df.iterrows():

	info = variable_dict[variable_names[df_index]]

	info['sci_name'] = ''.join([x for x in row['Scientific Name'] if ord(x) < 128])
	info['cn'] = row['C:N Ratio']
	info['sun'] = row['Shade Tolerance']
	info['root_depth'] = row['Root Depth, Minimum (inches)']
	info['growth'] = row['Growth Rate']
	info['size'] = row['Height, Mature (feet)']

	max_population = calc_pop(area_msq, row['Height, Mature (feet)'])
	# globals()[variable_names[df_index]] = LpVariable(info['sci_name'], 0, max_population, cat="Integer")
	globals()[variable_names[df_index]] = LpVariable(info['sci_name'], 0, max_population)

	df_index += 1

## Objective
# prob += x_1 + x_2 + x_3 ...

# Growth rate weight
_fast = 1.3
_norm = 1.0
_slow = 0.6

growth_size_list = []

for index, value in enumerate(variable_names):
	temp_growth = variable_dict[value]['growth']
	temp_size = variable_dict[value]['size']

	if temp_growth == "Slow":
		temp_growth = _slow
	if temp_growth == "Moderate":
		temp_growth = _norm
	if temp_growth == "Rapid":
		temp_growth = _fast

	temp_rate = temp_growth*temp_size

	str_rate = str(temp_rate) + "*" + value

	growth_size_list.append(str_rate)


obj = " + ".join(growth_size_list)
prob += eval(obj)

## Constraints

# -----
## C:N Ratio contraint

_low = 1/23
_med = 1/41
_high = 1/91

_cn_max = 1/24
_cn_ideal = 1/30

cn_ideal_list = ['_cn_ideal*{}'.format(var) for var in variable_names]
cn_ideal_str = " + ".join(cn_ideal_list)

cn_actual_list = []

for index, value in enumerate(variable_names):
	temp_cn = variable_dict[value]['cn']
	if temp_cn == "Low":
		temp_cn = _low
	if temp_cn == "Medium":
		temp_cn = _med
	if temp_cn == "High":
		temp_cn = _high

	str_cn = str(temp_cn) + '*' + value

	cn_actual_list.append(str_cn)

cn_actual_str = " + ".join(cn_actual_list)

cn_full_str = cn_actual_str + ">=" + cn_ideal_str
prob += eval(cn_full_str)

# prob += _low*x_1 + _med*x_2 +_med*x_3 >= _cn_ideal*x_1 + _cn_ideal*x_2 + _cn_ideal*x_3
## prob += _low*x_1 + _med*x_2 +_med*x_3 <= _cn_max*x_1 + _cn_max*x_2 + _cn_max*x_3


# -----
## Sunlight contraint
# Space width by height, to maximize leaf production

# Shade intolerant, from tree to groundcover
# prob += x_1 + x_3 >= 7

# Shade intolerant groundcover condition

# Shade intermediate, limit max height to shrub
# prob += x_2 >= 7

# Shade tolerant, limit max height to groundcover


# -----
## Root depth constraint
# Occupy all laters fully
# cm^2*seeds >= total_cm^2

# < 12"
# prob += 1*x_3 >= 7

# 13-24"

# 25-36"
# prob += 1*x_1 + 1*x_2 >= 7

# 37-48"

# > 48"


# Solve

GLPK().solve(prob)

v = prob.variables()

output = []

for solution in v:
	_value = solution.varValue	
	_name = solution.name

	if _value > 0:
		output.append((_name, round(_value)))

print('\Objective: ')
print(prob.objective)

print('\nOUTPUT: ')
print(output)
print(len(output))