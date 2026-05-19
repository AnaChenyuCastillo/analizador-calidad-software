import os
import subprocess
from datetime import datetime
import shutil
import copy
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pypdf import PdfWriter
from pathlib import Path

# flujo_procesar_datos.py
from graphviz import Digraph

from analizador_calidad_software.analisis_herramientas.cc_grafo.quitar_coment_java import quitar_coment_java1
from analizador_calidad_software.analisis_herramientas.cc_grafo.detectar_class_y_metodos import detect_class_met

from analizador_calidad_software.cli import obtener_repo_root

def seleccionar_archivo():
    try:
        # Abre el cuadro de diálogo para seleccionar un archivo
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=(
                ("Archivos java", "*.java"),
                ("Todos los archivos", "*.*"),
                ("Archivos de texto", "*.txt")
                
            )
        )
        

        # Si el usuario cancela, ruta_archivo será una cadena vacía
        if not ruta_archivo:
            messagebox.showinfo("Información", "No se seleccionó ningún archivo.")
            return

        # Validar que el archivo existe
        if not os.path.isfile(ruta_archivo):
            messagebox.showerror("Error", "El archivo seleccionado no existe.")
            return

        # Mostrar la ruta seleccionada
        messagebox.showinfo("Archivo seleccionado", f"Ruta: {ruta_archivo}")
        return ruta_archivo
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error(1): {e}")





def formatear_codigo(file_path, work_file)  : 
    """
    quitar_coment_java
    quita comentarios , deja las llaves en una linea, corrige identacion y pone un espacio antes de ;

    detectar_class_y_metodos
    detecta las clases y metodos, antepone a las lineas de clases y metodos 'class nombre_clase'  o 'metodo nombre metodo' para facilitar su tratamiento.
    
    :param file_path: Ruta del archivo a formatear, archivo resultado 
    
    """
    if not os.path.isfile(file_path):
        print(f"Error: El archivo '{file_path}' no existe.")
        return
    
        
    try:
       
        
        # Crear cfichero de trabajo
        shutil.copy(file_path, work_file)
       
     
         # llama a quitar quitar_coment_java.py, quita comentarios , deja las llaves en una linea, corrige identacion y pone un espacio antes de ;
        result = quitar_coment_java1(file_path, work_file)
       
         #  llama a detectar_class_y_metodos detecta las clases y metodos, antepone a las lineas de clases y metodos 'class nombre_clase'  o 'metodo nombre metodo' 
         # para facilitar su tratamiento posterior.
         #ejecutar_detect_class_met
        result = detect_class_met(work_file)
        
     
    except Exception as e:
        print(f"Ocurrió un error(2): {e}")

# Función para contar espacios al inicio de una línea
def contar_espacios_inicio(linea):
    contador = 0
    for char in linea:
        if char == ' ':
            contador += 1
        else:
            break
    return contador        
# busca la salida del bloque exceptuando palabras claves 
def buscar_salida_bloque(z,espacios,palabras_exc:list[str]=""):
    
    xfila=z
    espacios_obj=espacios
    max_item=len(T_procesos)
    while (T_procesos[xfila][0]>espacios_obj) or (T_procesos[xfila][1] in palabras_exc):
        xfila=xfila+1
        if xfila==max_item:
           return xfila-1
    return xfila

# busca una palabra en desde una posicion hacia arriba o hacia abajo(direcc=1 o -1)
def buscar_palabra(inicio,fin,espacios,palabras:list[str],direcc=1):
    
    
    num_palabra=0
    
    for yfila in range(inicio,fin,direcc):
        if (T_procesos[yfila][0]) == espacios:
            if  T_procesos[yfila][1] in palabras :
                num_palabra=yfila
    return num_palabra

# tratamiento case y default para identar procesos al mismo nivel de case y default sumanadoles 4
def Tratar_case_default():
    global T_procesos
    for x in range(1,len(T_procesos)):
        proceso_ini=T_procesos[x][1]
        espacios_ini=T_procesos[x][0]
        salida=0
        if T_procesos[x][1] in ("switch"): 
            #busacr posicion switch
            pos_switch=x
            espacios_switch=T_procesos[x][0]
            fin_switch=buscar_salida_bloque(pos_switch+1,espacios_switch) 
            numcase=0
            for y in range(x,fin_switch):
                if T_procesos[y][1] in ("case","default:") :
                    numcase=numcase+1
                else:
                    if numcase>0:
                        T_procesos[y][0]=T_procesos[y][0]+4

