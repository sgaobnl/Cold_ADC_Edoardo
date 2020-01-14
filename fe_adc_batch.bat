::Cd = 150pF
::python all_ps_on.py
::python ADC_CFG_INIT.py BJT NoSDC NEW_CALI
::python noise_acq.py        05us 14mVfC PLS_DIS 900mV BUF_OFF DC disable  01  
::python noise_acq.py        10us 14mVfC PLS_DIS 900mV BUF_OFF DC disable  02  
::python noise_acq.py        20us 14mVfC PLS_DIS 900mV BUF_OFF DC disable  03  
::python noise_acq.py        30us 14mVfC PLS_DIS 900mV BUF_OFF DC disable  04  
::python gain_measure_acq.py 05us 14mVfC PLS_EN  900mV BUF_OFF DC Internal 01  
::python gain_measure_acq.py 10us 14mVfC PLS_EN  900mV BUF_OFF DC Internal 02  
::python gain_measure_acq.py 20us 14mVfC PLS_EN  900mV BUF_OFF DC Internal 03  
::python gain_measure_acq.py 30us 14mVfC PLS_EN  900mV BUF_OFF DC Internal 04  
::python gain_fit_plot.py
::python enc_plot.py
::python enc_plot_tps.py
python all_ps_off.py
pause
::
