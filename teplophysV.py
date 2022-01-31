#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3 as db
import PySimpleGUI as sg


def get_data(con,table: str) -> dict:
    cur = con.cursor().execute(f'SELECT * FROM {table}')
    data = [list(line) for line in cur.fetchall()]
    headers = list(next(zip(*cur.description)))
    return {'headers': headers, 'data': data}

def add_rec(db, table_name, field_names, field_vals):
    cur = db.cursor()
    sql_stm = "INSERT INTO "+table_name+" "+field_names
    num_fields = len(field_vals)
    val = " VALUES ("+"?,"*(num_fields-1)+"?) "
    sql_stm += val
    cur.execute(sql_stm,field_vals)
    db.commit()
    sql_stm = "SELECT * FROM "+table_name
    cur.execute(sql_stm)
    rows = cur.fetchall()
    return rows[-1]


def set_data(con, table: str, data: list) -> None:
    cur = con.cursor()
    column_count = len(data)
    cur.execute(f'INSERT INTO {table} VALUES (?{", ?" * (column_count - 1)})', data)
    con.commit()

def save_results(data):
    with open("results.txt", 'a') as f:
        f.write(data)

    sg.popup('Результаты сохранены в файле results.txt')

    
def composition_window():
    conn = db.connect(database="teplophys.db")
    cur = conn.cursor()

    table = 'Composit_Descr'
    sql_stm = "SELECT Composition_ID, Composition_Name, Composition_Descr FROM "+table
    cur.execute(sql_stm)
    compositions = cur.fetchall()
    compositions_headings = ['ID','Наименование','Описание']
    results =''
    def recipy_choose(rec_ID):
        fields = "Composit_Descr.Composition_Name, Ingredients.Ingr_Name, Composit_Rec.Mass_PHR " 
        recipy=cur.execute("select " +fields+ "  from Composit_Descr, Ingredients, Composit_Rec where Composit_Descr.Composition_ID=Composit_Rec.Composition_ID and Ingredients.Ingr_ID=Composit_Rec.Ingr_ID and Composit_Rec.Composition_ID = " + str(rec_ID))
        rec_lst = []
        for row in recipy:
            rec_lst.append(list(row)[1:])
        return(rec_lst)
        
    def composition_choose(rec_ID):
        fields = "Composit_Descr.Composition_Name, Ingredients.Ingr_Name, Ingredients.Ingr_Descr, Ingredients.a_field, Ingredients.lamb_field, Ingredients.rho_field, Ingredients.C_field, Composit_Rec.Mass_PHR " 
        recipy_full=cur.execute("select " +fields+ "  from Composit_Descr, Ingredients, Composit_Rec where Composit_Descr.Composition_ID=Composit_Rec.Composition_ID and Ingredients.Ingr_ID=Composit_Rec.Ingr_ID and Composit_Rec.Composition_ID = " + str(rec_ID))        
        rec_lst = []
        for row in recipy_full:
            rec_lst.append(list(row))
        return(rec_lst)    

    def edit_composition(rec_ID): 
        fields = "Composit_Descr.Composition_Name, Composit_Descr.Composition_Descr, Ingredients.Ingr_Name, Composit_Rec.Mass_PHR, Composit_Rec.Ingr_ID " 
        recipy=cur.execute("select " +fields+ "  from Composit_Descr, Ingredients, Composit_Rec where Composit_Descr.Composition_ID=Composit_Rec.Composition_ID and Ingredients.Ingr_ID=Composit_Rec.Ingr_ID and Composit_Rec.Composition_ID = " + str(rec_ID))
        rec_lst = []
        for row in recipy:
            rec_lst.append(list(row))
        recipy=[]
        for i in range(len(rec_lst)):
            recipy.append(rec_lst[i][2:])
        layout = [  
                   [sg.Text('Отредактировать наименование/описание:', justification='с', text_color = 'red', font = ('bold'))],
                   [sg.Text('Наименование', justification='r', size=(13,1)),
              sg.Input(size=(13,1),do_not_clear=True, key='-Name-', default_text = rec_lst[0][0])],
              [sg.Text('Описание', justification='r', size=(13,1)),
              sg.Input(size=(35,1),do_not_clear=True, key='-Descr-', default_text = rec_lst[0][1])],
              [sg.Text('Отредактировать состав:', justification='с', text_color = 'red', font = ('bold'))]
              ]
        for i in range(len(recipy)):
            layout.append([
                        sg.Text(recipy[i][0], justification='l', size=(55,1)),
                        sg.Input(size=(5,1),do_not_clear=True, key='-Comp'+str(i)+'-',default_text = recipy[i][1])])              
        layout.append([ sg.B('Принять'),sg.B('Выход')]) 
 
        window = sg.Window('Композиции', layout,finalize=True)
        while True:
            event, values = window.read()
            if event in (None, 'Exit', 'Выход'):
                break
            if event == 'Принять':
                error = False
                for i in range(len(rec_lst)):
                    rec_lst[i][0]=values['-Name-']
                    rec_lst[i][1]=values['-Descr-']
                    try:
                        rec_lst[i][3]=float(values['-Comp'+str(i)+'-'])
                    except:
                        sg.popup('Данные не корректны!')
                        error = True
                        break    
                if error == False:
                    cur.execute('update Composit_Descr SET Composition_Name = "'+rec_lst[0][0]+'", Composition_Descr = "'+rec_lst[0][1]+'" WHERE Composition_ID = '+ str(rec_ID))
                    for i in range(len(rec_lst)):
                        cur.execute('update Composit_Rec SET Mass_PHR = '+str(rec_lst[i][3])+' WHERE Composition_ID = '+ str(rec_ID)+' AND Composit_Rec.Ingr_ID = '+str(rec_lst[i][4]))
                    conn.commit()
                    sg.popup('Изменения внесены')                    
        window.close()                     

    def new_composition():
        ingreds = cur.execute("select Ingr_ID, Ingr_Name from Ingredients") 
        ing_lst = []
        for row in ingreds:
            ing_lst.append(list(row))
        ing_headings = ['ID','Наименование'] 
        recipy_lst = []
        layout = [  
                   [sg.Text('Создайте наименование/описание:', justification='с', text_color = 'red', font = ('bold'))],
                   [sg.Text('Наименование', justification='r', size=(13,1)),
              sg.Input(size=(13,1),do_not_clear=True, key='-Name-')],
              [sg.Text('Описание', justification='r', size=(13,1)),
              sg.Input(size=(35,1),do_not_clear=True, key='-Descr-')],
              [sg.Text('Выделите компонент:', justification='с', text_color = 'red', font = ('bold'))]
              ]
        layout.append([sg.Table(values=ing_lst,
                      headings=ing_headings,
                      justification='l',
                      display_row_numbers=False,
                      key='-TABLE1-')       
                      ])
        layout.append([sg.Text('Введите содержание, мас.частей:', justification='r', size=(30,1),text_color = 'red', font = ('bold')),
                      sg.Input(size=(6,1),do_not_clear=True, key='-PHR-'),sg.B('Добавить компонент')
                      ])
        layout.append([sg.Table(values=[['    ','                      ','    ']],
                      headings=['ID','Наименование','Мас.ч.'],
                      justification='l',
                      display_row_numbers=False,
                      key='-TABLE2-')
        
                      ])                                    
        layout.append([ sg.B('Принять композицию'),sg.B('Выход')])                   
        window = sg.Window('Новая композиция', layout,finalize=True)
        while True:
            event, values = window.read()
            if event in (None, 'Exit', 'Выход'):
                break
            if event == 'Добавить компонент':
                recipy_row = ing_lst[values['-TABLE1-'][0]]
                if values['-PHR-']:
                    try:
                        phr = float(values['-PHR-'])
                        recipy_row.append(phr)
                        recipy_lst.append(recipy_row)
                        window['-TABLE2-'].update(values=recipy_lst)
                        window.refresh()
                    except: 
                        sg.popup('Данные не корректны!')               
            if event == 'Принять композицию':
                if not (values['-Name-'] and values['-Descr-']):
                    sg.popup('Поля не должны быть пустыми!')
                elif recipy_lst == []:
                    sg.popup('Нужно создать рецепт!')
                else:
                    try:
                        insert_Name=cur.execute('INSERT INTO Composit_Descr (Composition_Name, Composition_Descr) Values ("'+values['-Name-']+'", "'+values['-Descr-']+'")')
                    except: 
                        sg.popup('Название должно быть уникальным!')
                        insert_Name = None
                    if insert_Name is not None:
                        conn.commit()
                        dic_table = get_data(conn,"Composit_Descr")
                        lastID = dic_table['data'][-1][0]
                        for i in range(len(recipy_lst)):
                            cur.execute('INSERT INTO Composit_Rec (Composition_ID, Ingr_ID, Mass_PHR) Values ('+str(lastID)+', '+str(recipy_lst[i][0])+', '+str(recipy_lst[i][2])+')')
                        conn.commit()
                        sg.popup('Запись добавлена')
                        break
        window.close()        

    rec_ID = 1
    recipy_headings = ['Компонент','Мас.ч.']
    rec_lst = recipy_choose(rec_ID)
    
    layout = [
              [sg.Text('Выбрать существующую композицию:', justification='с')],
              [sg.Table(values=compositions,
                      headings=compositions_headings,
                      justification='r',
                      display_row_numbers=False,
                      num_rows=10,
                      key='-TABLE1-',
                      enable_events = True),
               sg.Table(values=rec_lst,
                      headings=recipy_headings,
                      justification='l',
                      display_row_numbers=False,
                      key='-TABLE2-')       
                      ],
              [ sg.B('Выбрать'),sg.B('Удалить'),sg.B('Редактировать'),sg.B('Создать'),sg.B('Обновить'),sg.B('Выход')]       
              ]
    window = sg.Window('Композиции', layout,finalize=True)
    while True:
        event, values = window.read()
        if event == '-TABLE1-':
            window['-TABLE2-'].update(values=recipy_choose(compositions[values['-TABLE1-'][0]][0]))
            window.refresh()
        if event in (None, 'Exit', 'Выход'):
            break
        if event == 'Выбрать':
            if values['-TABLE1-']:
                recipy=recipy_choose(compositions[values['-TABLE1-'][0]][0])
                to_print = 'Состав композиции ' + compositions[values['-TABLE1-'][0]][1] + ':' 
                results += to_print+'\n'
                print(to_print)
                for i in range(len(recipy)):
                    to_print = recipy[i][0] + '  ' + str(recipy[i][1])
                    results += to_print+'\n'                  
                    print(to_print)    
                rec_lst=composition_choose(compositions[values['-TABLE1-'][0]][0])
                TotVol=0
                Vols=[]
                for i in range(len(rec_lst)):
                    Vols.append(rec_lst[i][-1]/rec_lst[i][-3])
                    TotVol += Vols[i]
                for i in range(len(rec_lst)):
                    rec_lst[i].append(Vols[i]/TotVol)    
                Lam=0
                for i in range(len(rec_lst)):
                    if rec_lst[i][2] != "Технический углерод":
                        Lam += rec_lst[i][-1]*rec_lst[i][-5] 
                for i in range(len(rec_lst)):
                    if rec_lst[i][2] == "Технический углерод":
                        Lam += 1.0E-2*rec_lst[i][-2]*rec_lst[i][-5]
                Rho=0
                for i in range(len(rec_lst)):
                    Rho += rec_lst[i][-1]*rec_lst[i][-4]
                Cp=0
                for i in range(len(rec_lst)):
                    Cp += rec_lst[i][-1]*rec_lst[i][-3]                
                to_print = 'Результаты расчета:'      
                print(to_print)
                results += to_print+'\n'
                to_print = 'Коэффициент теплопроводности, Вт/(м*К)  '+str(round(Lam,3))
                results += to_print+'\n'
                print(to_print)
                aT = 0
                for i in range(len(rec_lst)):
                    aT += rec_lst[i][-1]*rec_lst[i][-6]
                to_print = 'Коэффициент температуропроводности, м2/с*10^8  ' + str(round(aT,3))
                results += to_print+'\n'
                print(to_print) 
                to_print = 'Плотность, кг/м^3   ' +  str(round(Rho,0))
                results += to_print+'\n'
                print(to_print)
                to_print = 'Теплоемкость, кДж/кг*К   ' +  str(round(Cp,2))+'\n'
                results += to_print+'\n'
                print(to_print)                                               
                window['-TABLE2-'].update(values=recipy_choose(compositions[values['-TABLE1-'][0]][0]))
                window.refresh()
        if event == 'Редактировать':
            if values['-TABLE1-']:
                edit_composition(compositions[values['-TABLE1-'][0]][0])
                window.refresh()
        if event == 'Создать':
            new_composition()
        if event == 'Удалить':
            if values['-TABLE1-']:
                rec_ID = compositions[values['-TABLE1-'][0]][0]
                sql_stm ='DELETE FROM ' +'Composit_Descr'+ ' WHERE Composition_ID=' +str(rec_ID) 
                cur.execute(sql_stm)
                cur.execute("PRAGMA foreign_keys =ON")
                conn.commit()
                table = 'Composit_Descr'
                sql_stm = "SELECT Composition_ID, Composition_Name, Composition_Descr FROM "+table
                cur.execute(sql_stm)
                compositions = cur.fetchall()
                window['-TABLE1-'].update(values=compositions)
                window['-TABLE2-'].update(values=['        ','     '])
                window.refresh() 
        if event == 'Обновить': 
            cur.execute('SELECT Composition_ID, Composition_Name, Composition_Descr FROM Composit_Descr')
            compositions = cur.fetchall()
            if values['-TABLE1-']: 
                window['-TABLE1-'].update(values=compositions)
                window['-TABLE2-'].update(values=recipy_choose(compositions[values['-TABLE1-'][0]][0]))       
    window.close()
    return(results)            