# Añadir procesos intermedios finales para if for while switch
def procesos_inter() :
    espacios_ini=0
    salida=0
    x=1
    while x < len(T_procesos):
        proceso_ini=T_procesos[x][1]
        espacios_ini=T_procesos[x][0]
        salida=0
        if T_procesos[x][1] in ("for","while","switch","if","case","default:"):  
            if T_procesos[x][1] in ("for","while","switch"):   
                salida=0
                salida=buscar_salida_bloque(x+1,T_procesos[x][0])
                espacios=T_procesos[salida][0]
            if T_procesos[x][1]=="if":    
                salida=0
                espacios=0
                salida=buscar_salida_bloque(x+1,T_procesos[x][0],["else if","else"])
            if T_procesos[x][1]=="case":  
                salida_case=buscar_salida_bloque(x+1,T_procesos[x][0])
            
                # Case y default al no ir entre {} no detecta proceso
                # comprueba que case tenga proceso e inserta un proceso si no tiene
                if salida_case==x+1:
                    espacios=T_procesos[x][0]+4
                    Insertar_proceso(x+1,espacios,"insertado",x+1,0,"",T_procesos[x][5]) 
                    # ponemos salida a cero para evitar doble insercion
                    salida=0

            if T_procesos[x][1]=="default:": 

                salida_default=buscar_salida_bloque(x+1,T_procesos[x][0])
                # Case y default al no ir entre {} no detecta proceso
                # comprueba que case tenga proceso e inserta un proceso si no tiene
                if salida_default==x+1:
                    Insertar_proceso(x+1,T_procesos[x][0]+4,"insertado",x+1,0,"",T_procesos[x][5]) 
                    # ponemos salida a cero para evitar doble insercion
                    salida=0

            if salida!=0 and espacios<espacios_ini:
               
                nombre_proc="insertado"
                etiqueta_proc="Fin"+T_procesos[x][1]
                Insertar_proceso(salida,espacios_ini,nombre_proc,T_procesos[salida][2],0,etiqueta_proc,T_procesos[x][5]) 
        x=x+1   

def Insertar_proceso(ifila,iespacios,itipo,inodo,inodo_sal=0,etiqueta='',igrafo=0):
   
    text_eti=etiqueta
    
    T_procesos.insert(ifila,[iespacios,itipo,inodo,inodo_sal,text_eti,igrafo])
    
    renumerar_procesos(ifila+1)

# renumera procesos al añadir a la tabla
def renumerar_procesos(z=1):
   
    for x in range(z,len(T_procesos)):
        T_procesos[x][2]=T_procesos[x][2]+1
        if T_procesos[x][3]!=0: 
            T_procesos[x][3]=T_procesos[x][3]+1 

# agrega nodo para el grafico
def agregar_nodo(num_grafo,num_nodo,nombre_nodo):
    if str(num_nodo)!=nombre_nodo:
        nombre_nodo=str(num_nodo)+" "+nombre_nodo
    Id_nodo="N"+str(num_grafo)+"-"+str(num_nodo)
    T_nodos.append([num_grafo,Id_nodo,nombre_nodo])
# agrega arista
def agregar_arista(num_grafo,nodo_i,nodo_f,texto_a=""):
    Id_nodo_i="N"+str(num_grafo)+"-"+str(nodo_i)
    Id_nodo_f="N"+str(num_grafo)+"-"+str(nodo_f)
    T_aristas.append([num_grafo,Id_nodo_i,Id_nodo_f,texto_a ])

