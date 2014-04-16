
function [x] =  cvx_ipl_optimization(A,Q,B,G,H,players, subs);
    n = size(Q,2);
    subs = double(subs);
    cvx_begin quiet
        variable x(n) binary

        minimize(Q*x)

        subject to
           A*x == B;
           G*x <= H;
           sum(sum(abs(x(players+1:end)-x(1:end-players))/2)) <= subs
    cvx_end
    x = int8(vec2mat(x,players));
    x'
  

