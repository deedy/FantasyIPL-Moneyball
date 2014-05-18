function filename = python2matlab()
    load('player-optimization-data.mat');
    A_new = kron(eye(days), A);
    B_new = repmat(B,days,1);
    G_new = kron(eye(days), G);
    H_new = repmat(H,days,1);
    fprintf(['Beginning Convex Optimization... \n'])
    curr_team = double(curr_team);
    uncapped_mask = repmat(-G(end-4,:)',days,1);
    [x, x_orig,subs_per_day] = cvx_ipl_optimization(A_new, Q_new, B_new, G_new, H_new, numplayers, substitutions, curr_team, uncapped_mask);
    data = clock;
    filename = ['player-sel-', num2str(data(2)) '-' num2str(data(3)) '-' num2str(data(1))...
        '-' num2str(data(4)) ':' num2str(data(5)) ':' num2str(int8(data(6))), '.mat'];
    fprintf(['Saving results as ' filename '\n'])
    nextsubs = subs_per_day(1);
    save(filename,'x','x_orig','scores','days','start_index','curr_team','nextsubs')

end