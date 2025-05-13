from scipy.stats import ttest_ind

#run all tests against each other here, and then run the collective against one another - 1vs1, 2vs2 etc. then all strat1 vs allstrat2 by importing from excel

#bot1 strategy1+2
print(ttest_ind([32,37,26,28,31,38,31,44,25,38],[36,23,42,48,49,49,41,34,37,34]))

#bot2 strategy1+2
print(ttest_ind([74,69,79,59,52,41,63,84,83,86],[73,79,55,57,63,82,77,64,82,62]))

#bot3 strategy1+2
print(ttest_ind([111,98,102,103,107,101,96,82,102,89],[87,101,116,92,105,70,86,93,70,104]))

#bot4 strategy1+2
print(ttest_ind([125,114,117,119,145,114,115,126,119,142],[136,111,121,114,133,115,126,118,131,105]))

#bot5 strategy1+2
print(ttest_ind([163,168,176,156,137,124,160,131,147,158],[125,121,167,152,106,154,157,148,129,149]))

#bot6 strategy1+2
print(ttest_ind([156,162,147,197,181,161,159,166,149,155],[171,178,207,160,169,158,152,140,165,158]))

#bot7 strategy1+2
print(ttest_ind([196,183,184,187,198,187,192,201,191,214],[189,190,196,220,169,159,181,157,134,201]))

#bot8 strategy1+2
print(ttest_ind([213,199,188,207,200,195,205,208,166,195],[185,187,192,142,201,222,170,179,219,191]))

#bot9 strategy1+2
print(ttest_ind([196,225,206,213,211,218,221,228,221,236],[192,208,180,192,209,218,212,225,194,208]))

#bot10 strategy1+2
print(ttest_ind([228,234,238,225,229,213,238,223,194,208],[191,210,199,204,199,212,211,203,221,196]))
