N ?= 4
export N
RTL = $(abspath ../../rtl)

SIM ?= icarus
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(RTL)/skew.v
COCOTB_TOPLEVEL = skew
COCOTB_TEST_MODULES = test_skew
COMPILE_ARGS += -Pskew.N=$(N)

include $(shell cocotb-config --makefiles)/Makefile.sim