def ingredients_window():
    conn = db.connect(database="teplophys.db")
    cur = conn.cursor()

    def edit_ingred(record):
        types_list=['Матрица','Ингредиент','Технический углерод' ]
        values_list=['-a_field-','-lamb_field-','-rho_field-','-C_field-']
        layout = [
                  [sg.Text('Отредактируйте поля:', justification='с')],
                  [sg.Text('Наименование', justification='r', size=(13,1)),
                    sg.Input(size=(80,1),do_not_clear=True, key='-Name-',default_text = record[1])],
                  [sg.Text('Выделите Тип', justification='r', size=(13,1)),
                    sg.Listbox(size=(20,1),values= types_list, key='-Type-',default_values = [record[2]])],
                  [sg.Text('Температуропроводность, м2/с*10^8', justification='r', size=(33,1)),
                    sg.Input(size=(6,1),do_not_clear=True, key='-a_field-',default_text = record[3])],
                  [sg.Text('Теплопроводность, Вт/(м*К)', justification='r', size=(33,1)),
                    sg.Input(size=(6,1),do_not_clear=True, key='-lamb_field-',default_text = record[4])],
                  [sg.Text('Плотность, кг/м3)', justification='r', size=(33,1)),
                    sg.Input(size=(6,1),do_not_clear=True, key='-rho_field-',default_text = record[5])],
                  [sg.Text('Теплоемкость, кДж/кг*К)', justification='r', size=(33,1)),
                    sg.Input(size=(6,1),do_not_clear=True, key='-C_field-',default_text = record[6])], 
                  [ sg.B('Изменить запись'),sg.B('Добавить запись'),sg.B('Выход')] 
                 ]
        window = sg.Window('Компонент', layout,finalize=True)
        while True:
            event, values = window.read()
            if event in (None, 'Exit', 'Выход'):
                break
            if event == 'Изменить запись':
                error = False
                for i in range(len(values_list)):
                    try:
                        float(values[values_list[i]])
                    except:
                        sg.popup('Данные не корректны!')
                        error = True
                        break
                if error == False:
                    cur.execute(
                'update Ingredients SET '+
                'Ingr_Name = "'+values['-Name-']+'",'+
                'Ingr_Descr = "'+values['-Type-'][0]+'",'+
                'a_field ='+str(values['-a_field-'])+','+
                'lamb_field ='+str(values['-lamb_field-'])+','+
                'rho_field ='+str(values['-rho_field-'])+','+
                'C_field ='+str(values['-C_field-'])+' '+               
                'WHERE Ingr_ID = '+ str(record[0]))
                    conn.commit()                 
                    sg.popup('Изменения внесены')
            if event == 'Добавить запись':
                error = False
                for i in range(len(values_list)):
                    try:
                        float(values[values_list[i]])
                    except:
                        sg.popup('Данные не корректны!')
                        error = True
                        break
                if error == False:
                    sql_stm = ('INSERT INTO Ingredients (Ingr_Name, Ingr_Descr, a_field, lamb_field, rho_field, C_field) Values ("'+
                    values['-Name-']+'","'+
                    values['-Type-'][0]+'",'+
                    str(values['-a_field-'])+','+
                    str(values['-lamb_field-'])+','+
                    str(values['-rho_field-'])+','+
                    str(values['-C_field-'])+')')
                    try:
                        cur.execute(sql_stm)
                        conn.commit()                 
                        sg.popup('Изменения внесены')
                    except:
                        sg.popup('Данные не корректны!')
                        error = True
                        break
        window.close()                     
                                     

    table = 'Ingredients'
    sql_stm = "SELECT * FROM "+table
    cur.execute(sql_stm)
    ingreds = cur.fetchall()
    ingreds_headings = ['ID','Наименование','Тип','a,м2/с*10^8', 'Lamba, Вт/(м*К)', 'Плотность, кг/м3', 'Cp, кДж/кг*К' ]
    layout = [
             [sg.Text('Компоненты', justification='с')],
             [sg.Table(values=ingreds,
                      headings=ingreds_headings,
                      justification='r',
                      display_row_numbers=False,
                      auto_size_columns = False,
                      col_widths =[4,20,10,15,15,15,15],
                      num_rows=20,
                      key='-TABLE1-',
                      enable_events = True),
                      ],
             [sg.B('Редактировать/Добавить'),sg.B('Удалить'),sg.B('Обновить'),sg.B('Выход')]
             ]
    window = sg.Window('Ингредиенты', layout,finalize=True)
    while True:
        event, values = window.read()
        if event == 'Редактировать/Добавить':
            if values['-TABLE1-']:
                edit_ingred(ingreds[values['-TABLE1-'][0]])
                window.refresh()            
        if event in (None, 'Exit', 'Выход'):
            break
        if event == 'Удалить':
            if values['-TABLE1-']:
                rec_ID = ingreds[values['-TABLE1-'][0]][0]
                sql_stm ='DELETE FROM ' +'Ingredients'+ ' WHERE Ingr_ID=' +str(rec_ID) 
                cur.execute(sql_stm)
                conn.commit()
                sg.popup('Запись удалена')
        if event == 'Обновить':
            cur.execute('SELECT * FROM Ingredients')
            ingreds = cur.fetchall() 
            window['-TABLE1-'].update(values=ingreds)                      

    window.close()