def examinar_proceso():
   sw_do=0
   nodos=1
   for x in range(1,len(T_procesos)):
       match T_procesos[x][1]: 
            case 'Inicio':
                agregar_nodo(T_procesos[x][5],nodos,"Inicio")
                agregar_arista(T_procesos[x][5],nodos,nodos+1,'')
                nodos=nodos+1
     
            case 'if':
                nodoif=nodos
                agregar_nodo(T_procesos[x][5],nodos,T_procesos[x][1])
                agregar_arista(T_procesos[x][5],nodos,nodos+1,"si")
                nodos=nodos+1
                fin_if=0
                ultimo_si=0
                fin_if=buscar_salida_bloque(x+1,T_procesos[x][0],["else if","else"])
                ultimo_si=buscar_salida_bloque(x+1,T_procesos[x][0])-1
                          
                T_procesos[ultimo_si][3]= fin_if 
                T_procesos[ultimo_si][4]="fin_if"
                # busca si tiene else o elif si no tiene agrega la arista del no
                sw_else=0
                #Arista no
                #sw_else ?
                #busca clausulas 'else if' o 'else'
               
                sw_else=buscar_palabra(x+1,fin_if,T_procesos[x][0],["else if","else"])

                sigue_bloque=buscar_salida_bloque(x+1,T_procesos[x][0])
                if sw_else==0:
                    agregar_arista(T_procesos[x][5],nodoif,sigue_bloque,"no")             
                nodo_elseif_ant=0
            case 'else if': 
            
                nodoelseif=nodos
                sigue_bloque=buscar_salida_bloque(x+1,T_procesos[x][0])
                agregar_nodo(T_procesos[x][5],nodos,T_procesos[x][1])
                agregar_arista(T_procesos[x][5],nodos,nodos+1,"si")

                # agregar arista del if a else if o a anterior else if
                if nodo_elseif_ant==0:
                   nodo_ant= nodoif
                else:
                   nodo_ant=  nodo_elseif_ant

                agregar_arista(T_procesos[x][5],nodo_ant,nodos,"no")
                         
                nodo_elseif_ant=nodoelseif
                nodos=nodos+1

                fin_if=0
                ultimo_si=0
                fin_if=buscar_salida_bloque(x+1,T_procesos[x][0],["else if","else"])
                
                ultimo_si=buscar_salida_bloque(x+1,T_procesos[x][0])-1
                T_procesos[ultimo_si][3]= fin_if 
                T_procesos[ultimo_si][4]="fin_if"
                

            case 'else':

                agregar_nodo(T_procesos[x][5],nodos,T_procesos[x][1])
                agregar_arista(T_procesos[x][5],nodos,nodos+1,T_procesos[x][1])
               
                # agregar arista del if a else 
                if nodo_elseif_ant==0:
                   nodo_ant= nodoif
                else:
                   nodo_ant=  nodo_elseif_ant

                agregar_arista(T_procesos[x][5],nodo_ant,nodos,'no')
                nodos=nodos+1
                fin_if=0
                fin_if=buscar_salida_bloque(x+1,T_procesos[x][0],["else if","else"])

                ultimo_si=buscar_salida_bloque(x+1,T_procesos[x][0])-1
                T_procesos[ultimo_si][3]= fin_if 
                T_procesos[ultimo_si][4]="fin_if"
 
            case 'try' : 
                nodotry=nodos
                n_finally=0
                num_except=0
                agregar_nodo(T_procesos[x][5],nodos,T_procesos[x][1])
                agregar_arista(T_procesos[x][5],nodos,nodos+1,"valid")
                nodos=nodos+1
                salida_try=0
                
                salida_try=buscar_salida_bloque(x+1,T_procesos[x][0],["catch","finally"])
                fin_valid_tray=0
                fin_valid_tray=buscar_salida_bloque(x+1,T_procesos[x][0])-1
                
                
                # busac finally
                n_finally=buscar_palabra(x+1,salida_try,T_procesos[x][0],["finally"])
                # siguiente nodo ultima validacion a finally si existe o salida try si no existe
                            
                if n_finally !=0  :
                    T_procesos[fin_valid_tray][3]= n_finally
                    T_procesos[fin_valid_tray][4]="fin valid"
                else:
                    T_procesos[fin_valid_tray][3]= salida_try
                    T_procesos[fin_valid_tray][4]="fin valid"
            case 'catch': 
            
                nodocatch=nodos
                num_except=num_except+1
                texto_nodo="catch "+str(num_except)
                sigue_bloque=buscar_salida_bloque(x+1,T_procesos[x][0])
                agregar_nodo(T_procesos[x][5],nodos,texto_nodo)
                agregar_arista(T_procesos[x][5],nodos,nodos+1,"")
                nodos=nodos+1
                # agregar arista de try a catch
                agregar_arista(T_procesos[x][5],nodotry,nodocatch,"catch")
                # agregar arista del catch a finally o a fintry si se cumple excepcion
                
                if n_finally is None:
                    n_finally=0

                if n_finally==0:
                   nodo_sigue=salida_try 
                else:
                   nodo_sigue=n_finally
                              
                T_procesos[sigue_bloque-1][3]= nodo_sigue
                T_procesos[sigue_bloque-1][4]="fin catch"
                         
                
                
        

            case 'finally':
                nodofinally=nodos
                
                agregar_nodo(T_procesos[x][5],nodos,T_procesos[x][1])
                agregar_arista(T_procesos[x][5],nodos,nodos+1,T_procesos[x][1])
                
                nodos=nodos+1
                fin_finally=0  
                esp_finally=0          
                fin_finally=buscar_salida_bloque(x+1,T_procesos[x+1][0])
                T_procesos[fin_finally][3]= salida_try
                T_procesos[fin_finally][4]="fin try"   
            case 'do':
                sw_do=1
                nododo=T_procesos[x][2]
                espacios= T_procesos[x][0]
                
                agregar_nodo(T_procesos[x][5],nodos,'do')
                agregar_arista(T_procesos[x][5],nodos,nodos+1,"do")  
                nodos=nodos+1
                
           
            
            case 'while':
                nodowhile=T_procesos[x][2]
                espacios= T_procesos[x][0]

                if sw_do==1:
                    
                    agregar_nodo(T_procesos[x][5],nodos,'while')
                    agregar_arista(T_procesos[x][5],nodos,nodos+1,"fin do")  
                    
                    # agregar arista retorno a do
                    agregar_arista(T_procesos[x][5],nodowhile,nododo,"do r")  
                else:
                    agregar_nodo(T_procesos[x][5],nodos,'while')
                    agregar_arista(T_procesos[x][5],nodos,nodos+1,"")  
                    
                    salida_while=buscar_salida_bloque(x+1,T_procesos[x+1][0])+1
                                      
                    #agregamos arista salida while
                    agregar_arista(T_procesos[x][5],nodos,salida_while,"fin while")  
                    #modificamos retorno fin while retorno
                    T_procesos[salida_while-1][3]=nodowhile
                    T_procesos[salida_while-1][4]="wh r"
                nodos=nodos+1    
                sw_do=0
            case 'for':

                nodofor=T_procesos[x][2]
                salida_for=0
                espacios= T_procesos[x][0]
                salida_for=buscar_salida_bloque(x+1,espacios)
                agregar_nodo(T_procesos[x][5],nodos,'for')
                agregar_arista(T_procesos[x][5],nodos,nodos+1,"for 1")  

                nodos=nodos+1
        
                agregar_arista(T_procesos[x][5],nodofor,T_procesos[salida_for][2],"for 2")

                #modificamos salida de fin for retorno
                T_procesos[salida_for-1][3]=nodofor
                T_procesos[salida_for-1][4]="for r"
                
           

            case 'switch':
                nodo_switch=x
                agregar_nodo(T_procesos[x][5],nodos,'switch')
                nodos=nodos+1
                espacios_switch=T_procesos[x][0]
                salida_switch=buscar_salida_bloque(x+1,espacios_switch,["case","default:"])

                numcase=0

            case 'case':
                T_case=[["linea_case"]]
                numcase=numcase+1
                nodo_case=x
                espacios_case=T_procesos[x][0]
                agregar_nodo(T_procesos[x][5],nodos,'case '+str(numcase))
                nodos=nodos+1
                
                salida_case=buscar_salida_bloque(x+1,espacios_case)
                
                #agregar arista de switch a case 
                agregar_arista(T_procesos[x][5],nodo_switch,nodo_case,'case'+str(numcase))
                                
                ultimo_case=salida_case-1
                # agregar arista a siguiente proceso
                agregar_arista(T_procesos[x][5],nodo_case,nodo_case+1)
       
                #modificar salida de los cases
                T_procesos[ultimo_case][3]=salida_switch
                T_procesos[ultimo_case][4]='fin case'+str(numcase)
               

            case 'default:':
                
                nodo_default=x
                espacios_default=T_procesos[x][0]
                agregar_nodo(T_procesos[x][5],nodos,'default')
                nodos=nodos+1
                salida_default=buscar_salida_bloque(x+1,espacios_default)
                ultimo_default=salida_default-1

                # agregar arista a siguiente proceso
                agregar_arista(T_procesos[x][5],nodo_default,nodo_default+1)
                #agergar arista de switch a default
                agregar_arista(T_procesos[x][5],nodo_switch,nodo_default,'default')
                # modificar salida ultimo default a salida switch
                T_procesos[ultimo_default][3]=salida_switch
                T_procesos[ultimo_default][4]='fin default'

            case 'intermedio'|'insertado':
                nodosigue=0
                agregar_nodo(T_procesos[x][5],nodos,T_procesos[x][1])
                
                if T_procesos[x][4]=="":
                    texto_arista=""
                else:
                    texto_arista=T_procesos[x][4]

                if T_procesos[x][3]==0:
                    nodosigue=nodos+1
                else:
                    nodosigue=T_procesos[x][3]
        
                agregar_arista(T_procesos[x][5],nodos,nodosigue,texto_arista)
                nodos=nodos+1  
    
            case 'Fin':
                agregar_nodo(T_procesos[x][5],nodos,"Fin")

