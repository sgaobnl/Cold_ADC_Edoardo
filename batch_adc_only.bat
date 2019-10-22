::::::::::::::::::::::::::::: Description ::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:: This is the executable for the ColdADC QA/QC testing procedure, ADC Only Teststand.
:: External files used:
:: (1) Configuration (adc_config.py): environment (RT or LN2), chip ID, board ID, sampling frequency (2 MHz or 500 kHz).
:: (2) Command Library (cmd_library.py): functions for testing purposes. 
:: (3) Board Library (brd_config.py): functions for testboard control.
:: Three main logs: Status (PASS or FAIL), Pass Log (checkout informations and characterization WARNINGs), Error Log (detailed description of issued errors).
:: Seven main files:
:: (1) Initialization Checkout: every part of ColdADC that does not include characterization. This file takes care of functional requirements for normal ColdADC behavior: power, communications, reference setting, channel mapping, calibration weights. This is the only file where a FAIL Status can be issued and where the Error Log can be adjourned. Every other file can only add WARNINGs to the Pass Log.
:: (2) Test Configuration: configures system frequency (4 Ms/s or 16 Ms/s as sampling frequencies of internal ADCs), reference settings, every ColdADC setting and reloads calibration weights. 
:: (3) DNL/INL Sinewave: linearity study with sinewave input signal from DS360 Stanford Generator.
:: (4) ENOB: dynamic behavior with sinewave input from DS360.
:: (5) DC Noise: RMS noise calculation and channel comparison, using a white noise output with DC offset (200 mV or 900 mV baseline) from DS360.
:: (6) Test Input Full: complete characterization (noise, linearity, dynamic behavior) for internal ADC only (ADC Test Input, differential).
:: (7) ADC Only PDF: complete PDF file with every output the previous tests, organized in an easily readable way. 
:: Refer to single scripts for more detailed descriptions.
:: All the procedure can be applied without distinction to room temperature (RT) and cold (LN2) environments.


::::::::::::::::::::::::::: ADC Only Testing :::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:::: All channels tests (Single Ended Input):
:::: Turn on RIGOL DP832 Power Supply (board power supply): 2.8 V (Channel 1), 2.8 V (Channel 2), 5 V (Channel 3)
:::: Turn on Kyeishgt Power Supply: voltages settings are not necessary.
:::: Connect power supply cables.
:::: Connect optical fiber links.
:::: Connect Single Ended SMA cable from DS360 positive output to the board.
:::: Connect Clock Synchronization cables from FPGA mezzanine jumpers to DS360 10 MHz input.
:::: Turn on DS360 Stanford Generator.
echo 'Confirm the cables were switch!'
echo 'Confirm the cables were switch!'
PAUSE
python all_ps_on.py
python adc_init_checkout.py      
python ADC_TEST_CFG.py           BJT NoSDC NEW_CALI 4 SYNC10M 
python adc_dnlinl_sinewave.py    BJT 
python adc_enob.py               BJT 
python adc_dc_noise.py           BJT 200 
python adc_dc_noise.py           BJT 900
python ADC_TEST_CFG.py           CMOS NoSDC NEW_CALI 4 SYNC10M 
python adc_dnlinl_sinewave.py    CMOS  
python adc_enob.py               CMOS 
python adc_dc_noise.py           CMOS 200
python adc_dc_noise.py           CMOS 900
echo 'Switch the cables'
echo 'Confirm the cables were switch!'
PAUSE
:::: Internal ADC Tests (Differential ADC Test Input):
:::: Disconnect Single Ended SMA output from DS360, connect differential output for ADC Test Input (P and N SMA cables).
:::: Disconnect clock synchronization cables from FPGA mezzanine.
::python ADC_TEST_CFG.py           BJT NoSDC NEW_CALI 16  UNSYNC 
::python adc_test_input_full.py    BJT 16
::python ADC_TEST_CFG.py           BJT NoSDC NEW_CALI 4  UNSYNC
::python adc_test_input_full.py    BJT 4
::python ADC_TEST_CFG.py           CMOS NoSDC NEW_CALI 16  UNSYNC
::python adc_test_input_full.py    CMOS  16
::python ADC_TEST_CFG.py           CMOS NoSDC NEW_CALI 4  UNSYNC
::python adc_test_input_full.py    CMOS  4
::python all_ps_off.py
::PAUSE
::python adc_only_pdf.py           NoSDC    
::PAUSE
