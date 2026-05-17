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

from analizador_calidad_software.analisis_herramientas.cc_grafo.quitar_coment import ejecutar_quitar_comentario
from analizador_calidad_software.cli import obtener_repo_root


def seleccionar_archivo():
    try:
        # Abre el cuadro de diálogo para seleccionar un archivo
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=(
                ("Archivos Python", "*.py"),
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




def replace_tabs_with_spaces(file_path, work_file, spaces_per_tab=4)  : 
    """
    Reemplaza todos los tabuladores en un archivo de texto por un número fijo de espacios 
    y elimina lineas en blanco y  comentarios
    
    :param file_path: Ruta del archivo a modificar.
    :param spaces_per_tab: Número de espacios que reemplazarán a cada tabulador.
    """
    if not os.path.isfile(file_path):
        print(f"Error: El archivo '{file_path}' no existe.")
        return
    
        
    try:
       
        
        # Crear cfichero de trabajo
        shutil.copy(file_path, work_file)
       
         # llama a quitar comentarios
        result = ejecutar_quitar_comentario(file_path, work_file)
       
        # Leer y reemplazar
        with open(work_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Usar expandtabs para convertir \t en espacios
        updated_content = content.expandtabs(spaces_per_tab)
        #elimina lineas en blanco
        lineas_sin_blanco = [linea for linea in updated_content.splitlines() if linea.strip()]
    
        # Unir de nuevo en un solo string
        updated_content = "\n".join(lineas_sin_blanco)

        #updated_content = [linea for linea in updated_content if linea.strip() != ""]
        # Guardar cambios
        with open(work_file, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
       
        
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

def Insertar_proceso(ifila,iespacios,itipo,inodo,inodo_sal=0,etiqueta='',xnum_grafo=0):
    global num_grafo
    text_eti=etiqueta
    xnum_grafo=num_grafo
    T_procesos.insert(ifila,[iespacios,itipo,inodo,inodo_sal,text_eti,num_grafo])

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
     

# busca la salida del bloque exceptuando palabras claves 
def buscar_salida_bloque(z,espacios,palabras_exc:list[str]=""):
    
    xfila=z
    espacios_obj=espacios
    max_item=len(T_procesos)
    while (T_procesos[xfila][0]>espacios_obj) or (T_procesos[xfila][1] in palabras_exc):
        xfila=xfila+1
        if xfila==max_item:
           return xfila -1
    return xfila

# busca una palabra en desde una posicion hacia arriba o hacia abajo(direcc=1 o -1)
def buscar_palabra(inicio,fin,espacios,palabras:list[str],direcc=1):
    
    
    num_palabra=0
    
    for yfila in range(inicio,fin,direcc):
        if (T_procesos[yfila][0]) == espacios:
            if  T_procesos[yfila][1] in palabras :
                num_palabra=yfila
    return num_palabra

def buscar_def():
    numdef=0
    for z in range(1,len(T_procesos)):
        global num_grafo
        proceso_ini=T_procesos[z][1]
        espacios_ini=T_procesos[z][0] 
        if proceso_ini=="def":
            num_grafo=num_grafo+1
            def_ini=z
            def_final=buscar_salida_bloque(def_ini+1,espacios_ini)-1
            etiqueta=T_procesos[z][4]
            for w in range(def_ini,def_final+1):
                T_procesos[w][5]=num_grafo
            texto_fin=etiqueta.find('(')
            #etiqueta=etiqueta[1:texto_fin]
            nombre_def=etiqueta[0:texto_fin]
            #etiqueta[1:texto_fin]
            numdef=numdef+1
            T_def.append([nombre_def,def_ini,def_final])

    num_grafo=0        
    return numdef
# Añadir procesos intermedios finales para if for while match 
def agregar_proces_inter() :   
    espacios_ini=0
    salida=0

    for x in range(1,len(T_procesos)):
        proceso_ini=T_procesos[x][1]
        espacios_ini=T_procesos[x][0]
        salida=0
        if T_procesos[x][1] in ("for","while","match"):   
            salida=0
            salida=buscar_salida_bloque(x+1,T_procesos[x][0])
            espacios=T_procesos[salida][0]
        elif T_procesos[x][1]=="if":    
            salida=0
            espacios=0
            salida=buscar_salida_bloque(x+1,T_procesos[x][0],["elif","else:"])
            espacios=T_procesos[salida][0]
        
        
        if salida!=0 and espacios<espacios_ini:
            nombre_proc="insertado"
            etiqueta_proc="Fin"+T_procesos[x][1]
            Insertar_proceso(salida,espacios_ini,nombre_proc,T_procesos[salida][2],0,etiqueta_proc,0) 
            


def examinar_proceso():
  nodos=1
  x=1
  while x < len(T_procesos):
    match T_procesos[x][1]: 
            case 'Inicio':
                agregar_nodo(T_procesos[x][5],nodos,T_procesos[x][1])
                agregar_arista(T_procesos[x][5],nodos,nodos+1,'inter')
                nodos=nodos+1
     
            case 'if':
                 
                nodoif=nodos
                agregar_nodo(T_procesos[x][5],nodos,T_procesos[x][1])
                agregar_arista(T_procesos[x][5],nodos,nodos+1,"si")
                nodos=nodos+1
                fin_if=0
                ultimo_si=0
                
                fin_if=buscar_salida_bloque(x+1,T_procesos[x][0],["elif","else:"])
                ultimo_si=buscar_salida_bloque(x+1,T_procesos[x][0])-1
                
                sigue_bloque=ultimo_si+1
                T_procesos[ultimo_si][3]= fin_if 
                T_procesos[ultimo_si][4]="fin_if"
                # busca si tiene else o elif si no tiene agrega la arista del no
                agregar_arista(T_procesos[x][5],nodoif,sigue_bloque,"no")             
                nodoelif_ant=0
            case 'elif': 
            
                nodoelif=nodos
                sigue_bloque=buscar_salida_bloque(x+1,T_procesos[x][0])
                agregar_nodo(T_procesos[x][5],nodos,T_procesos[x][1])
                agregar_arista(T_procesos[x][5],nodos,nodos+1,"si")

                agregar_arista(T_procesos[x][5],nodos,sigue_bloque,"no")        

                nodoelif_ant=nodoelif
                nodos=nodos+1
                

                ultimo_si=sigue_bloque-1
                T_procesos[ultimo_si][3]= fin_if 
                T_procesos[ultimo_si][4]="fin_if"

            case 'else:':

                # determinar si es de if o tipo else try o el try , busca hacia arriba if o else
                #def buscar_palabra(inicio,fin,espacios,palabras:list[str],direcc=1):
                npos=buscar_palabra(x-1, 1, T_procesos[x][0] ,["if","try:"],-1)  
                xtipo=T_procesos[npos][1]
                #xtipo=buscar_if_try(x-1,T_procesos[x][0])
                

                if xtipo=="if" :
                    agregar_nodo(T_procesos[x][5],nodos,T_procesos[x][1])
                    agregar_arista(T_procesos[x][5],nodos,nodos+1,T_procesos[x][1])
                    # agregar arista del if a else elif
                    nodo_ant=nodoif
            
                    nodos=nodos+1
                    

                    ultimo_si=buscar_salida_bloque(x+1,T_procesos[x][0])-1
                    T_procesos[ultimo_si][3]= fin_if 
                    T_procesos[ultimo_si][4]="fin_if"
                if xtipo=="try:" :  
                   nodoelse=nodos
                   agregar_nodo(T_procesos[x][5],nodos,"else_try")
                   
                   agregar_arista(T_procesos[x][5],nodos,nodos+1,T_procesos[x][1])
                  
                   
                   nodos=nodos+1




            case 'try:' : 
                nodotry=nodos
                nodo_finally=0
                num_except=0
                agregar_nodo(T_procesos[x][5],nodos,T_procesos[x][1])
                agregar_arista(T_procesos[x][5],nodos,nodos+1,"valid")
                nodos=nodos+1
                salida_try=0
                
                salida_try=buscar_salida_bloque(x+1,T_procesos[x][0],["else:","finally:","except"])
                fin_valid_tray=0
                fin_valid_tray=buscar_salida_bloque(x+1,T_procesos[x][0])-1
                
                #input("teclea")
                # busca else en try
                elsetry=0
                elsetry=buscar_palabra(x+1,salida_try-1,T_procesos[x][0],["else:"])
                
                # buscar finally
                n_finally=0
                n_finally=buscar_palabra(x+1,salida_try-1,T_procesos[x][0],["finally:"])

                
                # busca else en try
                if elsetry !=0 :
                    T_procesos[fin_valid_tray][3]= elsetry
                    T_procesos[fin_valid_tray][4]="exito"

                else: 
                    
                    if n_finally !=0  :
                       T_procesos[fin_valid_tray][3]= n_finally
                       T_procesos[fin_valid_tray][4]="exito"
                    else:
                       T_procesos[fin_valid_tray][3]= salida_try
                       T_procesos[fin_valid_tray][4]="exito"

            case 'finally:':
                nodofinally=nodos
                
                agregar_nodo(T_procesos[x][5],nodos,T_procesos[x][1])
                agregar_arista(T_procesos[x][5],nodos,nodos+1,T_procesos[x][1])
                
                nodos=nodos+1
                fin_finally=0  
                esp_finally=0          
                fin_finally=buscar_salida_bloque(x+1,T_procesos[x+1][0])
                T_procesos[fin_finally][3]= salida_try
                T_procesos[fin_except][4]="fin try"   
                
            case 'except' : 
                num_except=num_except+1
                text_nodo="Except "+str(num_except)
                nodoexcept=nodos
                
                agregar_nodo(T_procesos[x][5],nodos,text_nodo)
                agregar_arista(T_procesos[x][5],nodos,nodos+1,T_procesos[x][1])
                # arista de try a except
                agregar_arista(T_procesos[x][5],nodotry,nodos,T_procesos[x][1])
                nodos=nodos+1
                fin_except=0  
                         
                fin_except=buscar_salida_bloque(x+1,T_procesos[x][0])-1
                
                if n_finally !=0 :
                    T_procesos[fin_except][3]= n_finally
                    T_procesos[fin_except][4]=""
                else:
                    T_procesos[fin_except][3]= salida_try
                    T_procesos[fin_except][4]=""

                
            
        
            case 'while':

                nodowhile=T_procesos[x][2]
                espacios= T_procesos[x][0]
                salida_while=buscar_salida_bloque(x+1,espacios)
                agregar_nodo(T_procesos[x][5],nodos,'while')
                agregar_arista(T_procesos[x][5],nodos,nodos+1,"while 1")  
                nodos=nodos+1
       
        
                agregar_arista(T_procesos[x][5],nodowhile,salida_while,"while 3")  
                #modificamos retorno fin while retorno
          
                T_procesos[salida_while-1][3]=nodowhile 
                T_procesos[salida_while-1][4]="wh r"
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

            case 'match':
                nodo_match=x
                agregar_nodo(T_procesos[x][5],nodos,'match')
                nodos=nodos+1
                espacios_match=T_procesos[x][0]
                salida_match=buscar_salida_bloque(x+1,espacios_match)
                ultimo_match=salida_match-1
                numcase=0

            case 'case':
                #T_case=[["linea_case"]]
                numcase=numcase+1
                nodo_case=x
                espacios_case=T_procesos[x][0]
                agregar_nodo(T_procesos[x][5],nodos,'case')
                nodos=nodos+1
                agregar_arista(T_procesos[x][5],nodo_match,nodo_case,'case'+str(numcase))
                agregar_arista(T_procesos[x][5],nodo_case,nodo_case+1,'case'+str(numcase))
                salida_case=buscar_salida_bloque(x+1,espacios_case)
                ultimo_case=salida_case-1
       
                #modificar salida de los cases
                T_procesos[ultimo_case][3]=salida_match
                T_procesos[ultimo_case][4]='fin case'+str(numcase)

            case 'intermedio'|'insertado':
                nodosigue=0
                agregar_nodo(T_procesos[x][5],nodos,T_procesos[x][1])
                if T_procesos[x][4]=="":
                    texto_arista="inter"
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
    x=x+1

#paso 2 leer fichero e identificar palabras clave y crear tabla procesos    
def leerf_palab_crear_proc(work_file):
    
    with open(work_file, 'r', encoding='utf-8') as archivo:
        
        Nivel_ident=1
        tipo="intermedio"
        nodo=1
        sw_newnode=1
        espacios_ant=0
    
        num_grafo=0
                
        # Cuenta 
        for numero_linea, linea in enumerate(archivo, start=1): 
            espacios = contar_espacios_inicio(linea)
            tipo="intermedio"
            if espacios != espacios_ant:
                sw_newnode=1
            cadena = linea
            palabras = cadena.split()
            if not palabras :
                continue
            
            if  palabras[0][0] == "#" :
                continue
                # print(palabras[0]) 
                    
            etiqueta=""    
            if palabras[0] in ("try:","except","finally:","def","if","for","while","match","elif","else:","match","case"):
                tipo=palabras[0]
                nodo_ant=nodo
                sw_newnode=1
                
                if palabras[0]=="def":
                    etiqueta=palabras[1]
                else:
                    etiqueta=""    
        
            
            
            if sw_newnode == 1:    
                T_procesos.append([espacios,tipo,nodo,0,etiqueta,0])
                sw_newnode=0
                nodo=nodo+1
            espacios_ant=espacios



    # Modificar inicio y fin para grafo 0
        T_procesos.insert(1,[0,'Inicio',1,0,'',0])
        
        x=len(T_procesos)
        T_procesos.append([0,'Fin',x+1,0,'',0]) 
        

        
    # Añadir procesos intermedios finales para if for while match           
    agregar_proces_inter()    
      
# paso 1 reemplazar tabuladores por espacios y copiar en file.txt 
def remmplaz_tab_cop_file(mi_archivo):
    ruta = Path(mi_archivo) # archivo a tratar
    
    nombre_dirsel=""
    Nombre_arch = ruta.stem
    directorio_arc = ruta.parent
    
   
 
    if directorio_sel!="" and directorio_sel!=directorio_arc:
        
        nombre_dirsel=directorio_sel
       
        nombre_dirsel="("+str(nombre_dirsel).replace("/", "_")+")"

   
    repo_root = obtener_repo_root()
   
    Directoriow=repo_root / "pruebas_herramientas" / "resultados"  # directorio trabajo
    if not os.path.exists(Directoriow):  
            os.makedirs(Directoriow)  
          
    

    work_file = Directoriow / f"{Nombre_arch}dcc.txt"
    grafo_file = Directoriow / f"{Nombre_arch}dcc"

    replace_tabs_with_spaces(ruta, work_file,  spaces_per_tab=4)
    return(work_file,grafo_file,repo_root,ruta)
#tratar def
def tratar_def():
    numdef=0
    T_def=[["nombre_def","fila_ini","fila_fin"]]

    numdef=buscar_def()
    numero_grafos=max(fila[5] for fila in T_procesos)
    return(numero_grafos)
# generar tabla de nodos Tnodos y aristas Taristas y generar grafo
def generar_nodos_aristas():
    global T_nodos,T_aristas,T_procesos
    graphviz_bin = repo_root / "herramientas" / "graphviz" / "bin"
    os.environ["PATH"] += os.pathsep + str(graphviz_bin) 
    for n_grafo in range(0,numero_grafos+1):
        # Modificar inicio y fin para grafo !=0
        

        T_nodos=[[num_grafo,"NUM_nodo","Nomb_nodo"]]
        T_aristas=[[num_grafo,"Nodo_I","Nodo_F","Texto_A"]]
       
        filtradas = [sublista for sublista in cop_T_procesos if sublista[5]== n_grafo]
        T_procesos=copy.deepcopy(filtradas)
        if n_grafo!=0:
            T_procesos.insert(1,[0,'Inicio',1,0,'',n_grafo])
        
            x=len(T_procesos)
            T_procesos.append([0,'Fin',len(T_procesos)-1,0,'',n_grafo]) 
        
        #Renumerar
        for z in range(1,len(T_procesos)):
            T_procesos[z][2]=z
        
        
        filas = len(T_procesos)
        
        nodos=1

        # examina el array proceso y genera los arrays nodos y aristas del grafo
        examinar_proceso()

            
        #Tabla aristas y nodos tienen cabecera en 0 
        calc_ciclo=(len(T_aristas) -1) - (len(T_nodos) -1) +2
        
        Nombre_grafico=""
        #nproc=T_procesos[n_grafo][5]
        mruta=ruta.as_posix()
        if n_grafo != 0:
            mruta=mruta + " def: " + T_def[n_grafo][0]
        
        Texto_Label= str(f"{mruta} \n Calculo complejidad ciclomatica (nº aristas-nº nodos +2): {str(len(T_aristas)-1)} - {str(len(T_nodos)-1)} +2= {str(calc_ciclo)}")
        from graphviz import Digraph    

        dot = Digraph(name=str(ruta), comment='Flujo de procesar_datos', format='pdf')
        dot.attr(label=Texto_Label, fontsize="18", labelloc="t")
        # numero de grafos len(T_def) -1 + 1 del principal(0) = len(T_def)

        for x in range(1,len(T_nodos)):
            dot.node(T_nodos[x][1],T_nodos[x][2])
        # ultimo nodo 'fin' en negrita
        dot.node(T_nodos[len(T_nodos)-1][1],T_nodos[len(T_nodos)-1][2],fontname="Helvetica-Bold")  

        for x in range(1,len(T_aristas)):
            dot.edge(T_aristas[x][1],T_aristas[x][2],T_aristas[x][3])
        
        grafo_file1 = Path(str(grafo_file) + str(n_grafo))
        grafo_file1pdf = Path(str(grafo_file1) + ".pdf")
        T_grafos_files.append(grafo_file1pdf)
        
        
        
        output_path = dot.render(engine="dot",filename=str(grafo_file1), cleanup=bool)
        dot.clear()
# fusionar pdf's 

def fusionar_pdfs():
    marca_tiempo=datetime.today().strftime("%Y%m%d%H%M%S")
    Nombre_arch_sin_ext = Path(ruta).stem
    nombre_pdf_final = f"{Nombre_arch_sin_ext}_dcc_{marca_tiempo}.pdf"
    Directoriow=repo_root / "src"/ "analizador_calidad_software" / "resultados"   # directorio trabajo
    grafo_file = Directoriow / nombre_pdf_final
    fusionador = PdfWriter()
    for pdf in T_grafos_files:
        fusionador.append(pdf)

    print(f'grafo_file:{grafo_file}')
    fusionador.write(grafo_file)
    fusionador.close()  
    return grafo_file

# flujo principal generar grafos         
def flujo_grafos_python(arch = "") :
    global mi_archivo,directorio_sel,work_file,grafo_file,repo_root,ruta,num_grafo,numero_grafos  
    global T_procesos,cop_T_procesos,T_def,T_grafos_files,T_nodos,T_aristas
    # Crear ventana principal oculta
    #root = tk.Tk()
    #root.withdraw()  # Oculta la ventana principal

    # Llamar a la función
    if arch != "":
        mi_archivo = arch
    else:    
        mi_archivo=seleccionar_archivo()

    #Esta es la ruta del archivo
    directorio_sel=""

    if len(sys.argv) >= 1:
        directorio_sel= Path(sys.argv[0])
    


    # Procesar fichero 
    # paso 1 reemplazar tabuladores por espacios y copiar en file.txt
    work_file,grafo_file,repo_root,ruta=remmplaz_tab_cop_file(mi_archivo)


    #paso 2 leer fichero e identificar palabras clave y crear tabla procesos 
    num_grafo=0 
    T_procesos=[["INDEN","TIPO","NODOI","NODO_sal","etiqueta",num_grafo]]  
    leerf_palab_crear_proc(work_file)   

    #tratar def
    T_def=[["nombre_def","fila_ini","fila_fin"]]
    numero_grafos=tratar_def()

    # preparar tabla pdfs
    T_grafos_files=[]
    #realiza copia de T_proceso para segmentar grafos
    cop_T_procesos=copy.deepcopy(T_procesos)

    # generar tabla de nodos Tnodos y aristas Taristas y generar grafos
    generar_nodos_aristas()

    # fusionar pdf's 
    print(f"Fusionando archivos")
    ruta = fusionar_pdfs()

    # borrar archivos de trabajo pdfs y work_file.txt
    for pdf in T_grafos_files:
        os.remove(pdf)
    os.remove(work_file)     
    return ruta

#              *** fin def ******

if __name__ == "__main__":
    flujo_grafos_python()