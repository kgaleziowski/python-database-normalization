from itertools import combinations

post_synthesis = dict()
canonical_list = []
domkniecia = {}
key_attributes = set()
non_key_attributes = set()
minimal_keys = set()
super_keys = set()
closure_string = ""
base_min = []
destroy_2PN = []
destroy_3PN = []

# START --- SEGMENT FUNKCJI #

# funkcja generująca wszystkie kombinacje do domknięć
def combo(attributes):
    length = len(attributes)
    temp = []
    for i in range(length):
        if i == 0:
            for j in attributes:
                temp.append(j)
        else:
            combs = combinations(attributes, i+1)
            for combo in combs:
                combo = sorted(combo)
                temp.append(','.join(combo))
    sorted_alphabetically = sorted(temp)
    sorted_len_alpha = sorted(sorted_alphabetically,key=len)
    return sorted_len_alpha

# funkcja zwracająca SET będący dopełnieniem dla podanego domknięcia
def closer(combination, relations):
    closing_set = set(combination)
    basic_length = len(closing_set)
    for relation in relations:
        set_attr = set(relation[0].split(","))
        if set_attr.issubset(closing_set):
            add = relation[1]
            closing_set.add(add)
            if len(closing_set) != basic_length:
                return closer(closing_set, relations)
    return_set = sorted(closing_set)
    return return_set

# funkcja zapamiętująca wszystkie domknięcia oraz wyznaczająca wszystkie klucze bez podziału na min. klucz kandydujący i nadklucze
def keys_gen(attributes, relations):
    all_combinations = combo(attributes)
    all_closures = []
    all_keys = []
    for combination in all_combinations:
        to_close = combination.split(",")
        closure = closer(to_close, relations)
        # zapis wszystkich domknięć
        all_closures.append(closure)
        # zapis wszystkich kluczy (bez podziału na minimalne klucze kandydujące i nadlucze)
        if(len(closure) == len(attributes)):
            all_keys.append(combination)
    return all_keys

# funkcja wyznaczająca spośród zbioru wszystkich kluczy zbiór minimalnych kluczy kandydujących oraz nadkluczy
def extract_minimal(all_keys_set):
    global minimal_keys
    global super_keys
    temp_all = set(all_keys_set)
    i = 0
    for y in all_keys_set:
        i = i + 1
        for x in all_keys_set[i:]:
            subset_candidat = set(y.split(","))
            master_set = set(x.split(","))
            if(subset_candidat.issubset(master_set) and subset_candidat != master_set):
                all_keys_set.remove(x)
    minimal_keys = sorted(set(all_keys_set))
    super_keys = sorted(sorted(temp_all.difference(minimal_keys)),key=len)

# funkcja wypisująca wszystkie domknięcia
def list_closure(attributes, relations):
    # zbiór wszystkich domknięć
    global minimal_keys
    global super_keys
    global closure_string
    all_combinations = combo(attributes)
    print("[DOMKNIĘCIA]")
    for combination in all_combinations:
        temp_attr = combination.split(',')
        closure = closer(temp_attr, canonical_list)
        closure_string = closure_string + "".join(closure)
        print('{' + combination.replace(",",", ") + '}+ = {' + ", ".join(closure).strip() + "}" , end="")
        if(combination in minimal_keys):
            print("          <----- MINIMALNY KLUCZ KANDYDUJĄCY")
        elif(combination in super_keys):
            print("          <----- NADKLUCZ")
        else:
            print("")
        # sprawdzenie czy domknięcie jest kluczem
    return key_attributes

# funkcja generująca string będący połączeniem wszystkich domknięć - potrzebna do weryfikacji czy można usunąć atrybut
def generate_closure_string(attributes, relations):
    closure_str = ""
    all_combinations = combo(attributes)
    for combination in all_combinations:
        temp_attr = combination.split(',')
        closure = closer(temp_attr, relations)
        closure_str= closure_str + "".join(closure)
    return closure_str

