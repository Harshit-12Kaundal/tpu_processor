module deskew #(parameter N = 4) (
    input  wire                clk,
    input  wire                rst,
    input  wire [N*32-1:0]     y_in_flat,
    output wire [N*32-1:0]     y_out_flat
);
    genvar c;
    generate
        for (c = 0; c < N; c = c + 1) begin : g_col
            if (c == N - 1) begin : g_zero
                assign y_out_flat[c*32 +: 32] = y_in_flat[c*32 +: 32];
            end else begin : g_delay
                localparam D = N - 1 - c;
                reg [31:0] sr [0:D-1];
                integer k;
                always @(posedge clk) begin
                    if (rst) begin
                        for (k = 0; k < D; k = k + 1) sr[k] <= 32'd0;
                    end else begin
                        sr[0] <= y_in_flat[c*32 +: 32];
                        for (k = 1; k < D; k = k + 1) sr[k] <= sr[k-1];
                    end
                end
                assign y_out_flat[c*32 +: 32] = sr[D-1];
            end
        end
    endgenerate
endmodule
