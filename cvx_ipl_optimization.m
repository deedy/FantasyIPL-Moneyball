
function [x, x_orig, subs_per_day] =  cvx_ipl_optimization(A,Q,B,G,H,players, subs, curr_team, uncapped_mask);
    n = size(Q,2);
    x_orig = [];
    if subs ~= 0 
        subs = double(subs);
        cvx_begin 
            cvx_precision(0.01)
            variable x(n) binary
            variable uncapped_subs
            minimize(Q*x)

            subject to
               A*x == B;
               G*x <= H;
               max(uncapped_mask.*(x(1:end)-[curr_team'; x(1:end-players)])) <= 1;
               uncapped_subs == sum(uncapped_mask.*(x(1:end)-[curr_team'; x(1:end-players)]));
               sum(sum(abs(x(1:end)-[curr_team'; x(1:end-players)])/2)) <= subs + uncapped_subs;
% % % %                %                sum(abs(x(1:players)-curr_team')/2) <= 10;
        cvx_end
        x_orig = x;
        x = int8(vec2mat(x,players));
    else
        cvx_begin quiet
            variable x(n) binary

            minimize(Q*x)

            subject to
               A*x == B;
               G*x <= H;
        cvx_end
        x_orig = x;
        x = int8(vec2mat(x,players))';
    end
    
    subs_per_day = sum(vec2mat(abs(x_orig(1:end)-[curr_team'; x_orig(1:end-178)]),178)')/2
    uncapped_subs
  

