import sys


def main():
    num_variables, minterms, dont_care = read(sys.argv[1])
    minterms_copy = minterms.copy()
    minterms.extend(dont_care)
    int_minterms = minterms.copy()
    minterms = convert_to_binary(minterms, num_variables)
    groups = agroup(minterms)
    implicants, prime = combine(groups)
    prime_implicants = get_prime_implicants(implicants)
    prime_implicants.update(prime)
    table_values = delete_duplicates(prime_implicants)
    table = make_table(table_values, int_minterms, dont_care)
    essential = get_essential_prime_implicants(table)
    output(sys.argv[2], table_values, essential, num_variables, minterms_copy, dont_care)


def get_essential_prime_implicants(table):
    restart = True
    essential = []
    delet = []
    to_delete = ""
    for key in table:
        if is_essencial(table, key):
            if key not in essential:
                essential.append(key)
            to_delete = delete(table, key)
            if to_delete != "":
                table.pop(to_delete, None)
                return get_essential_prime_implicants(table)

    if len(essential) == 0: #This happens there are no 'x' free
        for key in table:
            delet.extend(delete_rows(table, key))
        for key in delet:
            table.pop(key, None)
        return get_essential_prime_implicants(table)
    return essential


def delete_rows(table, key):
    x_quantity = table[key].count('x')
    count, index, to_delete = 0, -1, []
    while count < x_quantity:
        index = table[key].index('x', index + 1)
        for id in table:
            if id != key and table[id][index] == 'x':
                if x_quantity > table[id].count('x'):
                    to_delete.append(id)
        count += 1
    return to_delete


def delete(table, key):
    index = -1  # Starts at minus 1 because it is adding 1 in an expression below
    to_delete = ""
    x_quantity = table[key].count('x')
    count = 0
    while count < x_quantity:
        index = table[key].index('x', index + 1)
        for id in table:
            if id != key and table[id][index] == 'x' and id not in to_delete and is_essencial(table, id) is False:  # If is not alone in that column
                to_delete = id
        count += 1
    return to_delete


def is_essencial(table, key):
    index = -1  # Starts at minus 1 because it is adding 1 in an expression below
    essencial = False
    end = False
    while end is False and essencial is False:
        essencial = True
        try:
            index = table[key].index('x', index + 1)
        except (ValueError, IndexError):
            end = True  #End cicle
        for id in table:
            if id != key and table[id][index] == 'x': #If is not alone in that column
                essencial = False
    return essencial


def make_table(table_values, minterms, dont_care):
    table = {}
    minterms = delete_dont_cares(minterms, dont_care)
    lenght = len(minterms)
    for key in table_values:
        position = 0
        list = []
        while position < lenght:
            if str(minterms[position]) in key.split(',') :#Find the minterms in the keys
                list.append('x')
            else:
                list.append(' ')
            position += 1
        if 'x' in list:
            table[key] = list
    return table


def delete_dont_cares(minterms, dont_care):
    minterms_copy = minterms.copy()
    minterms = []
    for element in minterms_copy:
        if element not in dont_care:
            minterms.append(element)
    return minterms


def delete_duplicates(implicants):
    list, table_values = [], {}
    for key in implicants:
        if implicants[key] not in list:
            list.append(implicants[key])
            table_values[key] = implicants[key]
    return table_values


def get_prime_implicants(groups):
    keys = get_keys(groups)
    keys.sort()
    lenght = len(keys)
    count, prime_implicants, checks = 0, {}, []
    next_group = 0
    while count < lenght - 1:
        actual_group = keys[count]
        next_group = keys[count+1]
        for imp in groups[actual_group]:
            for target in groups[next_group]:
                result, comb = match(groups[actual_group][imp], groups[next_group][target])
                if result:
                    key = imp + ',' + target
                    prime_implicants[key] = comb
                    checks.append(imp)
                    checks.append(target)
            if imp not in checks:
                prime_implicants[imp] = groups[actual_group][imp]
        count += 1
    if next_group != 0:
        for imp in groups[next_group]: #Check the ones of the last group
            if imp not in checks:
                prime_implicants[imp] = groups[next_group][imp]
    return prime_implicants