# funkcja usuwającą zbędne atrybuty z lewej strony
def delete(input_list):
    global canonical_list
    global attributes
    global base_min
    global closure_string
    default_relations = list(input_list)
    for x in input_list:
        defaultLeft = x[0].split(",")
        if(len(defaultLeft) > 1):
            for i in range(len(defaultLeft)):
                if(len(x[0]) == 1):
                    break
                defaultLeft = x[0].split(",")
                defaultLeft.pop(i)
                new_relation = [",".join(defaultLeft),x[1]]
                temp_list = list(default_relations)
                temp_list.remove(x)
                temp_list.append(new_relation)
                # sprawdzam czy po usunięciu atrybuty z lewej strony domknięcia są takie same, jeśli tak to znaczy że można usunąc atrybuty i próbuje usunąć kolejny (rekurencyjnie)
                if(closure_string == generate_closure_string(attributes, temp_list)):
                    for x in temp_list:
                        print(x[0] + " -> " + x[1])
                    base_min = list(temp_list)
                    return delete(temp_list)
        base_min = list(default_relations)

# funkcja usuwająca zbędne związki funkcyjne - próbuje usuwać każdy po kolei, jeśli nie wpływa to w żadeń sposób na domknięcia to usuwam
def del_relations():
    global attributes
    global base_min
    global closure_string
    temp_relations = list(base_min)
    for x in base_min:
        if x in temp_relations:
            temp_relations.remove(x)
            generated_closure = generate_closure_string(attributes,temp_relations)
            if(closure_string == generated_closure):
                base_min.remove(x)
            temp_relations = list(base_min)

# funkcja pomocnicza do wyznaczania bazy minimalnej
def minimal_base(canonical_relations):
    global base_min
    global canonical_list
    # usuwanie atrybutów z lewej
    delete(canonical_relations)
    # usuwanie zbędnych zależności
    del_relations()
    # wypisanie bazy minimalnej
    b_set = set(tuple(x) for x in base_min)
    canonical_list = [list(x) for x in b_set if x[0] != x[1]]
    if(canonical_list):
        for x in sorted(sorted(canonical_list), key=len):
            print(x[0] + " -> " + x[1])
    else:
        print("brak")

# dopełnienia dla 2PN
def closer2PN(subset):
    global destroy_2PN
    global non_key_attributes
    global base_min
    # dany podzbiór właściwy klucza
    closing_set = set(subset)
    for relation in base_min:
        # lewa strona relacji
        left_set = set(relation[0].split(","))
        # jesli lewa strona jest podzbiorem klucza czyli jest jego podzbiorem własciwym i prawa strona nie jest atrybutem kluczowym to zależność niszczy 2PN
        if(left_set.issubset(closing_set) and relation[1] in non_key_attributes and left_set != closing_set):
            destroy_2PN.append(relation)

# wysyłam każdy klucz minimalny relacji i sprawdzam czy jeśli po lewej stronie znajduje się podzbiór klucza to czy prawa strona jest atrybutem niekluczowym
def is2PN():
    global base_min
    global minimal_keys
    global destroy_2PN
    for key in minimal_keys:
        subsets = combo(key.split(","))
        for subset in subsets:
            closer2PN(subset.split(","))
    b_set = set(tuple(x) for x in destroy_2PN)
    destroy_2PN = [list(x) for x in b_set if x[0] != x[1]]
    if(destroy_2PN):
        return False
    else:
        return True

#  test na 3PN za pomocą negacji alternatywy ~(p lub q lub r)
def is3PN():
    global base_min
    global key_attributes
    global super_keys
    global destroy_3PN
    for relation in base_min:
        left = relation[0].split(",")
        if (relation[1] not in left) and (relation[1] not in key_attributes) and (left not in super_keys):
            destroy_3PN.append(relation)
    b_set = set(tuple(x) for x in destroy_3PN)
    destroy_3PN = [list(x) for x in b_set if x[0] != x[1]]
    if(destroy_3PN):
        return False
    else:
        return True

