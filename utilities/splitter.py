def splitter(exp: str):
    if exp.__contains__(',') or exp.__contains__('-'):
        return splittedExp(exp)
    return exp

def splittedExp(exp: str):
    expList = exp.split(' ')
    possibilityList = []
    for expressionItem in expList:
        if expressionItem.__contains__(','):
            possibilityList.append(expressionItem.split(','))
        elif expressionItem.__contains__('-'):
            months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
            weekDays = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
            lowerAndUpperRange = expressionItem.split('-')            
            if len(lowerAndUpperRange)==2:
                lower = lowerAndUpperRange[0]
                upper = lowerAndUpperRange[1]
                rangeList = []
                if lower in months:
                    for i in months[months.index(lower):months.index(upper)+1]:
                        rangeList.append(i)
                elif lower in weekDays:
                    for i in weekDays[weekDays.index(lower):weekDays.index(upper)+1]:
                        rangeList.append(i)
                else:
                    for i in range(int(lower),int(upper)+1):
                        rangeList.append(str(i))
                possibilityList.append(rangeList)
            else:
                raise ValueError('invalid value provided with range separator(-)')
        else:
            possibilityList.append([expressionItem])
    import itertools
    # a = [[0],[5],[10],['?'],['*'],['MON','WED','FRI']]
    return list(itertools.product(*possibilityList))
