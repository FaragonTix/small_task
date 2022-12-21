#application logic and administration
def main() -> None:
    from argparse import ArgumentParser
    from pathlib import Path
    import os.path
    #create parser and add the arguments for input
    parser = ArgumentParser()
    parser.add_argument('-funkce1', help='funkce1', action="store_true")
    parser.add_argument('-funkce2', help='funkce2', action="store_true")
    #input and output files, can be repalced with next arguments
    input_file='D327971_fc1.i'
    output_file='cns.txt'
    #check, if the input file exists
    if os.path.exists(input_file)==False:
        raise Exception("Requested input file {} not found.".format(input_file))
    args = parser.parse_args()
    #raise error if script has run without arguments
    if args.funkce1==False and args.funkce2==False:
        raise Exception("Add -funkce1 or -funkce2 arguments.")

    #create list of blocks; Each blosk make as dictionary, set number as key
    #so data will have json-like structure [{"000":[{X:00, Y:00}, {}]},{}]
    # it can be simplyfied -> {"000":[{X:00, Y:00}, {}], "001":[{}, {}]} if we have guarantee, that
    #names/numbers of blocks will not appears twise
    list_of_blocks=[]
    #flag for entering the data
    start=False
    end=False
    #flag for entering into first block data
    firstenter=True
    #header of the input file
    input_header=[]
    #footer of the input file
    input_footer=[]
    #open input file
    with open(input_file, encoding='utf8', newline='') as f:
        for line in f:
            #take just pure string without formating
            line=line.strip()
            #start of data condition
            if 'Zacatek bloku vrtani' in line:
                start=True 
                input_header.append(line)
            #end of data condition
            if 'Konec bloku vrtani' in line:
                start=False
                end=True
                #all data was collected, save last block
                list_of_blocks.append(dict({key_of_block:list_of_values}))

            if start:
                #condition to eleminate empty rows and rows with bad formating
                if line.startswith('X'):
                    #start of block was found
                    if 'T' in line:
                        #save data from previous block if this is not the first one
                        if not firstenter:
                            list_of_blocks.append(dict({key_of_block:list_of_values}))
                        #separate number of block as key from row and x,y data
                        xy_tuple, key_of_block = t_separator(line)
                        #clear all values
                        list_of_values=[]
                        #add dictionary with x.y values to the list
                        list_of_values.append(xy_slovar(xy_tuple))
                        firstenter=False
                    #just add x,y data from block    
                    else:
                        list_of_values.append(xy_slovar(separator(line)))
            #We are not found the start of data, take header
            else:
                if not end:
                    input_header.append(line)
                #end of data was reached, collect the footer 
                else:
                    input_footer.append(line)
    #run func1 if -funkce1 argument was used
    if args.funkce1:
        list_of_blocks=func1(list_of_blocks)
        #create the outpt file
        write_to_output(output_file, input_header, list_of_blocks, input_footer)
        
    #run func2 if -funkce2 argument was used
    if args.funkce2:
        func2(list_of_blocks)
        


      
def write_to_output(output_file:str, input_header:list, list_of_blocks:list, input_footer:list )-> None:
    with open(output_file, 'w', encoding='utf8') as w:
            #write header
            for line in input_header:
                w.write(line+"\n")
            w.write("\n")
            #write data
            for block_dict in list_of_blocks:
                for key_of_block,values_of_block in block_dict.items():
                    block_start=True
                    for xy_dict in values_of_block:
                        line=""
                        for key, value in xy_dict.items():
                            line=line+key+f'{value:.3f}'
                        if block_start:
                            line=line+"T"+key_of_block
                            block_start=False
                        w.write(line+"\n")
            #write supports
            w.write("\n")
            w.write("$"+"\n")
            w.write("\n")
            #write footer
            for i in range(0, len(input_footer)):
                if i!=len(input_footer)-1:
                    w.write(input_footer[i]+"\n")
                else:
                    w.write(input_footer[i])

#logic for the first argument funkce1
def func1(list_of_blocks: list)->list:
    for block_dict in list_of_blocks:
        for key_of_block,values_of_block in block_dict.items():
            for xy_dict in values_of_block:
                if xy_dict["X"]>50:
                    xy_dict["Y"]+=10
    
    return sort_dicts_by_key(list_of_blocks)

    

#logic for the first argument funkce1
def func2(list_of_blocks:list)-> None:
    all_x=collect_values_by_name("X", list_of_blocks)
    all_y=collect_values_by_name("Y", list_of_blocks)
    print("Min_X: ",min(all_x))
    print("Max_X: ",max(all_x))
    print("Min_Y: ",min(all_y))
    print("Max_Y: ",max(all_y))

#create xy dictionary from tuple
def xy_slovar(xy_tuple: tuple)-> dict:
    xy_dikt=dict({"X":xy_tuple[0], "Y":xy_tuple[1]})
    return xy_dikt

#split the line and create x,y tuple
def separator(line: str) -> tuple:
    line=line.replace("X", "")
    x, y  = line.split("Y")
    try:
        x_value = float(x)
        y_value = float(y)
        return (x_value, y_value)
    #if data can not be converted raise error
    except:
        raise Exception("Unsupported data in file.")

#separte the line as block number and x,y data
def t_separator(line:str) -> list:
    xy_part, t_part = line.split('T')
    xy_tuple= separator(xy_part)
    return xy_tuple, t_part

def sort_dicts_by_key(dict_list):
  # Sort the list of dictionaries by the keys of the dictionaries
  sorted_dict_list = sorted(dict_list, key=lambda x: list(x.keys())[0])
  return sorted_dict_list

#collect all X or Y values
def collect_values_by_name(name:str, data:list)->list:
    reslist=[]
    for block in data:
        for key, values in block.items():
            for value in values:
                reslist.append(value[name])
                            
    return reslist
    
#entery point
if __name__ == '__main__':
    main()