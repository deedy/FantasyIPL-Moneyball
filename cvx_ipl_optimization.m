 
function [x, x_orig, subs_per_day] =  cvx_ipl_optimization(A,Q,B,G,H,players, subs, curr_team, uncapped_mask);
    n = size(Q,2);
    x_orig = [];
    if subs ~= 0 
        subs = double(subs);
        k=1;
        cvx_begin 
            cvx_precision(0.01);
            variable x(n) binary
%             variable uncapped_subs(n)
%             variable uncap
            minimize(Q*x)

            subject to
               A*x == B;
               G*x <= H;
%                max(sum(vec2mat(uncapped_mask.*(x(1:end)-[curr_team'; x(1:end-players)]),178)')) <=1
%                max(uncapped_mask.*(x(1:end)-[curr_team'; x(1:end-players)])) <= 1;
%                uncapped_subs ==  (sum(uncapped_mask.*(x(1:end)-[curr_team'; x(1:end-players)]))>0).*(sum(uncapped_mask.*(x(1:end)-[curr_team'; x(1:end-players)])))
%                uncapped_subs == sum(uncapped_mask.*(x(1:end)-[curr_team'; x(1:end-players)]));
               
                
               
               
%                uncapped_subs ==  uncapped_mask.*(x(1:end)-[curr_team'; x(1:end-players)])
%                for k = 0 : (n/players)-1,
%                    sum(uncapped_subs((k*players + 1): ((k+1)*players))) <=1
% %                    sum(abs(x((k*players + 1): ((k+1)*players)) - x(((k-1)*players + 1): (k*players)))/2) <=4;
%                end
%                (sum(uncapped_subs) + (sum(abs(uncapped_subs)) - sum(uncapped_subs))/2) == uncap
                % overall sub cap
               sum(sum(abs(x(1:end)-[curr_team'; x(1:end-players)])/2)) <= subs  ;
               
               % Arbitrary daily trading cap
               sum(abs(x(1:players)-curr_team')/2) <= 3;
               for k = 1 : (n/players)-1,
%                 sum(abs(x(179, 356))) <= 10;
                        sum(abs(x((k*players + 1): ((k+1)*players)) - x(((k-1)*players + 1): (k*players)))/2) <=3;
               end
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
%     uncapped_subs
  

