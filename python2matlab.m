load('player-optimization-data.mat');
A_new = kron(eye(days), A);
B_new = repmat(B,days,1);
G_new = kron(eye(days), G);
H_new = repmat(H,days,1);
fprintf(['Beginning Convex Optimization... \n'])
x = cvx_ipl_optimization(A_new, Q_new, B_new, G_new, H_new, numplayers, substitutions)
data = clock;
filename = ['player-selections-', num2str(data(2)) '-' num2str(data(3)) '-' num2str(data(1))...
    '-' num2str(data(4)) ':' num2str(data(5)) ':' num2str(data(6)), '.mat'];
fprintf(['Saving results as ' filename '\n'])
save(filename,'x','scores','days')