# funkcja wyznaczająca i wypisująca atrybuty kluczowe i niekluczowe
def attributes_specification():
    global minimal_keys
    global super_keys
    global non_key_attributes
    global key_attributes
    key_attrs = set()
    non_key_attrs = set()
    for x in minimal_keys:
        x = x.split(",")
        for y in x:
            key_attrs.add(y)
    key_attributes = sorted(key_attrs)
    print("Atrybuty kluczowe: ",end="")
    if(not len(key_attrs)):
        print("brak")
    else:
        print(", ".join(sorted(key_attrs)))
    non_key_attrs = sorted(attributes.difference(key_attrs))
    print("Atrybuty niekluczowe: ",end="")
    if(not len(non_key_attrs)):
        print("brak")
    else:
        print(", ".join(sorted(non_key_attrs)))
    non_key_attributes = non_key_attrs

# funkcja nie sprawdza czy jest schemat zawierajacy któryś z kluczy i nie łączy zawierajacych się w sobie - w danej chwili tylko dzieli
# schematy zostają zapisane w słowniku w postaci 'U': 'F', prawa strona jest zbiorem
def synthesis_closure(uni_and_func):
    global post_synthesis
    final_closure = []
    final_relations = []
    keys = []
    move_relations = []
    for x in uni_and_func:
        closure = set(x.split(","))
        relations = set()
        # wejscie w zależności z takim samym atrybutem po lewo
        for y in uni_and_func.values():
            # przejscie po nich i dodawanie do domknięcia
            for z in y:
                if z[0] == x:
                    closure.add(z[1])
                    relation = z[0] + " -> " + z[1]
                    relations.add(relation)
        # print(post_synthesis)
        # dodanie zwrotnych
        for y in uni_and_func.values():
            for z in y:
                if z[1] == x:
                    if(set(z[0].split(",")).issubset(closure)):
                        relation = z[0] + ' -> '+ z[1]
                        relations.add(relation)
        # WAŻNA KONTROLKA BO CZASAMI NADPISYWALO
        if(",".join(sorted(closure)) in post_synthesis.keys()):
            move_relations = post_synthesis[",".join(sorted(closure))]
            move_relations = set(move_relations)
            for x in move_relations:
                relations.add(x)
        post_synthesis[",".join(sorted(closure))] = relations
        #
        if(move_relations):
            post_synthesis[",".join(sorted(closure))] = relations
        # print(post_synthesis)

# funkcja sprawdza czy są schematy zawierające się w sobie oraz czy trzeba dodać schemat z U = klucz F = brak
def synthesis_final():
    global post_synthesis
    global minimal_keys
    key_in = False
    # print(post_synthesis)
    # sprawdzenie czy klucz jest pozbiorem któregoś schematu, jeśli nie to dodaje
    for x in minimal_keys:
        x = set(x.split(","))
        for y in post_synthesis.keys():
            y = set(y.split(","))
            if(x.issubset(y)):
                key_in = True
    if(not key_in):
        rand_key = minimal_keys[0]
        post_synthesis[rand_key] = "brak"
    # print(post_synthesis)
    # sprawdzenie czy któryś schemat jest podzbiorem innego
    for x in post_synthesis.keys():
        x_subset = set(x.split(","))
        for y in post_synthesis.keys():
            y_subset = set(y.split(","))
            if x_subset.issubset(y_subset) and x_subset != y_subset:
                move_relations = post_synthesis[x]
                post_synthesis[x] = ''
                for z in move_relations:
                    post_synthesis[y].add(z)
                break
    # print(post_synthesis)

