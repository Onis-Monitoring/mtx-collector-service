def event_type():
    try:
        with open('./mefs.log','r') as fp:
            line = fp.readline()

            # -rw-r--r-- 1 mtxdepmef mtxdepmef     203 2021-08-10 00:13:24.007968290 -0500 mef_1628458940_8868242_8868339.xml.gz
            counter = 0
            missing_gaps = []
            while line:
                if '.xml.gz' in line.strip():
                    formatted = line.strip().replace('.', '_').split('_')
                    if counter == 0:
                        counter = formatted[4]
                    elif (int(counter) + 1) == int(formatted[3]):
                        counter = formatted[4]
                    else:
                        if (int(counter) + 1) < int(formatted[4]):
                            missing_gaps.append('{} - {}'.format(counter,formatted[3]))
                        if (int(counter) + 1) > int(formatted[2]):
                            print('Duplicated? {} - {}'.format(counter,formatted[3]))
                        counter = formatted[4]
                line = fp.readline()
         
    except Exception as e:
        print(e)
        
    print(missing_gaps)
 
event_type()