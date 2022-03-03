from time import sleep
import smtplib, ssl

from instruments import Fridge_handler

sender_email = 'criokids2022@gmail.com'
sender_pass = input(:'Inserisci la password della mail: ')

receiver_emails = [
    'r.carobene@campus.unimib.it',
    'e.cipelli@campus.unimib.it',
    'p.campana1@campus.unimib.it',
    'marco.faverzani@unimib.it']

name_sens = ['SET POINT T FOR SORB',
             'SORB TEMP',
             '1 K POT TEMP',
             'MIX CHAMBER TEMP',
             'MIX CHAMBER POWER',
             'STILL POWER',
             'SORB POWER',
             'STEPPER V6 TARGET',
             'STEPPER V12 TARGET',
             'STEPPER N/V TARGET',
             'TEMP REGISTRER',
             'CH1 FREQ/4',
             'CH2 FREQ/4',
             'CH3 FREQ/4',
             'A/D I/P GAUGE G1',
             'A/D I/P GAUGE G2',
             'A/D I/P 4 (SPARE)',
             'A/D I/P 5 (SPARE)',
             'A/D I/P 6 (SPARE)',
             'A/D I/P GAUGE G3',
             'A/D I/P PIRANI P1',
             'A/D I/P PIRANI P2',
             'RAW A/D I/P 1',
             'RAW A/D I/P 2',
             'RAW A/D I/P 3',
             'RAW A/D I/P 4',
             'RAW A/D I/P 5',
             'RAW A/D I/P 6',
             'RAW A/D I/P 7',
             'RAW A/D I/P 8',
             'Mixing Chamber Proportional Band in units of 0.1%',
             'Mixing Chamber Integral Action time in units of 0.1min',
             'Mixing Chamber Temperature in units of 0.1mK',
             'Mixing Chamber Set Point in units of 0.1mK',
             'Mixing Chamber Sensore Conductance in units of 0.1muS',
             'Mixing Chamber Sensor Resistance in units of 0.1kohm']

def get_log_mail():
    message = 'Subject: ALERT CRIOSTATO!\n\n'
    message = message + name_sens[3] + '\t' + str(fridge.get_sens(3)) + '\n' 
    message = message + name_sens[14] + '\t' + str(fridge.get_sens(14)) + '\n' 
    message = message + name_sens[15] + '\t' + str(fridge.get_sens(15)) + '\n\n\n' 

    for i in range(0,36):
        message = message + name_sens[i] + '\t' + str(fridge.get_sens(i)) + '\n' 

    return message


def send_email():
    message = get_log_mail()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(sender_email, sender_pass)
        for receiver in receiver_emails:
            server.sendmail(sender_email, receiver, message)

if __name__ == '__main__':
    fridge = Fridge_handler()

    while(True):
        g1 = fridge.get_sens(14) # gauge g1
        g2 = fridge.get_sens(15) # gauge g2
        t2 = fridge.get_sens(2)  # temp 1k pot
        p2 = fridge.get_sens(21)  # p1
    
        if(g1 > 2800 or g2 > 2800 or t2 > 2800 or (t2 < 1700 and p2 < 45)):
            print("Alert!")
            send_email()
            sleep(60*60)
        else:
            print("Tutto ok")
            sleep(60*5)
