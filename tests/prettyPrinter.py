

def print_list(leading_str, listy, empty_message='No elements in list'):

    if len(listy)==0:
        print(empty_message)
        return

    for element in listy:
        print(leading_str + '' + str(element))
