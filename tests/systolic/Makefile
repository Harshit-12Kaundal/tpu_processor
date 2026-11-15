N ?= 4
export N
RTL = $(abspath ../../rtl)

SIM ?= icarus
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(RTL)/pe.v $(RTL)/systolic.v
COCOTB_TOPLEVEL = systolic
COCOTB_TEST_MODULES = test_systolic
COMPILE_ARGS += -Psystolic.N=$(N)

include $(shell cocotb-config --makefiles)/Makefile.sim
