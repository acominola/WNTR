from __future__ import print_function
from nose.tools import *
from nose import SkipTest
from os.path import abspath, dirname, join
import wntr

testdir = dirname(abspath(str(__file__)))
datadir = join(testdir,'..','..','tests','networks_for_testing')
net3dir = join(testdir,'..','..','..','examples','networks')
packdir = join(testdir,'..','..','..')

def test_average_water_consumed_net3_node101():
    inp_file = join(net3dir,'Net3.inp')
    wn = wntr.network.WaterNetworkModel(inp_file)
    qbar = wntr.metrics.average_water_consumed(wn)
    expected = 0.012813608
    error = abs((qbar['101'] - expected)/expected)
    assert_less(error, 0.01) # 1% error

def test_population_net6():
    inp_file = join(net3dir,'Net6.inp')
    wn = wntr.network.WaterNetworkModel(inp_file)
    pop = wntr.metrics.population(wn)
    expected = 152000
    error = abs((pop.sum() - expected)/expected)
    assert_less(error, 0.01) # 1% error

"""
Compare the following results to WST impact files using TSG file
121          SETPOINT      100000          0                86400
"""
def test_mass_consumed():
    inp_file = join(net3dir,'Net3.inp')

    wn = wntr.network.WaterNetworkModel(inp_file)

    wn.options.quality.mode = 'CHEMICAL'
    newpat = wntr.network.elements.Pattern.BinaryPattern('NewPattern', 0, 24*3600, wn.options.time.pattern_timestep, wn.options.time.duration)
    wn.add_pattern(newpat.name, newpat)
    wn.add_source('Source1', '121', 'SETPOINT', 100, 'NewPattern')

    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()

    junc_results = results.node.loc[:, :, wn.junction_name_list]
    
    MC = wntr.metrics.mass_contaminant_consumed(junc_results)
    MC_timeseries = MC.sum(axis=1)
    MC_cumsum = MC_timeseries.cumsum()
    #MC_timeseries.to_csv('MC.txt')

    expected = float(39069900000/1000000) # hour 2
    error = abs((MC_cumsum[2*3600] - expected)/expected)
    # print(MC_cumsum[900], expected, error)
    assert_less(error, 0.01) # 1% error

    expected = float(1509440000000/1000000) # hour 12
    error = abs((MC_cumsum[12*3600] - expected)/expected)
    # print(MC_cumsum[12*3600], expected, error)
    assert_less(error, 0.01) # 1% error

def test_volume_consumed():

    inp_file = join(net3dir,'Net3.inp')

    wn = wntr.network.WaterNetworkModel(inp_file)
    
    wn.options.quality.mode = 'CHEMICAL'
    newpat = wntr.network.elements.Pattern.BinaryPattern('NewPattern', 0, 24*3600, wn.options.time.pattern_timestep, wn.options.time.duration)
    wn.add_pattern(newpat.name, newpat)
    wn.add_source('Source1', '121', 'SETPOINT', 100, 'NewPattern')

    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()

    junc_results = results.node.loc[:, :, wn.junction_name_list]

    VC = wntr.metrics.volume_contaminant_consumed(junc_results, 0)
    VC_timeseries = VC.sum(axis=1)
    VC_cumsum = VC_timeseries.cumsum()
    #VC_timeseries.to_csv('VC.txt')

    expected = float(156760/264.172) # hour 2, convert gallons to m3
    error = abs((VC_cumsum[2*3600] - expected)/expected)
    print(VC_cumsum[2*3600], expected, error)
    assert_less(error, 0.02) # 2% error

    expected = float(4867920/264.172) # hour 12, convert gallons to m3
    error = abs((VC_cumsum[12*3600] - expected)/expected)
    print(VC_cumsum[12*3600], expected, error)
    assert_less(error, 0.01) # 1% error

def test_extent_contaminated():

    inp_file = join(net3dir,'Net3.inp')

    wn = wntr.network.WaterNetworkModel(inp_file)
    
    wn.options.quality.mode = 'CHEMICAL'
    newpat = wntr.network.elements.Pattern.BinaryPattern('NewPattern', 0, 24*3600, wn.options.time.pattern_timestep, wn.options.time.duration)
    wn.add_pattern(newpat.name, newpat)
    wn.add_source('Source1', '121', 'SETPOINT', 100, 'NewPattern')

    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()

    EC_cummax = wntr.metrics.extent_contaminant(results.node, results.link, wn, 0)

    expected = float(80749.9*0.3048) # hour 2
    error = abs((EC_cummax[2*3600] - expected)/expected)
    assert_less(error, 0.01) # 1% error

    expected = float(135554*0.3048) # hour 12
    error = abs((EC_cummax[12*3600] - expected)/expected)
    assert_less(error, 0.01) # 1% error

if __name__ == '__main__':
    test_mass_consumed()
    test_volume_consumed()
    test_extent_contaminated()
