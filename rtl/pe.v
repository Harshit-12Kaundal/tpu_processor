module pe (
    input  wire               clk,
    input  wire               rst,      // unused: datapath needs no reset
    input  wire               load_w,
    input  wire signed [7:0]  w_in,
    input  wire signed [7:0]  a_in,
    input  wire signed [31:0] psum_in,
    output reg  signed [7:0]  a_out,
    output reg  signed [31:0] psum_out
);
    reg signed [7:0] w;

    always @(posedge clk) begin
        if (load_w) w <= w_in;
        a_out    <= a_in;
        psum_out <= psum_in + a_in * w;
    end
endmodule
