clear
close all

%% load data from csv files
data_raw_1 = load("../logs/log_0.1_meta.csv");
data_raw_2 = load("../logs/log_0.3_meta.csv");
data_raw_3 = load("../logs/log_0.5_meta.csv");
data_raw_4 = load("../logs/log_0.7_meta.csv");
data_raw_5 = load("../logs/log_0.9_meta.csv");


%%
jne1_1 = data_raw_1(:,2);
jne1_2 = data_raw_1(:,3) - data_raw_1(:,2);
jne1_3 = data_raw_1(:,4) - data_raw_1(:,3);

jne2_1 = data_raw_2(:,2);
jne2_2 = data_raw_2(:,3) - data_raw_2(:,2);
jne2_3 = data_raw_2(:,4) - data_raw_2(:,3);

jne3_1 = data_raw_3(:,2);
jne3_2 = data_raw_3(:,3) - data_raw_3(:,2);
jne3_3 = data_raw_3(:,4) - data_raw_3(:,3);

jne4_1 = data_raw_4(:,2);
jne4_2 = data_raw_4(:,3) - data_raw_4(:,2);
jne4_3 = data_raw_4(:,4) - data_raw_4(:,3);

jne5_1 = data_raw_5(:,2);
jne5_2 = data_raw_5(:,3) - data_raw_5(:,2);
jne5_3 = data_raw_5(:,4) - data_raw_5(:,3);

