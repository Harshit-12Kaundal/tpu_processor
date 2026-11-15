module systolic_skew #(parameter N = 4) (
    input  wire                clk,
    input  wire                rst,
    input  wire [N*N-1:0]    load_en,
    input  wire [N*N*8-1:0]    w_flat,
    input  wire [N*8-1:0]      a_flat,    // plain row of activations, no skew needed
    output wire [N*32-1:0]     y_flat
);
    wire [N*8-1:0] a_skewed;

    skew #(.N(N)) u_skew (
        .clk(clk), .rst(rst),
        .a_in_flat(a_flat),
        .a_out_flat(a_skewed)
    );

    systolic #(.N(N)) u_sys (
        .clk(clk), .rst(rst), .load_en(load_en),
        .w_flat(w_flat),
        .a_flat(a_skewed),
        .y_flat(y_flat)
    );
endmodule
