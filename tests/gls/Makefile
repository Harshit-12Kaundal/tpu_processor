N = 4
export N
PDK := $(shell ls -d $(HOME)/.ciel/ciel/sky130/versions/*/sky130A | head -1)
CELLS = $(PDK)/libs.ref/sky130_fd_sc_hd/verilog
NETLIST ?= $(HOME)/tpu-project/librelane/accel_top/runs/RUN_2026-11-15_11-18-31/final/nl/accel_top.nl.v

SIM ?= icarus
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(CELLS)/primitives.v $(CELLS)/sky130_fd_sc_hd.v $(NETLIST)
COCOTB_TOPLEVEL = accel_top
COCOTB_TEST_MODULES = test_accel_top
COMPILE_ARGS += -DFUNCTIONAL -DUNIT_DELAY=\#1

include $(shell cocotb-config --makefiles)/Makefile.sim
