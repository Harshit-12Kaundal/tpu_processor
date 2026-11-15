N ?= 4
export N
RTL = $(abspath ../../rtl)

SIM ?= icarus
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(RTL)/pe.v $(RTL)/skew.v $(RTL)/systolic.v $(RTL)/deskew.v $(RTL)/matmul_core.v $(RTL)/act.v $(RTL)/accel_core.v
COCOTB_TOPLEVEL = accel_core
COCOTB_TEST_MODULES = test_accel_core
COMPILE_ARGS += -Paccel_core.N=$(N)

include $(shell cocotb-config --makefiles)/Makefile.sim
