close all

dat = load("../logs/log_1.5_raw.csv");

e  = dat(:,1);
t  = dat(:,2);
x1 = dat(:,3);
x2 = dat(:,4);

cmap = autumn(9);    % or other color map
dmap = winter(9);    % or other color map

f1 = figure();
f2 = figure();

w = 5000;
tt = 0 + w;

while (tt < 100000 - w)
    set(0, 'currentfigure', f1);
    set(gcf, 'Position',  [100, 100, 2000, 400])
    hold off

    for i=0:8
        subplot(2,9,i+1)
        data_within_window_a = x2(x1==i & t < tt & t > tt - w);
        histogram(data_within_window_a, 'facecolor', cmap(i+1, :))
        if i < 4
            task_type = "HI";
        else
            task_type = "LO";
        end
        title("Task " + i + " (" + task_type + ")")
    end
    
    sgtitle("Response Time with sliding window (before (top) and after (bottom))")

    %figure
    
    for i=0:8
        subplot(2,9,i + 9 +1)
        data_within_window_b = x2(x1==i & t > tt & t < tt + w);
        histogram(data_within_window_b, 'facecolor', dmap(i+1, :))
    end
    
    tt = tt + w;

    set(0, 'currentfigure', f2);
    
    %[x, fval] = gdf(data_within_window_a, data_within_window_b, @emd);

    pause(1)
end
