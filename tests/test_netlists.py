import pytest
import simulador

def netlist(filename):
    c = simulador.import_netlist('tests/' + filename)
    r = c.run()
    r.export('tests/' + filename.replace('.net', '.sim.test'))

def test_chua():
    netlist('chua.net')

def test_dc_source():
    netlist('dc_source.net')

def test_lc():
    netlist('lc.net')

def test_mosfet_curve():
    netlist('mosfet_curve.net')

def test_oscilator():
    netlist('oscilator.net')

def test_pulse():
    netlist('pulse.net')

def test_sinusoidal():
    netlist('sinusoidal.net')