module accel_core #(parameter N = 4) (
    input  wire                clk,
    input  wire                rst,
    input  wire [N*N-1:0]    load_en,
    input  wire [N*N*8-1:0]    w_flat,
    input  wire [N*8-1:0]      a_flat,
    input  wire                relu_en,
    input  wire [4:0]          shift,
    output wire [N*8-1:0]      y_flat
);
    wire [N*32-1:0] y_acc;

    matmul_core #(.N(N)) u_mm (
        .clk(clk), .rst(rst), .load_en(load_en),
        .w_flat(w_flat), .a_flat(a_flat), .y_flat(y_acc)
    );

    act #(.N(N)) u_act (
        .clk(clk), .rst(rst),
        .relu_en(relu_en), .shift(shift),
        .y_in_flat(y_acc), .y_out_flat(y_flat)
    );
endmodule
