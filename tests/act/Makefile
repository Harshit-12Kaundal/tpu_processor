N ?= 4
export N
RTL = $(abspath ../../rtl)

SIM ?= icarus
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(RTL)/act.v
COCOTB_TOPLEVEL = act
COCOTB_TEST_MODULES = test_act
COMPILE_ARGS += -Pact.N=$(N)

include $(shell cocotb-config --makefiles)/Makefile.sim