# paso 1 formatear fichero y copiar en file.txt                
def formatear_file():
    ruta = Path(mi_archivo) # archivo a tratar
        
    nombre_dirsel=""
    Nombre_arch = ruta.stem
    directorio_arc = ruta.parent
        
    
    
    if directorio_sel!="" and directorio_sel!=directorio_arc:

        nombre_dirsel=directorio_sel

        nombre_dirsel="("+str(nombre_dirsel).replace("/", "_")+")"
        
    repo_root = obtener_repo_root()
    
    Directoriow=repo_root / "src"/ "analizador_calidad_software" / "resultados"  # directorio trabajo
    if not os.path.exists(Directoriow):  
            os.makedirs(Directoriow)  
            print(f"Directorio creado: {Directoriow}")
        

    work_file = Directoriow / f"{Nombre_arch}dcc.txt"
    grafo_file = Directoriow / f"{Nombre_arch}dcc"

    formatear_codigo(ruta, work_file)
    return(work_file,grafo_file,Directoriow)

#paso 2 leer fichero e identificar palabras clave y crear tabla procesos
def palabras_crear_procesos(work_file):
    with open(work_file, 'r', encoding='utf-8') as archivo:
        
        Nivel_ident=1
        tipo="intermedio"
        nodo=1
        sw_newnode=1
        llaves_ant=0
    
        num_grafo=0
        
    

        #
        numero_metodo=0
        espacios_ant=0
        
        for numero_linea, linea in enumerate(archivo, start=1): 
            espacios = contar_espacios_inicio(linea)
            
            tipo="intermedio"
            if espacios != espacios_ant:
                sw_newnode=1
            cadena = linea
            palabras = cadena.split()
            if not palabras :
                continue
            
            if  palabras[0][0] in ("#","{","}") :
                continue
                # print(palabras[0]) 
            if  palabras[0] != "metodo" and numero_metodo==0 :
                continue
                # salta hasta el primer metodo     
                    
            etiqueta=""    

            if palabras[0] in ("metodo","for","while","do","if","else","try","catch","finally","switch","case","default:"):
                tipo=palabras[0]
                tipo_ant=tipo
                nodo_ant=nodo
                sw_newnode=1
                
                if palabras[0] =="metodo":
                    numero_metodo=numero_metodo+1
                    etiqueta=palabras[1]
                else:
                    etiqueta="" 
                    
                if palabras[0]=="else" and len(palabras)>1 and palabras[1]=="if":
                    tipo="else if"
        
            
            
            if sw_newnode == 1: 
                T_procesos.append([espacios,tipo,nodo,0,etiqueta,numero_metodo])
                sw_newnode=0
                nodo=nodo+1
            espacios_ant=espacios

