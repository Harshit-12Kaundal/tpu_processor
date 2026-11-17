module buf_ctrl #(parameter N = 4, parameter DEPTH = 16) (
    input  wire               clk,
    input  wire               rst,
    input  wire               cfg_we,
    input  wire               cfg_re,
    input  wire [3:0]         cfg_addr,
    input  wire [7:0]         cfg_data,
    output reg  [7:0]         cfg_rdata,
    output wire [N*8-1:0]     a_flat,
    input  wire [N*8-1:0]     y_flat
);
    localparam LATW = 2*N + 1;      // cnt value at which output row 0 is valid
    localparam NB   = DEPTH*N;
    localparam PW   = $clog2(NB);

    reg [7:0]     in_mem  [0:NB-1];
    reg [7:0]     out_mem [0:NB-1];
    reg [PW-1:0]  in_wptr, out_rptr;
    reg [7:0]     m_rows;
    reg [15:0]    cnt;
    reg           busy, done;
    reg [N*8-1:0] a_q;

    assign a_flat = a_q;

    wire [N*8-1:0] a_row;
    genvar r;
    generate
        for (r = 0; r < N; r = r + 1) begin : g_arow
            assign a_row[r*8 +: 8] = in_mem[cnt*N + r];
        end
    endgenerate

    wire        feed    = busy && (cnt < m_rows);
    wire [15:0] wr_row  = cnt - LATW;
    wire        store   = busy && (cnt >= LATW) && (wr_row < m_rows);

    integer k;
    always @(posedge clk) begin
        if (rst) begin
            in_wptr   <= {PW{1'b0}};
            out_rptr  <= {PW{1'b0}};
            m_rows    <= 8'd0;
            cnt       <= 16'd0;
            busy      <= 1'b0;
            done      <= 1'b0;
            cfg_rdata <= 8'd0;
            a_q       <= {N*8{1'b0}};
        end else begin
            a_q <= feed ? a_row : {N*8{1'b0}};

            if (cfg_we) begin
                case (cfg_addr)
                    4'd4: begin
                        in_mem[in_wptr] <= cfg_data;
                        in_wptr <= in_wptr + 1'b1;
                    end
                    4'd5: begin
                        in_wptr  <= {PW{1'b0}};
                        out_rptr <= {PW{1'b0}};
                        done     <= 1'b0;
                    end
                    4'd6: if (!busy) begin
                        m_rows   <= cfg_data;
                        cnt      <= 16'd0;
                        busy     <= 1'b1;
                        done     <= 1'b0;
                        out_rptr <= {PW{1'b0}};
                    end
                    default: ;
                endcase
            end

            if (cfg_re) begin
                case (cfg_addr)
                    4'd7: begin
                        cfg_rdata <= out_mem[out_rptr];
                        out_rptr  <= out_rptr + 1'b1;
                    end
                    4'd8:    cfg_rdata <= {6'b0, busy, done};
                    default: cfg_rdata <= 8'd0;
                endcase
            end

            if (busy) begin
                if (store) begin
                    for (k = 0; k < N; k = k + 1)
                        out_mem[wr_row*N + k] <= y_flat[k*8 +: 8];
                end
                if (cnt == m_rows + LATW - 1) begin
                    busy <= 1'b0;
                    done <= 1'b1;
                end else begin
                    cnt <= cnt + 1'b1;
                end
            end
        end
    end
endmodule
