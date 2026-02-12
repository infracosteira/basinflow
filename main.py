#myapp.py
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import networkx as nx
import numpy as np
from data_utils import clean_dataframe_columns, FILE_SCHEMAS, load_dat_file, calculate_water_routing, calculate_sediment_routing

logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s - %(levelname)s: %(message)s'
logging.basicConfig(filename='myapp.log', level=logging.INFO,format=FORMAT)
logger.info('Started')

dataframes = {}

def selecionar_arquivo(entry_widget, chave):

    file_path = filedialog.askopenfilename(
        title=f"Selecionar arquivo {chave}",
        filetypes=[("Arquivos DAT", "*.dat"), ("Todos os arquivos", "*.*")]
    )

    if not file_path:
        return

    entry_widget.config(state=tk.NORMAL)
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, file_path)
    entry_widget.config(state=tk.DISABLED)

    try:
        config = FILE_SCHEMAS[chave]

        df = load_dat_file(
            file_path,
            config,
            clean_dataframe_columns
        )

        dataframes[chave] = df

        txt_saida['state'] = tk.NORMAL
        txt_saida.insert(tk.END, f"Arquivo '{chave}' carregado com sucesso\n")
        txt_saida.see(tk.END)
        txt_saida['state'] = tk.DISABLED

    except Exception as e:
        messagebox.showerror(
            "Erro",
            f"Erro ao ler o arquivo {chave}:\n{e}"
        )

        txt_saida['state'] = tk.NORMAL
        txt_saida.insert(tk.END, f"Erro ao ler o arquivo {chave}:\n{e}\n")
        txt_saida.see(tk.END)
        txt_saida['state'] = tk.DISABLED


def toggle_sedimentos():
    
    # Define o estado com base no valor do checkbox
    novo_estado = tk.NORMAL if sedimentos_checkbox.get() else tk.DISABLED
    #                NORMAL = HABILITADO DISABLED = DESABILITADO
    # Lista de componentes que devem ser habilitados/desabilitados
    componentes = [ent_sed, btn_sed, rb_file, rb_manual, ent_param_file, btn_param_file, ent_density, ent_efficiency]
    
    for comp in componentes:
        comp.config(state=novo_estado)

# --- Interface Principal ---
root = tk.Tk()
root.title("Simulador Hidrológico")
root.geometry("650x800")

# 1. ENTRADA DE DADOS
frame_entrada = tk.LabelFrame(root, text="Entrada de dados", padx=10, pady=10)
# pad adiciona espaço interno

frame_entrada.pack(fill="x", padx=20, pady=10)
#o pack com fill="x" faz o frame ocupar toda a largura disponível, então esse retagunlo em especifico
#vai ser o retangulo que engloba toda a seção de entrada de dados
labels = ["routing.dat", "runoff.dat", "reservoir.dat"]

row_name = tk.Frame(frame_entrada)
row_name.pack(fill="x", pady=2)
tk.Label(row_name, text=f"Nome do arquivo:", width=25, anchor="w").pack(side="left")
ent_name = tk.Entry(row_name, state=tk.NORMAL)
ent_name.pack(side='left', expand=True,fill='x',padx=5)

for label in labels:
    row = tk.Frame(frame_entrada)
    row.pack(fill="x", pady=2)

    tk.Label(row, text=f"Carregar arquivo {label}:", width=25, anchor="w").pack(side="left")

    ent = tk.Entry(row, textvariable=label, state=tk.DISABLED)
    ent.pack(side="left", expand=True, fill="x", padx=5)

    tk.Button(
        row,
        text="...",
        command=lambda e=ent, l=label: selecionar_arquivo(e, l)
    ).pack(side="right")


# 2. SIMULAR DINÂMICA DE SEDIMENTOS
sedimentos_checkbox = tk.BooleanVar(value=False) # Começa DESMARCADA
frame_sedimentos = tk.LabelFrame(root, padx=15, pady=10)
frame_sedimentos.pack(fill="x", padx=20, pady=10)

check_btn = tk.Checkbutton(frame_sedimentos, text="Simular dinâmica de sedimentos", 
                           variable=sedimentos_checkbox, command=toggle_sedimentos, font=('Arial', 10, 'bold'))

frame_sedimentos.configure(labelwidget=check_btn)