# wypisanie dekompozycji
def synthesis(canonical_list):
    global post_synthesis
    uni_and_func = dict()
    left_closures = set()
    for x in canonical_list:
        left_closures.add(x[0])
        uni_and_func[x[0]] = list()
    for x in canonical_list:
        if x[0] in uni_and_func.keys():
            uni_and_func[x[0]].append(x)
    synthesis_closure(uni_and_func)
    synthesis_final()
    i = 0
    for x in post_synthesis:
        if post_synthesis[x] != '':
            print("R" + str(i) + " = " + "(" + " U" + str(i) + " = " + "{" + x + "}, F" + str(i) + " = " + str(post_synthesis[x]) + " )")
            i = i + 1




# KONIEC --- SEGMENT FUNKCJI #

# START --- MAIN #

# start setup #
while True:
    relation_set = set()
    attributes = set()
    post_synthesis = dict()
    canonical_list = []
    domkniecia = {}
    key_attributes = set()
    non_key_attributes = set()
    minimal_keys = set()
    super_keys = set()
    closure_string = ""
    base_min = []
    destroy_2PN = []
    destroy_3PN = []

    print("Działanie: ")
    print("1 - wpisanie atrybutów i związków ręcznie")
    print("2 - wczytanie atrybutów i związków z pliku")
    print("Aby wyjść wpisz jakikolwiek inny znak")
    option = input("Opcja: ")
    if(option == '1'):
        print("Atrybuty wpisz w jednej lini odzielając jedynie przecinkiem.")
        print("Każdą zależność funkcyjną wpisuj w osobnej linii. Po wpisaniu wszystkich, również w osobnej lini wpisz END aby przejść dalej.")
        # wczytanie atrybutów
        input_attributes = input("Atrybuty: ").split(",")
        attributes = set(input_attributes)
        # wczytanie zależności funkcyjnych
        print("Wpisując zależnosci funkcyjne zachowaj format: atrybuty/y -> atrybuty/y czyli np. A,B -> D,C")
        print("Zależności funkcyjne: ")
        line = ""
        while(line != "END"):
            line = input()
            if(line != "END"):
                relation_set.add(line)
    elif(option == '2'):
        print("Testy podstawowe wybierz wpisując liczbę od 01-10 (z zerem poprzedzającym).")
        print("Jeśli chcesz wczytać z pliku własny test, stwórz plik w folderze z testami podstawowymi i nazwij go oraz wypełnij zachowując widoczną konwencję.")
        test_number = input("Numer testu: ")
        # obsługa wczytania z pliku
        path = "testy/test-" + test_number + ".txt"
        test = open(path, "r")
        attributesLine = test.readline().split(',')
        # wczytuje do zbioru atrybuty - usuwam od razu ewentualne duplikaty
        for x in attributesLine:
            attributes.add(x.strip())
        # wczytuje do zbioru zależności funkcyjne - usuwam od razu ewentualne duplikaty
        for x in test:
            x = x.rstrip()
            relation_set.add(x)
    else:
        break

    # end setup #
    # atrybuty i zależnosci funkcyjne są już wczytane, kolejnym krokiem jest sprawdzenie poprawności wczytanych danych, jeśli weryfikacja inkluzji F w U i U w F nie będzie pomyślna program nie wykona się
    print("--------------------------------------------------------------------------------------------------------------------------------")
    print("[ANALIZA - START]")
    print("Atrybuty: " + ','.join(sorted(attributes)))
    print("Zależnosci funkcyjne: ")
    for x in sorted(relation_set):
        print(x)

    relations_dict = {}
    canonical_base = {}

    # wczytanie zaleznosci do slownika, lewo jest kluczem - po prawo jest zbiór, zatem
    # A,B -> C
    # A,B -> D
    # slowniku to bedzie klucz A,B: ['C','D'] (jako zbior) po prawej
    for relation in relation_set:
        left = relation.rsplit('-')[0].strip()
        del_repeat = sorted(set(left.split(",")))
        left = ",".join(del_repeat)
        canonical_base[left] = set()

    for relation in relation_set:
        left = relation.rsplit('-')[0].strip()
        right = relation.rsplit('>')[1].strip()

        del_repeat = sorted(set(left.split(",")))
        left = ",".join(del_repeat)

        relations_dict[left] = right

        # rozbijanie np. A -> B,C na A -> B; A -> C

        rightAttributes = right.split(",")
        for i in rightAttributes:
            canonical_base[left].add(i.strip())

    # po wczytaniu wszystkiego do słownika mam pewność że nie mam już duplikatów, mogę przejść do listy i z niej przechodzić na postać kanoniczną
    canonical_list = []
    for i in canonical_base:
        right_values = canonical_base[i]
        for j in right_values:
            canonical_list.append([i, j])

    print("")
    print("[WERYFIKACJA]")
    fun_F = set()
    # tutaj mogą być po lewej np. A,B,C,D -> E dlatego split()
    for x in canonical_base:
        attr_in_F = x.split(",")
        for y in attr_in_F:
            fun_F.add(y)

    for x in canonical_base.values():
        attr_in_F = x
        for y in attr_in_F:
            fun_F.add(y)

    print("Atrybuty z U: " + ", ".join(sorted(attributes)))
    print("Atrybuty z F: " + ", ".join(sorted(fun_F)))

    # WERYFIKACJA POPRAWNOWŚCI DANYCH WEJŚCIOWYCH
    if(attributes.issubset(fun_F) == False):
        print("W U znajduje się przynajmniej jeden atrybut który nie jest w F. Dodaje zależność/i trywialną.")
        for x in attributes:
            if x not in fun_F:
                print(x + " -> " + x)
        print("--------------------------------------------------------------------------------------------------------------------------------")
    if (fun_F.issubset(attributes) == False):
        print("W F znajduje się przynajmniej jeden atrybut który nie jest w U. Weryfikacja niepomyślna.")
        print("--------------------------------------------------------------------------------------------------------------------------------")
    else:
        print("Atrybuty w F oraz U są zgodne. Weryfikacja pomyślna.")
        print("")
        # zapamiętanie wszystkich kluczy - bez podziału
        all_keys = keys_gen(attributes, canonical_list)
        # wyciągnięcie minimialnych kluczy kandydujących
        extract_minimal(all_keys)
        # wypisanie domknięć
        key_attributes = sorted(list_closure(attributes, canonical_base))
        # wypisanie atrybutów z podziałem na kluczowe i niekluczowe
        print("")
        print("[OKRESLENIE ATRYBUTOW]")
        attributes_specification()
        print("")
        print("[BAZA MINIMALNA]")
        minimal_base(canonical_list)
        print("")
        print("[TEST NA 2PN]")
        if(not is2PN()):
            print("""Relacja nie jest w 2 postaci normalnej.
Aby relacja była w 2PN konieczne jest, aby każdy atrybut niekluczowy był w pełni funkcyjnie zależny od każdego klucza tej relacji.  
W podanym schemacie istnieje przyjemniej jedna częściowa zależność funkcyjna, która narusza 2PN.
Te zależności to: """)
            for x in destroy_2PN:
                print(x[0] + " -> " + x[1])
        else:
            print("Relacja jest w 2 postaci normalnej.")
        if(not is3PN()):
            print("")
            print("Aby relacja była w 3PN konieczne jest, aby oprócz bycia w 2PN, każda jej zależność funkcyjna X -> Y miała jedną z następujących własności:")
            print("""(1) zależność jest trywialna (Y zawiera się w X) lub
(2) X jest nadkluczem lub
(3) Y jest atrybutem kluczowym
                """)
            print("[TEST NA 3PN]")
            print("Relacja nie jest w 3 postaci normalnej. Zależności, które nie spełniają żadnego z powyższych warunków to: ")
            for x in destroy_3PN:
                print(x[0] + " -> " + x[1])
            print("")
            print("[DEKOMPOZYCJA ALGORYTMEM SYNTEZY]")
            synthesis(canonical_list)
            print("--------------------------------------------------------------------------------------------------------------------------------")
        else:
            print("Relacja jest w 3 postaci normalnej.")
            print("--------------------------------------------------------------------------------------------------------------------------------")