def main_window():
    howto = '''
            В пункте "Композиции" меню "База данных" выделите и отредактируйте имеющуюся композицию
            или создайте новую с помощью кнопок "Редактировать" и "Создать".
            Кнопка "Удалить" удаляет композицию из базы данных.
            Кнопка "Обновить" обновляет окно композиций после создания новой композиции. 
            При нажатии кнопки "Выбрать" для выделенной композиции будут расчитаны 
            коэффициент теплопроводности и коэффициент температуропроводности.
            Для сохранения результатов расчета в текстовом файле выберите в меню
            "Файл" пункт "Сохранить". 
            Пункт "Ингредиенты" в меню "Базы данных" открывает форму для редактирования таблицы
            ингредиентов. 
            '''
    about = '''
            Программа расчета теплофизических характеристик полимерных композиций.
            Программа содержит 3 части - интерфейс, расчетный модуль и базу данных теплофизических характеристик.
            Расчет производится на основании "правила смесей", в соотвествии с которым значение
            выходного параметра композиции (плотность, теплоемкость, теплопроводность) рассчитывается
            как сумма данных параметров каждого компонента, умноженных на их объемные доли в смеси.
            Для технического углерода теплофизические свойства композиции вычисляются как линейная функция массового
            содержания каждого вида технического углерода.
            Версия 1.0 2022 г.
            '''       
    sg.set_options(element_padding=(0, 0))        
    menu_def = [['Файл', ['Сохранить', 'Выход' ]],
                ['База данных', ['Композиции','Ингредиенты']],
                ['Справка', ['Порядок расчета','О программе' ]]
                ]
    layout = [
              [sg.Menu(menu_def, tearoff=False, pad=(20,1))],
              [sg.Output(size=(110,20),key ='-Out-')],
              [sg.Cancel('Выход')],
              ]
    window = sg.Window("Расчет теплофизических свойств полимерной композиции",
                       layout,
                       default_element_size=(12, 1),
                       grab_anywhere=True,
                       default_button_element_size=(12, 1))                       
    while True:
        event, values = window.read()
        if event in (None, 'Exit', 'Выход'):
           break 
        if event == 'Порядок расчета':
            sg.popup('Порядок расчета',howto,grab_anywhere=True)
        if event == 'О программе':
            sg.popup('О программе',about,grab_anywhere=True)            
        if event == 'Композиции':
            results=composition_window()
        if event == 'Ингредиенты':
            ingredients_window()
        if event == 'Сохранить':
            try:
                save_results(results)
            except:
                sg.popup('Окно пустое')
    window.close()

main_window()

