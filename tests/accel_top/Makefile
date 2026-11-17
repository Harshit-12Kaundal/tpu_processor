N ?= 4
export N
RTL = $(abspath ../../rtl)

SIM ?= icarus
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(RTL)/pe.v $(RTL)/skew.v $(RTL)/systolic.v $(RTL)/deskew.v $(RTL)/matmul_core.v $(RTL)/act.v $(RTL)/accel_core.v $(RTL)/cfg_regs.v $(RTL)/weight_loader.v $(RTL)/buf_ctrl.v $(RTL)/accel_top.v
COCOTB_TOPLEVEL = accel_top
COCOTB_TEST_MODULES = test_accel_top
COMPILE_ARGS += -Paccel_top.N=$(N)

include $(shell cocotb-config --makefiles)/Makefile.sim
