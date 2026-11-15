import os
import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

N = int(os.environ.get("N", "4"))


@cocotb.test()
async def skew_delays(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    dut.a_in_flat.value = 0
    for _ in range(3):
        await RisingEdge(dut.clk)
    dut.rst.value = 0

    T = 50
    x = [[random.randint(0, 255) for _ in range(N)] for _ in range(T)]

    for k in range(T):
        packed = 0
        for r in range(N):
            packed |= x[k][r] << (r * 8)
        dut.a_in_flat.value = packed
        await Timer(1, unit="ns")          # let combinational row 0 settle
        out = int(dut.a_out_flat.value)    # what the next flop would capture at edge k
        for r in range(N):
            got = (out >> (r * 8)) & 0xFF
            exp = x[k - r][r] if k >= r else 0   # row r is r cycles late
            assert got == exp, f"cycle {k} row {r}: got {got}, expected {exp}"
        await RisingEdge(dut.clk)

    dut._log.info(f"skew N={N}: row r is delayed by exactly r cycles")