# Linha do arquivo sedyield.dat
row_sed = tk.Frame(frame_sedimentos)
row_sed.pack(fill="x", pady=5)
tk.Label(row_sed, text="Carregar arquivo sedyield.dat:", width=25, anchor="w").pack(side="left")
ent_sed = tk.Entry(row_sed, state=tk.DISABLED)
ent_sed.pack(side="left", expand=True, fill="x", padx=5)
btn_sed = tk.Button(row_sed, text="...", state=tk.DISABLED, command=lambda: selecionar_arquivo(ent_sed, "sedyield.dat"))
btn_sed.pack(side="right")

# Sub-seção Parâmetros Sedimentológicos

subframe_params = tk.LabelFrame(frame_sedimentos, text="Parâmetros sedimentológicos", padx=10, pady=10)
subframe_params.pack(fill="x", pady=5)

radio_var = tk.IntVar(value=1)

# Opção 1: Carregar do arquivo
row_p1 = tk.Frame(subframe_params)
row_p1.pack(fill="x")
rb_file = tk.Radiobutton(row_p1, text="Carregar do arquivo:", variable=radio_var, value=1, state=tk.DISABLED)
rb_file.pack(side="left")
ent_param_file = tk.Entry(row_p1, state=tk.DISABLED)
ent_param_file.pack(side="left", expand=True, fill="x", padx=5)
btn_param_file = tk.Button(row_p1, text="...", state=tk.DISABLED, command=lambda: selecionar_arquivo(ent_param_file, "sed_param.dat"))
btn_param_file.pack(side="right")

# Opção 2: Valores manuais
rb_manual = tk.Radiobutton(subframe_params, text="Utilizar valores abaixo:", variable=radio_var, value=2, state=tk.DISABLED)
rb_manual.pack(anchor="w")

# Campos de densidade e eficiência
row_manual = tk.Frame(subframe_params)
row_manual.pack(fill="x", padx=20)
tk.Label(row_manual, text="Densidade aparente seca da barragem de terra (g/cm³):").grid(row=0, column=0, sticky="w")
ent_density = tk.Entry(row_manual, width=10, state=tk.DISABLED)
ent_density.insert(0, "1,5")
ent_density.grid(row=0, column=1, padx=5, pady=2)

tk.Label(row_manual, text="Eficiência da retenção de sedimentos em reservatórios (%):").grid(row=1, column=0, sticky="w")
ent_efficiency = tk.Entry(row_manual, width=10, state=tk.DISABLED)
ent_efficiency.insert(0, "50%")
ent_efficiency.grid(row=1, column=1, padx=5, pady=2)

# FUNÇÃO PRINCIPAL DE CÁLCULO

