N ?= 4
export N
RTL = $(abspath ../../rtl)

SIM ?= icarus
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(RTL)/pe.v $(RTL)/skew.v $(RTL)/systolic.v $(RTL)/systolic_skew.v
COCOTB_TOPLEVEL = systolic_skew
COCOTB_TEST_MODULES = test_systolic_skew
COMPILE_ARGS += -Psystolic_skew.N=$(N)

include $(shell cocotb-config --makefiles)/Makefile.sim
