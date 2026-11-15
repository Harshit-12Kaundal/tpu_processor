import os
import random
import numpy as np
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

N = int(os.environ.get("N", "4"))


def golden(vals, shift, relu):
    v = np.array(vals, dtype=np.int64)
    if relu:
        v = np.maximum(v, 0)
    return np.clip(v >> shift, -128, 127).tolist()


async def apply(dut, vals, shift, relu):
    packed = 0
    for i, x in enumerate(vals):
        packed |= (x & 0xFFFFFFFF) << (i * 32)
    dut.shift.value = shift
    dut.relu_en.value = int(relu)
    await RisingEdge(dut.clk)        # lane copies capture the config
    dut.y_in_flat.value = packed
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    out = int(dut.y_out_flat.value)
    res = []
    for i in range(N):
        b = (out >> (i * 8)) & 0xFF
        res.append(b - 256 if b & 0x80 else b)
    return res


async def reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst.value = 1
    dut.relu_en.value = 0
    dut.shift.value = 0
    dut.y_in_flat.value = 0
    for _ in range(3):
        await RisingEdge(dut.clk)
    dut.rst.value = 0


@cocotb.test()
async def edge_cases(dut):
    await reset(dut)
    specials = [2**31 - 1, -2**31, 0, 1, -1, 127, 128, -128, -129, 255, 256, -256, 100000, -100000]
    for shift in (0, 1, 7, 8, 16, 24, 31):
        for relu in (False, True):
            for start in range(len(specials)):
                vals = [specials[(start + i) % len(specials)] for i in range(N)]
                got = await apply(dut, vals, shift, relu)
                exp = golden(vals, shift, relu)
                assert got == exp, f"shift={shift} relu={relu} vals={vals} got={got} exp={exp}"


@cocotb.test()
async def random_values(dut):
    await reset(dut)
    for _ in range(500):
        shift = random.randint(0, 31)
        relu = random.random() < 0.5
        vals = [random.randint(-2**31, 2**31 - 1) >> random.randint(0, 24) for _ in range(N)]
        got = await apply(dut, vals, shift, relu)
        exp = golden(vals, shift, relu)
        assert got == exp, f"shift={shift} relu={relu} vals={vals} got={got} exp={exp}"
    dut._log.info(f"act N={N}: ReLU, shift and clamp match NumPy")