def combine(groups):
    keys = get_keys(groups)
    keys.sort()
    lenght = len(keys)
    count, result, comb = 0, False, ''
    implicants = {}
    checks = []
    prime_implicants = {}
    next_key = keys[count]
    while count < lenght-1:
        key = keys[count]
        next_key = keys[count+1]
        for number in groups[key]:
            for target in groups[next_key]:
                result, comb = match(number, target)
                if result:
                    id = str(int(number, 2)) + ',' + str(int(target, 2))
                    checks.append(number)
                    checks.append(target)
                    if key not in implicants:
                        implicants[key] = {}
                    implicants[key][id] = comb
            if number not in checks:
                number_int = str(int(number, 2))
                prime_implicants[number_int] = number
        count += 1
    for number in groups[next_key]:  # Check the ones of the last group
        if number not in checks:
            number_int = str(int(number, 2))
            prime_implicants[number_int] = number
    return implicants, prime_implicants


def match(number, match):
    lenght = len(number)
    pos, diff = 0, 0
    result = False
    comb = ''
    while pos < lenght:
        if number[pos] != match[pos]:
            comb = comb + '-'
            diff += 1
        else:
            comb = comb + number[pos]
        pos += 1
    if diff == 1:
        result = True
    return result, comb


def agroup(minterms):
    groups = {}
    for number in minterms:
        key = number.count('1')
        if key not in groups:
            groups[key] = []
        groups[key].append(number)
    return groups


def convert_to_binary(minterms, num_variables):
    lenght = len(minterms)
    position = 0
    while position < lenght:
        number = minterms[position]
        minterms[position] = format(number, '0'+str(num_variables)+'b')
        minterms[position] = minterms[position]
        position += 1
    return minterms


def output(output_file, prime_implicants, essentials, num_variables, minterms, dont_care):
    file = open("outfile.txt", "w")
    s = "# Example #1 – Simple Boolean function \n# Problem parameters:\n"
    s = s + "#   num_variables –          " + str(num_variables) + "\n"
    s = s + "#   num_minterms –           " + str(len(minterms)) + "\n"
    s = s + "#   num_minterms_dont_care – " + str(len(dont_care)) + "\n"
    s = s + "# Minterms " + str(minterms).strip('[]') + "\n"
    s = s + "\n# Output:\n"
    s = s + "# variables –    " + str(num_variables) + "\n"
    s = s + "# essential –    " + str(len(essentials)) + "\n"
    s = s + "# Prime –        " + str(len(prime_implicants) - len(essentials)) + "\n"
    s = s + "\n# Essentials\n"
    for key in essentials:
        s = s + prime_implicants[key] + "\n"
    s = s + "\n# Non-Essential primes\n"
    for key in prime_implicants:
        if key not in essentials:
            s = s + prime_implicants[key] + "\n"
    s = s + "\n# End of file"
    file.write(s)


def read(input_file):
    file = open(input_file)
    text = file.read()
    file.close()
    list = text.split('\n')
    count, num_variables, num_minterms, num_minterms_dont_care = 0, 0, 0, 0
    minterms, dont_care = [], []
    for element in list:
        if element != '' and element[0] != '#' and element[0] != ' ':
            if count == 0: #Take the parameters
                element = element.split(' ')
                num_variables = int(element[0]) #Convert to integer
                num_minterms = int(element[1])
                num_minterms_dont_care = int(element[2])
            if 0 < count <= num_minterms: #Take the minterms
                minterms.append(int(element))
            if count > num_minterms and num_minterms_dont_care != 0: #Take the dont care minterms
                dont_care.append(int(element))
            count += 1
    return num_variables, minterms, dont_care


def get_keys(dict):
    keys = []
    for key in dict:
        keys.append(key)
    return keys


main()

