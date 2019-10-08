::Cd = 150pF
::python ADC_CFG_INIT.py RT BJT NoSDC
::python noise_acq.py        05us 14mVfC PLS_DIS 900mV BUF_OFF DC disable  01 RT 
::python noise_acq.py        10us 14mVfC PLS_DIS 900mV BUF_OFF DC disable  02 RT 
::python noise_acq.py        20us 14mVfC PLS_DIS 900mV BUF_OFF DC disable  03 RT 
::python noise_acq.py        30us 14mVfC PLS_DIS 900mV BUF_OFF DC disable  04 RT 
::python gain_measure_acq.py 05us 14mVfC PLS_EN  900mV BUF_OFF DC Internal 01 RT 
::python gain_measure_acq.py 10us 14mVfC PLS_EN  900mV BUF_OFF DC Internal 02 RT 
::python gain_measure_acq.py 20us 14mVfC PLS_EN  900mV BUF_OFF DC Internal 03 RT 
::python gain_measure_acq.py 30us 14mVfC PLS_EN  900mV BUF_OFF DC Internal 04 RT 
python gain_fit_plot.py
python enc_plot.py
python enc_plot_tps.py