# generar tabla de nodos Tnodos y aristas Taristas y generar grafos            
def generar_nodos_aristas():
    global T_nodos,T_aristas,T_procesos
    repo_root = obtener_repo_root()
    graphviz_bin = repo_root / "herramientas" / "graphviz" / "bin"
    os.environ["PATH"] += os.pathsep + str(graphviz_bin) 
    for n_grafo in range(1,numero_grafos+1):
        # Modificar inicio y fin para grafo !=0
        

        T_nodos=[[num_grafo,"NUM_nodo","Nomb_nodo","Atributos"]]
        T_aristas=[[num_grafo,"Nodo_I","Nodo_F","Texto_A"]]
        filtradas = [sublista for sublista in cop_T_procesos if sublista[5]== n_grafo]
        T_procesos=copy.deepcopy(filtradas)
        if n_grafo!=0:
            T_procesos.insert(1,[0,'Inicio',1,0,'',n_grafo])
        
            x=len(T_procesos)
            T_procesos.append([0,'Fin',x+1,0,'',n_grafo]) 
        
        
        # Renumerar procesos

        
        filas = len(T_procesos)
        for y in range(1,filas):
            T_procesos[y][2]=y
    
        
        nodos=1
        # examina el array proceso y genera los arrays nodos y aristas del grafo
        examinar_proceso()

            
        #Tabla aristas y nodos tienen cabecera en 0 
        calc_ciclo=(len(T_aristas) -1) - (len(T_nodos) -1) +2
        
        Nombre_grafico=""
        #nproc=T_procesos[n_grafo][5]
        ruta = Path(mi_archivo) # archivo a tratar
        mruta=ruta.as_posix()
        if n_grafo != 0:
            mruta=mruta +  " metodo: " + T_procesos[0][4]

        Texto_Label= str(f"{mruta} \n Calculo complejidad ciclomatica (nº aristas-nº nodos +2): {str(len(T_aristas)-1)} - {str(len(T_nodos)-1)} +2= {str(calc_ciclo)}")
        from graphviz import Digraph    

        

        dot = Digraph(name=str(ruta), comment='Flujo de procesar_datos', format='pdf')
        dot.attr(label=Texto_Label, fontsize="18", labelloc="t")
        # numero de grafos len(T_def) -1 + 1 del principal(0) = len(T_def)


        for x in range(1,len(T_nodos)):
            dot.node(T_nodos[x][1],T_nodos[x][2])

        dot.node(T_nodos[len(T_nodos)-1][1],T_nodos[len(T_nodos)-1][2],fontname="Helvetica-Bold")   
        for x in range(1,len(T_aristas)):
            dot.edge(T_aristas[x][1],T_aristas[x][2],T_aristas[x][3])
        
        
        grafo_file1 = Path(str(grafo_file) + str(n_grafo))
        grafo_file1pdf = Path(str(grafo_file1) + ".pdf")
        T_grafos_files.append(grafo_file1pdf)
        print("grafo_file1:",str(grafo_file1))
        
    
        print("grafo_file1_final:",grafo_file1)
    
        print("tipo grafo_file1:",type(grafo_file1))
        output_path = dot.render(engine="dot",filename=str(grafo_file1), cleanup=bool)
        dot.clear()