def on_calcular_click():

    if ent_name.get():
        nome = ent_name.get()
    else:
        nome = "result_discharge"

    logger.info('Cálculo iniciado pelo usuário')

    txt_saida['state'] = tk.NORMAL
    txt_saida.insert(tk.END, f"Cálculo iniciado pelo usuário...\n")
    txt_saida.see(tk.END)
    txt_saida['state'] = tk.DISABLED

    df_reservoir = dataframes.get('reservoir.dat')
    df_routing = dataframes.get('routing.dat')
    df_runoff = dataframes.get('runoff.dat')

    txt_saida['state'] = tk.NORMAL
    txt_saida.insert(tk.END, f"Calculando casos de ruptura...\n")
    txt_saida.see(tk.END)
    txt_saida['state'] = tk.DISABLED 

    result_discharge, G, ruptura_dict, sequencia_processamento, df_merged = calculate_water_routing(
    df_reservoir,
    df_routing,
    df_runoff
)

    
    if sedimentos_checkbox.get():

        df_sedyield = dataframes.get('sedyield.dat')
        if df_sedyield is None:
            messagebox.showerror("Erro", "Arquivo sedyield.dat não carregado.")
            return

        if radio_var.get() == 1:
            df_sed_param = dataframes.get('sed_param.dat')
            if df_sed_param is None:
                messagebox.showerror("Erro", "Arquivo sed_param.dat não carregado.")
                return
            density = None
            efficiency = None
        else:
            try:
                density = float(ent_density.get().replace(',', '.')) if ent_density.get() else 1.5
                efficiency = float(ent_efficiency.get().replace('%','').replace(',', '.')) / 100 if ent_efficiency.get() else 0.5
                df_sed_param = None
            except ValueError:
                messagebox.showerror("Erro", "Valores manuais inválidos.")
                return

        result_discharge = calculate_sediment_routing(
            result_discharge,
            G,
            ruptura_dict,
            sequencia_processamento,
            df_sedyield,
            df_merged,
            radio_var.get(),
            df_sed_param,
            density,
            efficiency
        )


        # Se valor manual não foi passado, usa padrão físico
        default_density = density_manual if density_manual is not None else 1.5
        default_efficiency = efficiency_manual if efficiency_manual is not None else 0.50

        sedimentos_discharge = pd.DataFrame(columns=["subasin_id"])
        sedimentos_discharge["subasin_id"] = result_discharge["subasin_id"]

        sedimentos_discharge['volume_sedimento_erodido'] = (
            result_discharge['rompeu'] * m * ( result_discharge['volume_total'] * pm_fenda * df_merged['dam_height'] ) ** n).round(2)

        sedimentos_discharge['massa_sedimento_erodido'] = (
            sedimentos_discharge['volume_sedimento_erodido'] * default_density
        ).round(2)

        sed_in = {} # Massa de sedimentos afluente - sediment routing (ton)
        sed_out = {} # Massa de sedimentos efluente - sediment routing (ton)

        logger.info('Iniciando cálculo de sedimentos')

        for i in sequencia_processamento:

            upstreams = list(G.predecessors(i)) #lista com todas as bacias acima da bacia atual

            # Tenta pegar do mapa (arquivo). Se não existir ou for modo manual, usa o default
            if radio_var.get() == 1:
                # No modo arquivo, se o ID não existir no .dat, você pode definir um fallback
                current_density = density_map.get(i)
                current_efficiency = efficiency_map.get(i)
            else:
                current_density = default_density
                current_efficiency = default_efficiency

            sed_local = G.nodes[i]['sed_enter_volume'] 

            if upstreams:
                sed_in[i] = sed_local + sum(sed_out[up] for up in upstreams)
            else:
                sed_in[i] = sed_local

            # 2. Saída de sedimentos
            if ruptura_dict[i]:
                # Cálculo da massa erodida local usando a densidade específica deste nó
                vol_erodido = sedimentos_discharge.loc[sedimentos_discharge['subasin_id'] == i, 'volume_sedimento_erodido'].values[0]
                massa_erodida = vol_erodido * current_density
                
                sed_out[i] = sed_in[i] + massa_erodida
            else:
                # Se não rompeu, aplica a eficiência de retenção
                sed_out[i] = current_efficiency * sed_in[i]

            """ print(
                f"Açude {i} | "
                f"Sed_in = {sed_in[i]:.2f} | "
                f"Sed_out = {sed_out[i]:.2f} | "
                f"Rompeu = {ruptura_dict[i]}"
            ) """

        logger.info('Finalizando cálculo de sedimentos')

        sedimentos_discharge['sedimento_afluente'] = (sedimentos_discharge['subasin_id'].map(sed_in).round(2))
        sedimentos_discharge['sedimento_efluente'] = (    sedimentos_discharge['subasin_id'].map(sed_out).round(2))

        result_discharge = result_discharge.merge(
            sedimentos_discharge,
            on='subasin_id')
        """ print("result_discharge com sedimentos:")
        print(result_discharge.head(10)) """

    result_discharge.to_csv(f"{nome}.dat", index=False)

    """ print("calculo de sedimentos finalizado!") """

    txt_saida['state'] = tk.NORMAL
    txt_saida.insert(tk.END, f"O arquivo {nome}.dat foi gerado com sucesso! \n")
    txt_saida.see(tk.END)
    txt_saida['state'] = tk.DISABLED
    

btn_calcular = tk.Button(root, command=on_calcular_click, text="Calcular", bg="#d9d9d9", font=('Arial', 12, 'bold'), height=2)
btn_calcular.pack(pady=15, padx=20, fill="x")

# 4. ÁREA DE SAÍDA (LOG)    
frame_saida = tk.LabelFrame(root, text="Saída", padx=10, pady=10)
frame_saida.pack(fill="both", expand=True, padx=20, pady=10)
txt_saida = tk.Text(frame_saida, height=6, bg="#ffffff", state=tk.DISABLED)
txt_saida.pack(fill="both", expand=True)


root.mainloop()

logger.info('Finished') 


#Diminuir o acoplamento usar mvc