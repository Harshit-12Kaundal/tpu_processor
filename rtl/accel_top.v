module accel_top #(parameter N = 4, parameter DEPTH = 8) (
    input  wire        clk,
    input  wire        rst,
    input  wire        cfg_we,
    input  wire        cfg_re,
    input  wire [3:0]  cfg_addr,
    input  wire [7:0]  cfg_data,
    output wire [7:0]  cfg_rdata
);
    wire              rst_core, relu_q;
    wire [4:0]        shift_q;
    wire [N*8-1:0]    w_rows, a_flat, y_flat;
    wire [N*N-1:0]    load_en;
    wire [N*N*8-1:0]  w_flat;

    genvar r;
    generate
        for (r = 0; r < N; r = r + 1) begin : g_wr
            assign w_flat[r*N*8 +: N*8] = {N{w_rows[r*8 +: 8]}};
        end
    endgenerate

    cfg_regs u_cfg (
        .clk(clk), .rst(rst),
        .cfg_we(cfg_we), .cfg_addr(cfg_addr), .cfg_data(cfg_data),
        .rst_core(rst_core), .shift_q(shift_q), .relu_q(relu_q)
    );

    weight_loader #(.N(N)) u_wl (
        .clk(clk), .rst(rst_core),
        .cfg_we(cfg_we), .cfg_addr(cfg_addr), .cfg_data(cfg_data),
        .w_rows(w_rows), .load_en(load_en)
    );

    buf_ctrl #(.N(N), .DEPTH(DEPTH)) u_bc (
        .clk(clk), .rst(rst_core),
        .cfg_we(cfg_we), .cfg_re(cfg_re), .cfg_addr(cfg_addr), .cfg_data(cfg_data),
        .cfg_rdata(cfg_rdata),
        .a_flat(a_flat), .y_flat(y_flat)
    );

    accel_core #(.N(N)) u_core (
        .clk(clk), .rst(rst_core), .load_en(load_en),
        .w_flat(w_flat), .a_flat(a_flat),
        .relu_en(relu_q), .shift(shift_q),
        .y_flat(y_flat)
    );
endmodule
