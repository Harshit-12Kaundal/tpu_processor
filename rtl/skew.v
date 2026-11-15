module skew #(parameter N = 4) (
    input  wire               clk,
    input  wire               rst,
    input  wire [N*8-1:0]     a_in_flat,
    output wire [N*8-1:0]     a_out_flat
);
    genvar r;
    generate
        for (r = 0; r < N; r = r + 1) begin : g_row
            if (r == 0) begin : g_zero
                assign a_out_flat[r*8 +: 8] = a_in_flat[r*8 +: 8];
            end else begin : g_delay
                reg [7:0] sr [0:r-1];
                integer k;
                always @(posedge clk) begin
                    if (rst) begin
                        for (k = 0; k < r; k = k + 1) sr[k] <= 8'd0;
                    end else begin
                        sr[0] <= a_in_flat[r*8 +: 8];
                        for (k = 1; k < r; k = k + 1) sr[k] <= sr[k-1];
                    end
                end
                assign a_out_flat[r*8 +: 8] = sr[r-1];
            end
        end
    endgenerate
endmodule
