def event_type():
    try:
        with open('./mefs.log','r') as fp:
            line = fp.readline()
            counter = 0
            missing_gaps = []
            while line:
                if '.xml.gz' in line.strip():
                    formatted = line.strip().replace('.', '_').split('_')
                    if counter == 0:
                        counter = formatted[3]
                    elif (int(counter) + 1) == int(formatted[2]):
                        counter = formatted[3]
                    else:
                        if (int(counter) + 1) < int(formatted[2]):
                            missing_gaps.append('{} - {}'.format(counter,formatted[2]))
                        counter = formatted[3]
                line = fp.readline()
         
    except Exception as e:
        print(e)
        
    print(missing_gaps)
 
event_type()