# fusionar archivos Pdfs de grafos        
def fusionar_pdfs():    
    global grafo_file
    marca_tiempo=datetime.today().strftime("%Y%m%d%H%M%S")
    grafo_file=str(grafo_file) + marca_tiempo +".pdf"
    fusionador = PdfWriter()
    for pdf in T_grafos_files:
        fusionador.append(pdf)

    print(f'grafo_file:{grafo_file}')
    fusionador.write(grafo_file)
    fusionador.close()
    # borrar archivos de trabajo pdfs y work_file.txt
    for pdf in T_grafos_files:
        os.remove(pdf)
    os.remove(work_file)  
    return grafo_file

def flujo_grafos_java(arch=""):
    global mi_archivo,directorio_sel,work_file,grafo_file,repo_root,ruta,num_grafo,numero_grafos  
    global T_procesos,cop_T_procesos,T_def,T_grafos_files,T_nodos,T_aristas
    # Crear ventana principal oculta
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal

    # Llamar a la función
    if arch != "":
        mi_archivo = arch
    else:    
        mi_archivo=seleccionar_archivo()
    
    #Esta es la ruta del archivo
    directorio_sel=""

    if len(sys.argv) >= 1:
        directorio_sel= Path(sys.argv[0])
          

    num_grafo=0
    T_procesos=[["INDEN","TIPO","NODOI","NODO_sal","etiqueta",num_grafo]]

    # Procesar fichero 
    # paso 1 formatear fichero y copiar en file.txt
    work_file,grafo_file,Directoriow=formatear_file()
    
    #paso 2 leer fichero e identificar palabras clave y crear tabla procesos
    palabras_crear_procesos(work_file)
    # tratamiento case y default para identar procesos al mismo nivel de case y default sumanadoles 4
   
    Tratar_case_default()
       
    # Añadir procesos intermedios finales para if for while switch
    procesos_inter()



    # numero de grafos=numero de metodos
    numero_grafos=max(fila[5] for fila in T_procesos)



    # preparar tabla pdfs
    T_grafos_files=[]
    #realiza copia de T_proceso para segmentar grafos
    cop_T_procesos=copy.deepcopy(T_procesos)


  
    # generar tabla de nodos Tnodos y aristas Taristas y generar grafos
    generar_nodos_aristas()
    
    # fusionar archivos Pdfs de grafos
    print(f"Fusionando archivos")
    ruta=fusionar_pdfs()

    return ruta



#              *********** Fin def  ************            
if __name__ == "__main__":
    flujo_grafos_java()        

