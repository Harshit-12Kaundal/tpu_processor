module act #(parameter N = 4) (
    input  wire               clk,
    input  wire               rst,
    input  wire               relu_en,
    input  wire [4:0]         shift,
    input  wire [N*32-1:0]    y_in_flat,
    output wire [N*8-1:0]     y_out_flat
);
    genvar i;
    generate
        for (i = 0; i < N; i = i + 1) begin : g_lane
            (* keep = "true" *) reg [4:0] sh_q;      // private copy per lane
            (* keep = "true" *) reg       relu_r;
            always @(posedge clk) begin
                sh_q   <= shift;
                relu_r <= relu_en;
            end

            wire signed [31:0] v = y_in_flat[i*32 +: 32];
            wire signed [31:0] r = (relu_r && v < 0) ? 32'sd0 : v;
            wire signed [31:0] s = r >>> sh_q;
            wire [7:0] c = (s > 32'sd127)  ? 8'h7F :
                           (s < -32'sd128) ? 8'h80 : s[7:0];
            reg  [7:0] q;
            always @(posedge clk) begin
                if (rst) q <= 8'd0;
                else     q <= c;
            end
            assign y_out_flat[i*8 +: 8] = q;
        end
    endgenerate
endmodule
