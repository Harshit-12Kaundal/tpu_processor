N ?= 4
export N
RTL = $(abspath ../../rtl)

SIM ?= icarus
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(RTL)/pe.v $(RTL)/skew.v $(RTL)/systolic.v $(RTL)/deskew.v $(RTL)/matmul_core.v
COCOTB_TOPLEVEL = matmul_core
COCOTB_TEST_MODULES = test_matmul_core
COMPILE_ARGS += -Pmatmul_core.N=$(N)

include $(shell cocotb-config --makefiles)/Makefile.sim