figure
subplot(5,1,1)
bar([jne1_1, jne1_2, jne1_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.1')

subplot(5,1,2)
bar([jne2_1, jne2_2, jne2_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.3')

subplot(5,1,3)
bar([jne3_1, jne3_2, jne3_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.5')

subplot(5,1,4)
bar([jne4_1, jne4_2, jne4_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.7')

subplot(5,1,5)
bar([jne5_1, jne5_2, jne5_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.9')





%
figure
subplot(2,1,1)
boxplot([jne1_2, jne1_3, [], jne2_2, jne2_3, [], jne3_2, jne3_3, [], jne4_2, jne4_3, [], jne5_2, jne5_3])
title("Distribution of JNE")

% set boxplot face color
colors = rand(12, 3);
h = findobj(gca,'Tag','Box');
for j=1:length(h)
    if mod(j,2)
        patch(get(h(j),'XData'),get(h(j),'YData'),colors(1,:),'FaceAlpha',.5);
    else
        patch(get(h(j),'XData'),get(h(j),'YData'),colors(2,:),'FaceAlpha',.5);
    end
end

subplot(2,1,2)
boxplot([(jne1_2 - jne1_3) ./ jne1_1, (jne2_2 - jne2_3) ./ jne2_1, (jne3_2 - jne3_3) ./ jne3_1, (jne4_2 - jne4_3) ./ jne4_1, (jne5_2 - jne5_3) ./ jne5_1])
xticklabels({'U = 0.1', '0.3', '0.5', '0.7', '0.9'})
title("Distribution of JNE improvement")




%%
jne1_1 = data_raw_1(:,2+3);
jne1_2 = data_raw_1(:,3+3) - data_raw_1(:,2+3);
jne1_3 = data_raw_1(:,4+3) - data_raw_1(:,3+3);

jne2_1 = data_raw_2(:,2+3);
jne2_2 = data_raw_2(:,3+3) - data_raw_2(:,2+3);
jne2_3 = data_raw_2(:,4+3) - data_raw_2(:,3+3);

jne3_1 = data_raw_3(:,2+3);
jne3_2 = data_raw_3(:,3+3) - data_raw_3(:,2+3);
jne3_3 = data_raw_3(:,4+3) - data_raw_3(:,3+3);

jne4_1 = data_raw_4(:,2+3);
jne4_2 = data_raw_4(:,3+3) - data_raw_4(:,2+3);
jne4_3 = data_raw_4(:,4+3) - data_raw_4(:,3+3);

jne5_1 = data_raw_5(:,2+3);
jne5_2 = data_raw_5(:,3+3) - data_raw_5(:,2+3);
jne5_3 = data_raw_5(:,4+3) - data_raw_5(:,3+3);

figure
subplot(5,1,1)
bar([jne1_1, jne1_2, jne1_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.1')

subplot(5,1,2)
bar([jne2_1, jne2_2, jne2_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.3')

subplot(5,1,3)
bar([jne3_1, jne3_2, jne3_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.5')

subplot(5,1,4)
bar([jne4_1, jne4_2, jne4_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.7')

subplot(5,1,5)
bar([jne5_1, jne5_2, jne5_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.9')

sgtitle("LDM")


%
figure
subplot(2,1,1)
boxplot([jne1_2, jne1_3, [], jne2_2, jne2_3, [], jne3_2, jne3_3, [], jne4_2, jne4_3, [], jne5_2, jne5_3])
title("Distribution of LDM")

% set boxplot face color
colors = rand(12, 3);
h = findobj(gca,'Tag','Box');
for j=1:length(h)
    if mod(j,2)
        patch(get(h(j),'XData'),get(h(j),'YData'),colors(1,:),'FaceAlpha',.5);
    else
        patch(get(h(j),'XData'),get(h(j),'YData'),colors(2,:),'FaceAlpha',.5);
    end
end

subplot(2,1,2)
boxplot([(jne1_2 - jne1_3) ./ jne1_1, (jne2_2 - jne2_3) ./ jne2_1, (jne3_2 - jne3_3) ./ jne3_1, (jne4_2 - jne4_3) ./ jne4_1, (jne5_2 - jne5_3) ./ jne5_1])
xticklabels({'U = 0.1', '0.3', '0.5', '0.7', '0.9'})
title("Distribution of LDM improvement")

%%
jne1_1 = data_raw_1(:,2+6);
jne1_2 = data_raw_1(:,3+6) - data_raw_1(:,2+6);
jne1_3 = data_raw_1(:,4+6) - data_raw_1(:,3+6);

jne2_1 = data_raw_2(:,2+6);
jne2_2 = data_raw_2(:,3+6) - data_raw_2(:,2+6);
jne2_3 = data_raw_2(:,4+6) - data_raw_2(:,3+6);

jne3_1 = data_raw_3(:,2+6);
jne3_2 = data_raw_3(:,3+6) - data_raw_3(:,2+6);
jne3_3 = data_raw_3(:,4+6) - data_raw_3(:,3+6);

jne4_1 = data_raw_4(:,2+6);
jne4_2 = data_raw_4(:,3+6) - data_raw_4(:,2+6);
jne4_3 = data_raw_4(:,4+6) - data_raw_4(:,3+6);

jne5_1 = data_raw_5(:,2+6);
jne5_2 = data_raw_5(:,3+6) - data_raw_5(:,2+6);
jne5_3 = data_raw_5(:,4+6) - data_raw_5(:,3+6);

figure
subplot(5,1,1)
bar([jne1_1, jne1_2, jne1_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.1')

subplot(5,1,2)
bar([jne2_1, jne2_2, jne2_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.3')

subplot(5,1,3)
bar([jne3_1, jne3_2, jne3_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.5')

subplot(5,1,4)
bar([jne4_1, jne4_2, jne4_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.7')

subplot(5,1,5)
bar([jne5_1, jne5_2, jne5_3])
legend(["baseline", "before", "after"])
title('U(LO) = 0.9')

sgtitle("HDM")

%
figure
subplot(2,1,1)
boxplot([jne1_2, jne1_3, [], jne2_2, jne2_3, [], jne3_2, jne3_3, [], jne4_2, jne4_3, [], jne5_2, jne5_3])
title("Distribution of HDM")

% set boxplot face color
colors = rand(12, 3);
h = findobj(gca,'Tag','Box');
for j=1:length(h)
    if mod(j,2)
        patch(get(h(j),'XData'),get(h(j),'YData'),colors(1,:),'FaceAlpha',.5);
    else
        patch(get(h(j),'XData'),get(h(j),'YData'),colors(2,:),'FaceAlpha',.5);
    end
end

subplot(2,1,2)
boxplot([(jne1_2 - jne1_3) ./ jne1_1, (jne2_2 - jne2_3) ./ jne2_1, (jne3_2 - jne3_3) ./ jne3_1, (jne4_2 - jne4_3) ./ jne4_1, (jne5_2 - jne5_3) ./ jne5_1])
xticklabels({'U = 0.1', '0.3', '0.5', '0.7', '0.9'})
title("Distribution of HDM improvement")