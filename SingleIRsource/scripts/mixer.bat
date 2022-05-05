@echo off
FOR /l %%y IN (0, 2, 10) DO python mixer_cal_bash.py 5.5 %%y
timeout /t 30
pause

@echo off
FOR %%y IN (5.345679 5.380116 5.638565 5.869609 ) DO python mixer_cal_bash.py %%y 20
timeout /t 30
pause