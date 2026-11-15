module accel_top #(parameter N = 4) (
    input  wire                clk,
    input  wire                rst,
    input  wire                cfg_we,
    input  wire [1:0]          cfg_addr,
    input  wire [7:0]          cfg_data,
    input  wire [N*8-1:0]      a_flat,
    output wire [N*8-1:0]      y_flat
);
    wire              rst_core, relu_q;
    wire [4:0]        shift_q;
    wire [N*8-1:0]    w_rows;
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

    accel_core #(.N(N)) u_core (
        .clk(clk), .rst(rst_core), .load_en(load_en),
        .w_flat(w_flat), .a_flat(a_flat),
        .relu_en(relu_q), .shift(shift_q),
        .y_flat(y_flat)
    );
endmodule
